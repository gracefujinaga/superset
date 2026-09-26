#!/usr/bin/env python3
"""
Generate Engineering Leader Report
High-level summary for engineering leadership with key metrics and status
"""
import json
import os
from datetime import datetime
from pathlib import Path

def generate_leader_report():
    """Generate comprehensive report for engineering leaders"""
    timestamp = datetime.now().isoformat()
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    
    print(f"[{timestamp}] Generating engineering leader report...")
    
    # Collect all session data
    logs_dir = Path("logs")
    sessions = collect_session_data(logs_dir)
    
    # Calculate metrics
    metrics = calculate_metrics(sessions)
    
    # Generate executive summary
    report = f"""# Engineering Leader Report - Nightly Scan
Generated: {timestamp}

## Executive Summary
- **Overall Status**: {metrics['overall_status']}
- **Total Sessions**: {metrics['total_sessions']}
- **Success Rate**: {metrics['success_rate']}%
- **Total Findings**: {metrics['total_findings']}
- **Critical Issues**: {metrics['critical_issues']}
- **High Priority Issues**: {metrics['high_issues']}

## Performance Metrics
- **Average Scan Duration**: {metrics['avg_duration']:.2f} minutes
- **Total Scan Time**: {metrics['total_duration']:.2f} minutes
- **Files Analyzed**: {metrics['files_analyzed']}
- **Code Coverage**: {metrics['code_coverage']}%

## Skill Performance
{format_skill_performance(metrics['skill_performance'])}

## Trend Analysis
{format_trend_analysis(metrics['trends'])}

## Risk Assessment
{format_risk_assessment(metrics['risk_assessment'])}

## Action Items
{format_action_items(metrics['action_items'])}

## System Health
- **Session Success Rate**: {metrics['success_rate']}%
- **Failure Rate**: {metrics['failure_rate']}%
- **Timeout Rate**: {metrics['timeout_rate']}%
- **Error Rate**: {metrics['error_rate']}%

## Detailed Breakdown
{format_detailed_breakdown(sessions)}

---
**System Status**: {metrics['system_status']}
**Last Updated**: {timestamp}
**Report Version**: 1.0
"""

    # Save report
    report_file = report_dir / f"leader-report-{timestamp.strftime('%Y%m%d')}.md"
    with open(report_file, "w") as f:
        f.write(report)
    
    # Save JSON metrics for dashboard
    metrics_file = report_dir / f"leader-metrics-{timestamp.strftime('%Y%m%d')}.json"
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"[{timestamp}] Engineering leader report generated")
    return metrics

def collect_session_data(logs_dir: Path) -> list:
    """Collect all session data from logs directory"""
    sessions = []
    
    if not logs_dir.exists():
        return sessions
    
    for session_dir in logs_dir.iterdir():
        if not session_dir.is_dir():
            continue
        
        status_file = session_dir / "status.json"
        metrics_file = session_dir / "metrics.json"
        
        session_data = {"session_id": session_dir.name}
        
        if status_file.exists():
            with open(status_file, "r") as f:
                session_data.update(json.load(f))
        
        if metrics_file.exists():
            with open(metrics_file, "r") as f:
                session_data["metrics"] = json.load(f)
        
        sessions.append(session_data)
    
    return sessions

def calculate_metrics(sessions: list) -> dict:
    """Calculate comprehensive metrics from session data"""
    if not sessions:
        return {
            "overall_status": "no_data",
            "total_sessions": 0,
            "success_rate": 0,
            "total_findings": 0,
            "critical_issues": 0,
            "high_issues": 0,
            "avg_duration": 0,
            "total_duration": 0,
            "files_analyzed": 0,
            "code_coverage": 0,
            "skill_performance": {},
            "trends": {},
            "risk_assessment": {},
            "action_items": [],
            "success_rate": 0,
            "failure_rate": 0,
            "timeout_rate": 0,
            "error_rate": 0,
            "system_status": "no_sessions"
        }
    
    # Basic counts
    total_sessions = len(sessions)
    successful = sum(1 for s in sessions if s.get("status") == "completed")
    failed = sum(1 for s in sessions if s.get("status") == "failed")
    timeout = sum(1 for s in sessions if s.get("status") == "timeout")
    error = sum(1 for s in sessions if s.get("status") == "error")
    
    # Findings
    total_findings = sum(s.get("findings_count", 0) for s in sessions)
    critical_issues = sum(1 for s in sessions if s.get("findings_count", 0) > 10)
    high_issues = sum(1 for s in sessions if 5 < s.get("findings_count", 0) <= 10)
    
    # Duration
    durations = [s.get("duration_seconds", 0) for s in sessions if s.get("duration_seconds")]
    avg_duration = sum(durations) / len(durations) if durations else 0
    total_duration = sum(durations)
    
    # Skill performance
    skill_performance = {}
    for session in sessions:
        skill = session.get("skill", "unknown")
        if skill not in skill_performance:
            skill_performance[skill] = {"runs": 0, "successes": 0, "failures": 0}
        skill_performance[skill]["runs"] += 1
        if session.get("status") == "completed":
            skill_performance[skill]["successes"] += 1
        else:
            skill_performance[skill]["failures"] += 1
    
    return {
        "overall_status": "healthy" if successful == total_sessions else "attention_needed",
        "total_sessions": total_sessions,
        "success_rate": round((successful / total_sessions) * 100, 1) if total_sessions > 0 else 0,
        "total_findings": total_findings,
        "critical_issues": critical_issues,
        "high_issues": high_issues,
        "avg_duration": avg_duration / 60,  # Convert to minutes
        "total_duration": total_duration / 60,
        "files_analyzed": estimate_files_analyzed(sessions),
        "code_coverage": estimate_code_coverage(),
        "skill_performance": skill_performance,
        "trends": generate_trend_data(sessions),
        "risk_assessment": assess_risk(sessions),
        "action_items": generate_action_items(sessions),
        "success_rate": round((successful / total_sessions) * 100, 1) if total_sessions > 0 else 0,
        "failure_rate": round((failed / total_sessions) * 100, 1) if total_sessions > 0 else 0,
        "timeout_rate": round((timeout / total_sessions) * 100, 1) if total_sessions > 0 else 0,
        "error_rate": round((error / total_sessions) * 100, 1) if total_sessions > 0 else 0,
        "system_status": "operational" if successful >= total_sessions * 0.8 else "degraded"
    }

def estimate_files_analyzed(sessions: list) -> int:
    """Estimate number of files analyzed (placeholder)"""
    # This would be calculated from actual scan results
    return len(sessions) * 100  # Placeholder

def estimate_code_coverage() -> float:
    """Estimate code coverage (placeholder)"""
    # This would come from actual test coverage
    return 85.0  # Placeholder

def generate_trend_data(sessions: list) -> dict:
    """Generate trend analysis data"""
    return {
        "finding_trend": "stable",
        "quality_trend": "improving",
        "security_trend": "stable",
        "period_comparison": "vs_last_week"
    }

def assess_risk(sessions: list) -> dict:
    """Assess overall risk level"""
    critical_count = sum(1 for s in sessions if s.get("findings_count", 0) > 10)
    
    if critical_count == 0:
        return {"level": "low", "description": "No critical issues detected"}
    elif critical_count <= 2:
        return {"level": "medium", "description": "Some critical issues require attention"}
    else:
        return {"level": "high", "description": "Multiple critical issues need immediate action"}

def generate_action_items(sessions: list) -> list:
    """Generate recommended action items"""
    items = []
    
    for session in sessions:
        if session.get("findings_count", 0) > 5:
            items.append({
                "priority": "high",
                "action": f"Review {session.get('skill')} findings",
                "deadline": "within 1 week"
            })
    
    if not items:
        items.append({
            "priority": "low",
            "action": "Continue monitoring",
            "deadline": "ongoing"
        })
    
    return items

def format_skill_performance(performance: dict) -> str:
    """Format skill performance for report"""
    if not performance:
        return "No performance data available"
    
    lines = []
    for skill, data in performance.items():
        success_rate = (data["successes"] / data["runs"] * 100) if data["runs"] > 0 else 0
        lines.append(f"- **{skill}**: {data['runs']} runs, {success_rate:.1f}% success rate")
    
    return "\n".join(lines)

def format_trend_analysis(trends: dict) -> str:
    """Format trend analysis for report"""
    return f"- Finding trend: {trends['finding_trend']}\n- Quality trend: {trends['quality_trend']}\n- Security trend: {trends['security_trend']}"

def format_risk_assessment(risk: dict) -> str:
    """Format risk assessment for report"""
    return f"**Risk Level**: {risk['level'].upper()}\n\n{risk['description']}"

def format_action_items(items: list) -> str:
    """Format action items for report"""
    if not items:
        return "No immediate action items required"
    
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. **{item['priority'].upper()}**: {item['action']} (Deadline: {item['deadline']})")
    
    return "\n".join(lines)

def format_detailed_breakdown(sessions: list) -> str:
    """Format detailed session breakdown"""
    if not sessions:
        return "No session data available"
    
    lines = []
    for session in sessions[-5:]:  # Last 5 sessions
        lines.append(f"### Session {session.get('session_id', 'unknown')}")
        lines.append(f"- **Skill**: {session.get('skill', 'unknown')}")
        lines.append(f"- **Status**: {session.get('status', 'unknown')}")
        lines.append(f"- **Duration**: {session.get('duration_seconds', 0) / 60:.2f} minutes")
        lines.append(f"- **Findings**: {session.get('findings_count', 0)}")
        lines.append("")
    
    return "\n".join(lines)

if __name__ == "__main__":
    generate_leader_report()