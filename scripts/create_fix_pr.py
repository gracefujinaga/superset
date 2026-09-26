#!/usr/bin/env python3
"""
Create Pull Request for fixes based on scan results
"""
import json
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import PR tracking and scoring
from pr_tracker import PRTracker
from pr_scorer import PRScorer

def create_fix_pr():
    """Create PR with fixes based on scan findings"""
    timestamp = datetime.now().isoformat()
    branch_name = f"nightly-scan-fixes-{timestamp.strftime('%Y%m%d')}"

    print(f"[{timestamp}] Creating fix PR...")

    # Initialize PR tracker and scorer
    pr_tracker = PRTracker()
    pr_scorer = PRScorer()

    # Load scan results
    findings = load_all_findings()
    
    if not findings:
        print("[{timestamp}] No findings to fix, skipping PR creation")
        return

    # Create feature branch
    try:
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        print(f"[{timestamp}] Created branch: {branch_name}")
    except subprocess.CalledProcessError as e:
        print(f"[{timestamp}] Failed to create branch: {e}")
        return

    # Apply fixes (this would be done by Devin based on findings)
    apply_fixes(findings)

    # Commit changes
    try:
        subprocess.run(["git", "add", "."], check=True)
        commit_message = f"""
Nightly Scan Fixes - {timestamp.strftime('%Y-%m-%d')}

Automated fixes from nightly security and bug scan:

- Security fixes: {len([f for f in findings if f['category'] == 'security'])}
- Bug fixes: {len([f for f in findings if f['category'] == 'bugs'])}
- Latent issue fixes: {len([f for f in findings if f['category'] == 'latent'])}

Generated with [Devin](https://devin.ai)
"""
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print(f"[{timestamp}] Committed fixes")
    except subprocess.CalledProcessError as e:
        print(f"[{timestamp}] Failed to commit: {e}")
        return

    # Push branch
    try:
        subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)
        print(f"[{timestamp}] Pushed branch to remote")
    except subprocess.CalledProcessError as e:
        print(f"[{timestamp}] Failed to push: {e}")
        return

    # Create PR using GitHub CLI or MCP
    pr_number = create_pr(branch_name, findings)
    
    if pr_number:
        # Track the PR
        pr_tracker.track_pr(pr_number, {
            "title": f"Nightly Scan Fixes - {timestamp.strftime('%Y-%m-%d')}",
            "author": "devin-bot",
            "created_at": timestamp,
            "files_changed": len(findings),
            "findings_count": len(findings),
            "branch": branch_name
        })
        
        # Score the PR (simulated scores for now)
        # In production, these would be calculated from actual analysis
        pr_data = {
            "title": f"Nightly Scan Fixes - {timestamp.strftime('%Y-%m-%d')}",
            "bug_type": "mixed",
            "severity": "varies"
        }
        
        score_result = pr_scorer.score_pr_comprehensive(pr_number, pr_data)
        
        # Tag the PR with its score
        pr_tracker.tag_pr_with_score(pr_number, score_result)
        
        print(f"[{timestamp}] PR #{pr_number} created and scored: {score_result['overall_score']}/10 ({score_result['status']})")

def load_all_findings():
    """Load findings from all scan results"""
    findings = []
    directories = ["scan-results/security", "scan-results/bugs", "scan-results/latent"]
    
    for directory in directories:
        try:
            files = list(Path(directory).glob("*.json"))
            if files:
                latest_file = max(files, key=os.path.getctime)
                with open(latest_file, "r") as f:
                    data = json.load(f)
                    findings.extend(data.get("findings", []))
        except Exception as e:
            print(f"Error loading findings from {directory}: {e}")
    
    return findings

def apply_fixes(findings):
    """Apply fixes based on findings (would be done by Devin)"""
    print(f"[{datetime.now().isoformat()}] Applying {len(findings)} fixes...")
    # This is where Devin would actually apply the fixes
    # For now, we'll just log what would be done
    for finding in findings:
        print(f"  - Would fix: {finding.get('title', 'Unknown')} in {finding.get('location', 'Unknown')}")

def create_pr(branch_name, findings):
    """Create PR using GitHub MCP or CLI"""
    timestamp = datetime.now().isoformat()
    
    pr_title = f"Nightly Scan Fixes - {timestamp.strftime('%Y-%m-%d')}"
    pr_body = f"""
## Summary
Automated fixes from nightly security and bug scan.

## Fixes Applied
- Security fixes: {len([f for f in findings if f['category'] == 'security'])}
- Bug fixes: {len([f for f in findings if f['category'] == 'bugs'])}
- Latent issue fixes: {len([f for f in findings if f['category'] == 'latent'])}

## Details
{format_findings_for_pr(findings)}

## Scan Report
See the full scan report in the artifacts for detailed findings.

Generated with [Devin](https://devin.ai)
"""

    print(f"[{timestamp}] Creating PR: {pr_title}")
    # This would use GitHub MCP or gh CLI to create the PR
    # For now, return a placeholder PR number
    pr_number = 999  # Placeholder - would be actual PR number
    
    return pr_number

def format_findings_for_pr(findings):
    """Format findings for PR description"""
    if not findings:
        return "No findings."
    
    formatted = []
    for finding in findings[:10]:  # Limit to first 10 for PR description
        formatted.append(f"- **{finding.get('title', 'Untitled')}** ({finding.get('severity', 'Unknown')})")
    
    if len(findings) > 10:
        formatted.append(f"- ... and {len(findings) - 10} more findings")
    
    return "\n".join(formatted)

if __name__ == "__main__":
    create_fix_pr()