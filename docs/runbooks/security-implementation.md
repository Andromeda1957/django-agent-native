# Security Implementation Runbook

Use this for every website/runtime implementation before changing code. The goal
is to make common OWASP-class bugs require bypassing multiple deliberate guards,
not one missed line.

This runbook is an execution gate, not background reading. If any trigger below
matches, keep using it through implementation, tests, and closeout.

## Applicability Check

Before editing runtime code, decide whether the change touches any trust
boundary:

- authentication, sessions, passwords, tokens, email verification, 2FA, or API
  keys;
- authorization, ownership, private account data, admin-only data, or any
  user-owned records, imports, exports, or APIs;
- forms, JSON bodies, query params, path params, headers, cookies, uploaded
  files, imported data, remote URLs, or other untrusted input;
- templates, rich text, Markdown-like rendering, raw HTML, JSON-in-HTML, static
  script injection, or client-side DOM writes;
- redirects, return URLs, canonical URL construction, provider callback URLs, or
  external links that affect navigation;
- outbound HTTP, webhooks, provider imports, proxy/reader services, metadata
  fetches, or DNS/IP/host parsing;
- filesystem paths, generated files, archive extraction, image processing,
  subprocesses, shell commands, serialization, deserialization, dynamic imports,
  or template rendering from strings;
- raw SQL, custom query construction, reporting/analytics filters, bulk update
  helpers, migrations with data movement, or management commands that may handle
  untrusted data;
- web-server config, Django settings, CSP, cookies, CORS, CSRF, security
  headers, admin routing, logging, scanners, deploy config, or debug/diagnostic
  surfaces.

If none match, state "Security runbook: applicability checked, no trust boundary
touched" in closeout. If any match, complete the rest of this runbook.

## Design Rules

- Deny by default. New data access starts empty and is expanded only after
  authentication, ownership, scope, and visibility filters are applied.
- Validate at the boundary, authorize at the object/queryset, and encode at the
  sink. Do not rely on one layer to cover another.
- Prefer Django/framework primitives over hand-built parsing, escaping, sessions,
  CSRF, SQL, redirects, or password/token handling.
- Keep views thin. Put reusable authorization, ownership, mutation, import,
  export, and parsing rules in services or query helpers.
- Bound all untrusted input by type, length, count, size, time, and nesting
  before expensive work.
- Fail closed. Ambiguous identity, missing ownership, malformed input, unexpected
  provider responses, and uncertain redirects must reject or return a safe
  fallback.
- Do not create security exceptions casually. Any exception must be narrow,
  documented in code or an allowlist, covered by a negative test when practical,
  and mentioned in closeout.

## Banned By Default

Do not add these in runtime code unless the user explicitly approves a narrow
exception and the exception is allowlisted:

- `eval`, `exec`, dynamic Python execution, dynamic imports from user input, or
  user-controlled template strings;
- `pickle`, unsafe YAML loading, unsafe deserialization, or deserializing objects
  whose class graph can execute code;
- shell interpolation, `shell=True`, `os.system`, `os.popen`, or subprocess
  calls with user-controlled command/argument values;
- raw SQL, `.extra()`, `RawSQL`, or manual SQL string building when the ORM or
  parameter binding can do the job;
- `mark_safe`, `SafeString`, raw HTML insertion, or disabled autoescape for
  user-controlled content;
- `csrf_exempt` for browser/session endpoints;
- arbitrary outbound fetches to user-supplied URLs or redirects to user-supplied
  destinations;
- path joins, file opens, archive extraction, or file deletion using untrusted
  path components without canonical root containment checks.

## Approved Patterns

Use these patterns unless the local code already has a safer project-specific
helper.

- **RCE/deserialization:** no dynamic execution; JSON or a schema-validated
  deserializer for untrusted payloads; subprocess commands as fixed argument
  lists with timeouts and no shell.
- **SQLi:** Django ORM/query expressions first. If raw SQL is unavoidable, use
  parameter binding, isolate it in a service/helper, document why ORM cannot
  express it, and test hostile parameter text.
- **IDOR/authz:** filter querysets by the authenticated user, token scope, public
  visibility, and object ownership before `get_object_or_404()`, `.get()`,
  mutation, export, or serialization. Never fetch then check when a scoped query
  can enforce ownership.
- **CSRF/session safety:** use Django CSRF for browser/session POSTs. Machine
  endpoints must authenticate with bearer tokens, signed payloads, provider
  signatures, or another non-cookie credential before considering `csrf_exempt`.
- **XSS:** keep template autoescape on. Use escaped text, `json_script`, safe DOM
  APIs such as `textContent`, and sanitizer allowlists for any intentionally rich
  HTML. `mark_safe` is allowed only after all user-controlled pieces have been
  escaped or sanitized.
- **Open redirects:** redirect to named routes, `reverse()` output, or a project
  helper that uses `url_has_allowed_host_and_scheme()` plus an internal fallback.
  Never redirect to a raw query/header value.
- **SSTI:** render only project-owned template files. Do not pass user-controlled
  strings to `Template`, template loaders, include paths, or template names.
- **SSRF:** do not fetch arbitrary URLs. Accept known provider URLs only after
  host/scheme/path validation, allowlist hosts, use HTTPS where available, set
  timeouts, cap response size, and reject private/internal/link-local hosts for
  any generic URL feature.
- **Uploads/files:** validate size, type, extension, image dimensions, and
  content parser limits. Resolve paths under a fixed root and reject traversal or
  symlink escapes before open/write/delete.
- **Secrets/logging:** never log secrets, tokens, passwords, recovery codes, raw
  authorization headers, raw IPs, raw user agents, query strings containing
  private data, or other user-private content.
- **Admin/debug:** never add unauthenticated diagnostics, public stack/config
  dumps, environment displays, admin path disclosure, or debug-only behavior to
  production routes.

## Required Negative Tests

Add focused negative tests when the trigger is present and the behavior can be
tested locally:

- Auth/ownership/API: another user or missing/insufficient token cannot read,
  mutate, export, import, delete, or enumerate the object.
- Object lookup: nonexistent, private, inactive, or wrong-owner objects return
  404/403 and do not leak existence through response details.
- CSRF/session POST: browser/session mutation rejects missing CSRF unless it is a
  documented non-cookie machine endpoint.
- Redirects: external, schemeless, backslash, encoded, and wrong-host return URLs
  fall back to an internal route.
- XSS/templates/DOM: hostile markup such as `<script>`, event handlers, SVG
  payloads, and closing-tag injection is escaped, sanitized, or rejected.
- SQL/search/filtering: hostile quotes, wildcards, comments, long tokens, and
  boolean-looking fragments are parameters/data, not SQL syntax.
- SSRF/outbound fetches: unsupported hosts, private/internal IPs, unexpected
  schemes, redirects to blocked hosts, oversize responses, and timeouts fail
  closed.
- Files/uploads: traversal (`../`), absolute paths, symlinks, oversize files,
  wrong MIME/extensions, malformed files, and archive escapes are rejected.
- Subprocess/worker: user-controlled values cannot change the executable, inject
  flags, escape the working root, remove timeout/size limits, or enter a shell.

If a negative test is not practical, write the reason in closeout and verify the
closest enforceable boundary.

## Static Gate

Run `python3 tools/check_security_patterns.py` for runtime changes. The checker
blocks high-risk primitives in application paths unless they are in its narrow
audited allowlist. When adding an allowlist entry:

- make the allowed scope as specific as possible;
- include a short reason in the allowlist;
- add or update negative tests for the risk class when practical;
- mention the exception in closeout.

## Closeout

Every runtime closeout must include:

- `Security runbook:` used, or applicability checked and not triggered.
- `Risk classes:` the relevant classes, such as RCE, SQLi, IDOR, CSRF, XSS,
  SSTI, SSRF, open redirect, file/upload, secrets/logging, or admin/debug.
- `Safe primitives:` the framework/project helpers used.
- `Negative tests:` added tests, existing tests exercised, or why not applicable.
- `Static gate:` whether `tools/check_security_patterns.py` passed or why it was
  not applicable.

Do not claim a class of bug is impossible. Report the concrete layers that make
it structurally unlikely in this change.
