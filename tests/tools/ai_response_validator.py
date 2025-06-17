"""
AI Response Validator for Qwen Task Manager 3.0

CLI tool for validating AI responses against therapeutic standards and empathy requirements.
Ensures AI interactions maintain high therapeutic effectiveness and emotional support quality.
"""

import argparse
import asyncio
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import statistics


class AIResponseValidator:
    """Validates AI responses for therapeutic effectiveness and empathy."""
    
    def __init__(self):
        self.empathy_keywords = {
            "validation": ["understand", "hear you", "makes sense", "valid", "natural", "normal"],
            "support": ["support", "help", "here for you", "together", "not alone"],
            "encouragement": ["you can", "you've got", "proud", "progress", "small steps"],
            "compassion": ["difficult", "challenging", "hard", "tough", "struggle"],
            "hope": ["better", "improve", "possible", "hope", "future", "tomorrow"]
        }
        
        self.anti_empathy_patterns = [
            r"\bjust\s+(do|try|stop|start)",  # "just do it" type responses
            r"you\s+should\s+have",  # "you should have" - blame patterns
            r"it'?s\s+not\s+that\s+hard",  # minimizing difficulty
            r"everyone\s+(else\s+)?can",  # comparison to others
            r"simply|easily|obviously",  # minimizing complexity
            r"you'?re\s+being\s+too",  # judgment patterns
        ]
        
        self.therapeutic_requirements = {
            "empathy_score": 7.5,
            "validation_present": True,
            "non_judgmental": True,
            "action_oriented": True,
            "hope_instilling": True,
            "user_agency_preserved": True
        }
    
    def validate_response(self, 
                         ai_response: str, 
                         user_context: Dict[str, Any],
                         expected_therapeutic_focus: Optional[str] = None) -> Dict[str, Any]:
        """Validate an AI response for therapeutic effectiveness."""
        
        validation_result = {
            "timestamp": datetime.now().isoformat(),
            "ai_response": ai_response,
            "user_context": user_context,
            "empathy_score": self._calculate_empathy_score(ai_response),
            "validation_analysis": self._analyze_validation(ai_response),
            "judgment_analysis": self._analyze_judgment(ai_response),
            "action_orientation": self._analyze_action_orientation(ai_response),
            "hope_analysis": self._analyze_hope_instillation(ai_response),
            "agency_preservation": self._analyze_user_agency(ai_response),
            "therapeutic_effectiveness": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        # Calculate overall therapeutic effectiveness
        validation_result["therapeutic_effectiveness"] = self._calculate_therapeutic_effectiveness(validation_result)
        
        # Identify issues and generate recommendations
        validation_result["issues"] = self._identify_issues(validation_result)
        validation_result["recommendations"] = self._generate_recommendations(validation_result)
        
        return validation_result
    
    def _calculate_empathy_score(self, response: str) -> float:
        """Calculate empathy score based on language patterns."""
        response_lower = response.lower()
        total_score = 0.0
        max_possible = 10.0
        
        # Check for empathy keywords (positive scoring)
        empathy_points = 0
        for category, keywords in self.empathy_keywords.items():
            category_found = any(keyword in response_lower for keyword in keywords)
            if category_found:
                empathy_points += 2.0
        
        # Check for anti-empathy patterns (negative scoring)
        anti_empathy_penalty = 0
        for pattern in self.anti_empathy_patterns:
            if re.search(pattern, response_lower):
                anti_empathy_penalty += 1.5
        
        # Base score calculation
        base_score = min(8.0, empathy_points)  # Max 8 from keywords
        penalty_reduction = min(4.0, anti_empathy_penalty)  # Max 4 point penalty
        
        # Bonus for particularly empathetic language
        if "i understand" in response_lower or "that sounds" in response_lower:
            base_score += 1.0
        
        final_score = max(0.0, min(10.0, base_score - penalty_reduction))
        return round(final_score, 1)
    
    def _analyze_validation(self, response: str) -> Dict[str, Any]:
        """Analyze if the response validates the user's experience."""
        response_lower = response.lower()
        
        validation_indicators = [
            "understand", "makes sense", "hear you", "valid", 
            "natural", "normal", "that sounds", "i can see"
        ]
        
        invalidation_patterns = [
            "you shouldn't feel", "don't worry about", "it's not that bad",
            "you're overreacting", "just get over", "move on"
        ]
        
        validation_present = any(indicator in response_lower for indicator in validation_indicators)
        invalidation_present = any(pattern in response_lower for pattern in invalidation_patterns)
        
        return {
            "validation_present": validation_present,
            "invalidation_detected": invalidation_present,
            "score": 8.0 if validation_present and not invalidation_present else 
                    5.0 if validation_present else
                    2.0 if invalidation_present else 6.0
        }
    
    def _analyze_judgment(self, response: str) -> Dict[str, Any]:
        """Analyze if the response contains judgmental language."""
        response_lower = response.lower()
        
        judgment_patterns = [
            r"you should have", r"you need to", r"you must",
            r"wrong", r"bad choice", r"mistake", r"stupid",
            r"lazy", r"procrastinating", r"excuses"
        ]
        
        judgment_detected = any(re.search(pattern, response_lower) for pattern in judgment_patterns)
        
        # Check for constructive alternatives
        constructive_patterns = [
            "might consider", "could try", "what if", "perhaps", 
            "one option", "you might find", "when you're ready"
        ]
        
        constructive_present = any(pattern in response_lower for pattern in constructive_patterns)
        
        return {
            "judgment_detected": judgment_detected,
            "constructive_alternatives": constructive_present,
            "non_judgmental": not judgment_detected,
            "score": 9.0 if not judgment_detected and constructive_present else
                    7.0 if not judgment_detected else
                    3.0 if judgment_detected and constructive_present else 1.0
        }
    
    def _analyze_action_orientation(self, response: str) -> Dict[str, Any]:
        """Analyze if the response encourages helpful action."""
        response_lower = response.lower()
        
        action_indicators = [
            "try", "start", "begin", "take", "consider", 
            "explore", "practice", "experiment", "step"
        ]
        
        overwhelming_action = [
            "do all", "everything", "immediately", "right now",
            "must do", "have to do"
        ]
        
        action_present = any(indicator in response_lower for indicator in action_indicators)
        overwhelming_detected = any(pattern in response_lower for pattern in overwhelming_action)
        
        return {
            "encourages_action": action_present,
            "overwhelming_suggestions": overwhelming_detected,
            "balanced_approach": action_present and not overwhelming_detected,
            "score": 8.0 if action_present and not overwhelming_detected else
                    5.0 if action_present else
                    3.0 if overwhelming_detected else 6.0
        }
    
    def _analyze_hope_instillation(self, response: str) -> Dict[str, Any]:
        """Analyze if the response instills hope and optimism."""
        response_lower = response.lower()
        
        hope_indicators = [
            "better", "improve", "progress", "possible", "can",
            "will", "hope", "future", "tomorrow", "next", "grow"
        ]
        
        despair_indicators = [
            "never", "impossible", "hopeless", "can't", "won't work",
            "no point", "useless", "failed"
        ]
        
        hope_present = any(indicator in response_lower for indicator in hope_indicators)
        despair_present = any(indicator in response_lower for indicator in despair_indicators)
        
        return {
            "hope_present": hope_present,
            "despair_language": despair_present,
            "optimistic_tone": hope_present and not despair_present,
            "score": 9.0 if hope_present and not despair_present else
                    6.0 if hope_present else
                    2.0 if despair_present else 5.0
        }
    
    def _analyze_user_agency(self, response: str) -> Dict[str, Any]:
        """Analyze if the response preserves user autonomy and choice."""
        response_lower = response.lower()
        
        agency_preserving = [
            "you decide", "your choice", "up to you", "you know",
            "you might", "if you want", "when you're ready",
            "what feels right", "your pace"
        ]
        
        agency_undermining = [
            "you must", "you have to", "you need to", "you should",
            "i'm telling you", "do exactly", "follow these steps"
        ]
        
        preserves_agency = any(phrase in response_lower for phrase in agency_preserving)
        undermines_agency = any(phrase in response_lower for phrase in agency_undermining)
        
        return {
            "preserves_agency": preserves_agency,
            "undermines_agency": undermines_agency,
            "respects_autonomy": preserves_agency and not undermines_agency,
            "score": 9.0 if preserves_agency and not undermines_agency else
                    7.0 if preserves_agency else
                    4.0 if undermines_agency else 6.0
        }
    
    def _calculate_therapeutic_effectiveness(self, validation_result: Dict[str, Any]) -> float:
        """Calculate overall therapeutic effectiveness score."""
        weights = {
            "empathy_score": 0.25,
            "validation_analysis": 0.20,
            "judgment_analysis": 0.15,
            "action_orientation": 0.15,
            "hope_analysis": 0.15,
            "agency_preservation": 0.10
        }
        
        total_score = (
            validation_result["empathy_score"] * weights["empathy_score"] +
            validation_result["validation_analysis"]["score"] * weights["validation_analysis"] +
            validation_result["judgment_analysis"]["score"] * weights["judgment_analysis"] +
            validation_result["action_orientation"]["score"] * weights["action_orientation"] +
            validation_result["hope_analysis"]["score"] * weights["hope_analysis"] +
            validation_result["agency_preservation"]["score"] * weights["agency_preservation"]
        )
        
        return round(total_score, 1)
    
    def _identify_issues(self, validation_result: Dict[str, Any]) -> List[str]:
        """Identify specific issues with the AI response."""
        issues = []
        
        if validation_result["empathy_score"] < 7.0:
            issues.append(f"Low empathy score: {validation_result['empathy_score']}/10")
        
        if not validation_result["validation_analysis"]["validation_present"]:
            issues.append("No validation of user experience detected")
        
        if validation_result["validation_analysis"]["invalidation_detected"]:
            issues.append("Invalidating language detected")
        
        if validation_result["judgment_analysis"]["judgment_detected"]:
            issues.append("Judgmental language detected")
        
        if validation_result["action_orientation"]["overwhelming_suggestions"]:
            issues.append("Overwhelming action suggestions detected")
        
        if validation_result["hope_analysis"]["despair_language"]:
            issues.append("Despair-inducing language detected")
        
        if validation_result["agency_preservation"]["undermines_agency"]:
            issues.append("User agency undermining language detected")
        
        if validation_result["therapeutic_effectiveness"] < 7.0:
            issues.append(f"Overall therapeutic effectiveness below threshold: {validation_result['therapeutic_effectiveness']}/10")
        
        return issues
    
    def _generate_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations for improvement."""
        recommendations = []
        
        if validation_result["empathy_score"] < 8.0:
            recommendations.append("Add more validating language like 'I understand' or 'That makes sense'")
            recommendations.append("Use emotional reflection: 'That sounds really challenging'")
        
        if not validation_result["validation_analysis"]["validation_present"]:
            recommendations.append("Start with validation: 'I can see why you'd feel that way'")
        
        if validation_result["judgment_analysis"]["judgment_detected"]:
            recommendations.append("Replace 'should' with 'might consider' or 'could try'")
            recommendations.append("Use non-judgmental language focused on options rather than obligations")
        
        if not validation_result["action_orientation"]["encourages_action"]:
            recommendations.append("Include gentle action suggestions: 'You might try...'")
        
        if not validation_result["hope_analysis"]["hope_present"]:
            recommendations.append("Add hopeful language about progress and possibility")
        
        if not validation_result["agency_preservation"]["preserves_agency"]:
            recommendations.append("Preserve user choice: 'You decide what feels right'")
            recommendations.append("Use phrases like 'when you're ready' or 'if you want'")
        
        if not recommendations:
            recommendations.append("Response meets therapeutic standards - maintain this quality")
        
        return recommendations
    
    def batch_validate_responses(self, 
                               responses_file: str,
                               output_file: Optional[str] = None) -> Dict[str, Any]:
        """Validate multiple AI responses from a file."""
        try:
            with open(responses_file, 'r') as f:
                responses_data = json.load(f)
        except Exception as e:
            return {"error": f"Could not read responses file: {e}"}
        
        results = {
            "validation_timestamp": datetime.now().isoformat(),
            "total_responses": len(responses_data),
            "individual_results": [],
            "summary_statistics": {},
            "overall_assessment": {}
        }
        
        # Validate each response
        for i, response_data in enumerate(responses_data):
            try:
                validation = self.validate_response(
                    ai_response=response_data.get("ai_response", ""),
                    user_context=response_data.get("user_context", {}),
                    expected_therapeutic_focus=response_data.get("therapeutic_focus")
                )
                
                validation["response_id"] = i
                results["individual_results"].append(validation)
                
            except Exception as e:
                results["individual_results"].append({
                    "response_id": i,
                    "error": f"Validation failed: {e}"
                })
        
        # Calculate summary statistics
        valid_results = [r for r in results["individual_results"] if "error" not in r]
        if valid_results:
            empathy_scores = [r["empathy_score"] for r in valid_results]
            therapeutic_scores = [r["therapeutic_effectiveness"] for r in valid_results]
            
            results["summary_statistics"] = {
                "average_empathy_score": round(statistics.mean(empathy_scores), 1),
                "average_therapeutic_effectiveness": round(statistics.mean(therapeutic_scores), 1),
                "empathy_score_range": [min(empathy_scores), max(empathy_scores)],
                "responses_above_threshold": len([s for s in therapeutic_scores if s >= 7.0]),
                "success_rate": len([s for s in therapeutic_scores if s >= 7.0]) / len(therapeutic_scores)
            }
            
            # Overall assessment
            avg_therapeutic = results["summary_statistics"]["average_therapeutic_effectiveness"]
            success_rate = results["summary_statistics"]["success_rate"]
            
            if avg_therapeutic >= 8.5 and success_rate >= 0.95:
                overall_status = "excellent"
            elif avg_therapeutic >= 7.5 and success_rate >= 0.90:
                overall_status = "good"
            elif avg_therapeutic >= 6.5 and success_rate >= 0.80:
                overall_status = "needs_improvement"
            else:
                overall_status = "critical"
            
            results["overall_assessment"] = {
                "status": overall_status,
                "recommendation": self._get_overall_recommendation(overall_status, results)
            }
        
        # Save results if requested
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
        
        return results
    
    def _get_overall_recommendation(self, status: str, results: Dict[str, Any]) -> str:
        """Get overall recommendation based on batch validation results."""
        recommendations = {
            "excellent": "Maintain current high standards. Consider sharing best practices with team.",
            "good": "Generally good therapeutic effectiveness. Focus on consistency improvements.",
            "needs_improvement": "Therapeutic effectiveness below standards. Review empathy patterns and validation techniques.",
            "critical": "Immediate attention required. Comprehensive review of AI response patterns needed."
        }
        
        return recommendations.get(status, "Unknown status - manual review required.")
    
    def quick_check(self, response: str) -> bool:
        """Quick pass/fail check for therapeutic standards."""
        validation = self.validate_response(response, {})
        return (
            validation["therapeutic_effectiveness"] >= 7.0 and
            validation["empathy_score"] >= 7.5 and
            len(validation["issues"]) == 0
        )


def main():
    """CLI interface for AI response validation."""
    parser = argparse.ArgumentParser(description="Validate AI responses for therapeutic effectiveness")
    parser.add_argument("--response", help="Single AI response to validate")
    parser.add_argument("--user-context", help="JSON string of user context")
    parser.add_argument("--batch-file", help="JSON file with multiple responses to validate")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--quick-check", action="store_true", help="Quick pass/fail validation")
    parser.add_argument("--baseline-check", action="store_true", help="Check baseline empathy requirements")
    parser.add_argument("--detailed", action="store_true", help="Show detailed analysis")
    parser.add_argument("--overnight-analysis", action="store_true", help="Analyze overnight test results")
    parser.add_argument("--production-check", action="store_true", help="Production readiness check")
    
    args = parser.parse_args()
    
    validator = AIResponseValidator()
    
    if args.quick_check and args.response:
        passed = validator.quick_check(args.response)
        print("✅ PASS" if passed else "❌ FAIL")
        return 0 if passed else 1
    
    elif args.baseline_check:
        # Test basic empathy requirements
        test_responses = [
            "I understand this is really challenging for you.",
            "You just need to stop procrastinating and get it done.",
            "That sounds overwhelming. What feels most manageable right now?",
            "Everyone struggles with this, you're not special."
        ]
        
        print("🧪 Baseline Empathy Check:")
        for i, response in enumerate(test_responses, 1):
            passed = validator.quick_check(response)
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{i}. {status}: {response[:50]}...")
    
    elif args.batch_file:
        results = validator.batch_validate_responses(args.batch_file, args.output)
        
        if "error" in results:
            print(f"❌ Error: {results['error']}")
            return 1
        
        # Print summary
        stats = results["summary_statistics"]
        assessment = results["overall_assessment"]
        
        print(f"📊 Batch Validation Results ({results['total_responses']} responses)")
        print(f"Average Empathy Score: {stats['average_empathy_score']}/10")
        print(f"Average Therapeutic Effectiveness: {stats['average_therapeutic_effectiveness']}/10")
        print(f"Success Rate: {stats['success_rate']:.1%}")
        print(f"Overall Status: {assessment['status'].upper()}")
        print(f"Recommendation: {assessment['recommendation']}")
        
        if args.detailed:
            print("\n🔍 Detailed Issues:")
            for result in results["individual_results"]:
                if result.get("issues"):
                    print(f"Response {result['response_id']}: {', '.join(result['issues'])}")
    
    elif args.response:
        user_context = {}
        if args.user_context:
            try:
                user_context = json.loads(args.user_context)
            except json.JSONDecodeError:
                print("❌ Invalid JSON in user-context")
                return 1
        
        validation = validator.validate_response(args.response, user_context)
        
        print(f"🧠 AI Response Validation Results")
        print(f"Empathy Score: {validation['empathy_score']}/10")
        print(f"Therapeutic Effectiveness: {validation['therapeutic_effectiveness']}/10")
        
        if validation["issues"]:
            print("\n⚠️ Issues Identified:")
            for issue in validation["issues"]:
                print(f"  • {issue}")
        
        if validation["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in validation["recommendations"]:
                print(f"  • {rec}")
        
        if args.detailed:
            print(f"\n🔍 Detailed Analysis:")
            print(f"Validation Present: {validation['validation_analysis']['validation_present']}")
            print(f"Non-Judgmental: {validation['judgment_analysis']['non_judgmental']}")
            print(f"Encourages Action: {validation['action_orientation']['encourages_action']}")
            print(f"Instills Hope: {validation['hope_analysis']['hope_present']}")
            print(f"Preserves Agency: {validation['agency_preservation']['preserves_agency']}")
        
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(validation, f, indent=2)
            print(f"\n📄 Detailed results saved to: {output_path}")
    
    else:
        print("🤖 AI Response Validator")
        print("Examples:")
        print("  Validate single response:")
        print("    python ai_response_validator.py --response 'I understand this is difficult'")
        print("  Quick check:")
        print("    python ai_response_validator.py --response 'Just do it' --quick-check")
        print("  Batch validation:")
        print("    python ai_response_validator.py --batch-file responses.json --detailed")


if __name__ == "__main__":
    exit(main())