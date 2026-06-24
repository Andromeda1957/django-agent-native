"""Check application code for high-risk security primitives.

A project-specific SAST gate (complements Semgrep). It flags dangerous calls —
dynamic execution, shell/subprocess, unsafe deserialization, outbound HTTP,
manual safe-string marking, raw SQL, runtime template rendering, CSRF exemption
— so each one is a conscious, reviewed decision rather than an accident.

When a flagged primitive is genuinely needed and safe, add a narrow entry to
ALLOWLIST (path + check id + enclosing scope) with a one-line justification, and
follow docs/runbooks/security-implementation.md.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# First-party application packages to scan. Add your apps here.
SCAN_ROOTS = (
    'config',
    'web',
)

EXCLUDED_PARTS = {
    '__pycache__',
    'migrations',
    'tests',
}

SUBPROCESS_CALLS = {
    'subprocess.Popen',
    'subprocess.call',
    'subprocess.check_call',
    'subprocess.check_output',
    'subprocess.run',
}

REQUESTS_CALLS = {
    'requests.delete',
    'requests.get',
    'requests.patch',
    'requests.post',
    'requests.put',
    'requests.request',
}

RAW_SQL_METHODS = {'extra', 'raw'}

# Narrow, reviewed exceptions: (relative_path, check_id, enclosing_scope) -> why.
# Keep each one specific and paired with a test and the security runbook. The
# base template ships with none.
ALLOWLIST: dict[tuple[str, str, str], str] = {}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    column: int
    check_id: str
    scope: str
    detail: str


def collect_aliases(tree: ast.AST) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local_name = alias.asname or alias.name.split('.')[0]
                aliases[local_name] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                if alias.name == '*':
                    continue
                local_name = alias.asname or alias.name
                aliases[local_name] = f'{node.module}.{alias.name}'
    return aliases


def dotted_name(node: ast.AST, aliases: dict[str, str] | None = None) -> str:
    aliases = aliases or {}
    if isinstance(node, ast.Name):
        return aliases.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        base = dotted_name(node.value, aliases)
        return f'{base}.{node.attr}' if base else node.attr
    if isinstance(node, ast.Call):
        return dotted_name(node.func, aliases)
    return ''


def literal_true(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and node.value is True


class SecurityVisitor(ast.NodeVisitor):
    def __init__(self, relative_path: str, aliases: dict[str, str]) -> None:
        self.relative_path = relative_path
        self.aliases = aliases
        self.scope_stack: list[str] = []
        self.findings: list[Finding] = []

    @property
    def scope(self) -> str:
        return '.'.join(self.scope_stack) or '<module>'

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.scope_stack.append(node.name)
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self.scope_stack.append(node.name)
        for decorator in node.decorator_list:
            self._check_decorator(decorator)
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:
        name = dotted_name(node.func, self.aliases)

        if name in {'eval', 'exec'}:
            self._record('python.dynamic_execution', node, f'dynamic execution via {name}()')
        elif name in {'os.system', 'os.popen'}:
            self._record('subprocess.shell', node, f'shell command via {name}()')
        elif name in SUBPROCESS_CALLS:
            if any(keyword.arg == 'shell' and literal_true(keyword.value) for keyword in node.keywords):
                self._record('subprocess.shell_true', node, f'{name}(..., shell=True)')
            else:
                self._record('subprocess.use', node, f'subprocess call via {name}()')
        elif name in {'pickle.load', 'pickle.loads'}:
            self._record('python.unsafe_deserialization', node, f'unsafe deserialization via {name}()')
        elif name == 'yaml.load':
            self._record('python.unsafe_yaml', node, 'YAML loading must use safe_load()')
        elif name in REQUESTS_CALLS:
            self._record('network.requests', node, f'outbound HTTP via {name}()')
        elif name == 'requests.Session':
            self._record('network.requests_session', node, 'outbound HTTP session creation')
        elif name in {'urlopen', 'urllib.request.urlopen'}:
            self._record('network.urlopen', node, f'outbound HTTP via {name}()')
        elif name in {'mark_safe', 'django.utils.safestring.mark_safe'}:
            self._record('django.mark_safe', node, 'manual safe-string marking')
        elif name in {'RawSQL', 'django.db.models.expressions.RawSQL'}:
            self._record('django.raw_sql', node, 'raw SQL expression')
        elif name in {'Template', 'django.template.Template'}:
            self._record('django.template_string', node, 'runtime template string rendering')
        elif isinstance(node.func, ast.Attribute) and node.func.attr in RAW_SQL_METHODS:
            self._record('django.raw_sql', node, f'raw queryset SQL via .{node.func.attr}()')

        self.generic_visit(node)

    def _check_decorator(self, decorator: ast.AST) -> None:
        name = dotted_name(decorator, self.aliases)
        if name in {'csrf_exempt', 'django.views.decorators.csrf.csrf_exempt'}:
            self._record('django.csrf_exempt', decorator, 'CSRF exemption')

    def _record(self, check_id: str, node: ast.AST, detail: str) -> None:
        key = (self.relative_path, check_id, self.scope)
        if key in ALLOWLIST:
            return
        self.findings.append(
            Finding(
                path=self.relative_path,
                line=getattr(node, 'lineno', 0),
                column=getattr(node, 'col_offset', 0) + 1,
                check_id=check_id,
                scope=self.scope,
                detail=detail,
            )
        )


def iter_python_files() -> list[Path]:
    paths: list[Path] = []
    for root_name in SCAN_ROOTS:
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob('*.py'):
            relative_parts = path.relative_to(ROOT).parts
            if any(part in EXCLUDED_PARTS for part in relative_parts):
                continue
            paths.append(path)
    return sorted(paths)


def main() -> None:
    findings: list[Finding] = []
    for path in iter_python_files():
        relative_path = str(path.relative_to(ROOT))
        tree = ast.parse(path.read_text(encoding='utf-8'), filename=relative_path)
        visitor = SecurityVisitor(relative_path, collect_aliases(tree))
        visitor.visit(tree)
        findings.extend(visitor.findings)

    if findings:
        print('security pattern check failed:')
        for finding in findings:
            print(
                f'- {finding.path}:{finding.line}:{finding.column} '
                f'[{finding.check_id}] {finding.scope}: {finding.detail}'
            )
        print()
        print('Follow docs/runbooks/security-implementation.md before adding an exception.')
        raise SystemExit(1)

    print('security pattern check passed')


if __name__ == '__main__':
    main()
