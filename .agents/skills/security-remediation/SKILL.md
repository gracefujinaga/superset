---
name: security-remediation
description: How Devin fixes security-scan findings and vulnerable/outdated dependencies in this repo - triage rules from SECURITY.md, the fix -> regression test -> pre-commit -> PR loop, and the reporting format. Use when triggered by the nightly security audit workflow, a `devin-fix` label, or a `/devin-fix` comment.
---

# Security remediation workflow

Triggered by the nightly GitHub Actions audit (security scan + dependency audit), a GitHub
issue labeled `devin-fix`, or a `/devin-fix` comment on an issue or PR. The trigger
payload is the work order.

## 1. Triage before touching code

- Read `SECURITY.md` and the "Security and Threat Model" section of `AGENTS.md`. A
  finding is in scope only if a principal (Public, Gamma, sql_lab, Alpha, embedded
  guest, custom role) can do something the role/capability matrix does not allow.
  Admin-only or operator-misconfiguration findings are out of scope: say so, open no PR.
- Confirm the vulnerable path still exists on `master` by reading the cited code. If
  it is already fixed or a false positive, report that and stop.
- For dependency findings: confirm the CVE applies to the pinned version and that a
  fixed release exists. Note whether the vulnerable code path is reachable from
  Superset (import used? feature gated?) - state that in the PR either way.

## 2. Fix

- Minimal, targeted change. Reuse existing controls (`@protect()`, `raise_for_access`,
  masking helpers such as the `encrypted_extra` masking in
  `superset/commands/database/export.py`, `validate_external_url`, ...) before writing
  new ones. Mirror the sibling code path that already does it right.
- Python: type hints, mypy-clean. Frontend: `@superset-ui/core`, no `any`.
- Dependencies: bump the pin in `requirements/base.in` / `development.in` with a
  `# Security: CVE-...` comment (see existing entries), then regenerate the `.txt`
  lockfiles with `./scripts/uv-pip-compile.sh` (see `requirements/README.md`).
  Frontend deps: bump in `superset-frontend/package.json` and refresh `package-lock.json`
  with npm 11 (`npm install --package-lock-only`).
- Never weaken or delete a test to make things pass.

## 3. Prove it

- Add or extend a test under `tests/unit_tests/` (or the frontend `*.test.tsx`) that
  fails without the fix and passes with it.
- `pre-commit run --files <changed files>`
- `pytest tests/unit_tests/<path> -q -p no:randomly` (see `superset-native-dev` skill
  for environment setup; `--timeout` is not available).

## 4. Ship

- Branch `devin/<unix-timestamp>-<slug>`, PR against `master`, title in Conventional
  Commits form (`fix(scope): ...`), body following `.github/PULL_REQUEST_TEMPLATE.md`.
- PR body must include: finding ID / CVE, assumed attacker principal and violated
  matrix row (for code findings), vulnerable behavior, the fix, the covering test, and
  the verification commands with results.
- One PR per finding group. Never push to `master`, never force-push, never commit
  secrets or `.env` files. If verification could not run, open as draft and say what
  was not verified.
- Final response (posted back to the trigger / emailed by the automation): one line
  per finding - fixed (PR link) / already fixed / false positive / needs human decision.
