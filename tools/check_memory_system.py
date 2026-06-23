"""Validate the project memory-system shape.

This is the gate that keeps the agent operating contract, runbooks, and topic
memory internally consistent and free of rot. It enforces structure, not
content: required files exist, the handoff holds only current state, topic memory
follows the standard section shape, the contract routes to the right runbooks,
AGENTS.md and CLAUDE.md stay byte-identical, and the security gate is wired into
every place it must run. Run it locally and in CI.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    'AGENTS.md',
    'CLAUDE.md',
    '.github/workflows/ci.yml',
    '.claude/settings.json',
    '.claude/hooks/session-start-context.sh',
    '.claude/skills/long-running-project-memory/SKILL.md',
    'PROJECT_MEMORY.md',
    'AGENT_HANDOFF.md',
    'docs/memory/workflow.md',
    'docs/memory/deployment.md',
    'docs/memory/production.md',
    'docs/memory/frontend.md',
    'docs/memory/security.md',
    'docs/memory/architecture.md',
    'docs/memory/typescript.md',
    'docs/plans/README.md',
    'docs/site_history/README.md',
    'deploy.sh',
    'docs/runbooks/task-memory-triage.md',
    'docs/runbooks/website-change.md',
    'docs/runbooks/docs-change.md',
    'docs/runbooks/security-implementation.md',
    'docs/runbooks/ui-verification.md',
    'docs/runbooks/deploy-backup.md',
    'docs/runbooks/production-ops.md',
    'docs/runbooks/memory-maintenance.md',
    'docs/runbooks/memory-review.md',
    'hooks/pre-commit',
    'tools/check_security_patterns.py',
]

# The handoff is current-state only. These headings signal history has leaked in.
FORBIDDEN_HANDOFF_HEADINGS = [
    '## Latest Completed',
    '## Changelog',
    '## Completed History',
    '## Deferred Follow-ups',
]

ALLOWED_HANDOFF_HEADINGS = {
    '# Agent Handoff',
    '## Active State Summary',
}

HANDOFF_HISTORY_PATTERNS = [
    r'\bdone\s*\+\s*deployed\b',
    r'\bcomplete\s*/\s*deployed\b',
    r'\bcompleted\s*/\s*deployed\b',
    r'\bdeployed\s*\+\s*live-verified\b',
    r'\blive-verified\b',
    r'\bdeployed via\b',
    r'\bshipped latest\b',
    r'\bdetail(?:s)? in changelog\b',
    r'\bsee changelog\b',
    r'\bdone end to end\b',
    r'\bno longer deferred\b',
    r'\bcommit(?:ted)?\s+(?:repo\s+)?state\b',
]

HANDOFF_DEPLOY_RUN_PATTERN = re.compile(r'\bdeploy run\b', re.IGNORECASE)
ACTIVE_DEPLOY_WORDS = (
    'active',
    'blocked',
    'failed',
    'in progress',
    'pending',
    'running',
    'waiting',
)

REQUIRED_TOPIC_SECTIONS = [
    '## Current Setup',
    '## Current Rules',
    '## Runbooks',
    '## Lookup Anchors',
    '## Deprecated / Historical',
]

MAX_HANDOFF_LINES = 120

DATED_CURRENT_PATTERN = re.compile(r'\bas of\s+\d{4}-\d{2}-\d{2}\b', re.IGNORECASE)
LAST_VERIFIED_PATTERN = re.compile(r'\bLast verified\s+\d{4}-\d{2}-\d{2}\b')
NUMBER_PATTERN = re.compile(r'\b\d{2,3}(?:,\d{3})*\b')

# Topic files where a Current Setup count is volatile and must carry a
# "Last verified YYYY-MM-DD" date. Map "docs/memory/<topic>.md" -> matching terms.
# The base template ships with none; add your own as your memory grows.
VOLATILE_COUNT_TERMS: dict[str, tuple[str, ...]] = {}

REQUIRED_MEMORY_REVIEW_PHRASES = [
    'Do not propose structural memory revisions when checks pass',
    'If the automated check passes and no rubric item fails',
]

CLAUDE_STARTUP_HOOK_COMMAND = '"$CLAUDE_PROJECT_DIR"/.claude/hooks/session-start-context.sh'

REQUIRED_SECURITY_RUNBOOK_PHRASES = [
    'Applicability Check',
    'Banned By Default',
    'Approved Patterns',
    'Required Negative Tests',
    'Static Gate',
    'Closeout',
    'RCE',
    'SQLi',
    'IDOR',
    'CSRF',
    'XSS',
    'open redirect',
    'SSTI',
    'SSRF',
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


def compact(text: str) -> str:
    return ' '.join(text.split())


def markdown_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    selected: list[str] = []
    in_section = False
    for line in lines:
        if line.startswith('## '):
            if in_section:
                break
            in_section = line == heading
            continue
        if in_section:
            selected.append(line)
    return '\n'.join(selected)


def bullet_blocks(section: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for line in section.splitlines():
        if line.startswith('- '):
            if current:
                blocks.append('\n'.join(current))
            current = [line]
            continue
        if current and (line.startswith('  ') or not line.strip()):
            current.append(line)
            continue
        if current:
            blocks.append('\n'.join(current))
            current = []
    if current:
        blocks.append('\n'.join(current))
    return blocks


def fail(message: str) -> None:
    raise SystemExit(f'memory-system check failed: {message}')


def require_claude_startup_hook() -> None:
    settings_path = ROOT / '.claude' / 'settings.json'
    try:
        settings = json.loads(settings_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        fail(f'.claude/settings.json is invalid JSON: {exc}')

    session_hooks = settings.get('hooks', {}).get('SessionStart', [])
    if not isinstance(session_hooks, list):
        fail('.claude/settings.json SessionStart hooks must be a list')

    has_startup_hook = False
    for entry in session_hooks:
        if not isinstance(entry, dict):
            continue
        for hook in entry.get('hooks', []):
            if not isinstance(hook, dict):
                continue
            if (
                hook.get('type') == 'command'
                and hook.get('command') == CLAUDE_STARTUP_HOOK_COMMAND
            ):
                has_startup_hook = True

    if not has_startup_hook:
        fail('.claude/settings.json must register the Claude SessionStart context hook')

    script_path = ROOT / '.claude' / 'hooks' / 'session-start-context.sh'
    if not script_path.stat().st_mode & 0o111:
        fail('.claude/hooks/session-start-context.sh must be executable')

    script = script_path.read_text(encoding='utf-8')
    for required_file in ('AGENTS.md', 'AGENT_HANDOFF.md', 'PROJECT_MEMORY.md'):
        if required_file not in script:
            fail(f'Claude SessionStart hook must inject {required_file}')
    if 'Before any tool use' not in script:
        fail('Claude SessionStart hook must remind Claude to classify before tool use')


def require_handoff_current_state(handoff: str) -> None:
    handoff_lines = handoff.splitlines()
    if len(handoff_lines) > MAX_HANDOFF_LINES:
        fail(f'AGENT_HANDOFF.md has {len(handoff_lines)} lines; max is {MAX_HANDOFF_LINES}')

    for line in handoff_lines:
        if not line.startswith('#'):
            continue
        if line not in ALLOWED_HANDOFF_HEADINGS:
            fail(
                'AGENT_HANDOFF.md must use only the standard active-state '
                f'headings; found {line!r}'
            )

    for heading in FORBIDDEN_HANDOFF_HEADINGS:
        if heading in handoff:
            fail(f'AGENT_HANDOFF.md contains forbidden heading {heading!r}')

    compacted = compact(handoff).lower()
    for pattern in HANDOFF_HISTORY_PATTERNS:
        if re.search(pattern, compacted):
            fail(
                'AGENT_HANDOFF.md appears to contain completed-work history '
                f'matching /{pattern}/'
            )

    for line_no, line in enumerate(handoff_lines, start=1):
        lowered = line.lower()
        if not HANDOFF_DEPLOY_RUN_PATTERN.search(lowered):
            continue
        if not any(word in lowered for word in ACTIVE_DEPLOY_WORDS):
            fail(
                'AGENT_HANDOFF.md references a deploy run without active '
                f'state context on line {line_no}'
            )


def require_project_memory_routes_all_topics(project_memory: str) -> None:
    for topic_path in sorted((ROOT / 'docs/memory').glob('*.md')):
        relative = str(topic_path.relative_to(ROOT))
        if relative not in project_memory:
            fail(f'PROJECT_MEMORY.md must route topic memory file {relative}')


def require_plan_readme_indexes_all_plans(plans_readme: str) -> None:
    for plan_path in sorted((ROOT / 'docs/plans').glob('*.md')):
        if plan_path.name == 'README.md':
            continue
        if plan_path.name not in plans_readme:
            fail(f'docs/plans/README.md must index {plan_path.name}')


def require_current_setup_dates_are_verified(topic_path: Path, text: str) -> None:
    current_setup = markdown_section(text, '## Current Setup')
    for block in bullet_blocks(current_setup):
        if DATED_CURRENT_PATTERN.search(block) and not LAST_VERIFIED_PATTERN.search(block):
            fail(
                f'{topic_path.relative_to(ROOT)} has an "as of" date in '
                'Current Setup without "Last verified YYYY-MM-DD" wording'
            )


def require_volatile_counts_are_verified(topic_path: Path, text: str) -> None:
    relative = str(topic_path.relative_to(ROOT))
    terms = VOLATILE_COUNT_TERMS.get(relative)
    if not terms:
        return
    current_setup = markdown_section(text, '## Current Setup')
    for block in bullet_blocks(current_setup):
        lowered = block.lower()
        if not any(term in lowered for term in terms):
            continue
        if NUMBER_PATTERN.search(block) and not LAST_VERIFIED_PATTERN.search(block):
            fail(
                f'{relative} has volatile Current Setup counts without '
                '"Last verified YYYY-MM-DD" wording'
            )


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        fail(f'missing required memory/runbook files: {", ".join(missing)}')

    handoff = read('AGENT_HANDOFF.md')
    require_handoff_current_state(handoff)

    project_memory = read('PROJECT_MEMORY.md')
    if 'docs/site_history/' not in project_memory:
        fail('PROJECT_MEMORY.md must route archived historical context')
    if 'This file is the memory router' not in project_memory:
        fail('PROJECT_MEMORY.md must remain a routing/index file')
    if 'docs/plans/' not in project_memory:
        fail('PROJECT_MEMORY.md must route deferred implementation plans')
    require_project_memory_routes_all_topics(project_memory)

    for topic_path in (ROOT / 'docs/memory').glob('*.md'):
        text = topic_path.read_text(encoding='utf-8')
        missing_sections = [section for section in REQUIRED_TOPIC_SECTIONS if section not in text]
        if missing_sections:
            fail(f'{topic_path.relative_to(ROOT)} missing sections: {", ".join(missing_sections)}')
        require_current_setup_dates_are_verified(topic_path, text)
        require_volatile_counts_are_verified(topic_path, text)

    agents = read('AGENTS.md')
    if 'Do not read `CHANGELOG.md` or `docs/site_history/` at startup by default.' not in agents:
        fail('AGENTS.md must keep history archives out of default startup reads')
    if 'docs/runbooks/memory-review.md' not in agents:
        fail('AGENTS.md must route memory reviews to docs/runbooks/memory-review.md')
    if 'docs/runbooks/security-implementation.md' not in agents:
        fail('AGENTS.md must route runtime security work to security-implementation.md')
    if 'docs/site_history/' not in agents:
        fail('AGENTS.md must include the site-history archive layer')
    if 'Do not make project-wide or structural recommendations from partial reads' not in compact(agents):
        fail('AGENTS.md must require proportional context before broad advice')

    claude = read('CLAUDE.md')
    if claude != agents:
        fail('CLAUDE.md must be an exact byte-for-byte mirror of AGENTS.md')
    if 'Treat sources outside the repo-backed hierarchy as leads' not in claude:
        fail('CLAUDE.md must keep the repo-backed source authority rule')

    require_claude_startup_hook()

    memory_review = read('docs/runbooks/memory-review.md')
    for phrase in REQUIRED_MEMORY_REVIEW_PHRASES:
        if phrase not in memory_review:
            fail(f'memory-review runbook missing anti-churn phrase: {phrase!r}')
    if 'whole relevant memory system' not in memory_review:
        fail('memory-review runbook must require full relevant context for structural advice')

    security_runbook = read('docs/runbooks/security-implementation.md')
    for phrase in REQUIRED_SECURITY_RUNBOOK_PHRASES:
        if phrase not in security_runbook:
            fail(f'security implementation runbook missing required phrase: {phrase!r}')

    website_change = read('docs/runbooks/website-change.md')
    if 'docs/runbooks/security-implementation.md' not in website_change:
        fail('website-change runbook must require the security implementation gate')
    if 'python3 tools/check_security_patterns.py' not in website_change:
        fail('website-change runbook must run the security pattern checker')

    deploy_backup = read('docs/runbooks/deploy-backup.md')
    if 'python3 tools/check_security_patterns.py' not in deploy_backup:
        fail('deploy-backup runbook must include the security pattern checker')

    pre_commit = read('hooks/pre-commit')
    if 'python3 tools/check_security_patterns.py' not in pre_commit:
        fail('pre-commit hook must run the security pattern checker')

    ci = read('.github/workflows/ci.yml')
    if 'python3 tools/check_security_patterns.py' not in ci:
        fail('GitHub CI must run the security pattern checker')

    deploy_script = read('deploy.sh')
    if 'python3 tools/check_security_patterns.py' not in deploy_script:
        fail('deploy.sh must run the security pattern checker before transfer')

    workflow = read('docs/memory/workflow.md')
    if '## Accepted Baseline / Known Tradeoffs' not in workflow:
        fail('workflow memory must record accepted baseline/tradeoffs')
    if 'docs/plans/' not in workflow:
        fail('workflow memory must include the plans layer')
    if 'docs/site_history/' not in workflow:
        fail('workflow memory must include the site-history archive layer')
    if 'docs/runbooks/security-implementation.md' not in workflow:
        fail('workflow memory must route the security implementation runbook')

    security_memory = read('docs/memory/security.md')
    if 'docs/runbooks/security-implementation.md' not in security_memory:
        fail('security memory must route the security implementation runbook')
    if 'tools/check_security_patterns.py' not in security_memory:
        fail('security memory must route the security pattern checker')

    local_memory_skill = read('.claude/skills/long-running-project-memory/SKILL.md')
    if 'docs/plans/' not in local_memory_skill:
        fail('Claude long-running memory skill must include docs/plans/')
    if 'docs/site_history/' not in local_memory_skill:
        fail('Claude long-running memory skill must include docs/site_history/')

    for plan_path in (ROOT / 'docs/plans').glob('*.md'):
        text = plan_path.read_text(encoding='utf-8')
        if 'historical record only' in text.lower():
            fail(
                f'{plan_path.relative_to(ROOT)} is a historical record; '
                'move it to docs/site_history/'
            )
        if plan_path.name == 'README.md' and '## Completed Records' in text:
            fail('docs/plans/README.md must not keep a Completed Records section')
        if plan_path.name == 'README.md':
            require_plan_readme_indexes_all_plans(text)

    claude_skills = ROOT / '.claude' / 'skills'
    if claude_skills.is_dir():
        for skill_path in claude_skills.glob('*/SKILL.md'):
            lines = skill_path.read_text(encoding='utf-8').splitlines()
            for idx, line in enumerate(lines):
                if 'Session start' not in line:
                    continue
                snippet = '\n'.join(lines[idx:idx + 5])
                if 'CHANGELOG.md' in snippet and 'Do not read `CHANGELOG.md` by default' not in snippet:
                    fail(
                        f'{skill_path.relative_to(ROOT)} tells agents to read '
                        'CHANGELOG.md at session start'
                    )

    print('memory-system check passed')


if __name__ == '__main__':
    main()
