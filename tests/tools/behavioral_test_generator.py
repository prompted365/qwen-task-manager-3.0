"""
Behavioral Test Generator for Qwen Task Manager 3.0

Automatically generates behavioral tests from user scenarios, personas, and therapeutic requirements.
Helps developers create comprehensive behavioral validation without deep psychology knowledge.
"""

import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import textwrap

# Import personas and scenarios from fixtures
import sys
sys.path.append(str(Path(__file__).parent.parent))

from fixtures.behavioral_scenarios.real_world_scenarios import (
    overwhelmed_user_scenario, 
    deadline_pressure_scenario,
    adhd_task_management_scenario
)
from fixtures.behavioral_scenarios.edge_cases import (
    complete_overwhelm_scenario,
    perfectionist_paralysis_scenario,
    chronic_illness_scenario
)


class BehavioralTestGenerator:
    """Generates behavioral tests from user scenarios and therapeutic requirements."""
    
    def __init__(self):
        self.personas = {
            "overwhelmed_professional": {
                "description": "High-achieving professional with too many responsibilities",
                "stress_triggers": ["deadlines", "task_volume", "interruptions"],
                "therapeutic_needs": ["organization", "prioritization", "stress_reduction"],
                "empathy_requirements": "high_validation"
            },
            "student_with_adhd": {
                "description": "Student managing ADHD symptoms while pursuing education",
                "stress_triggers": ["focus_issues", "time_management", "executive_function"],
                "therapeutic_needs": ["structure", "gentle_reminders", "self_compassion"],
                "empathy_requirements": "neurodivergent_awareness"
            },
            "caregiver_burnout": {
                "description": "Person caring for family while managing own responsibilities",
                "stress_triggers": ["competing_priorities", "guilt", "exhaustion"],
                "therapeutic_needs": ["self_care", "boundary_setting", "emotional_support"],
                "empathy_requirements": "compassionate_understanding"
            },
            "perfectionist_user": {
                "description": "Person whose perfectionism creates paralysis and anxiety",
                "stress_triggers": ["imperfection", "criticism", "incompletion"],
                "therapeutic_needs": ["permission_to_be_imperfect", "progress_celebration", "anxiety_management"],
                "empathy_requirements": "gentle_encouragement"
            },
            "chronic_illness_user": {
                "description": "Managing tasks while dealing with chronic health conditions",
                "stress_triggers": ["energy_fluctuations", "unpredictability", "limitations"],
                "therapeutic_needs": ["flexibility", "energy_management", "self_acceptance"],
                "empathy_requirements": "health_aware_support"
            }
        }
        
        self.test_templates = {
            "stress_reduction": {
                "pattern": "test_reduces_{emotion}_for_{persona}",
                "focus": "emotional_impact",
                "assertions": ["stress_level_decreases", "emotional_state_improves", "coping_increases"]
            },
            "empathy_validation": {
                "pattern": "test_ai_shows_empathy_to_{persona}_in_{situation}",
                "focus": "ai_response_quality",
                "assertions": ["empathy_score_high", "validation_present", "judgment_absent"]
            },
            "cognitive_load": {
                "pattern": "test_manages_cognitive_load_for_{persona}",
                "focus": "mental_burden",
                "assertions": ["decisions_simplified", "options_manageable", "clarity_improved"]
            },
            "confidence_building": {
                "pattern": "test_builds_confidence_for_{persona}",
                "focus": "self_efficacy",
                "assertions": ["confidence_increases", "accomplishment_celebrated", "progress_acknowledged"]
            },
            "behavioral_activation": {
                "pattern": "test_encourages_action_for_{persona}",
                "focus": "motivation_and_action",
                "assertions": ["motivation_increases", "action_taken", "momentum_built"]
            }
        }
    
    def generate_test_from_scenario(self, 
                                  persona: str, 
                                  scenario_type: str, 
                                  complexity: str = "medium") -> str:
        """Generate a complete behavioral test from a scenario."""
        
        if persona not in self.personas:
            raise ValueError(f"Unknown persona: {persona}")
        
        persona_data = self.personas[persona]
        test_name = f"test_{scenario_type}_{persona}_{complexity}"
        
        # Generate test method
        test_code = self._generate_test_method(
            test_name=test_name,
            persona=persona,
            persona_data=persona_data,
            scenario_type=scenario_type,
            complexity=complexity
        )
        
        return test_code
    
    def _generate_test_method(self, 
                            test_name: str,
                            persona: str, 
                            persona_data: Dict,
                            scenario_type: str,
                            complexity: str) -> str:
        """Generate the actual test method code."""
        
        # Create docstring
        docstring = f'"""Test {scenario_type} scenario for {persona_data["description"]}."""'
        
        # Select appropriate scenario function
        scenario_func = self._get_scenario_function(scenario_type, persona)
        
        # Generate test body
        test_body = self._generate_test_body(persona, persona_data, scenario_type, complexity)
        
        # Combine into full test method
        test_code = f'''
    @pytest.mark.behavioral_impact("high")
    @pytest.mark.persona("{persona}")
    @pytest.mark.scenario_complexity("{complexity}")
    async def {test_name}(self, app_context, {persona}_fixture):
        {docstring}
        
        # Arrange: Set up scenario
        scenario = {scenario_func}
        user_state = {persona}_fixture.with_emotional_state(
            stress_level={self._get_initial_stress_level(persona, scenario_type)},
            confidence_level={self._get_initial_confidence_level(persona, scenario_type)},
            energy_level={self._get_initial_energy_level(persona, scenario_type)}
        )
        
        {test_body}
'''
        
        return textwrap.dedent(test_code)
    
    def _generate_test_body(self, 
                          persona: str, 
                          persona_data: Dict, 
                          scenario_type: str, 
                          complexity: str) -> str:
        """Generate the test body with appropriate assertions."""
        
        therapeutic_needs = persona_data["therapeutic_needs"]
        stress_triggers = persona_data["stress_triggers"]
        
        test_body_parts = [
            "# Act: Execute the scenario",
            "result = await app_context.run_behavioral_scenario(",
            "    scenario=scenario,",
            "    user_state=user_state,",
            f"    complexity='{complexity}'",
            ")",
            "",
            "# Assert: Therapeutic outcomes"
        ]
        
        # Add specific assertions based on therapeutic needs
        if "stress_reduction" in therapeutic_needs:
            test_body_parts.extend([
                "assert result.stress_level_change < -1.0, 'Should significantly reduce stress'",
                "assert result.emotional_state_improvement > 0.5, 'Should improve emotional state'"
            ])
        
        if "organization" in therapeutic_needs:
            test_body_parts.extend([
                "assert result.organization_score > 7.0, 'Should improve organization'",
                "assert result.clarity_improvement > 1.0, 'Should increase clarity'"
            ])
        
        if "self_compassion" in therapeutic_needs:
            test_body_parts.extend([
                "assert result.self_compassion_score > 7.5, 'Should foster self-compassion'",
                "assert result.self_criticism_reduction < -0.5, 'Should reduce self-criticism'"
            ])
        
        # Add empathy-specific assertions
        empathy_req = persona_data["empathy_requirements"]
        if empathy_req == "high_validation":
            test_body_parts.append("assert result.validation_score > 8.0, 'Should provide strong validation'")
        elif empathy_req == "neurodivergent_awareness":
            test_body_parts.append("assert result.neurodivergent_sensitivity > 8.5, 'Should show neurodivergent awareness'")
        elif empathy_req == "compassionate_understanding":
            test_body_parts.append("assert result.compassion_score > 8.0, 'Should show deep compassion'")
        
        # Add general therapeutic assertions
        test_body_parts.extend([
            "",
            "# Behavioral effectiveness assertions",
            "assert result.overall_therapeutic_score >= 7.0, 'Should meet therapeutic effectiveness threshold'",
            "assert result.user_agency_preserved, 'Should preserve user autonomy'",
            "assert result.hope_instilled > 0.5, 'Should instill hope for improvement'"
        ])
        
        return "\n        ".join(test_body_parts)
    
    def _get_scenario_function(self, scenario_type: str, persona: str) -> str:
        """Get the appropriate scenario function call."""
        scenario_map = {
            "overwhelm": "overwhelmed_user_scenario()",
            "deadline_pressure": "deadline_pressure_scenario()",
            "adhd_management": "adhd_task_management_scenario()",
            "perfectionism": "perfectionist_paralysis_scenario()",
            "chronic_illness": "chronic_illness_scenario()",
            "complete_overwhelm": "complete_overwhelm_scenario()"
        }
        
        return scenario_map.get(scenario_type, "overwhelmed_user_scenario()")
    
    def _get_initial_stress_level(self, persona: str, scenario_type: str) -> int:
        """Get realistic initial stress level for persona/scenario combination."""
        base_stress = {
            "overwhelmed_professional": 7,
            "student_with_adhd": 6,
            "caregiver_burnout": 8,
            "perfectionist_user": 7,
            "chronic_illness_user": 6
        }
        
        scenario_modifier = {
            "overwhelm": 2,
            "deadline_pressure": 3,
            "perfectionism": 2,
            "chronic_illness": 1,
            "complete_overwhelm": 3
        }
        
        return min(10, base_stress.get(persona, 6) + scenario_modifier.get(scenario_type, 1))
    
    def _get_initial_confidence_level(self, persona: str, scenario_type: str) -> int:
        """Get realistic initial confidence level."""
        base_confidence = {
            "overwhelmed_professional": 5,
            "student_with_adhd": 4,
            "caregiver_burnout": 4,
            "perfectionist_user": 3,
            "chronic_illness_user": 5
        }
        
        return base_confidence.get(persona, 5)
    
    def _get_initial_energy_level(self, persona: str, scenario_type: str) -> int:
        """Get realistic initial energy level."""
        base_energy = {
            "overwhelmed_professional": 4,
            "student_with_adhd": 6,
            "caregiver_burnout": 3,
            "perfectionist_user": 5,
            "chronic_illness_user": 4
        }
        
        return base_energy.get(persona, 5)
    
    def generate_test_suite(self, 
                          personas: List[str], 
                          scenario_types: List[str],
                          output_file: Optional[str] = None) -> str:
        """Generate a complete test suite for multiple personas and scenarios."""
        
        test_suite_parts = [
            '"""',
            'Generated Behavioral Test Suite for Qwen Task Manager 3.0',
            '',
            f'Generated on: {datetime.now().isoformat()}',
            f'Personas: {", ".join(personas)}',
            f'Scenarios: {", ".join(scenario_types)}',
            '"""',
            '',
            'import pytest',
            'from tests.fixtures.behavioral_scenarios.real_world_scenarios import *',
            'from tests.fixtures.behavioral_scenarios.edge_cases import *',
            'from tests.utils.test_helpers import BehavioralAssertion',
            '',
            '',
            'class TestGeneratedBehavioralScenarios:',
            '    """Generated behavioral tests for therapeutic effectiveness validation."""'
        ]
        
        # Generate tests for all combinations
        for persona in personas:
            for scenario_type in scenario_types:
                for complexity in ["simple", "medium", "complex"]:
                    try:
                        test_code = self.generate_test_from_scenario(
                            persona=persona,
                            scenario_type=scenario_type,
                            complexity=complexity
                        )
                        test_suite_parts.append(test_code)
                    except Exception as e:
                        print(f"Warning: Could not generate test for {persona}/{scenario_type}: {e}")
        
        full_suite = '\n'.join(test_suite_parts)
        
        # Save to file if requested
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(full_suite)
            print(f"✅ Test suite generated: {output_path}")
        
        return full_suite
    
    def suggest_improvements(self, days: int = 7) -> List[str]:
        """Suggest behavioral test improvements based on recent results."""
        suggestions = []
        
        # Analyze recent behavioral metrics to suggest improvements
        try:
            from tests.reporting.behavioral_metrics import BehavioralMetricsCollector
            metrics = BehavioralMetricsCollector()
            stats = metrics.generate_summary_stats(days)
            
            if "error" not in stats:
                # Suggest based on low scores
                if stats.get("empathy", {}).get("average", 0) < 8.0:
                    suggestions.append("Add more empathy-focused test scenarios")
                    suggestions.append("Create tests for emotional validation responses")
                
                if stats.get("stress_reduction", {}).get("average", 0) > -1.0:
                    suggestions.append("Develop stress-reduction focused test cases")
                    suggestions.append("Test calming interaction patterns")
                
                # Suggest based on persona performance
                persona_breakdown = stats.get("persona_breakdown", {})
                for persona, data in persona_breakdown.items():
                    if data.get("effectiveness_rate", 0) < 0.8:
                        suggestions.append(f"Create more diverse scenarios for {persona}")
                        suggestions.append(f"Test edge cases specific to {persona} needs")
        
        except ImportError:
            suggestions.append("Install behavioral metrics module for data-driven suggestions")
        except Exception as e:
            suggestions.append(f"Unable to analyze metrics: {e}")
        
        # General suggestions
        if not suggestions:
            suggestions = [
                "Explore advanced therapeutic scenarios",
                "Add tests for seasonal affective patterns",
                "Create tests for crisis intervention scenarios",
                "Develop long-term therapeutic relationship tests"
            ]
        
        return suggestions
    
    def validate_scenarios(self) -> Dict[str, Any]:
        """Validate that all scenario functions are accessible and working."""
        validation_results = {
            "accessible_scenarios": [],
            "missing_scenarios": [],
            "errors": []
        }
        
        scenario_functions = [
            "overwhelmed_user_scenario",
            "deadline_pressure_scenario", 
            "adhd_task_management_scenario",
            "complete_overwhelm_scenario",
            "perfectionist_paralysis_scenario",
            "chronic_illness_scenario"
        ]
        
        for func_name in scenario_functions:
            try:
                # Try to import and call the function
                if func_name == "overwhelmed_user_scenario":
                    scenario = overwhelmed_user_scenario()
                elif func_name == "deadline_pressure_scenario":
                    scenario = deadline_pressure_scenario()
                elif func_name == "adhd_task_management_scenario":
                    scenario = adhd_task_management_scenario()
                elif func_name == "complete_overwhelm_scenario":
                    scenario = complete_overwhelm_scenario()
                elif func_name == "perfectionist_paralysis_scenario":
                    scenario = perfectionist_paralysis_scenario()
                elif func_name == "chronic_illness_scenario":
                    scenario = chronic_illness_scenario()
                
                validation_results["accessible_scenarios"].append(func_name)
                
            except Exception as e:
                validation_results["errors"].append(f"{func_name}: {str(e)}")
                validation_results["missing_scenarios"].append(func_name)
        
        return validation_results
    
    def generate_tips(self, level: str = "beginner") -> List[str]:
        """Generate behavioral testing tips for developers."""
        
        beginner_tips = [
            "Start with simple persona scenarios before complex edge cases",
            "Always test both positive and negative emotional outcomes",
            "Use realistic stress levels - not everyone starts at maximum stress",
            "Remember: empathy score should typically be 7.5+ for therapeutic effectiveness",
            "Test the user's emotional journey, not just task completion",
            "Consider cognitive load - don't overwhelm users with choices",
            "Validate that AI responses feel human and understanding"
        ]
        
        intermediate_tips = [
            "Test edge cases where therapeutic approaches might conflict",
            "Validate consistency across different personas in similar situations",
            "Check that stress reduction is meaningful (typically -1.0+ point reduction)",
            "Test scenarios where users might resist helpful suggestions",
            "Ensure confidence building is gradual and sustainable",
            "Test therapeutic effectiveness across different complexity levels",
            "Validate that error scenarios still maintain empathy and support"
        ]
        
        advanced_tips = [
            "Create longitudinal tests that track therapeutic relationship development",
            "Test cultural sensitivity in therapeutic approaches",
            "Validate effectiveness across neurodivergent user patterns",
            "Test crisis intervention scenarios with appropriate escalation",
            "Create tests for therapeutic boundary maintenance",
            "Validate that AI maintains consistency in therapeutic approach",
            "Test scenarios where therapeutic and productivity goals conflict"
        ]
        
        tip_sets = {
            "beginner": beginner_tips,
            "intermediate": intermediate_tips,
            "advanced": advanced_tips
        }
        
        return tip_sets.get(level, beginner_tips)


def main():
    """CLI interface for behavioral test generation."""
    parser = argparse.ArgumentParser(description="Generate behavioral tests for therapeutic effectiveness")
    parser.add_argument("--feature", help="Feature to generate tests for")
    parser.add_argument("--user-personas", help="Comma-separated list of user personas")
    parser.add_argument("--scenarios", help="Comma-separated list of scenario types")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--complexity", choices=["simple", "medium", "complex"], default="medium")
    parser.add_argument("--validate-scenarios", action="store_true", help="Validate scenario functions")
    parser.add_argument("--suggest-improvements", action="store_true", help="Suggest test improvements")
    parser.add_argument("--generate-tips", choices=["beginner", "intermediate", "advanced"], help="Generate testing tips")
    parser.add_argument("--team-workshop", action="store_true", help="Generate team workshop scenarios")
    parser.add_argument("--difficulty", choices=["beginner", "intermediate", "advanced"], default="intermediate")
    
    args = parser.parse_args()
    
    generator = BehavioralTestGenerator()
    
    if args.validate_scenarios:
        results = generator.validate_scenarios()
        print("📋 Scenario Validation Results:")
        print(f"✅ Accessible: {len(results['accessible_scenarios'])}")
        print(f"❌ Missing: {len(results['missing_scenarios'])}")
        if results['errors']:
            print("🔍 Errors:")
            for error in results['errors']:
                print(f"  • {error}")
    
    elif args.suggest_improvements:
        suggestions = generator.suggest_improvements()
        print("💡 Behavioral Testing Improvement Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
    
    elif args.generate_tips:
        tips = generator.generate_tips(args.generate_tips)
        print(f"🎯 {args.generate_tips.title()} Behavioral Testing Tips:")
        for i, tip in enumerate(tips, 1):
            print(f"{i}. {tip}")
    
    elif args.team_workshop:
        print(f"🎓 Team Workshop: {args.difficulty.title()} Behavioral Testing")
        print("\n🧠 Learning Objectives:")
        print("- Understand therapeutic effectiveness validation")
        print("- Practice writing empathy-focused tests")
        print("- Learn persona-based testing approaches")
        
        print("\n📝 Workshop Exercise:")
        personas = ["overwhelmed_professional", "student_with_adhd"]
        scenarios = ["deadline_pressure", "overwhelm"]
        
        for persona in personas:
            for scenario in scenarios:
                test_code = generator.generate_test_from_scenario(
                    persona=persona,
                    scenario_type=scenario,
                    complexity=args.difficulty
                )
                print(f"\n## Example: {persona} - {scenario}")
                print("```python")
                print(test_code[:500] + "..." if len(test_code) > 500 else test_code)
                print("```")
    
    elif args.feature and args.user_personas:
        personas = [p.strip() for p in args.user_personas.split(",")]
        scenarios = [s.strip() for s in args.scenarios.split(",")] if args.scenarios else ["overwhelm"]
        
        test_suite = generator.generate_test_suite(
            personas=personas,
            scenario_types=scenarios,
            output_file=args.output
        )
        
        if not args.output:
            print("Generated Test Suite:")
            print("=" * 50)
            print(test_suite)
    
    else:
        # Default: show available personas and scenarios
        print("🧠 Available Personas:")
        for persona, data in generator.personas.items():
            print(f"  • {persona}: {data['description']}")
        
        print("\n📋 Available Scenarios:")
        scenarios = ["overwhelm", "deadline_pressure", "adhd_management", "perfectionism", "chronic_illness"]
        for scenario in scenarios:
            print(f"  • {scenario}")
        
        print("\n💡 Example Usage:")
        print("python behavioral_test_generator.py --feature=task_prioritization \\")
        print("  --user-personas=overwhelmed_professional,student_with_adhd \\")
        print("  --scenarios=overwhelm,deadline_pressure \\")
        print("  --output=tests/behavioral/test_generated_prioritization.py")


if __name__ == "__main__":
    main()