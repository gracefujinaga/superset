#!/usr/bin/env python3
"""
PR Tracker and Scoring System
Track PRs over time, score them on bug detection and fix quality, and store historical data
"""
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

class PRTracker:
    """Track and score PRs for bug detection and fix quality"""
    
    def __init__(self, storage_dir: str = "pr_tracking"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.pr_database = self.storage_dir / "pr_database.json"
        self.scores_database = self.storage_dir / "scores_database.json"
        self._initialize_databases()
    
    def _initialize_databases(self):
        """Initialize database files if they don't exist"""
        if not self.pr_database.exists():
            with open(self.pr_database, "w") as f:
                json.dump({}, f)
        
        if not self.scores_database.exists():
            with open(self.scores_database, "w") as f:
                json.dump([], f)
    
    def track_pr(self, pr_number: int, pr_data: Dict[str, Any]) -> None:
        """Track a new PR with its metadata"""
        pr_data["tracked_at"] = datetime.now().isoformat()
        pr_data["scored"] = False
        
        # Load existing database
        with open(self.pr_database, "r") as f:
            database = json.load(f)
        
        # Add/update PR
        database[str(pr_number)] = pr_data
        
        # Save updated database
        with open(self.pr_database, "w") as f:
            json.dump(database, f, indent=2)
        
        print(f"Tracked PR #{pr_number}")
    
    def score_pr(self, pr_number: int, bug_detection_score: float, fix_quality_score: float) -> Dict[str, Any]:
        """
        Score a PR on two metrics:
        - Bug Detection Score (0-10): How accurate was the bug detection
        - Fix Quality Score (0-10): How good was the fix applied
        
        Returns overall score and component scores
        """
        timestamp = datetime.now().isoformat()
        
        # Calculate overall score (weighted average)
        # Bug detection: 40% weight, Fix quality: 60% weight
        overall_score = (bug_detection_score * 0.4) + (fix_quality_score * 0.6)
        
        score_data = {
            "pr_number": pr_number,
            "bug_detection_score": round(bug_detection_score, 1),
            "fix_quality_score": round(fix_quality_score, 1),
            "overall_score": round(overall_score, 1),
            "scored_at": timestamp,
            "status": self._calculate_status(overall_score)
        }
        
        # Load scores database
        with open(self.scores_database, "r") as f:
            scores = json.load(f)
        
        # Add score
        scores.append(score_data)
        
        # Save updated scores
        with open(self.scores_database, "w") as f:
            json.dump(scores, f, indent=2)
        
        # Update PR database to mark as scored
        with open(self.pr_database, "r") as f:
            database = json.load(f)
        
        if str(pr_number) in database:
            database[str(pr_number)]["scored"] = True
            database[str(pr_number)]["score"] = score_data
        
        with open(self.pr_database, "w") as f:
            json.dump(database, f, indent=2)
        
        print(f"Scored PR #{pr_number}: Detection={bug_detection_score}, Fix={fix_quality_score}, Overall={overall_score:.1f}")
        
        return score_data
    
    def _calculate_status(self, score: float) -> str:
        """Calculate status from score (0-10 scale)"""
        if score >= 8.0:
            return "correct"
        elif score >= 5.0:
            return "partial"
        else:
            return "incorrect"
    
    def tag_pr_with_score(self, pr_number: int, score_data: Dict[str, Any]) -> bool:
        """Tag the PR with its score using GitHub CLI"""
        try:
            # Create score tag format (0-10 scale)
            tag_message = f"📊 PR Score: {score_data['overall_score']}/10 (Status: {score_data['status']})\n" \
                        f"Bug Detection: {score_data['bug_detection_score']}/10\n" \
                        f"Fix Quality: {score_data['fix_quality_score']}/10"
            
            # Use GitHub CLI to add comment with score
            result = subprocess.run(
                ["gh", "pr", "comment", str(pr_number), "--body", tag_message],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"Successfully tagged PR #{pr_number} with score")
                return True
            else:
                print(f"Failed to tag PR #{pr_number}: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error tagging PR #{pr_number}: {e}")
            return False
    
    def get_pr_score(self, pr_number: int) -> Optional[Dict[str, Any]]:
        """Get the score for a specific PR"""
        with open(self.scores_database, "r") as f:
            scores = json.load(f)
        
        for score in scores:
            if score["pr_number"] == pr_number:
                return score
        
        return None
    
    def get_historical_scores(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get historical scores for trend analysis"""
        with open(self.scores_database, "r") as f:
            scores = json.load(f)
        
        # Sort by scored_at and return last N
        scores.sort(key=lambda x: x["scored_at"], reverse=True)
        return scores[:limit]
    
    def get_score_trends(self) -> Dict[str, Any]:
        """Calculate scoring trends over time"""
        scores = self.get_historical_scores(100)
        
        if len(scores) < 2:
            return {"trend": "insufficient_data"}
        
        # Split into two halves for trend comparison
        mid_point = len(scores) // 2
        first_half = scores[:mid_point]
        second_half = scores[mid_point:]
        
        # Calculate averages
        first_avg = sum(s["overall_score"] for s in first_half) / len(first_half)
        second_avg = sum(s["overall_score"] for s in second_half) / len(second_half)
        
        # Calculate trends
        bug_detection_trend = "improving" if second_avg > first_avg else "declining"
        fix_quality_trend = "improving" if second_avg > first_avg else "declining"
        
        return {
            "overall_trend": "improving" if second_avg > first_avg else "declining",
            "change": second_avg - first_avg,
            "first_half_avg": round(first_avg, 2),
            "second_half_avg": round(second_avg, 2),
            "bug_detection_trend": bug_detection_trend,
            "fix_quality_trend": fix_quality_trend,
            "total_prs_scored": len(scores)
        }

def main():
    """Example usage of PR tracker"""
    tracker = PRTracker()
    
    # Example: Track a PR
    tracker.track_pr(123, {
        "title": "Fix security vulnerability in authentication",
        "author": "devin-bot",
        "created_at": datetime.now().isoformat(),
        "files_changed": 5,
        "bug_type": "security"
    })
    
    # Example: Score a PR
    score_data = tracker.score_pr(123, bug_detection_score=85.0, fix_quality_score=92.0)
    
    # Example: Tag the PR
    tracker.tag_pr_with_score(123, score_data)
    
    # Example: Get trends
    trends = tracker.get_score_trends()
    print(f"Score trends: {trends}")

if __name__ == "__main__":
    main()