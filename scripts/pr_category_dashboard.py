#!/usr/bin/env python3
"""
PR Category Dashboard
Track PR categories (correct/partial/incorrect) with time-bucketed counts
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

def generate_pr_category_dashboard():
    """Generate PR category tracking dashboard with time-bucketed counts"""
    timestamp = datetime.now().isoformat()
    
    # Load historical data
    storage_dir = Path("pr_tracking")
    scores_database = storage_dir / "scores_database.json"
    
    if not scores_database.exists():
        print("No category data available yet")
        return
    
    with open(scores_database, "r") as f:
        categories = json.load(f)
    
    # Calculate time-bucketed counts
    time_buckets = calculate_time_buckets(categories)
    
    # Calculate overall statistics
    stats = calculate_category_stats(categories)
    
    # Generate HTML dashboard
    dashboard_html = generate_category_dashboard_html(time_buckets, stats, timestamp)
    
    # Save dashboard
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    dashboard_file = reports_dir / "pr-category-dashboard.html"
    with open(dashboard_file, "w") as f:
        f.write(dashboard_html)
    
    # Save JSON data for API consumption
    json_file = reports_dir / "pr-category-data.json"
    with open(json_file, "w") as f:
        json.dump({"time_buckets": time_buckets, "stats": stats, "timestamp": timestamp}, f, indent=2)
    
    print(f"[{timestamp}] PR category dashboard generated")
    return time_buckets

def calculate_time_buckets(categories: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate category counts in time buckets (daily/weekly)"""
    time_buckets = {
        "daily": {},
        "weekly": {}
    }
    
    # Group by date
    for category in categories:
        categorized_at = category.get("categorized_at", "")
        if not categorized_at:
            continue
        
        date = categorized_at.split("T")[0]
        if date not in time_buckets["daily"]:
            time_buckets["daily"][date] = {"correct": 0, "partial": 0, "incorrect": 0}
        
        cat = category.get("category", "unknown")
        if cat in time_buckets["daily"][date]:
            time_buckets["daily"][date][cat] += 1
    
    # Calculate weekly aggregates
    for date, counts in time_buckets["daily"].items():
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            week_key = f"{dt.year}-W{dt.isocalendar()[1]:02d}"
            
            if week_key not in time_buckets["weekly"]:
                time_buckets["weekly"][week_key] = {"correct": 0, "partial": 0, "incorrect": 0}
            
            time_buckets["weekly"][week_key]["correct"] += counts["correct"]
            time_buckets["weekly"][week_key]["partial"] += counts["partial"]
            time_buckets["weekly"][week_key]["incorrect"] += counts["incorrect"]
        except ValueError:
            continue
    
    return time_buckets

def calculate_category_stats(categories: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate overall category statistics"""
    if not categories:
        return {"total_prs": 0}
    
    total_prs = len(categories)
    category_counts = {"correct": 0, "partial": 0, "incorrect": 0}
    
    for category in categories:
        cat = category.get("category", "unknown")
        if cat in category_counts:
            category_counts[cat] += 1
    
    return {
        "total_prs": total_prs,
        "category_counts": category_counts,
        "most_common_category": max(category_counts, key=category_counts.get) if category_counts else "N/A"
    }

def generate_category_dashboard_html(time_buckets: Dict[str, Any], stats: Dict[str, Any], timestamp: str) -> str:
    """Generate HTML dashboard for PR category tracking"""
    daily_data = time_buckets.get("daily", {})
    weekly_data = time_buckets.get("weekly", {})
    
    # Get last 30 days for display
    sorted_dates = sorted(daily_data.keys())[-30:]
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>PR Category Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
        .summary-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{ background: #f9f9f9; padding: 20px; border-radius: 8px; text-align: center; }}
        .card-value {{ font-size: 2em; font-weight: bold; color: #333; }}
        .card-label {{ color: #666; font-size: 0.9em; }}
        .bucket-section {{ margin-bottom: 30px; }}
        .bucket-container {{ background: #f9f9f9; padding: 20px; border-radius: 8px; }}
        .data-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        .data-table th, .data-table td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        .data-table th {{ background: #2196F3; color: white; }}
        .category-correct {{ color: #4CAF50; font-weight: bold; }}
        .category-partial {{ color: #FF9800; font-weight: bold; }}
        .category-incorrect {{ color: #f44336; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 PR Category Dashboard</h1>
            <div>
                <strong>Last Updated:</strong> {timestamp}
            </div>
        </div>
        
        <h2>Overall Statistics</h2>
        <div class="summary-cards">
            <div class="card">
                <div class="card-value">{stats['total_prs']}</div>
                <div class="card-label">Total PRs Categorized</div>
            </div>
            <div class="card">
                <div class="card-value">{stats['category_counts']['correct']}</div>
                <div class="card-label">Correct</div>
            </div>
            <div class="card">
                <div class="card-value">{stats['category_counts']['partial']}</div>
                <div class="card-label">Partial</div>
            </div>
            <div class="card">
                <div class="card-value">{stats['category_counts']['incorrect']}</div>
                <div class="card-label">Incorrect</div>
            </div>
            <div class="card">
                <div class="card-value">{stats['most_common_category']}</div>
                <div class="card-label">Most Common Category</div>
            </div>
        </div>
        
        <div class="bucket-section">
            <h2>Daily Category Buckets (Last 30 Days)</h2>
            <div class="bucket-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Correct</th>
                            <th>Partial</th>
                            <th>Incorrect</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {generate_daily_bucket_rows(sorted_dates, daily_data)}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="bucket-section">
            <h2>Weekly Category Buckets</h2>
            <div class="bucket-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Week</th>
                            <th>Correct</th>
                            <th>Partial</th>
                            <th>Incorrect</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {generate_weekly_bucket_rows(weekly_data)}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script>
        setTimeout(() => location.reload(), 60000); // Refresh every minute
    </script>
</body>
</html>"""

def generate_daily_bucket_rows(dates: List[str], daily_data: Dict[str, Any]) -> str:
    """Generate table rows for daily category buckets"""
    if not dates:
        return "<tr><td colspan='5'>No data available</td></tr>"
    
    rows = []
    for date in reversed(dates):
        data = daily_data.get(date, {"correct": 0, "partial": 0, "incorrect": 0})
        total = data["correct"] + data["partial"] + data["incorrect"]
        
        rows.append(f"""
            <tr>
                <td>{date}</td>
                <td class="category-correct">{data['correct']}</td>
                <td class="category-partial">{data['partial']}</td>
                <td class="category-incorrect">{data['incorrect']}</td>
                <td>{total}</td>
            </tr>
        """)
    
    return "\n".join(rows)

def generate_weekly_bucket_rows(weekly_data: Dict[str, Any]) -> str:
    """Generate table rows for weekly category buckets"""
    if not weekly_data:
        return "<tr><td colspan='5'>No data available</td></tr>"
    
    rows = []
    for week in sorted(weekly_data.keys(), reverse=True):
        data = weekly_data[week]
        total = data["correct"] + data["partial"] + data["incorrect"]
        
        rows.append(f"""
            <tr>
                <td>{week}</td>
                <td class="category-correct">{data['correct']}</td>
                <td class="category-partial">{data['partial']}</td>
                <td class="category-incorrect">{data['incorrect']}</td>
                <td>{total}</td>
            </tr>
        """)
    
    return "\n".join(rows)

if __name__ == "__main__":
    generate_pr_category_dashboard()
