#!/usr/bin/env python3
"""
Update Status Dashboard
Create a simple status dashboard for real-time monitoring
"""
import json
from datetime import datetime
from pathlib import Path

def update_status_dashboard():
    """Update the status dashboard with latest scan results"""
    timestamp = datetime.now().isoformat()
    
    print(f"[{timestamp}] Updating status dashboard...")
    
    # Collect current status
    status = collect_current_status()
    
    # Generate dashboard HTML
    dashboard_html = generate_dashboard_html(status, timestamp)
    
    # Save dashboard
    dashboard_dir = Path("reports")
    dashboard_dir.mkdir(exist_ok=True)
    
    dashboard_file = dashboard_dir / "status-dashboard.html"
    with open(dashboard_file, "w") as f:
        f.write(dashboard_html)
    
    # Also save JSON for API consumption
    status_file = dashboard_dir / "current-status.json"
    with open(status_file, "w") as f:
        json.dump(status, f, indent=2)
    
    print(f"[{timestamp}] Status dashboard updated")

def collect_current_status() -> dict:
    """Collect current status from all sources"""
    logs_dir = Path("logs")
    
    status = {
        "timestamp": datetime.now().isoformat(),
        "system_health": "unknown",
        "active_sessions": [],
        "recent_sessions": [],
        "overall_status": "unknown",
        "skills": {
            "security-check": {"status": "unknown", "last_run": None, "findings": 0},
            "bug-scan": {"status": "unknown", "last_run": None, "findings": 0},
            "latent-bugs": {"status": "unknown", "last_run": None, "findings": 0}
        }
    }
    
    if not logs_dir.exists():
        return status
    
    # Collect session data
    sessions = []
    for session_dir in logs_dir.iterdir():
        if not session_dir.is_dir():
            continue
        
        status_file = session_dir / "status.json"
        if status_file.exists():
            with open(status_file, "r") as f:
                session_data = json.load(f)
                sessions.append(session_data)
                
                # Update skill status
                skill = session_data.get("skill")
                if skill in status["skills"]:
                    status["skills"][skill]["status"] = session_data.get("status")
                    status["skills"][skill]["last_run"] = session_data.get("end_time")
                    status["skills"][skill]["findings"] = session_data.get("findings_count", 0)
    
    # Sort by timestamp
    sessions.sort(key=lambda x: x.get("end_time", ""), reverse=True)
    
    # Recent sessions (last 10)
    status["recent_sessions"] = sessions[:10]
    
    # Active sessions (running)
    status["active_sessions"] = [s for s in sessions if s.get("status") == "running"]
    
    # Overall status
    if status["active_sessions"]:
        status["overall_status"] = "running"
    elif sessions:
        latest_status = sessions[0].get("status") if sessions else "unknown"
        status["overall_status"] = latest_status
        status["system_health"] = "healthy" if latest_status == "completed" else "attention_needed"
    
    return status

def generate_dashboard_html(status: dict, timestamp: str) -> str:
    """Generate HTML dashboard for status visualization"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Nightly Scan Status Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
        .status-badge {{ padding: 8px 16px; border-radius: 20px; font-weight: bold; }}
        .status-healthy {{ background: #4CAF50; color: white; }}
        .status-attention {{ background: #FF9800; color: white; }}
        .status-running {{ background: #2196F3; color: white; }}
        .status-unknown {{ background: #9E9E9E; color: white; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: #f9f9f9; padding: 20px; border-radius: 8px; text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #333; }}
        .metric-label {{ color: #666; font-size: 0.9em; }}
        .skills-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .skill-card {{ border: 1px solid #ddd; border-radius: 8px; padding: 20px; }}
        .skill-status {{ font-weight: bold; margin-bottom: 10px; }}
        .skill-status.completed {{ color: #4CAF50; }}
        .skill-status.failed {{ color: #f44336; }}
        .skill-status.running {{ color: #2196F3; }}
        .skill-status.unknown {{ color: #9E9E9E; }}
        .recent-sessions {{ margin-top: 30px; }}
        .session-item {{ padding: 10px; border-bottom: 1px solid #eee; }}
        .timestamp {{ color: #666; font-size: 0.8em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Nightly Scan Status Dashboard</h1>
            <div class="status-badge status-{status['overall_status']}">
                {status['overall_status'].upper()}
            </div>
        </div>
        
        <p><strong>Last Updated:</strong> {timestamp}</p>
        
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{len(status['recent_sessions'])}</div>
                <div class="metric-label">Recent Sessions</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(status['active_sessions'])}</div>
                <div class="metric-label">Active Sessions</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{status['skills']['security-check']['findings']}</div>
                <div class="metric-label">Security Issues</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{status['skills']['bug-scan']['findings']}</div>
                <div class="metric-label">Bugs Found</div>
            </div>
        </div>
        
        <h2>Skill Status</h2>
        <div class="skills-grid">
            {generate_skill_cards(status['skills'])}
        </div>
        
        <div class="recent-sessions">
            <h2>Recent Sessions</h2>
            {generate_session_list(status['recent_sessions'])}
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>"""

def generate_skill_cards(skills: dict) -> str:
    """Generate HTML for skill status cards"""
    cards = []
    for skill_name, skill_data in skills.items():
        status_class = skill_data.get("status", "unknown")
        cards.append(f"""
            <div class="skill-card">
                <div class="skill-status {status_class}">
                    {skill_data['status'].upper()}
                </div>
                <h3>{skill_name}</h3>
                <p><strong>Last Run:</strong> {skill_data.get('last_run', 'Never')}</p>
                <p><strong>Findings:</strong> {skill_data.get('findings', 0)}</p>
            </div>
        """)
    return "".join(cards)

def generate_session_list(sessions: list) -> str:
    """Generate HTML for recent sessions list"""
    if not sessions:
        return "<p>No recent sessions</p>"
    
    items = []
    for session in sessions[:5]:
        items.append(f"""
            <div class="session-item">
                <strong>{session.get('skill', 'Unknown')}</strong>
                <span class="timestamp">{session.get('end_time', 'Unknown time')}</span>
                <br>
                Status: {session.get('status', 'Unknown')} | 
                Duration: {session.get('duration_seconds', 0) / 60:.1f} min |
                Findings: {session.get('findings_count', 0)}
            </div>
        """)
    return "".join(items)

if __name__ == "__main__":
    update_status_dashboard()