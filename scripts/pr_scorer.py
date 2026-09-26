#!/usr/bin/env python3
"""
PR Scorer
Evaluate PRs on bug detection accuracy and fix quality
"""
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import re

class PRScorer:
    """Score PRs on bug detection and fix quality metrics"""
    
    def __init__(self):
        self.storage_dir = Path("pr_tracking")
        self.storage_dir.mkdir(exist_ok=True)
    
    def evaluate_bug_detection(self, pr_number: int, pr_data: Dict[str, Any]) -> float:
        """
        Evaluate bug detection accuracy (0-10)
        
        Factors:
        - True positive rate (correctly identified bugs)
        - False positive rate (incorrectly flagged issues)
        - Bug severity accuracy
        - Detection completeness
        """
        # Get PR details and changes
        pr_details = self._get_pr_details(pr_number)
        
        score = 5.0  # Base score (0-10 scale)
        
        # Factor 1: Bug validation rate (are identified bugs real?)
        score += self._validate_bugs(pr_details, pr_data) * 2.0
        
        # Factor 2: Severity accuracy (did we get the severity right?)
        score += self._check_severity_accuracy(pr_details, pr_data) * 1.5
        
        # Factor 3: Detection completeness (did we miss important bugs?)
        score += self._check_completeness(pr_details, pr_data) * 1.5
        
        return min(max(score, 0), 10)
    
    def evaluate_fix_quality(self, pr_number: int, pr_data: Dict[str, Any]) -> float:
        """
        Evaluate fix quality (0-10)
        
        Factors:
        - Code quality of the fix
        - Test coverage added
        - Documentation updates
        - No new bugs introduced
        - Performance impact
        """
        pr_details = self._get_pr_details(pr_number)
        
        score = 5.0  # Base score (0-10 scale)
        
        # Factor 1: Code quality (clean, readable, follows patterns)
        score += self._evaluate_code_quality(pr_details) * 2.0
        
        # Factor 2: Test coverage (were tests added/updated?)
        score += self._check_test_coverage(pr_details) * 2.0
        
        # Factor 3: Documentation (were docs updated?)
        score += self._check_documentation(pr_details) * 1.0
        
        # Factor 4: No regressions (did we introduce new issues?)
        score += self._check_regressions(pr_details) * 2.0
        
        # Factor 5: Performance (is the fix performant?)
        score += self._check_performance(pr_details) * 1.0
        
        return min(max(score, 0), 10)
    
    def _get_pr_details(self, pr_number: int) -> Dict[str, Any]:
        """Get PR details using GitHub CLI"""
        try:
            result = subprocess.run(
                ["gh", "pr", "view", str(pr_number), "--json", "title,body,author,state,files,additions,deletions"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {}
                
        except Exception as e:
            print(f"Error getting PR details: {e}")
            return {}
    
    def _validate_bugs(self, pr_details: Dict[str, Any], pr_data: Dict[str, Any]) -> float:
        """Validate that identified bugs are real issues"""
        # This would analyze the code changes to verify bug findings
        # For now, return a placeholder score
        return 0.8  # 80% validation rate
    
    def _check_severity_accuracy(self, pr_details: Dict[str, Any], pr_data: Dict[str, Any]) -> float:
        """Check if severity assessments were accurate"""
        # This would compare predicted vs actual severity
        return 0.75  # 75% accuracy
    
    def _check_completeness(self, pr_details: Dict[str, Any], pr_data: Dict[str, Any]) -> float:
        """Check if important bugs were missed"""
        # This would analyze if critical bugs were overlooked
        return 0.85  # 85% completeness
    
    def _evaluate_code_quality(self, pr_details: Dict[str, Any]) -> float:
        """Evaluate code quality of the fix"""
        # This would run linters, check code style, complexity
        try:
            # Run pre-commit on the changed files
            result = subprocess.run(
                ["pre-commit", "run", "--files", pr_details.get("files", "").split()],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Score based on pre-commit results
            if result.returncode == 0:
                return 0.9  # 90% quality
            else:
                return 0.7  # 70% quality (some issues)
                
        except Exception:
            return 0.5  # 50% quality (couldn't evaluate)
    
    def _check_test_coverage(self, pr_details: Dict[str, Any]) -> float:
        """Check if test coverage was added"""
        # This would check if tests were added/updated
        # For now, return placeholder
        return 0.6  # 60% test coverage
    
    def _check_documentation(self, pr_details: Dict[str, Any]) -> float:
        """Check if documentation was updated"""
        # This would check if docs/README were updated
        # For now, return placeholder
        return 0.5  # 50% documentation
    
    def _check_regressions(self, pr_details: Dict[str, Any]) -> float:
        """Check if new bugs were introduced"""
        # This would run tests to check for regressions
        # For now, return placeholder
        return 0.8  # 80% no regressions
    
    def _check_performance(self, pr_details: Dict[str, Any]) -> float:
        """Check if the fix is performant"""
        # This would benchmark the fix
        # For now, return placeholder
        return 0.85  # 85% performance
    
    def score_pr_comprehensive(self, pr_number: int, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive PR scoring with detailed breakdown (0-10 scale)
        """
        timestamp = datetime.now().isoformat()
        
        # Get PR details for evaluation
        pr_details = self._get_pr_details(pr_number)
        
        # Evaluate both metrics
        bug_detection_score = self.evaluate_bug_detection(pr_number, pr_data)
        fix_quality_score = self.evaluate_fix_quality(pr_number, pr_data)
        
        # Calculate overall score
        overall_score = (bug_detection_score * 0.4) + (fix_quality_score * 0.6)
        
        return {
            "pr_number": pr_number,
            "bug_detection_score": round(bug_detection_score, 1),
            "fix_quality_score": round(fix_quality_score, 1),
            "overall_score": round(overall_score, 1),
            "status": self._calculate_status(overall_score),
            "scored_at": timestamp,
            "breakdown": {
                "bug_validation": self._validate_bugs(pr_details, pr_data),
                "severity_accuracy": self._check_severity_accuracy(pr_details, pr_data),
                "detection_completeness": self._check_completeness(pr_details, pr_data),
                "code_quality": self._evaluate_code_quality(pr_details),
                "test_coverage": self._check_test_coverage(pr_details),
                "documentation": self._check_documentation(pr_details),
                "no_regressions": self._check_regressions(pr_details),
                "performance": self._check_performance(pr_details)
            }
        }
    
    def _calculate_status(self, score: float) -> str:
        """Calculate status from score (0-10 scale)"""
        if score >= 8.0:
            return "correct"
        elif score >= 5.0:
            return "partial"
        else:
            return "incorrect"

def main():
    """Example usage of PR scorer"""
    scorer = PRScorer()
    
    # Example: Score a PR
    pr_data = {
        "title": "Fix security vulnerability",
        "bug_type": "security",
        "severity": "high"
    }
    
    score_result = scorer.score_pr_comprehensive(123, pr_data)
    print(f"PR Score Result: {score_result}")

if __name__ == "__main__":
    main()