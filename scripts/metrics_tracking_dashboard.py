#!/usr/bin/env python3
"""
Metrics Tracking Dashboard
Track and visualize all system metrics over time
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

def generate_metrics_tracking_dashboard():
    """Generate comprehensive metrics tracking dashboard with time-series data"""
    timestamp = datetime.now().isoformat()
    
    # Collect data from all sources
    logs_dir = Path("logs")
    pr_tracking_dir = Path("pr_tracking")
    reports_dir = Path("reports")
    
    # Collect session data
    session_data = collect_session_data(logs_dir)
    
    # Collect PR scoring data
    pr_data = collect_pr_data(pr_tracking_dir)
    
    # Collect metrics data
    metrics_data = collect_metrics_data(reports_dir)
    
    # Generate time-series data
    time_series = generate_time_series(session_data, pr_data, metrics_data)
    
    # Calculate overall trends
    trends = calculate_overall_trends(time_series)
    
    # Generate dashboard HTML
    dashboard_html = generate_dashboard_html(time_series, trends, timestamp)
    
    # Save dashboard
    reports_dir.mkdir(exist_ok=True)
    dashboard_file = reports_dir / "metrics-tracking-dashboard.html"
    with open(dashboard_file, "w") as f:
        f.write(dashboard_html)
    
    # Save JSON data for API consumption
    json_file = reports_dir / "metrics-tracking-data.json"
    with open(json_file, "w") as f:
        json.dump({"time_series": time_series, "trends": trends, "timestamp": timestamp}, f, indent=2)
    
    print(f"[{timestamp}] Metrics tracking dashboard generated")
    return time_series

def collect_session_data(logs_dir: Path) -> List[Dict[str, Any]]:
    """Collect session data from logs"""
    sessions = []
    
    if not logs_dir.exists():
        return sessions
    
    for session_dir in logs_dir.iterdir():
        if not session_dir.is_dir():
            continue
        
        status_file = session_dir / "status.json"
        if status_file.exists():
            with open(status_file, "r") as f:
                session_data = json.load(f)
                session_data["session_id"] = session_dir.name
                sessions.append(session_data)
    
    # Sort by timestamp
    sessions.sort(key=lambda x: x.get("end_time", x.get("start_time", "")), reverse=True)
    return sessions

def collect_pr_data(pr_tracking_dir: Path) -> List[Dict[str, Any]]:
    """Collect PR scoring data"""
    scores_file = pr_tracking_dir / "scores_database.json"
    
    if not scores_file.exists():
        return []
    
    with open(scores_file, "r") as f:
        scores = json.load(f)
    
    # Sort by timestamp
    scores.sort(key=lambda x: x["scored_at"], reverse=True)
    return scores

def collect_metrics_data(reports_dir: Path) -> List[Dict[str, Any]]:
    """Collect metrics data from reports"""
    metrics_files = list(reports_dir.glob("metrics-*.json"))
    
    if not metrics_files:
        return []
    
    all_metrics = []
    for metrics_file in sorted(metrics_files, reverse=True):
        with open(metrics_file, "r") as f:
            metrics = json.load(f)
            metrics["source_file"] = metrics_file.name
            all_metrics.append(metrics)
    
    return all_metrics

def generate_time_series(session_data: List[Dict], pr_data: List[Dict], metrics_data: List[Dict]) -> Dict[str, Any]:
    """Generate time-series data for dashboard"""
    # Group by date
    time_series = {
        "daily": {},
        "weekly": {},
        "monthly": {}
    }
    
    # Process session data
    for session in session_data:
        end_time = session.get("end_time", session.get("start_time", ""))
        if not end_time:
            continue
        
        date = end_time.split("T")[0]
        if date not in time_series["daily"]:
            time_series["daily"][date] = {
                "sessions": 0,
                "successful": 0,
                "failed": 0,
                "findings": 0,
                "duration_total": 0
            }
        
        time_series["daily"][date]["sessions"] += 1
        if session.get("status") == "completed":
            time_series["daily"][date]["successful"] += 1
        else:
            time_series["daily"][date]["failed"] += 1
        time_series["daily"][date]["findings"] += session.get("findings_count", 0)
        time_series["daily"][date]["duration_total"] += session.get("duration_seconds", 0)
    
    # Process PR data
    for pr in pr_data:
        categorized_at = pr.get("categorized_at", "")
        if not categorized_at:
            continue
        
        date = categorized_at.split("T")[0]
        if date not in time_series["daily"]:
            time_series["daily"][date] = {
                "sessions": 0,
                "successful": 0,
                "failed": 0,
                "findings": 0,
                "duration_total": 0,
                "prs_categorized": 0,
                "correct": 0,
                "partial": 0,
                "incorrect": 0
            }
        
        if "prs_categorized" not in time_series["daily"][date]:
            time_series["daily"][date]["prs_categorized"] = 0
            time_series["daily"][date]["correct"] = 0
            time_series["daily"][date]["partial"] = 0
            time_series["daily"][date]["incorrect"] = 0
        
        time_series["daily"][date]["prs_categorized"] += 1
        category = pr.get("category", "unknown")
        if category in time_series["daily"][date]:
            time_series["daily"][date][category] += 1
    
    # Calculate averages for PRs
    for date, data in time_series["daily"].items():
        if data.get("prs_categorized", 0) > 0:
            total = data["correct"] + data["partial"] + data["incorrect"]
            # No numeric averages needed, just counts
        if data.get("sessions", 0) > 0:
            data["avg_duration"] = round(data["duration_total"] / data["sessions"] / 60, 2)  # minutes
    
    # Generate weekly aggregates
    for date, data in sorted(time_series["daily"].items()):
        # Calculate week number
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            week_key = f"{dt.year}-W{dt.isocalendar()[1]:02d}"
            
            if week_key not in time_series["weekly"]:
                time_series["weekly"][week_key] = {
                    "sessions": 0,
                    "successful": 0,
                    "failed": 0,
                    "findings": 0,
                    "prs_categorized": 0,
                    "correct": 0,
                    "partial": 0,
                    "incorrect": 0
                }
            
            time_series["weekly"][week_key]["sessions"] += data.get("sessions", 0)
            time_series["weekly"][week_key]["successful"] += data.get("successful", 0)
            time_series["weekly"][week_key]["failed"] += data.get("failed", 0)
            time_series["weekly"][week_key]["findings"] += data.get("findings", 0)
            time_series["weekly"][week_key]["prs_categorized"] += data.get("prs_categorized", 0)
            time_series["weekly"][week_key]["correct"] += data.get("correct", 0)
            time_series["weekly"][week_key]["partial"] += data.get("partial", 0)
            time_series["weekly"][week_key]["incorrect"] += data.get("incorrect", 0)
        except ValueError:
            continue
    
    # Calculate weekly totals (no averages needed, just counts)
    for week, data in time_series["weekly"].items():
        # No numeric averages needed, just aggregate counts
        pass
    
    return time_series

def calculate_overall_trends(time_series: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall trends from time-series data (category-based)"""
    daily_data = time_series.get("daily", {})
    
    if len(daily_data) < 2:
        return {"trend": "insufficient_data"}
    
    # Get last 7 days and previous 7 days
    sorted_dates = sorted(daily_data.keys())
    recent = sorted_dates[-7:] if len(sorted_dates) >= 7 else sorted_dates
    previous = sorted_dates[-14:-7] if len(sorted_dates) >= 14 else sorted_dates[:len(sorted_dates)//2]
    
    # Calculate category counts
    recent_correct = sum(daily_data[d].get("correct", 0) for d in recent)
    recent_partial = sum(daily_data[d].get("partial", 0) for d in recent)
    recent_incorrect = sum(daily_data[d].get("incorrect", 0) for d in recent)
    
    previous_correct = sum(daily_data[d].get("correct", 0) for d in previous)
    previous_partial = sum(daily_data[d].get("partial", 0) for d in previous)
    previous_incorrect = sum(daily_data[d].get("incorrect", 0) for d in previous)
    
    # Determine trends
    correct_trend = "increasing" if recent_correct > previous_correct else "decreasing" if recent_correct < previous_correct else "stable"
    partial_trend = "increasing" if recent_partial > previous_partial else "decreasing" if recent_partial < previous_partial else "stable"
    incorrect_trend = "increasing" if recent_incorrect > previous_incorrect else "decreasing" if recent_incorrect < previous_incorrect else "stable"
    
    return {
        "recent": {
            "correct": recent_correct,
            "partial": recent_partial,
            "incorrect": recent_incorrect,
            "total": recent_correct + recent_partial + recent_incorrect
        },
        "previous": {
            "correct": previous_correct,
            "partial": previous_partial,
            "incorrect": previous_incorrect,
            "total": previous_correct + previous_partial + previous_incorrect
        },
        "trends": {
            "correct_trend": correct_trend,
            "partial_trend": partial_trend,
            "incorrect_trend": incorrect_trend
        },
        "data_points": len(daily_data)
    }

def generate_dashboard_html(time_series: Dict[str, Any], trends: Dict[str, Any], timestamp: str) -> str:
    """Generate HTML dashboard for metrics tracking"""
    daily_data = time_series.get("daily", {})
    weekly_data = time_series.get("weekly", {})
    
    # Get last 30 days for display
    sorted_dates = sorted(daily_data.keys())[-30:]
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Metrics Tracking Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
        .trend-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{ background: #f9f9f9; padding: 20px; border-radius: 8px; }}
        .card-title {{ font-weight: bold; margin-bottom: 10px; color: #333; }}
        .card-value {{ font-size: 1.5em; font-weight: bold; color: #2196F3; }}
        .card-trend {{ font-size: 0.9em; margin-top: 5px; }}
        .trend-up {{ color: #4CAF50; }}
        .trend-down {{ color: #f44336; }}
        .trend-stable {{ color: #9E9E9E; }}
        .chart-section {{ margin-bottom: 30px; }}
        .chart-container {{ background: #f9f9f9; padding: 20px; border-radius: 8px; }}
        .data-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        .data-table th, .data-table td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        .data-table th {{ background: #2196F3; color: white; }}
        .metric-good {{ color: #4CAF50; font-weight: bold; }}
        .metric-warning {{ color: #FF9800; font-weight: bold; }}
        .metric-bad {{ color: #f44336; font-weight: bold; }}
        .category-correct {{ color: #4CAF50; font-weight: bold; }}
        .category-partial {{ color: #FF9800; font-weight: bold; }}
        .category-incorrect {{ color: #f44336; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Metrics Tracking Dashboard</h1>
            <div>
                <strong>Last Updated:</strong> {timestamp}
            </div>
        </div>
        
        <h2>Recent Trends (Last 7 Days vs Previous 7 Days)</h2>
        <div class="trend-cards">
            {generate_trend_card("Success Rate", trends.get('recent', {}).get('success_rate', 0), trends.get('trends', {}).get('success_rate', 'stable'))}
            {generate_trend_card("Findings per Day", trends.get('recent', {}).get('findings_per_day', 0), trends.get('trends', {}).get('findings_per_day', 'stable'))}
            {generate_trend_card("Bug Detection Score", trends.get('recent', {}).get('avg_bug_detection', 0), trends.get('trends', {}).get('avg_bug_detection', 'stable'))}
            {generate_trend_card("Fix Quality Score", trends.get('recent', {}).get('avg_fix_quality', 0), trends.get('trends', {}).get('avg_fix_quality', 'stable'))}
            {generate_trend_card("Overall PR Score", trends.get('recent', {}).get('avg_overall_score', 0), trends.get('trends', {}).get('avg_overall_score', 'stable'))}
        </div>
        
        <div class="chart-section">
            <h2>Daily Metrics (Last 30 Days)</h2>
            <div class="chart-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Sessions</th>
                            <th>Success Rate</th>
                            <th>Findings</th>
                            <th>PRs Scored</th>
                            <th>Bug Detection</th>
                            <th>Fix Quality</th>
                            <th>Overall Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        {generate_daily_table_rows(sorted_dates, daily_data)}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="chart-section">
            <h2>Weekly Aggregates</h2>
            <div class="chart-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Week</th>
                            <th>Sessions</th>
                            <th>Success Rate</th>
                            <th>Total Findings</th>
                            <th>PRs Scored</th>
                            <th>Avg Bug Detection</th>
                            <th>Avg Fix Quality</th>
                            <th>Avg Overall Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        {generate_weekly_table_rows(weekly_data)}
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

def generate_trend_card(title: str, value: float, trend: str) -> str:
    """Generate a trend card HTML"""
    trend_class = f"trend-{trend}"
    trend_symbol = "↑" if trend == "increasing" else "↓" if trend == "decreasing" else "→"
    
    return f"""
        <div class="card">
            <div class="card-title">{title}</div>
            <div class="card-value">{value:.2f}</div>
            <div class="card-trend {trend_class}">
                {trend_symbol} {trend.upper()}
            </div>
        </div>
    """

def generate_daily_table_rows(dates: List[str], daily_data: Dict[str, Any]) -> str:
    """Generate table rows for daily data"""
    if not dates:
        return "<tr><td colspan='8'>No data available</td></tr>"
    
    rows = []
    for date in reversed(dates):
        data = daily_data.get(date, {})
        sessions = data.get("sessions", 0)
        success_rate = round((data.get("successful", 0) / sessions * 100), 2) if sessions > 0 else 0
        
        rows.append(f"""
            <tr>
                <td>{date}</td>
                <td>{sessions}</td>
                <td class="{get_metric_class(success_rate, is_percentage=True)}">{success_rate}%</td>
                <td>{data.get('findings', 0)}</td>
                <td>{data.get('prs_categorized', 0)}</td>
                <td class="category-correct">{data.get('correct', 0)}</td>
                <td class="category-partial">{data.get('partial', 0)}</td>
                <td class="category-incorrect">{data.get('incorrect', 0)}</td>
            </tr>
        """)
    
    return "\n".join(rows)

def generate_weekly_table_rows(weekly_data: Dict[str, Any]) -> str:
    """Generate table rows for weekly data"""
    if not weekly_data:
        return "<tr><td colspan='8'>No data available</td></tr>"
    
    rows = []
    for week in sorted(weekly_data.keys(), reverse=True):
        data = weekly_data[week]
        sessions = data.get("sessions", 0)
        success_rate = round((data.get("successful", 0) / sessions * 100), 2) if sessions > 0 else 0
        
        rows.append(f"""
            <tr>
                <td>{week}</td>
                <td>{sessions}</td>
                <td class="{get_metric_class(success_rate, is_percentage=True)}">{success_rate}%</td>
                <td>{data.get('findings', 0)}</td>
                <td>{data.get('prs_categorized', 0)}</td>
                <td class="category-correct">{data.get('correct', 0)}</td>
                <td class="category-partial">{data.get('partial', 0)}</td>
                <td class="category-incorrect">{data.get('incorrect', 0)}</td>
            </tr>
        """)
    
    return "\n".join(rows)

def get_metric_class(value: float, is_percentage: bool = False) -> str:
    """Get CSS class based on metric value (0-10 scale, or percentage)"""
    if is_percentage:
        if value >= 80:
            return "metric-good"
        elif value >= 60:
            return "metric-warning"
        else:
            return "metric-bad"
    else:
        if value >= 8.0:
            return "metric-good"
        elif value >= 6.0:
            return "metric-warning"
        else:
            return "metric-bad"

if __name__ == "__main__":
    generate_metrics_tracking_dashboard()