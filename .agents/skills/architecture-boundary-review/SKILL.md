---
name: architecture-boundary-review
description: Review a software repository for monolith drift, weak domain separation, oversized modules, thin-view/service-boundary violations, cross-domain imports, duplicated helpers, and maintainability risks. Use when the user asks to review architecture, domain boundaries, large files such as views/services/admin/frontend controllers/tests, whether another separation pass is needed, or how to prevent code from becoming an unmaintainable monolith.
---

# Architecture Boundary Review

## Purpose

Perform a findings-first architecture review that is proportional to the requested scope. Prefer evidence from repo-backed instructions, source files, import graphs, tests, and enforcement tools over intuition.

This skill is for review and recommendations. Do not edit files unless the user explicitly asks to implement changes.

## Workflow

1. **Set scope before tools**
   - Classify the request: targeted review, project-wide review, implementation follow-up, or status check.
   - State exactly what will be inspected. Do not widen scope beyond the user's request.
   - If the user asks for "everything", inspect all major code surfaces, not just the example file.

2. **Load governing context**
   - Follow repo-local agent contracts first, such as `AGENTS.md`, `CLAUDE.md`, or runbooks.
   - Read architecture docs that define intended boundaries, such as `docs/memory/architecture.md`, package README files, ADRs, or import-linter contracts (`.importlinter`).
   - Treat hidden memory and previous chat summaries as leads only. Verify current state against files and commands.

3. **Map hotspots**
   - Start with `git status --short` so user or other-agent work is not accidentally blamed or reverted.
   - Use fast file discovery and search: `rg --files`, `rg`, `wc -l`, `find` only when `rg` is not enough.
   - Identify unusually large files and repeated surfaces across:
     - backend views/controllers/routes
     - domain services and helpers
     - models/entities/schema files
     - admin dashboards/internal tools
     - management commands/workers/jobs
     - frontend controllers/modules
     - templates/styles
     - tests and fixtures

4. **Inspect boundary risks**
   - Look for mixed responsibilities in one file: page rendering plus JSON API, command orchestration plus parsing, UI controller plus domain algorithms, admin registration plus health checks.
   - Check whether views/controllers contain business rules, mutations, query construction, export assembly, or serialization that belongs in services.
   - Check whether services import across domains in ways the architecture docs discourage.
   - Check whether shared helpers are duplicated across domains or hidden in one domain where another domain now depends on the same behavior.
   - Check whether tests mirror oversized production boundaries; test monoliths are usually secondary evidence, not the first refactor target.
   - Do not recommend creating new apps/packages only to make the tree look cleaner. Prefer the repo's existing architecture unless current docs or behavior justify a stronger boundary.

5. **Check enforcement**
   - Inspect import-linter, dependency-cruiser, ESLint boundaries, package visibility, or equivalent rules if present.
   - Run read-only validation tools when practical, especially architecture checks and type/lint gates.
   - Distinguish "the rule passes" from "the rule covers the risky area"; passing checks can still leave coverage gaps.

6. **Prioritize**
   - Lead with risks that can cause drift or inconsistent behavior, not just line counts.
   - Prefer small guardrails before large refactors when possible: add enforcement, extract duplicated request/response helpers, split API/page surfaces, then split internals.
   - Separate current bugs from maintainability risks. Say clearly when a finding is preventive rather than broken today.

## Reporting

Use a code-review style response:

- Findings first, ordered by severity or leverage.
- Each finding includes concrete file and line references when possible.
- Include what was checked and what was not checked if the review was not truly exhaustive.
- Include validation commands run and their result.
- End with a short recommended sequence of next steps.

Avoid speculative redesigns from partial reads. If the evidence is incomplete, say the recommendation is provisional and name the missing context.

## Useful Commands

Use commands appropriate to the repo. These are examples, not a fixed script:

```bash
git status --short
rg --files
wc -l path/to/files
rg -n "class |def |function |export |urlpatterns|router|service|helper" path
```

For this Python/Django repo, useful checks often include:

```bash
ruff check .
lint-imports
python3 manage.py test web
```

For TypeScript/frontend surfaces:

```bash
npm run typecheck
```
