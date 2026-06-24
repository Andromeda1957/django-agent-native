# Gemini Read-Only Overlay

This file is for Google Antigravity / Gemini when used with this repository. It
is a narrower safety overlay, not the project-wide operating contract.

Use this repository in read-only mode. The allowed uses are answering questions,
explaining code, reviewing code, and brainstorming implementation approaches.

Do not modify files, create files, delete files, rename files, run formatters,
apply patches, commit, push, deploy, run database migrations, or mutate local or
remote state.

If asked to implement a change, provide a proposed patch or step-by-step plan in
chat instead of editing files.

For the source-of-truth hierarchy, project workflows, and current project state,
consult `AGENTS.md`, `AGENT_HANDOFF.md`, `PROJECT_MEMORY.md`, and the relevant
runbooks. If those files describe mutation workflows, treat them as context only
in Gemini sessions unless the owner explicitly changes this read-only policy.

This read-only default is deliberate: Gemini's agentic-coding reliability is
weaker than Claude's or GPT's, so by default it reviews and proposes rather than
modifies. If Gemini is your only agent, you can promote it to full read/write by
replacing this overlay with a mirror of `AGENTS.md` (see the agent tiers section
of the README) — but treat full install/deploy driven by Gemini as untested, and
rely on the pre-commit and CI gates as the safety net. No agent deploys to
production unattended; the `Deploy` workflow is manual and confirmation-gated.
