#!/usr/bin/env python3
"""
Security Scan Script
Invokes Devin CLI with security-check skill for nightly automation
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from devin_session_manager import DevinSessionManager

def run_devin_security_check():
    """Run Devin CLI with security-check skill"""
    manager = DevinSessionManager()
    result = manager.run_skill("security-check")
    return result.get("status") == "completed"

if __name__ == "__main__":
    success = run_devin_security_check()
    exit(0 if success else 1)