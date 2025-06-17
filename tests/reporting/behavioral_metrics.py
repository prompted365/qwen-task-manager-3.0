"""
Behavioral Metrics Collection and Analysis for Qwen Task Manager 3.0

This module provides comprehensive tracking and analysis of behavioral testing outcomes,
focusing on therapeutic effectiveness and user psychological impact.
"""

import asyncio
import json
import sqlite3
import statistics
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import argparse

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


@dataclass
class BehavioralTestResult:
    """Represents the outcome of a behavioral test."""
    test_name: str
    timestamp: datetime
    empathy_score: float
    stress_reduction: float
    confidence_boost: float
    cognitive_load_impact: float
    trust_building: float
    therapeutic_effectiveness: float
    user_persona: str
    scenario_complexity: str
    duration_ms: int
    ai_response_quality: float
    
    @property
    def overall_score(self) -> float:
        """Calculate weighted overall behavioral effectiveness score."""
        weights = {
            'empathy_score': 0.25,
            'stress_reduction': 0.20,
            'confidence_boost': 0.20,
            'trust_building': 0.15,
            'therapeutic_effectiveness': 0.20
        }
        
        return (
            self.empathy_score * weights['empathy_score'] +
            abs(self.stress_reduction) * weights['stress_reduction'] +  # Stress reduction is negative, so abs
            self.confidence_boost * weights['confidence_boost'] +
            self.trust_building * weights['trust_building'] +
            self.therapeutic_effectiveness * weights['therapeutic_effectiveness']
        )


class BehavioralMetricsCollector:
    """Collects, stores, and analyzes behavioral testing metrics."""
    
    def __init__(self, db_path: str = "tests/data/behavioral_metrics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database for metrics storage."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS behavioral_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_name TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    empathy_score REAL NOT NULL,
                    stress_reduction REAL NOT NULL,
                    confidence_boost REAL NOT NULL,
                    cognitive_load_impact REAL NOT NULL,
                    trust_building REAL NOT NULL,
                    therapeutic_effectiveness REAL NOT NULL,
                    user_persona TEXT NOT NULL,
                    scenario_complexity TEXT NOT NULL,
                    duration_ms INTEGER NOT NULL,
                    ai_response_quality REAL NOT NULL,
                    overall_score REAL NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON behavioral_results(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_test_name 
                ON behavioral_results(test_name)
            """)
    
    def record_test_result(self, result: BehavioralTestResult):
        """Record a behavioral test result."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO behavioral_results 
                (test_name, timestamp, empathy_score, stress_reduction, 
                 confidence_boost, cognitive_load_impact, trust_building,
                 therapeutic_effectiveness, user_persona, scenario_complexity,
                 duration_ms, ai_response_quality, overall_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.test_name,
                result.timestamp.isoformat(),
                result.empathy_score,
                result.stress_reduction,
                result.confidence_boost,
                result.cognitive_load_impact,
                result.trust_building,
                result.therapeutic_effectiveness,
                result.user_persona,
                result.scenario_complexity,
                result.duration_ms,
                result.ai_response_quality,
                result.overall_score
            ))
    
    def get_recent_results(self, days: int = 7) -> List[BehavioralTestResult]:
        """Get behavioral test results from the last N days."""
        since = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM behavioral_results 
                WHERE timestamp >= ? 
                ORDER BY timestamp DESC
            """, (since.isoformat(),))
            
            results = []
            for row in cursor.fetchall():
                result = BehavioralTestResult(
                    test_name=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    empathy_score=row[3],
                    stress_reduction=row[4],
                    confidence_boost=row[5],
                    cognitive_load_impact=row[6],
                    trust_building=row[7],
                    therapeutic_effectiveness=row[8],
                    user_persona=row[9],
                    scenario_complexity=row[10],
                    duration_ms=row[11],
                    ai_response_quality=row[12]
                )
                results.append(result)
            
            return results
    
    def generate_summary_stats(self, days: int = 7) -> Dict[str, Any]:
        """Generate summary statistics for behavioral metrics."""
        results = self.get_recent_results(days)
        
        if not results:
            return {"error": "No results found for the specified period"}
        
        # Extract key metrics
        empathy_scores = [r.empathy_score for r in results]
        stress_reductions = [r.stress_reduction for r in results]
        confidence_boosts = [r.confidence_boost for r in results]
        overall_scores = [r.overall_score for r in results]
        
        return {
            "period": f"Last {days} days",
            "total_tests": len(results),
            "empathy": {
                "average": statistics.mean(empathy_scores),
                "min": min(empathy_scores),
                "max": max(empathy_scores),
                "std_dev": statistics.stdev(empathy_scores) if len(empathy_scores) > 1 else 0
            },
            "stress_reduction": {
                "average": statistics.mean(stress_reductions),
                "median": statistics.median(stress_reductions),
                "effective_tests": len([s for s in stress_reductions if s < -0.5])
            },
            "confidence_boost": {
                "average": statistics.mean(confidence_boosts),
                "positive_impact_rate": len([c for c in confidence_boosts if c > 0.5]) / len(confidence_boosts)
            },
            "overall_effectiveness": {
                "average": statistics.mean(overall_scores),
                "above_threshold": len([s for s in overall_scores if s >= 7.0]) / len(overall_scores),
                "trend": self._calculate_trend(overall_scores)
            },
            "persona_breakdown": self._analyze_by_persona(results),
            "complexity_analysis": self._analyze_by_complexity(results)
        }
    
    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate trend direction for scores."""
        if len(scores) < 5:
            return "insufficient_data"
        
        # Simple linear trend analysis
        x = list(range(len(scores)))
        slope = np.polyfit(x, scores, 1)[0]
        
        if slope > 0.1:
            return "improving"
        elif slope < -0.1:
            return "declining"
        else:
            return "stable"
    
    def _analyze_by_persona(self, results: List[BehavioralTestResult]) -> Dict[str, Dict]:
        """Analyze results by user persona."""
        persona_groups = {}
        
        for result in results:
            if result.user_persona not in persona_groups:
                persona_groups[result.user_persona] = []
            persona_groups[result.user_persona].append(result)
        
        analysis = {}
        for persona, persona_results in persona_groups.items():
            overall_scores = [r.overall_score for r in persona_results]
            empathy_scores = [r.empathy_score for r in persona_results]
            
            analysis[persona] = {
                "count": len(persona_results),
                "avg_overall_score": statistics.mean(overall_scores),
                "avg_empathy": statistics.mean(empathy_scores),
                "effectiveness_rate": len([s for s in overall_scores if s >= 7.0]) / len(overall_scores)
            }
        
        return analysis
    
    def _analyze_by_complexity(self, results: List[BehavioralTestResult]) -> Dict[str, Dict]:
        """Analyze results by scenario complexity."""
        complexity_groups = {}
        
        for result in results:
            if result.scenario_complexity not in complexity_groups:
                complexity_groups[result.scenario_complexity] = []
            complexity_groups[result.scenario_complexity].append(result)
        
        analysis = {}
        for complexity, complexity_results in complexity_groups.items():
            overall_scores = [r.overall_score for r in complexity_results]
            
            analysis[complexity] = {
                "count": len(complexity_results),
                "avg_score": statistics.mean(overall_scores),
                "success_rate": len([s for s in overall_scores if s >= 7.0]) / len(overall_scores)
            }
        
        return analysis
    
    def generate_behavioral_report(self, days: int = 7, output_format: str = "text") -> str:
        """Generate a comprehensive behavioral report."""
        stats = self.generate_summary_stats(days)
        
        if "error" in stats:
            return f"Unable to generate report: {stats['error']}"
        
        if output_format == "text":
            return self._format_text_report(stats)
        elif output_format == "json":
            return json.dumps(stats, indent=2)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _format_text_report(self, stats: Dict[str, Any]) -> str:
        """Format statistics as a readable text report."""
        report = []
        report.append(f"📊 Behavioral Metrics Report - {stats['period']}")
        report.append("━" * 50)
        report.append("")
        
        # Overall summary
        report.append(f"🧪 Total Tests: {stats['total_tests']}")
        report.append(f"📈 Overall Effectiveness: {stats['overall_effectiveness']['average']:.1f}/10")
        report.append(f"✅ Success Rate: {stats['overall_effectiveness']['above_threshold']:.1%}")
        report.append(f"📊 Trend: {stats['overall_effectiveness']['trend'].replace('_', ' ').title()}")
        report.append("")
        
        # Key metrics
        report.append("🎯 Key Metrics:")
        report.append(f"  • Empathy Score: {stats['empathy']['average']:.1f}/10 (±{stats['empathy']['std_dev']:.1f})")
        report.append(f"  • Stress Reduction: {stats['stress_reduction']['average']:.1f} points")
        report.append(f"  • Confidence Boost: {stats['confidence_boost']['average']:.1f} points")
        report.append(f"  • Positive Impact Rate: {stats['confidence_boost']['positive_impact_rate']:.1%}")
        report.append("")
        
        # Persona analysis
        report.append("👥 Performance by User Persona:")
        for persona, data in stats['persona_breakdown'].items():
            report.append(f"  • {persona.replace('_', ' ').title()}:")
            report.append(f"    - Tests: {data['count']}")
            report.append(f"    - Effectiveness: {data['avg_overall_score']:.1f}/10")
            report.append(f"    - Success Rate: {data['effectiveness_rate']:.1%}")
        
        report.append("")
        
        # Complexity analysis
        report.append("🔄 Performance by Complexity:")
        for complexity, data in stats['complexity_analysis'].items():
            report.append(f"  • {complexity.replace('_', ' ').title()}:")
            report.append(f"    - Average Score: {data['avg_score']:.1f}/10")
            report.append(f"    - Success Rate: {data['success_rate']:.1%}")
        
        return "\n".join(report)
    
    def export_metrics_csv(self, days: int = 30, filename: str = None) -> str:
        """Export metrics to CSV for external analysis."""
        results = self.get_recent_results(days)
        
        if not results:
            return "No data to export"
        
        # Convert to DataFrame
        data = [asdict(result) for result in results]
        df = pd.DataFrame(data)
        
        # Format timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"behavioral_metrics_{timestamp}.csv"
        
        output_path = Path("tests/reports") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(output_path, index=False)
        return str(output_path)


def main():
    """CLI interface for behavioral metrics analysis."""
    parser = argparse.ArgumentParser(description="Behavioral Metrics Analysis")
    parser.add_argument("--days", type=int, default=7, help="Number of days to analyze")
    parser.add_argument("--yesterday-summary", action="store_true", help="Show yesterday's summary")
    parser.add_argument("--weekly-report", action="store_true", help="Generate weekly report")
    parser.add_argument("--trend-analysis", action="store_true", help="Show trend analysis")
    parser.add_argument("--export-csv", action="store_true", help="Export metrics to CSV")
    parser.add_argument("--team-dashboard", action="store_true", help="Generate team dashboard")
    
    args = parser.parse_args()
    
    collector = BehavioralMetricsCollector()
    
    if args.yesterday_summary:
        print(collector.generate_behavioral_report(days=1))
    elif args.weekly_report:
        print(collector.generate_behavioral_report(days=7))
    elif args.trend_analysis:
        stats = collector.generate_summary_stats(days=args.days)
        trend = stats.get('overall_effectiveness', {}).get('trend', 'unknown')
        print(f"📈 Trend Analysis ({args.days} days): {trend.replace('_', ' ').title()}")
    elif args.export_csv:
        filename = collector.export_metrics_csv(days=args.days)
        print(f"📊 Metrics exported to: {filename}")
    elif args.team_dashboard:
        print(collector.generate_behavioral_report(days=7))
        print("\n" + "="*50)
        print("🎯 Weekly Focus Areas:")
        stats = collector.generate_summary_stats(7)
        
        # Identify areas needing attention
        if stats['empathy']['average'] < 8.0:
            print("  • Improve AI empathy responses")
        if stats['stress_reduction']['average'] > -1.0:
            print("  • Enhance stress reduction effectiveness")
        if stats['overall_effectiveness']['above_threshold'] < 0.9:
            print("  • Focus on overall therapeutic effectiveness")
    else:
        print(collector.generate_behavioral_report(days=args.days))


if __name__ == "__main__":
    main()