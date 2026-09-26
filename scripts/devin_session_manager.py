#!/usr/bin/env python3
"""
Devin Session Manager
Programmatically initiate and manage Devin sessions with proper observability
"""
import subprocess
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class DevinSessionManager:
    """Manage Devin CLI sessions with observability and error handling"""
    
    def __init__(self, workspace_dir: str = "."):
        self.workspace_dir = Path(workspace_dir)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = self.workspace_dir / "logs" / f"session_{self.session_id}"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.status_file = self.log_dir / "status.json"
        self.metrics_file = self.log_dir / "metrics.json"
        
    def run_skill(self, skill_name: str, args: str = "") -> Dict[str, Any]:
        """
        Run a Devin skill with full observability
        
        Args:
            skill_name: Name of the skill to run (e.g., "security-check")
            args: Additional arguments for the skill
            
        Returns:
            Dict containing session results and metrics
        """
        start_time = time.time()
        timestamp = datetime.now().isoformat()
        
        # Initialize session status
        self._update_status({
            "session_id": self.session_id,
            "skill": skill_name,
            "status": "running",
            "start_time": timestamp,
            "progress": 0,
            "current_step": "initializing"
        })
        
        try:
            # Construct Devin CLI command
            command = ["devin", "--non-interactive", f"/{skill_name}"]
            if args:
                command.append(args)
            
            self._update_status({
                "current_step": "executing_devin",
                "progress": 10
            })
            
            # Run Devin CLI with output capture
            result = subprocess.run(
                command,
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hour timeout
                env=os.environ.copy()
            )
            
            duration = time.time() - start_time
            
            # Parse results
            findings = self._parse_devin_output(result.stdout, result.stderr)
            
            # Update final status
            status_data = {
                "session_id": self.session_id,
                "skill": skill_name,
                "status": "completed" if result.returncode == 0 else "failed",
                "end_time": datetime.now().isoformat(),
                "duration_seconds": duration,
                "progress": 100,
                "current_step": "completed",
                "exit_code": result.returncode,
                "findings_count": len(findings),
                "findings": findings
            }
            
            self._update_status(status_data)
            
            # Update metrics
            self._update_metrics({
                "session_id": self.session_id,
                "skill": skill_name,
                "duration": duration,
                "success": result.returncode == 0,
                "findings_count": len(findings),
                "timestamp": timestamp
            })
            
            return status_data
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            error_data = {
                "session_id": self.session_id,
                "skill": skill_name,
                "status": "timeout",
                "end_time": datetime.now().isoformat(),
                "duration_seconds": duration,
                "progress": 100,
                "current_step": "timeout",
                "error": "Session timed out after 1 hour"
            }
            self._update_status(error_data)
            return error_data
            
        except Exception as e:
            duration = time.time() - start_time
            error_data = {
                "session_id": self.session_id,
                "skill": skill_name,
                "status": "error",
                "end_time": datetime.now().isoformat(),
                "duration_seconds": duration,
                "progress": 100,
                "current_step": "error",
                "error": str(e)
            }
            self._update_status(error_data)
            return error_data
    
    def _update_status(self, status_data: Dict[str, Any]):
        """Update session status file"""
        with open(self.status_file, "w") as f:
            json.dump(status_data, f, indent=2)
        
        # Also log to console for CI/CD visibility
        print(f"[STATUS] {status_data.get('current_step', 'unknown')}: {status_data.get('status', 'unknown')}")
        if "error" in status_data:
            print(f"[ERROR] {status_data['error']}")
    
    def _update_metrics(self, metrics_data: Dict[str, Any]):
        """Update metrics file"""
        existing_metrics = []
        if self.metrics_file.exists():
            with open(self.metrics_file, "r") as f:
                existing_metrics = json.load(f)
        
        existing_metrics.append(metrics_data)
        
        with open(self.metrics_file, "w") as f:
            json.dump(existing_metrics, f, indent=2)
    
    def _parse_devin_output(self, stdout: str, stderr: str) -> list:
        """Parse Devin CLI output to extract findings"""
        findings = []
        
        # Try to parse JSON output if Devin returns structured data
        try:
            if stdout:
                # Look for JSON blocks in output
                for line in stdout.split('\n'):
                    if line.strip().startswith('{') and line.strip().endswith('}'):
                        try:
                            data = json.loads(line)
                            if isinstance(data, dict) and 'findings' in data:
                                findings.extend(data['findings'])
                        except json.JSONDecodeError:
                            continue
        except Exception:
            pass
        
        # If no structured data, create basic finding from output
        if not findings and stdout:
            findings.append({
                "title": "Scan completed",
                "description": stdout[:500],  # Truncate if too long
                "severity": "info",
                "location": "various"
            })
        
        return findings
    
    def get_status(self) -> Dict[str, Any]:
        """Get current session status"""
        if self.status_file.exists():
            with open(self.status_file, "r") as f:
                return json.load(f)
        return {"status": "not_started"}
    
    def get_metrics(self) -> list:
        """Get all metrics for this session"""
        if self.metrics_file.exists():
            with open(self.metrics_file, "r") as f:
                return json.load(f)
        return []

def main():
    """Example usage of session manager"""
    manager = DevinSessionManager()
    
    # Run security check
    print("Running security check...")
    security_result = manager.run_skill("security-check")
    print(f"Security check: {security_result['status']}")
    
    # Run bug scan
    print("Running bug scan...")
    bug_result = manager.run_skill("bug-scan")
    print(f"Bug scan: {bug_result['status']}")
    
    # Run latent bugs scan
    print("Running latent bugs scan...")
    latent_result = manager.run_skill("latent-bugs")
    print(f"Latent bugs scan: {latent_result['status']}")
    
    # Get overall metrics
    metrics = manager.get_metrics()
    print(f"Total metrics recorded: {len(metrics)}")

if __name__ == "__main__":
    main()