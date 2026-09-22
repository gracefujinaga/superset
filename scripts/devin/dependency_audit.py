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
"""Nightly dependency audit used by the Devin security automation.

Runs ``pip-audit`` against the pinned Python requirements and ``npm audit``
against the frontend lockfile, then writes one machine-readable JSON report
plus a Markdown summary. Exit code is 0 when nothing was found and 1 when at
least one vulnerability was reported, so callers can gate on it.

Usage::

    python scripts/devin/dependency_audit.py --out /tmp/dependency-audit

Requires ``pip-audit`` on PATH (``uv pip install pip-audit``) and npm >= 11.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_REQUIREMENTS = [
    REPO_ROOT / "requirements" / "base.txt",
    REPO_ROOT / "requirements" / "development.txt",
]
FRONTEND_DIR = REPO_ROOT / "superset-frontend"
NPM_SEVERITIES = ("critical", "high", "moderate", "low")


@dataclass
class Vulnerability:
    ecosystem: str
    package: str
    installed: str
    advisory: str
    severity: str
    fix_versions: list[str] = field(default_factory=list)
    source: str = ""


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        cmd, cwd=cwd, capture_output=True, text=True, check=False
    )


def audit_python() -> tuple[list[Vulnerability], list[str]]:
    findings: list[Vulnerability] = []
    errors: list[str] = []
    if shutil.which("pip-audit") is None:
        return findings, ["pip-audit is not installed"]

    seen: set[tuple[str, str, str]] = set()
    for req in PYTHON_REQUIREMENTS:
        proc = run(
            [
                "pip-audit",
                "--requirement",
                str(req),
                "--no-deps",
                "--format",
                "json",
                "--progress-spinner",
                "off",
            ],
            REPO_ROOT,
        )
        # pip-audit exits 1 when vulnerabilities are found; anything else is an error
        if proc.returncode not in (0, 1) or not proc.stdout.strip():
            errors.append(f"pip-audit failed for {req.name}: {proc.stderr.strip()}")
            continue
        report = json.loads(proc.stdout)
        for dep in report.get("dependencies", []):
            for vuln in dep.get("vulns", []):
                key = (dep["name"], dep["version"], vuln["id"])
                if key in seen:
                    continue
                seen.add(key)
                findings.append(
                    Vulnerability(
                        ecosystem="python",
                        package=dep["name"],
                        installed=dep["version"],
                        advisory=vuln["id"],
                        severity="unknown",
                        fix_versions=list(vuln.get("fix_versions", [])),
                        source=str(req.relative_to(REPO_ROOT)),
                    )
                )
    return findings, errors


def audit_npm() -> tuple[list[Vulnerability], list[str]]:
    findings: list[Vulnerability] = []
    if shutil.which("npm") is None:
        return findings, ["npm is not installed"]

    proc = run(["npm", "audit", "--json", "--audit-level=low"], FRONTEND_DIR)
    if not proc.stdout.strip():
        return findings, [f"npm audit produced no output: {proc.stderr.strip()}"]
    report = json.loads(proc.stdout)
    if "error" in report:
        return findings, [f"npm audit error: {report['error']}"]

    for name, info in report.get("vulnerabilities", {}).items():
        advisories = [
            via["title"] if isinstance(via, dict) else f"via {via}"
            for via in info.get("via", [])
        ]
        fix = info.get("fixAvailable")
        fix_versions = (
            [f"{fix['name']}@{fix['version']}"]
            if isinstance(fix, dict)
            else (["available"] if fix else [])
        )
        findings.append(
            Vulnerability(
                ecosystem="npm",
                package=name,
                installed=info.get("range", ""),
                advisory="; ".join(advisories) or "unknown",
                severity=info.get("severity", "unknown"),
                fix_versions=fix_versions,
                source="superset-frontend/package-lock.json",
            )
        )
    return findings, []


def to_markdown(findings: list[Vulnerability], errors: list[str]) -> str:
    lines = ["# Dependency audit", ""]
    if not findings:
        lines.append("No known vulnerabilities in pinned Python or npm dependencies.")
    else:
        lines.append(f"{len(findings)} vulnerable dependency pin(s) found.")
        lines.append("")
        lines.append("| Ecosystem | Package | Installed | Advisory | Severity | Fix |")
        lines.append("|---|---|---|---|---|---|")
        for f in findings:
            fix = ", ".join(f.fix_versions) or "none published"
            lines.append(
                f"| {f.ecosystem} | {f.package} | {f.installed} | {f.advisory} "
                f"| {f.severity} | {fix} |"
            )
    if errors:
        lines += ["", "## Errors", ""] + [f"- {e}" for e in errors]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("dependency-audit"),
        help="Output path prefix; writes <out>.json and <out>.md",
    )
    args = parser.parse_args()

    py_findings, py_errors = audit_python()
    npm_findings, npm_errors = audit_npm()
    findings = py_findings + npm_findings
    errors = py_errors + npm_errors

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.with_suffix(".json").write_text(
        json.dumps(
            {"findings": [asdict(f) for f in findings], "errors": errors}, indent=2
        )
    )
    markdown = to_markdown(findings, errors)
    args.out.with_suffix(".md").write_text(markdown)
    sys.stdout.write(markdown)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
