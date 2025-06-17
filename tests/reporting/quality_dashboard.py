"""
Quality Dashboard for Qwen Task Manager 3.0

Real-time dashboard for monitoring therapeutic effectiveness and behavioral testing metrics.
Provides visual insights into the ongoing impact of the task management system.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

from behavioral_metrics import BehavioralMetricsCollector, BehavioralTestResult


class QualityDashboard:
    """Real-time dashboard for monitoring behavioral and technical quality metrics."""
    
    def __init__(self, metrics_collector: Optional[BehavioralMetricsCollector] = None):
        self.metrics_collector = metrics_collector or BehavioralMetricsCollector()
        self.dashboard_data = {}
        self.alerts = []
    
    def generate_dashboard_data(self, days: int = 7) -> Dict[str, Any]:
        """Generate comprehensive dashboard data."""
        
        # Get recent behavioral metrics
        behavioral_stats = self.metrics_collector.generate_summary_stats(days)
        recent_results = self.metrics_collector.get_recent_results(days)
        
        # Calculate real-time metrics
        current_time = datetime.now()
        
        dashboard_data = {
            "timestamp": current_time.isoformat(),
            "period": f"Last {days} days",
            "behavioral_overview": self._create_behavioral_overview(behavioral_stats),
            "quality_indicators": self._create_quality_indicators(behavioral_stats),
            "trend_analysis": self._create_trend_analysis(recent_results),
            "alerts": self._generate_alerts(behavioral_stats),
            "recommendations": self._generate_quick_recommendations(behavioral_stats),
            "health_score": self._calculate_health_score(behavioral_stats)
        }
        
        return dashboard_data
    
    def _create_behavioral_overview(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Create behavioral overview section."""
        if "error" in stats:
            return {"status": "error", "message": stats["error"]}
        
        return {
            "total_tests": stats.get("total_tests", 0),
            "therapeutic_effectiveness": {
                "score": stats.get("overall_effectiveness", {}).get("average", 0),
                "trend": stats.get("overall_effectiveness", {}).get("trend", "unknown"),
                "success_rate": stats.get("overall_effectiveness", {}).get("above_threshold", 0)
            },
            "empathy_metrics": {
                "average": stats.get("empathy", {}).get("average", 0),
                "consistency": stats.get("empathy", {}).get("std_dev", 0),
                "range": {
                    "min": stats.get("empathy", {}).get("min", 0),
                    "max": stats.get("empathy", {}).get("max", 0)
                }
            },
            "stress_impact": {
                "average_reduction": stats.get("stress_reduction", {}).get("average", 0),
                "effective_tests": stats.get("stress_reduction", {}).get("effective_tests", 0)
            },
            "confidence_building": {
                "average_boost": stats.get("confidence_boost", {}).get("average", 0),
                "positive_rate": stats.get("confidence_boost", {}).get("positive_impact_rate", 0)
            }
        }
    
    def _create_quality_indicators(self, stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create quality indicator widgets."""
        if "error" in stats:
            return [{"name": "Error", "status": "critical", "message": stats["error"]}]
        
        indicators = []
        
        # Therapeutic Effectiveness Indicator
        effectiveness = stats.get("overall_effectiveness", {}).get("average", 0)
        if effectiveness >= 8.5:
            status = "excellent"
            color = "green"
        elif effectiveness >= 7.5:
            status = "good"
            color = "blue"
        elif effectiveness >= 6.5:
            status = "warning"
            color = "yellow"
        else:
            status = "critical"
            color = "red"
        
        indicators.append({
            "name": "Therapeutic Effectiveness",
            "value": f"{effectiveness:.1f}/10",
            "status": status,
            "color": color,
            "trend": stats.get("overall_effectiveness", {}).get("trend", "stable")
        })
        
        # Empathy Indicator
        empathy = stats.get("empathy", {}).get("average", 0)
        if empathy >= 9.0:
            empathy_status = "excellent"
            empathy_color = "green"
        elif empathy >= 8.0:
            empathy_status = "good"
            empathy_color = "blue"
        elif empathy >= 7.0:
            empathy_status = "warning"
            empathy_color = "yellow"
        else:
            empathy_status = "critical"
            empathy_color = "red"
        
        indicators.append({
            "name": "AI Empathy Score",
            "value": f"{empathy:.1f}/10",
            "status": empathy_status,
            "color": empathy_color,
            "consistency": f"±{stats.get('empathy', {}).get('std_dev', 0):.1f}"
        })
        
        # Stress Reduction Indicator
        stress_reduction = stats.get("stress_reduction", {}).get("average", 0)
        if stress_reduction <= -2.0:
            stress_status = "excellent"
            stress_color = "green"
        elif stress_reduction <= -1.5:
            stress_status = "good"
            stress_color = "blue"
        elif stress_reduction <= -1.0:
            stress_status = "warning"
            stress_color = "yellow"
        else:
            stress_status = "critical"
            stress_color = "red"
        
        indicators.append({
            "name": "Stress Reduction",
            "value": f"{stress_reduction:.1f} pts",
            "status": stress_status,
            "color": stress_color,
            "effective_tests": stats.get("stress_reduction", {}).get("effective_tests", 0)
        })
        
        # Success Rate Indicator
        success_rate = stats.get("overall_effectiveness", {}).get("above_threshold", 0)
        if success_rate >= 0.95:
            success_status = "excellent"
            success_color = "green"
        elif success_rate >= 0.90:
            success_status = "good"
            success_color = "blue"
        elif success_rate >= 0.80:
            success_status = "warning"
            success_color = "yellow"
        else:
            success_status = "critical"
            success_color = "red"
        
        indicators.append({
            "name": "Success Rate",
            "value": f"{success_rate:.1%}",
            "status": success_status,
            "color": success_color,
            "target": "90%+"
        })
        
        return indicators
    
    def _create_trend_analysis(self, recent_results: List[BehavioralTestResult]) -> Dict[str, Any]:
        """Analyze trends in recent test results."""
        if len(recent_results) < 5:
            return {
                "status": "insufficient_data",
                "message": "Need at least 5 recent results for trend analysis"
            }
        
        # Sort by timestamp
        sorted_results = sorted(recent_results, key=lambda x: x.timestamp)
        
        # Calculate daily averages
        daily_scores = {}
        for result in sorted_results:
            date_key = result.timestamp.strftime("%Y-%m-%d")
            if date_key not in daily_scores:
                daily_scores[date_key] = []
            daily_scores[date_key].append(result.overall_score)
        
        # Average scores by day
        daily_averages = {
            date: sum(scores) / len(scores) 
            for date, scores in daily_scores.items()
        }
        
        # Calculate trend
        dates = sorted(daily_averages.keys())
        scores = [daily_averages[date] for date in dates]
        
        if len(scores) >= 3:
            # Simple trend calculation
            recent_avg = sum(scores[-3:]) / 3
            earlier_avg = sum(scores[:-3]) / len(scores[:-3]) if len(scores) > 3 else scores[0]
            
            trend_direction = "improving" if recent_avg > earlier_avg + 0.2 else \
                            "declining" if recent_avg < earlier_avg - 0.2 else "stable"
        else:
            trend_direction = "stable"
        
        return {
            "trend_direction": trend_direction,
            "daily_averages": daily_averages,
            "recent_average": sum(scores[-3:]) / 3 if len(scores) >= 3 else scores[-1] if scores else 0,
            "data_points": len(sorted_results),
            "date_range": {
                "start": sorted_results[0].timestamp.strftime("%Y-%m-%d"),
                "end": sorted_results[-1].timestamp.strftime("%Y-%m-%d")
            }
        }
    
    def _generate_alerts(self, stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alerts for critical issues."""
        alerts = []
        
        if "error" in stats:
            alerts.append({
                "level": "critical",
                "title": "Data Collection Error",
                "message": stats["error"],
                "action": "Check behavioral metrics collection system"
            })
            return alerts
        
        # Check therapeutic effectiveness
        effectiveness = stats.get("overall_effectiveness", {}).get("average", 0)
        if effectiveness < 6.5:
            alerts.append({
                "level": "critical",
                "title": "Low Therapeutic Effectiveness",
                "message": f"Average effectiveness is {effectiveness:.1f}/10, below critical threshold",
                "action": "Immediate review of AI responses and user interactions required"
            })
        elif effectiveness < 7.5:
            alerts.append({
                "level": "warning",
                "title": "Therapeutic Effectiveness Below Target",
                "message": f"Average effectiveness is {effectiveness:.1f}/10, below 7.5 target",
                "action": "Review and optimize therapeutic interaction patterns"
            })
        
        # Check empathy scores
        empathy = stats.get("empathy", {}).get("average", 0)
        if empathy < 7.0:
            alerts.append({
                "level": "critical",
                "title": "Low AI Empathy",
                "message": f"AI empathy score is {empathy:.1f}/10, below acceptable threshold",
                "action": "Review AI response templates and empathy training"
            })
        elif empathy < 8.0:
            alerts.append({
                "level": "warning",
                "title": "Empathy Score Needs Improvement",
                "message": f"AI empathy score is {empathy:.1f}/10, below 8.0 target",
                "action": "Consider empathy enhancement in AI responses"
            })
        
        # Check stress reduction
        stress_reduction = stats.get("stress_reduction", {}).get("average", 0)
        if stress_reduction > -0.5:
            alerts.append({
                "level": "critical",
                "title": "Insufficient Stress Reduction",
                "message": f"Average stress reduction is only {stress_reduction:.1f} points",
                "action": "Analyze and improve stress-reducing interaction patterns"
            })
        elif stress_reduction > -1.0:
            alerts.append({
                "level": "warning",
                "title": "Stress Reduction Below Target",
                "message": f"Stress reduction is {stress_reduction:.1f} points, target is -1.0+",
                "action": "Optimize calming and supportive interactions"
            })
        
        # Check trend
        trend = stats.get("overall_effectiveness", {}).get("trend", "stable")
        if trend == "declining":
            alerts.append({
                "level": "warning",
                "title": "Declining Effectiveness Trend",
                "message": "Therapeutic effectiveness is trending downward",
                "action": "Investigate recent changes and implement corrective measures"
            })
        
        return alerts
    
    def _generate_quick_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Generate quick actionable recommendations."""
        if "error" in stats:
            return ["Fix data collection system to enable proper monitoring"]
        
        recommendations = []
        
        # Based on empathy scores
        empathy = stats.get("empathy", {}).get("average", 0)
        if empathy < 8.0:
            recommendations.append("Enhance AI empathy through response template improvements")
        
        # Based on stress reduction
        stress_reduction = stats.get("stress_reduction", {}).get("average", 0)
        if stress_reduction > -1.5:
            recommendations.append("Implement additional stress-reduction interaction patterns")
        
        # Based on success rate
        success_rate = stats.get("overall_effectiveness", {}).get("above_threshold", 0)
        if success_rate < 0.9:
            recommendations.append("Focus on improving consistency across all user scenarios")
        
        # Based on persona performance
        persona_breakdown = stats.get("persona_breakdown", {})
        for persona, data in persona_breakdown.items():
            if data.get("effectiveness_rate", 0) < 0.8:
                recommendations.append(f"Improve {persona.replace('_', ' ')} user experience")
        
        # Default recommendation if all is well
        if not recommendations:
            recommendations.append("Maintain current high standards and explore advanced scenarios")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _calculate_health_score(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall system health score."""
        if "error" in stats:
            return {
                "score": 0,
                "status": "error",
                "components": {}
            }
        
        # Component scores (0-100)
        components = {}
        
        # Therapeutic effectiveness (40% weight)
        effectiveness = stats.get("overall_effectiveness", {}).get("average", 0)
        components["therapeutic_effectiveness"] = min(100, (effectiveness / 10) * 100)
        
        # Empathy (25% weight)
        empathy = stats.get("empathy", {}).get("average", 0)
        components["empathy"] = min(100, (empathy / 10) * 100)
        
        # Stress reduction (20% weight) - convert to positive scale
        stress_reduction = abs(stats.get("stress_reduction", {}).get("average", 0))
        components["stress_reduction"] = min(100, (stress_reduction / 3) * 100)  # Scale to -3 max
        
        # Success rate (15% weight)
        success_rate = stats.get("overall_effectiveness", {}).get("above_threshold", 0)
        components["success_rate"] = success_rate * 100
        
        # Calculate weighted overall score
        weights = {
            "therapeutic_effectiveness": 0.40,
            "empathy": 0.25,
            "stress_reduction": 0.20,
            "success_rate": 0.15
        }
        
        overall_score = sum(
            components[component] * weights[component]
            for component in components
        )
        
        # Determine status
        if overall_score >= 90:
            status = "excellent"
        elif overall_score >= 80:
            status = "good"
        elif overall_score >= 70:
            status = "warning"
        else:
            status = "critical"
        
        return {
            "score": round(overall_score, 1),
            "status": status,
            "components": components
        }
    
    def generate_dashboard_html(self, days: int = 7) -> str:
        """Generate HTML dashboard."""
        dashboard_data = self.generate_dashboard_data(days)
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Qwen Task Manager 3.0 - Quality Dashboard</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f7; }
        .dashboard { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #1d1d1f; font-size: 2.5em; margin: 0; }
        .header p { color: #86868b; font-size: 1.1em; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .metric-value { font-size: 2em; font-weight: bold; margin: 10px 0; }
        .metric-label { color: #86868b; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px; }
        .health-score { text-align: center; background: white; border-radius: 12px; padding: 30px; margin-bottom: 30px; }
        .health-circle { width: 120px; height: 120px; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; color: white; font-size: 2em; font-weight: bold; }
        .excellent { background: #34c759; }
        .good { background: #007aff; }
        .warning { background: #ff9500; }
        .critical { background: #ff3b30; }
        .alerts { background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
        .alert { padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid; }
        .alert.critical { background: #fff5f5; border-color: #ff3b30; }
        .alert.warning { background: #fffbf0; border-color: #ff9500; }
        .recommendations { background: white; border-radius: 12px; padding: 20px; }
        .recommendation { padding: 10px 0; border-bottom: 1px solid #f0f0f0; }
        .recommendation:last-child { border-bottom: none; }
        .trend-indicator { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; color: white; }
        .improving { background: #34c759; }
        .stable { background: #8e8e93; }
        .declining { background: #ff3b30; }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🧠 Quality Dashboard</h1>
            <p>Therapeutic effectiveness monitoring for Qwen Task Manager 3.0</p>
            <p><small>Generated: {timestamp} | Period: {period}</small></p>
        </div>
        
        <div class="health-score">
            <div class="health-circle {health_status}">
                {health_score}
            </div>
            <h2>Overall System Health</h2>
            <p>Therapeutic effectiveness and user experience quality</p>
        </div>
        
        <div class="metrics-grid">
            {quality_indicators}
        </div>
        
        {alerts_section}
        
        <div class="recommendations">
            <h3>💡 Quick Recommendations</h3>
            {recommendations_list}
        </div>
    </div>
</body>
</html>
        """
        
        # Format quality indicators
        indicators_html = ""
        for indicator in dashboard_data["quality_indicators"]:
            trend_html = ""
            if "trend" in indicator:
                trend_class = indicator["trend"].replace("_", "-")
                trend_html = f'<span class="trend-indicator {trend_class}">{indicator["trend"].replace("_", " ").title()}</span>'
            
            indicators_html += f"""
            <div class="metric-card">
                <div class="metric-label">{indicator["name"]}</div>
                <div class="metric-value" style="color: {indicator.get('color', '#1d1d1f')}">{indicator["value"]}</div>
                {trend_html}
            </div>
            """
        
        # Format alerts
        alerts_html = ""
        if dashboard_data["alerts"]:
            alerts_content = ""
            for alert in dashboard_data["alerts"]:
                alerts_content += f"""
                <div class="alert {alert['level']}">
                    <strong>{alert['title']}</strong><br>
                    {alert['message']}<br>
                    <em>Action: {alert['action']}</em>
                </div>
                """
            alerts_html = f"""
            <div class="alerts">
                <h3>⚠️ Alerts</h3>
                {alerts_content}
            </div>
            """
        
        # Format recommendations
        recommendations_html = ""
        for rec in dashboard_data["recommendations"]:
            recommendations_html += f'<div class="recommendation">• {rec}</div>'
        
        return html_template.format(
            timestamp=dashboard_data["timestamp"],
            period=dashboard_data["period"],
            health_score=dashboard_data["health_score"]["score"],
            health_status=dashboard_data["health_score"]["status"],
            quality_indicators=indicators_html,
            alerts_section=alerts_html,
            recommendations_list=recommendations_html
        )
    
    def start_dashboard_server(self, port: int = 8080, auto_refresh: int = 30):
        """Start a simple HTTP server for the dashboard."""
        try:
            import http.server
            import socketserver
            import webbrowser
            import tempfile
            import os
            
            # Generate dashboard HTML
            dashboard_html = self.generate_dashboard_html()
            
            # Create temporary HTML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(dashboard_html)
                temp_file = f.name
            
            # Simple HTTP server
            class DashboardHandler(http.server.SimpleHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/' or self.path == '/dashboard':
                        # Regenerate dashboard data
                        fresh_html = QualityDashboard().generate_dashboard_html()
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Cache-Control', 'no-cache')
                        self.end_headers()
                        self.wfile.write(fresh_html.encode())
                    else:
                        super().do_GET()
            
            with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
                print(f"🌐 Quality Dashboard running at http://localhost:{port}")
                print(f"🔄 Auto-refresh every {auto_refresh} seconds")
                print("Press Ctrl+C to stop")
                
                # Open browser
                webbrowser.open(f"http://localhost:{port}")
                
                httpd.serve_forever()
                
        except KeyboardInterrupt:
            print("\n📊 Dashboard stopped")
        except Exception as e:
            print(f"❌ Error starting dashboard: {e}")
        finally:
            # Clean up temp file
            if 'temp_file' in locals():
                try:
                    os.unlink(temp_file)
                except:
                    pass


def main():
    """CLI interface for quality dashboard."""
    parser = argparse.ArgumentParser(description="Quality Dashboard for Behavioral Testing")
    parser.add_argument("--port", type=int, default=8080, help="Port for dashboard server")
    parser.add_argument("--days", type=int, default=7, help="Days of data to analyze")
    parser.add_argument("--json", action="store_true", help="Output JSON data instead of HTML")
    parser.add_argument("--alerts-only", action="store_true", help="Show only alerts")
    parser.add_argument("--health-check", action="store_true", help="Show health score only")
    
    args = parser.parse_args()
    
    dashboard = QualityDashboard()
    
    if args.json:
        data = dashboard.generate_dashboard_data(args.days)
        print(json.dumps(data, indent=2))
    elif args.alerts_only:
        data = dashboard.generate_dashboard_data(args.days)
        alerts = data["alerts"]
        if alerts:
            print("⚠️ Active Alerts:")
            for alert in alerts:
                print(f"  {alert['level'].upper()}: {alert['title']}")
                print(f"    {alert['message']}")
                print(f"    Action: {alert['action']}")
                print()
        else:
            print("✅ No alerts - system is performing well")
    elif args.health_check:
        data = dashboard.generate_dashboard_data(args.days)
        health = data["health_score"]
        print(f"🏥 System Health: {health['score']}/100 ({health['status'].upper()})")
    else:
        # Start dashboard server
        dashboard.start_dashboard_server(port=args.port)


if __name__ == "__main__":
    main()