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
    
    def categorize_pr(self, pr_number: int, category: str) -> Dict[str, Any]:
        """
        Categorize a PR into one of three categories:
        - correct: Bug detection and fix quality both meet standards
        - partial: Either bug detection or fix quality partially meets standards
        - incorrect: Neither bug detection nor fix quality meets standards
        
        Returns category data
        """
        timestamp = datetime.now().isoformat()
        
        # Validate category
        valid_categories = ["correct", "partial", "incorrect"]
        if category not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {valid_categories}")
        
        category_data = {
            "pr_number": pr_number,
            "category": category,
            "categorized_at": timestamp
        }
        
        # Load scores database
        with open(self.scores_database, "r") as f:
            scores = json.load(f)
        
        # Add category
        scores.append(category_data)
        
        # Save updated scores
        with open(self.scores_database, "w") as f:
            json.dump(scores, f, indent=2)
        
        # Update PR database to mark as categorized
        with open(self.pr_database, "r") as f:
            database = json.load(f)
        
        if str(pr_number) in database:
            database[str(pr_number)]["categorized"] = True
            database[str(pr_number)]["category"] = category_data
        
        with open(self.pr_database, "w") as f:
            json.dump(database, f, indent=2)
        
        print(f"Categorized PR #{pr_number}: {category}")
        
        return category_data
    
    def tag_pr_with_category(self, pr_number: int, category_data: Dict[str, Any]) -> bool:
        """Tag the PR with its category using GitHub CLI"""
        try:
            # Create category tag format
            tag_message = f"📊 PR Category: {category_data['category']}\n" \
                        f"Categorized at: {category_data['categorized_at']}"
            
            # Use GitHub CLI to add comment with category
            result = subprocess.run(
                ["gh", "pr", "comment", str(pr_number), "--body", tag_message],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"Successfully tagged PR #{pr_number} with category")
                return True
            else:
                print(f"Failed to tag PR #{pr_number}: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error tagging PR #{pr_number}: {e}")
            return False
    
    def get_pr_category(self, pr_number: int) -> Optional[Dict[str, Any]]:
        """Get the category for a specific PR"""
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