"""
Comprehensive Test Report Generator for Qwen Task Manager 3.0

Generates detailed reports combining technical testing results with behavioral insights,
providing actionable feedback for maintaining therapeutic effectiveness.
"""

import argparse
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import xml.etree.ElementTree as ET

import jinja2
from behavioral_metrics import BehavioralMetricsCollector, BehavioralTestResult


class TestReportGenerator:
    """Generates comprehensive test reports with behavioral insights."""
    
    def __init__(self, output_dir: str = "tests/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_collector = BehavioralMetricsCollector()
        self.template_env = self._setup_templates()
    
    def _setup_templates(self) -> jinja2.Environment:
        """Setup Jinja2 templates for report generation."""
        template_dir = Path(__file__).parent / "templates"
        template_dir.mkdir(exist_ok=True)
        
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def run_pytest_with_coverage(self, test_path: str = "tests/") -> Dict[str, Any]:
        """Run pytest with coverage and return results."""
        try:
            # Run tests with coverage and JSON output
            result = subprocess.run([
                "python", "-m", "pytest", test_path,
                "--tb=short", "--quiet",
                "--cov=.", "--cov-report=json",
                "--json-report", "--json-report-file=tests/reports/pytest_results.json"
            ], capture_output=True, text=True, timeout=300)
            
            # Parse JSON results if available
            json_report_path = self.output_dir / "pytest_results.json"
            if json_report_path.exists():
                with open(json_report_path) as f:
                    pytest_data = json.load(f)
            else:
                pytest_data = {"summary": {"total": 0, "passed": 0, "failed": 0}}
            
            # Parse coverage data if available
            coverage_data = self._parse_coverage_data()
            
            return {
                "pytest_results": pytest_data,
                "coverage": coverage_data,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Test execution timed out"}
        except Exception as e:
            return {"error": f"Test execution failed: {str(e)}"}
    
    def _parse_coverage_data(self) -> Dict[str, Any]:
        """Parse coverage data from coverage.json."""
        coverage_path = Path("coverage.json")
        if coverage_path.exists():
            try:
                with open(coverage_path) as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {"totals": {"percent_covered": 0}}
    
    def generate_comprehensive_report(self, 
                                    report_type: str = "daily",
                                    include_behavioral: bool = True,
                                    include_coverage: bool = True) -> str:
        """Generate a comprehensive test report."""
        
        timestamp = datetime.now()
        report_data = {
            "generated_at": timestamp.isoformat(),
            "report_type": report_type,
            "project_name": "Qwen Task Manager 3.0"
        }
        
        # Run technical tests
        if include_coverage:
            test_results = self.run_pytest_with_coverage()
            report_data["technical_results"] = test_results
        
        # Gather behavioral metrics
        if include_behavioral:
            days = {"daily": 1, "weekly": 7, "monthly": 30}.get(report_type, 7)
            behavioral_stats = self.metrics_collector.generate_summary_stats(days)
            report_data["behavioral_metrics"] = behavioral_stats
        
        # Generate insights and recommendations
        report_data["insights"] = self._generate_insights(report_data)
        report_data["recommendations"] = self._generate_recommendations(report_data)
        
        # Format report
        report_content = self._format_comprehensive_report(report_data)
        
        # Save report
        filename = f"{report_type}_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        report_path = self.output_dir / filename
        
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        return str(report_path)
    
    def _generate_insights(self, report_data: Dict[str, Any]) -> List[str]:
        """Generate actionable insights from test data."""
        insights = []
        
        # Technical insights
        if "technical_results" in report_data:
            tech_results = report_data["technical_results"]
            if "pytest_results" in tech_results:
                pytest_data = tech_results["pytest_results"]
                summary = pytest_data.get("summary", {})
                
                total_tests = summary.get("total", 0)
                passed_tests = summary.get("passed", 0)
                failed_tests = summary.get("failed", 0)
                
                if total_tests > 0:
                    pass_rate = passed_tests / total_tests
                    if pass_rate < 0.95:
                        insights.append(f"⚠️ Test pass rate is {pass_rate:.1%}, below 95% target")
                    elif pass_rate >= 0.98:
                        insights.append(f"✅ Excellent test pass rate: {pass_rate:.1%}")
                
                if failed_tests > 0:
                    insights.append(f"🔍 {failed_tests} failing tests require immediate attention")
            
            # Coverage insights
            if "coverage" in tech_results:
                coverage = tech_results["coverage"].get("totals", {}).get("percent_covered", 0)
                if coverage < 80:
                    insights.append(f"📊 Code coverage at {coverage:.1f}%, recommend increasing to 80%+")
                elif coverage >= 90:
                    insights.append(f"🎯 Excellent code coverage: {coverage:.1f}%")
        
        # Behavioral insights
        if "behavioral_metrics" in report_data:
            behavioral = report_data["behavioral_metrics"]
            
            if "overall_effectiveness" in behavioral:
                effectiveness = behavioral["overall_effectiveness"]
                avg_score = effectiveness.get("average", 0)
                success_rate = effectiveness.get("above_threshold", 0)
                trend = effectiveness.get("trend", "unknown")
                
                if avg_score < 7.0:
                    insights.append(f"🧠 Therapeutic effectiveness below target: {avg_score:.1f}/10")
                elif avg_score >= 8.5:
                    insights.append(f"🌟 Outstanding therapeutic effectiveness: {avg_score:.1f}/10")
                
                if success_rate < 0.85:
                    insights.append(f"📈 Success rate needs improvement: {success_rate:.1%}")
                
                if trend == "declining":
                    insights.append("📉 Behavioral effectiveness is declining - urgent attention needed")
                elif trend == "improving":
                    insights.append("📈 Behavioral effectiveness is improving - great work!")
            
            # Empathy insights
            if "empathy" in behavioral:
                avg_empathy = behavioral["empathy"].get("average", 0)
                if avg_empathy < 8.0:
                    insights.append(f"💝 AI empathy score needs attention: {avg_empathy:.1f}/10")
                elif avg_empathy >= 9.0:
                    insights.append(f"💖 Exceptional AI empathy: {avg_empathy:.1f}/10")
            
            # Stress reduction insights
            if "stress_reduction" in behavioral:
                avg_stress_reduction = behavioral["stress_reduction"].get("average", 0)
                if avg_stress_reduction > -1.0:
                    insights.append(f"😰 Stress reduction insufficient: {avg_stress_reduction:.1f} points")
                elif avg_stress_reduction <= -2.0:
                    insights.append(f"😌 Excellent stress reduction: {avg_stress_reduction:.1f} points")
        
        return insights
    
    def _generate_recommendations(self, report_data: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on test results."""
        recommendations = []
        
        # Technical recommendations
        if "technical_results" in report_data:
            tech_results = report_data["technical_results"]
            
            if tech_results.get("returncode", 0) != 0:
                recommendations.append("🔧 Fix failing tests before proceeding with development")
            
            coverage = tech_results.get("coverage", {}).get("totals", {}).get("percent_covered", 0)
            if coverage < 80:
                recommendations.append("📊 Add unit tests to improve code coverage")
        
        # Behavioral recommendations
        if "behavioral_metrics" in report_data:
            behavioral = report_data["behavioral_metrics"]
            
            # Check empathy scores
            if behavioral.get("empathy", {}).get("average", 0) < 8.0:
                recommendations.append("💝 Review AI response templates for empathy improvement")
                recommendations.append("🎭 Conduct empathy training session for AI prompts")
            
            # Check stress reduction
            if behavioral.get("stress_reduction", {}).get("average", 0) > -1.0:
                recommendations.append("😰 Analyze user workflows for stress-inducing patterns")
                recommendations.append("🧘 Implement additional calming interaction patterns")
            
            # Check persona-specific issues
            persona_breakdown = behavioral.get("persona_breakdown", {})
            for persona, data in persona_breakdown.items():
                if data.get("effectiveness_rate", 0) < 0.8:
                    recommendations.append(f"👤 Focus on improving {persona} user experience")
            
            # Check complexity handling
            complexity_analysis = behavioral.get("complexity_analysis", {})
            for complexity, data in complexity_analysis.items():
                if data.get("success_rate", 0) < 0.8:
                    recommendations.append(f"🔄 Improve handling of {complexity} scenarios")
        
        # General recommendations
        if not recommendations:
            recommendations.append("🎉 All metrics are performing well - maintain current practices!")
            recommendations.append("📈 Consider exploring advanced behavioral testing scenarios")
        
        return recommendations
    
    def _format_comprehensive_report(self, report_data: Dict[str, Any]) -> str:
        """Format the comprehensive report as markdown."""
        lines = []
        
        # Header
        lines.append(f"# Qwen Task Manager 3.0 - {report_data['report_type'].title()} Test Report")
        lines.append(f"*Generated: {report_data['generated_at']}*")
        lines.append("")
        
        # Executive Summary
        lines.append("## 📋 Executive Summary")
        lines.append("")
        
        if "behavioral_metrics" in report_data:
            behavioral = report_data["behavioral_metrics"]
            overall_score = behavioral.get("overall_effectiveness", {}).get("average", 0)
            success_rate = behavioral.get("overall_effectiveness", {}).get("above_threshold", 0)
            total_tests = behavioral.get("total_tests", 0)
            
            if overall_score >= 8.5:
                status_emoji = "🌟"
                status = "Excellent"
            elif overall_score >= 7.5:
                status_emoji = "✅"
                status = "Good"
            elif overall_score >= 6.5:
                status_emoji = "⚠️"
                status = "Needs Attention"
            else:
                status_emoji = "❌"
                status = "Critical"
            
            lines.append(f"{status_emoji} **Overall Status**: {status}")
            lines.append(f"📊 **Therapeutic Effectiveness**: {overall_score:.1f}/10")
            lines.append(f"🎯 **Success Rate**: {success_rate:.1%}")
            lines.append(f"🧪 **Total Behavioral Tests**: {total_tests}")
        
        if "technical_results" in report_data:
            tech_results = report_data["technical_results"]
            pytest_data = tech_results.get("pytest_results", {})
            summary = pytest_data.get("summary", {})
            
            total_tech_tests = summary.get("total", 0)
            passed_tech_tests = summary.get("passed", 0)
            coverage = tech_results.get("coverage", {}).get("totals", {}).get("percent_covered", 0)
            
            lines.append(f"🔧 **Technical Tests**: {passed_tech_tests}/{total_tech_tests} passed")
            lines.append(f"📈 **Code Coverage**: {coverage:.1f}%")
        
        lines.append("")
        
        # Key Insights
        if report_data.get("insights"):
            lines.append("## 💡 Key Insights")
            lines.append("")
            for insight in report_data["insights"]:
                lines.append(f"- {insight}")
            lines.append("")
        
        # Behavioral Metrics Detail
        if "behavioral_metrics" in report_data:
            lines.append("## 🧠 Behavioral Metrics")
            lines.append("")
            
            behavioral = report_data["behavioral_metrics"]
            
            # Core metrics
            if "empathy" in behavioral:
                empathy = behavioral["empathy"]
                lines.append(f"### 💝 Empathy Analysis")
                lines.append(f"- **Average Score**: {empathy.get('average', 0):.1f}/10")
                lines.append(f"- **Range**: {empathy.get('min', 0):.1f} - {empathy.get('max', 0):.1f}")
                lines.append(f"- **Consistency**: ±{empathy.get('std_dev', 0):.1f} standard deviation")
                lines.append("")
            
            if "stress_reduction" in behavioral:
                stress = behavioral["stress_reduction"]
                lines.append(f"### 😌 Stress Reduction Impact")
                lines.append(f"- **Average Reduction**: {stress.get('average', 0):.1f} points")
                lines.append(f"- **Median Impact**: {stress.get('median', 0):.1f} points")
                lines.append(f"- **Effective Tests**: {stress.get('effective_tests', 0)} with >0.5 point reduction")
                lines.append("")
            
            if "confidence_boost" in behavioral:
                confidence = behavioral["confidence_boost"]
                lines.append(f"### 🚀 Confidence Building")
                lines.append(f"- **Average Boost**: {confidence.get('average', 0):.1f} points")
                lines.append(f"- **Positive Impact Rate**: {confidence.get('positive_impact_rate', 0):.1%}")
                lines.append("")
        
        # Technical Results Detail
        if "technical_results" in report_data:
            lines.append("## 🔧 Technical Testing Results")
            lines.append("")
            
            tech_results = report_data["technical_results"]
            pytest_data = tech_results.get("pytest_results", {})
            
            if "summary" in pytest_data:
                summary = pytest_data["summary"]
                lines.append(f"- **Total Tests**: {summary.get('total', 0)}")
                lines.append(f"- **Passed**: {summary.get('passed', 0)}")
                lines.append(f"- **Failed**: {summary.get('failed', 0)}")
                lines.append(f"- **Skipped**: {summary.get('skipped', 0)}")
                
                if summary.get('failed', 0) > 0:
                    lines.append("")
                    lines.append("### ❌ Failed Tests")
                    # Would need to parse failed test details from pytest output
                    lines.append("*See pytest output for detailed failure information*")
            
            lines.append("")
        
        # Recommendations
        if report_data.get("recommendations"):
            lines.append("## 🎯 Recommendations")
            lines.append("")
            for i, rec in enumerate(report_data["recommendations"], 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        # Next Steps
        lines.append("## 🚀 Next Steps")
        lines.append("")
        lines.append("1. Address any critical issues identified above")
        lines.append("2. Review failed tests and behavioral regressions")
        lines.append("3. Implement recommended improvements")
        lines.append("4. Monitor trends in next reporting period")
        lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("*This report combines technical testing metrics with behavioral impact analysis*")
        lines.append("*to ensure Qwen Task Manager maintains both functionality and therapeutic effectiveness.*")
        
        return "\n".join(lines)
    
    def generate_impact_stories(self, days: int = 7) -> str:
        """Generate user impact stories from behavioral test data."""
        behavioral_results = self.metrics_collector.get_recent_results(days)
        
        if not behavioral_results:
            return "No behavioral test data available for impact stories."
        
        # Group by persona for storytelling
        persona_groups = {}
        for result in behavioral_results:
            if result.user_persona not in persona_groups:
                persona_groups[result.user_persona] = []
            persona_groups[result.user_persona].append(result)
        
        stories = []
        stories.append(f"# User Impact Stories - Last {days} Days")
        stories.append("")
        
        for persona, results in persona_groups.items():
            avg_empathy = sum(r.empathy_score for r in results) / len(results)
            avg_stress_reduction = sum(r.stress_reduction for r in results) / len(results)
            avg_confidence = sum(r.confidence_boost for r in results) / len(results)
            
            persona_name = persona.replace('_', ' ').title()
            
            stories.append(f"## 👤 {persona_name}")
            stories.append("")
            
            # Create a narrative based on the metrics
            if avg_empathy >= 8.5 and avg_stress_reduction <= -1.5:
                stories.append(f"**Excellent Support Experience**: Users in this category consistently")
                stories.append(f"report feeling understood (empathy: {avg_empathy:.1f}/10) and significantly")
                stories.append(f"less stressed (reduction: {avg_stress_reduction:.1f} points). The AI")
                stories.append(f"interactions are creating a truly supportive environment.")
            elif avg_empathy >= 7.0:
                stories.append(f"**Good Progress**: These users feel reasonably supported")
                stories.append(f"(empathy: {avg_empathy:.1f}/10) with moderate stress relief")
                stories.append(f"({avg_stress_reduction:.1f} points). There's room for improvement")
                stories.append(f"in making interactions feel more personalized.")
            else:
                stories.append(f"**Needs Attention**: Users report lower satisfaction")
                stories.append(f"(empathy: {avg_empathy:.1f}/10) and insufficient stress relief")
                stories.append(f"({avg_stress_reduction:.1f} points). This persona requires")
                stories.append(f"immediate attention to improve their experience.")
            
            stories.append("")
            stories.append(f"- **Confidence Building**: {avg_confidence:.1f} point average increase")
            stories.append(f"- **Test Scenarios**: {len(results)} scenarios evaluated")
            stories.append("")
        
        return "\n".join(stories)


def main():
    """CLI interface for test report generation."""
    parser = argparse.ArgumentParser(description="Generate comprehensive test reports")
    parser.add_argument("--today", action="store_true", help="Generate daily report")
    parser.add_argument("--weekly", action="store_true", help="Generate weekly report")
    parser.add_argument("--monthly", action="store_true", help="Generate monthly report")
    parser.add_argument("--behavioral-focus", action="store_true", help="Focus on behavioral metrics")
    parser.add_argument("--pr-report", action="store_true", help="Generate PR-specific report")
    parser.add_argument("--production-report", action="store_true", help="Generate production report")
    parser.add_argument("--impact-stories", action="store_true", help="Generate user impact stories")
    parser.add_argument("--output", default="tests/reports", help="Output directory")
    
    args = parser.parse_args()
    
    generator = TestReportGenerator(args.output)
    
    if args.impact_stories:
        days = 7 if args.today else 30 if args.monthly else 7
        stories = generator.generate_impact_stories(days)
        print(stories)
    elif args.today:
        report_path = generator.generate_comprehensive_report("daily")
        print(f"📊 Daily report generated: {report_path}")
    elif args.weekly:
        report_path = generator.generate_comprehensive_report("weekly")
        print(f"📊 Weekly report generated: {report_path}")
    elif args.monthly:
        report_path = generator.generate_comprehensive_report("monthly")
        print(f"📊 Monthly report generated: {report_path}")
    elif args.pr_report:
        report_path = generator.generate_comprehensive_report("pr", include_coverage=True)
        print(f"📊 PR report generated: {report_path}")
    elif args.production_report:
        report_path = generator.generate_comprehensive_report("production", include_coverage=False)
        print(f"📊 Production report generated: {report_path}")
    else:
        report_path = generator.generate_comprehensive_report("weekly")
        print(f"📊 Weekly report generated: {report_path}")


if __name__ == "__main__":
    main()