#!/usr/bin/env python3
"""
Get session status for GitHub Actions outputs
"""
import json
import sys
from pathlib import Path
from datetime import datetime

def get_session_status(skill_name: str):
    """Get the latest status for a specific skill"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        return "not_started"
    
    # Find the most recent session
    session_dirs = sorted([d for d in logs_dir.iterdir() if d.is_dir()], reverse=True)
    if not session_dirs:
        return "not_started"
    
    latest_session = session_dirs[0]
    status_file = latest_session / "status.json"
    
    if not status_file.exists():
        return "not_started"
    
    with open(status_file, "r") as f:
        status = json.load(f)
    
    return status.get("status", "unknown")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        skill = sys.argv[1]
        print(get_session_status(skill))
    else:
        print("Usage: python get_session_status.py <skill_name>")