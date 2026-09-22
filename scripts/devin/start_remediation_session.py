# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Start a Devin remediation session from a dependency audit report.

Reads the JSON written by ``dependency_audit.py``, builds a prompt that follows
``.agents/skills/security-remediation/SKILL.md`` and calls the Devin v3 API
(``POST /v3/organizations/{org_id}/sessions``). Prints the session URL and, when
``GITHUB_OUTPUT`` is set, exports ``session_id`` and ``session_url`` for later
workflow steps.

Usage::

    DEVIN_API_KEY=... DEVIN_ORG_ID=org-... \
        python scripts/devin/start_remediation_session.py \
        --report /tmp/dependency-audit.json --repo gracefujinaga/superset

Only the standard library is used so the script runs on a bare CI runner.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_BASE = "https://api.devin.ai/v3"
PROMPT_TEMPLATE = """Nightly security + dependency audit for @{repo} (run {run_url}).

Follow `.agents/skills/security-remediation/SKILL.md` and
`.agents/skills/superset-native-dev/SKILL.md` exactly.

## Dependency findings ({count})

{table}

## What to do

1. For each finding, confirm the pin still exists on the default branch and
   that a fixed release exists. Group findings by package/manifest.
2. For each group open ONE pull request on a `devin/<unix-timestamp>-<slug>`
   branch against the default branch:
   - Python pins: edit `requirements/*.in`, regenerate the lockfiles with
     `RUNNING_IN_DOCKER=1 ./scripts/uv-pip-compile.sh`, never hand-edit `*.txt`.
   - npm: `npm audit fix` or a targeted `npm install <pkg>@<fixed>` in
     `superset-frontend`; keep `package-lock.json` consistent.
   - Run `pre-commit run --files <changed files>` and the relevant tests.
   - PR body: advisory IDs, fixed version, whether Superset reaches the
     vulnerable code path, verification commands and output.
3. If no fix is published, do not open a PR; list it under "needs human
   decision" in the report.
4. Also list open findings of Devin code scan `{scan_id}`, but do NOT
   remediate finding `sfind-d012d87e737e4a36a84ac618f97e3405`
   (dataset export `encrypted_extra`) - it is intentionally left open.
5. Finish with a Markdown report attached to the session (counts, advisory
   IDs, fix versions, PR links, skipped items) and a final status line of
   `FINDINGS: <n> PRs opened` or `clean`.

Never push to the default branch, never force-push, never commit secrets.
"""


def load_findings(report: Path) -> list[dict[str, object]]:
    data = json.loads(report.read_text())
    findings = data.get("findings", [])
    if not isinstance(findings, list):
        raise SystemExit(f"{report}: 'findings' must be a list")
    return findings


def findings_table(findings: list[dict[str, object]]) -> str:
    rows = [
        "| Ecosystem | Package | Installed | Advisory | Severity | Fix |",
        "|---|---|---|---|---|---|",
    ]
    for f in findings:
        fix_versions = f.get("fix_versions") or []
        fix = (
            ", ".join(str(v) for v in fix_versions)
            if isinstance(fix_versions, list)
            else str(fix_versions)
        )
        rows.append(
            f"| {f.get('ecosystem', '')} | {f.get('package', '')} "
            f"| {f.get('installed', '')} | {f.get('advisory', '')} "
            f"| {f.get('severity', '')} | {fix or 'none published'} |"
        )
    return "\n".join(rows)


def create_session(
    api_key: str, org_id: str, payload: dict[str, object]
) -> dict[str, object]:
    request = urllib.request.Request(  # noqa: S310
        f"{API_BASE}/organizations/{org_id}/sessions",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
            body = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise SystemExit(f"Devin API returned HTTP {exc.code}: {detail}") from exc
    if not isinstance(body, dict):
        raise SystemExit(f"Unexpected Devin API response: {body!r}")
    return body


def write_github_output(session: dict[str, object]) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as fh:
        fh.write(f"session_id={session.get('session_id', '')}\n")
        fh.write(f"session_url={session.get('url', '')}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report", type=Path, required=True, help="dependency_audit JSON"
    )
    parser.add_argument("--repo", required=True, help="owner/name of the repository")
    parser.add_argument(
        "--scan-id",
        default="scan-09d073e1f57c4498ba37a053c6696035",
        help="Devin code scan whose open findings the session should list",
    )
    parser.add_argument("--run-url", default=os.environ.get("RUN_URL", "manual"))
    parser.add_argument("--max-acu", type=int, default=30)
    parser.add_argument(
        "--dry-run", action="store_true", help="Print the request body and exit"
    )
    args = parser.parse_args()

    findings = load_findings(args.report)
    if not findings:
        print("No dependency findings; not starting a Devin session.")
        return 0

    payload: dict[str, object] = {
        "prompt": PROMPT_TEMPLATE.format(
            repo=args.repo,
            run_url=args.run_url,
            count=len(findings),
            table=findings_table(findings),
            scan_id=args.scan_id,
        ),
        "title": f"Nightly dependency remediation: {len(findings)} finding(s)",
        "tags": ["superset", "security-audit", "nightly"],
        "repos": [args.repo],
        "max_acu_limit": args.max_acu,
        "bypass_approval": True,
    }
    if args.dry_run:
        print(json.dumps(payload, indent=2))
        return 0

    api_key = os.environ.get("DEVIN_API_KEY")
    org_id = os.environ.get("DEVIN_ORG_ID")
    if not api_key or not org_id:
        raise SystemExit("DEVIN_API_KEY and DEVIN_ORG_ID must be set")

    session = create_session(api_key, org_id, payload)
    print(f"Started Devin session {session.get('session_id')}: {session.get('url')}")
    write_github_output(session)
    return 0


if __name__ == "__main__":
    sys.exit(main())
