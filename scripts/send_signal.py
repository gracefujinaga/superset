#!/usr/bin/env python3
"""
Send Success/Failure Signals
External notifications for system observability
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

def send_signal(signal_type: str):
    """Send signal about scan completion status"""
    timestamp = datetime.now().isoformat()
    
    print(f"[{timestamp}] Sending {signal_type} signal...")
    
    # Create signal record
    signal = {
        "type": signal_type,
        "timestamp": timestamp,
        "workflow_run": os.environ.get("GITHUB_RUN_NUMBER", "local"),
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "branch": os.environ.get("GITHUB_REF_NAME", "local")
    }
    
    # Save signal record
    signals_dir = Path("signals")
    signals_dir.mkdir(exist_ok=True)
    
    signal_file = signals_dir / f"{signal_type}-{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
    with open(signal_file, "w") as f:
        json.dump(signal, f, indent=2)
    
    # Here you could integrate with external systems:
    # - Slack/Teams notifications
    # - PagerDuty alerts
    # - Custom webhooks
    # - Monitoring systems (Datadog, New Relic, etc.)
    
    print(f"[{timestamp}] {signal_type.upper()} signal sent successfully")
    
    # Log to stdout for CI/CD visibility
    if signal_type == "success":
        print("✅ NIGHTLY SCAN COMPLETED SUCCESSFULLY")
    else:
        print("❌ NIGHTLY SCAN FAILED - ATTENTION REQUIRED")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        signal_type = sys.argv[1]
        send_signal(signal_type)
    else:
        print("Usage: python send_signal.py <success|failure>")