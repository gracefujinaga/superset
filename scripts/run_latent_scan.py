#!/usr/bin/env python3
"""
Latent Bugs Scan Script
Invokes Devin CLI with latent-bugs skill for nightly automation
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from devin_session_manager import DevinSessionManager

def run_devin_latent_scan():
    """Run Devin CLI with latent-bugs skill"""
    manager = DevinSessionManager()
    result = manager.run_skill("latent-bugs")
    return result.get("status") == "completed"

if __name__ == "__main__":
    success = run_devin_latent_scan()
    exit(0 if success else 1)