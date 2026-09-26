#!/usr/bin/env python3
"""
PR Scoring Dashboard
Generate dashboard showing PR scoring trends and historical data
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

def generate_pr_scoring_dashboard():
    """Generate comprehensive PR scoring dashboard"""
    timestamp = datetime.now().isoformat()
    
    # Load historical data
    storage_dir = Path("pr_tracking")
    scores_database = storage_dir / "scores_database.json"
    pr_database = storage_dir / "pr_database.json"
    
    if not scores_database.exists():
        print("No scoring data available yet")
        return
    
    with open(scores_database, "r") as f:
        scores = json.load(f)
    
    # Calculate trends and statistics
    dashboard_data = {
        "timestamp": timestamp,
        "summary": calculate_summary(scores),
        "trends": calculate_trends(scores),
        "top_prs": get_top_prs(scores),
        "grade_distribution": get_grade_distribution(scores),
        "metric_comparison": compare_metrics(scores)
    }
    
    # Generate HTML dashboard
    dashboard_html = generate_dashboard_html(dashboard_data)
    
    # Save dashboard
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    dashboard_file = reports_dir / "pr-scoring-dashboard.html"
    with open(dashboard_file, "w") as f:
        f.write(dashboard_html)
    
    # Save JSON data for API consumption
    json_file = reports_dir / "pr-scoring-data.json"
    with open(json_file, "w") as f:
        json.dump(dashboard_data, f, indent=2)
    
    print(f"[{timestamp}] PR scoring dashboard generated")
    return dashboard_data

def calculate_summary(scores: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate summary statistics"""
    if not scores:
        return {"total_prs": 0}
    
    total_prs = len(scores)
    avg_overall = sum(s["overall_score"] for s in scores) / total_prs
    avg_bug_detection = sum(s["bug_detection_score"] for s in scores) / total_prs
    avg_fix_quality = sum(s["fix_quality_score"] for s in scores) / total_prs
    
    grade_counts = {}
    for score in scores:
        grade = score["grade"]
        grade_counts[grade] = grade_counts.get(grade, 0) + 1
    
    return {
        "total_prs": total_prs,
        "average_overall_score": round(avg_overall, 2),
        "average_bug_detection": round(avg_bug_detection, 2),
        "average_fix_quality": round(avg_fix_quality, 2),
        "grade_distribution": grade_counts,
        "top_grade": max(grade_counts.keys()) if grade_counts else "N/A"
    }

def calculate_trends(scores: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate scoring trends over time"""
    if len(scores) < 4:
        return {"trend": "insufficient_data"}
    
    # Split into quarters for trend analysis
    quarter_size = len(scores) // 4
    quarters = [
        scores[:quarter_size],
        scores[quarter_size:quarter_size*2],
        scores[quarter_size*2:quarter_size*3],
        scores[quarter_size*3:]
    ]
    
    quarter_avgs = [sum(s["overall_score"] for s in q) / len(q) if q else 0 for q in quarters]
    
    # Determine trend
    if quarter_avgs[-1] > quarter_avgs[0]:
        trend = "improving"
    elif quarter_avgs[-1] < quarter_avgs[0]:
        trend = "declining"
    else:
        trend = "stable"
    
    return {
        "trend": trend,
        "quarter_averages": [round(avg, 2) for avg in quarter_avgs],
        "improvement": round(quarter_avgs[-1] - quarter_avgs[0], 2)
    }

def get_top_prs(scores: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    """Get top performing PRs"""
    sorted_scores = sorted(scores, key=lambda x: x["overall_score"], reverse=True)
    return sorted_scores[:limit]

def get_grade_distribution(scores: List[Dict[str, Any]]) -> Dict[str, int]:
    """Get distribution of grades"""
    distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for score in scores:
        distribution[score["grade"]] += 1
    return distribution

def compare_metrics(scores: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compare bug detection vs fix quality metrics"""
    if not scores:
        return {}
    
    avg_bug_detection = sum(s["bug_detection_score"] for s in scores) / len(scores)
    avg_fix_quality = sum(s["fix_quality_score"] for s in scores) / len(scores)
    
    # Count which metric is stronger
    bug_stronger = sum(1 for s in scores if s["bug_detection_score"] > s["fix_quality_score"])
    fix_stronger = sum(1 for s in scores if s["fix_quality_score"] > s["bug_detection_score"])
    
    return {
        "average_bug_detection": round(avg_bug_detection, 2),
        "average_fix_quality": round(avg_fix_quality, 2),
        "bug_stronger_count": bug_stronger,
        "fix_stronger_count": fix_stronger,
        "stronger_metric": "bug_detection" if bug_stronger > fix_stronger else "fix_quality"
    }

def generate_dashboard_html(data: Dict[str, Any]) -> str:
    """Generate HTML dashboard for PR scoring"""
    summary = data["summary"]
    trends = data["trends"]
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>PR Scoring Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
        .summary-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{ background: #f9f9f9; padding: 20px; border-radius: 8px; text-align: center; }}
        .card-value {{ font-size: 2em; font-weight: bold; color: #333; }}
        .card-label {{ color: #666; font-size: 0.9em; }}
        .trend-section {{ margin-bottom: 30px; }}
        .grade-bar {{ display: flex; height: 30px; margin: 10px 0; }}
        .grade-segment {{ height: 100%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; }}
        .grade-A {{ background: #4CAF50; }}
        .grade-B {{ background: #2196F3; }}
        .grade-C {{ background: #FF9800; }}
        .grade-D {{ background: #f44336; }}
        .grade-F {{ background: #9E9E9E; }}
        .top-prs {{ margin-top: 30px; }}
        .pr-item {{ padding: 15px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }}
        .pr-score {{ font-weight: bold; }}
        .score-high {{ color: #4CAF50; }}
        .score-medium {{ color: #FF9800; }}
        .score-low {{ color: #f44336; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 PR Scoring Dashboard</h1>
            <div>
                <strong>Last Updated:</strong> {data['timestamp']}
            </div>
        </div>
        
        <h2>Summary Statistics</h2>
        <div class="summary-cards">
            <div class="card">
                <div class="card-value">{summary['total_prs']}</div>
                <div class="card-label">Total PRs Scored</div>
            </div>
            <div class="card">
                <div class="card-value">{summary['average_overall_score']}</div>
                <div class="card-label">Average Overall Score</div>
            </div>
            <div class="card">
                <div class="card-value">{summary['average_bug_detection']}</div>
                <div class="card-label">Avg Bug Detection</div>
            </div>
            <div class="card">
                <div class="card-value">{summary['average_fix_quality']}</div>
                <div class="card-label">Avg Fix Quality</div>
            </div>
            <div class="card">
                <div class="card-value">{summary['top_grade']}</div>
                <div class="card-label">Most Common Grade</div>
            </div>
        </div>
        
        <div class="trend-section">
            <h2>Scoring Trends</h2>
            <p><strong>Trend:</strong> {trends.get('trend', 'N/A').upper()}</p>
            <p><strong>Improvement:</strong> {trends.get('improvement', 0):+f}</p>
            <p><strong>Quarterly Averages:</strong> {', '.join(map(str, trends.get('quarter_averages', [])))}</p>
        </div>
        
        <h2>Grade Distribution</h2>
        {generate_grade_bar(data['grade_distribution'])}
        
        <div class="top-prs">
            <h2>Top Performing PRs</h2>
            {generate_top_prs_list(data['top_prs'])}
        </div>
        
        <div class="trend-section">
            <h2>Metric Comparison</h2>
            <p><strong>Average Bug Detection:</strong> {data['metric_comparison'].get('average_bug_detection', 'N/A')}</p>
            <p><strong>Average Fix Quality:</strong> {data['metric_comparison'].get('average_fix_quality', 'N/A')}</p>
            <p><strong>Stronger Metric:</strong> {data['metric_comparison'].get('stronger_metric', 'N/A').upper()}</p>
        </div>
    </div>
    
    <script>
        setTimeout(() => location.reload(), 60000); // Refresh every minute
    </script>
</body>
</html>"""

def generate_grade_bar(distribution: Dict[str, int]) -> str:
    """Generate grade distribution bar"""
    total = sum(distribution.values())
    if total == 0:
        return "<p>No grade data available</p>"
    
    segments = []
    for grade in ["A", "B", "C", "D", "F"]:
        count = distribution.get(grade, 0)
        if count > 0:
            percentage = (count / total) * 100
            segments.append(f"""
                <div class="grade-bar">
                    <div class="grade-segment grade-{grade}" style="width: {percentage}%">
                        {grade}: {count} ({percentage:.1f}%)
                    </div>
                </div>
            """)
    
    return "\n".join(segments)

def generate_top_prs_list(top_prs: List[Dict[str, Any]]) -> str:
    """Generate list of top PRs"""
    if not top_prs:
        return "<p>No PR data available</p>"
    
    items = []
    for pr in top_prs:
        score_class = "score-high" if pr["overall_score"] >= 80 else "score-medium" if pr["overall_score"] >= 60 else "score-low"
        
        items.append(f"""
            <div class="pr-item">
                <span><strong>PR #{pr['pr_number']}</strong></span>
                <span class="pr-score {score_class}">{pr['overall_score']}/100 ({pr['grade']})</span>
                <span>Bug: {pr['bug_detection_score']}/100 | Fix: {pr['fix_quality_score']}/100</span>
            </div>
        """)
    
    return "\n".join(items)

if __name__ == "__main__":
    generate_pr_scoring_dashboard()