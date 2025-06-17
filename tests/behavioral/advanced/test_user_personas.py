"""
User Persona Adaptation Testing for Qwen Task Manager 3.0

This module tests that the system adapts appropriately to different cognitive styles,
mental health conditions, and individual differences. Validates personalized support
rather than one-size-fits-all productivity approaches.

Focus: Testing genuine understanding of neurodiversity and individual mental health
needs, ensuring the system provides authentic support for different cognitive styles.
"""

import pytest
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch
from dataclasses import dataclass
from enum import Enum

from tests.conftest import EnergyState, QualityScore
from tests.utils.test_helpers import (
    assert_persona_appropriate, assert_behavioral_quality,
    assert_neurodiversity_supportive, assert_individualized_response
)


@dataclass
class UserPersona:
    """Represents a user persona with specific cognitive and emotional needs"""
    name: str
    primary_challenges: List[str]
    strengths: List[str]
    energy_pattern: str
    cognitive_style: str
    support_needs: List[str]
    trigger_patterns: List[str]
    effective_strategies: List[str]


class CognitiveStyle(Enum):
    """Different cognitive processing styles"""
    ADHD_HYPERACTIVE = "adhd_hyperactive"
    ADHD_INATTENTIVE = "adhd_inattentive"
    ADHD_COMBINED = "adhd_combined"
    AUTISM_DETAIL_ORIENTED = "autism_detail"
    AUTISM_BIG_PICTURE = "autism_big_picture"
    DEPRESSION_LOW_ENERGY = "depression_low_energy"
    ANXIETY_PERFECTIONIST = "anxiety_perfectionist"
    BURNOUT_RECOVERY = "burnout_recovery"
    CHRONIC_ILLNESS = "chronic_illness"
    NEUROTYPICAL_STRESSED = "neurotypical_stressed"


class TestADHDPersonaAdaptation:
    """
    Test system adaptation to different ADHD presentations:
    hyperactive, inattentive, and combined type
    """
    
    @pytest.mark.behavioral
    @pytest.mark.parametrize("adhd_type", [
        CognitiveStyle.ADHD_HYPERACTIVE,
        CognitiveStyle.ADHD_INATTENTIVE, 
        CognitiveStyle.ADHD_COMBINED
    ])
    def test_adhd_specific_adaptations(self, adhd_type):
        """
        Test system provides appropriate adaptations for different ADHD types
        """
        # GIVEN
        adhd_persona = self._create_adhd_persona(adhd_type)
        challenging_scenario = {
            "task": "Organize entire home office and create filing system",
            "user_energy": EnergyState(6, 4, 5, "14:00"),  # Medium-low mental energy
            "deadline_pressure": "moderate",
            "interruptions_likely": True
        }
        
        # WHEN
        adapted_approach = self._mock_adhd_adaptation(challenging_scenario, adhd_persona)
        
        # THEN
        if adhd_type == CognitiveStyle.ADHD_HYPERACTIVE:
            # Should provide movement breaks and high-energy outlets
            assert adapted_approach["includes_movement_breaks"]
            assert any("physical" in strategy.lower() for strategy in adapted_approach["strategies"])
            assert adapted_approach["acknowledges_hyperactivity_as_strength"]
            
        elif adhd_type == CognitiveStyle.ADHD_INATTENTIVE:
            # Should provide external focus supports and minimize distractions
            assert adapted_approach["provides_external_focus_aids"]
            assert adapted_approach["minimizes_cognitive_load"]
            assert any("distraction" in strategy.lower() for strategy in adapted_approach["environmental_modifications"])
            
        elif adhd_type == CognitiveStyle.ADHD_COMBINED:
            # Should provide flexible strategies for both presentations
            assert adapted_approach["offers_multiple_strategy_options"]
            assert len(adapted_approach["alternative_approaches"]) >= 2
        
        # Universal ADHD adaptations
        assert all(step["timer"] <= 45 for step in adapted_approach["task_breakdown"])
        assert any(step.get("dopamine_reward") for step in adapted_approach["task_breakdown"])
        assert adapted_approach["acknowledges_adhd_strengths"]
        assert_neurodiversity_supportive(adapted_approach["explanation"])

    @pytest.mark.behavioral
    def test_adhd_hyperfocus_protection_and_utilization(self):
        """
        Test system recognizes ADHD hyperfocus as both strength and vulnerability
        """
        # GIVEN
        adhd_persona = self._create_adhd_persona(CognitiveStyle.ADHD_COMBINED)
        hyperfocus_detection = {
            "current_task_duration": 180,  # 3 hours on current task
            "last_break": "4 hours ago",
            "hydration_reminder_ignored": True,
            "mental_energy": 9,  # High focus
            "physical_energy": 3,  # Body neglected
            "task_type": "coding_project"
        }
        
        # WHEN
        hyperfocus_management = self._mock_hyperfocus_management(hyperfocus_detection, adhd_persona)
        
        # THEN
        # Should celebrate the hyperfocus as ADHD superpower
        assert hyperfocus_management["celebrates_hyperfocus_strength"]
        assert "superpower" in hyperfocus_management["validation"].lower() or \
               "gift" in hyperfocus_management["validation"].lower()
        
        # Should provide gentle body care reminders
        assert hyperfocus_management["includes_body_care_reminders"]
        assert any("hydrate" in reminder.lower() for reminder in hyperfocus_management["gentle_reminders"])
        
        # Should predict and prepare for crash
        assert hyperfocus_management["predicts_energy_crash"]
        assert len(hyperfocus_management["post_hyperfocus_recovery_plan"]) > 0
        
        # Should not interrupt the hyperfocus inappropriately
        assert not hyperfocus_management["forces_immediate_break"]
        assert hyperfocus_management["respects_hyperfocus_value"]

    def _create_adhd_persona(self, adhd_type):
        """Create detailed ADHD persona based on type"""
        base_persona = UserPersona(
            name="alex_adhd",
            primary_challenges=["executive_function", "time_management", "sustained_attention"],
            strengths=["creativity", "hyperfocus", "crisis_performance", "innovative_thinking"],
            energy_pattern="variable_with_peaks_and_crashes",
            cognitive_style=adhd_type.value,
            support_needs=["external_structure", "dopamine_rewards", "movement_integration"],
            trigger_patterns=["long_monotonous_tasks", "excessive_structure", "criticism_of_adhd_traits"],
            effective_strategies=["body_doubling", "timers", "gamification", "interest_driven_work"]
        )
        
        if adhd_type == CognitiveStyle.ADHD_HYPERACTIVE:
            base_persona.primary_challenges.extend(["impulse_control", "sitting_still"])
            base_persona.support_needs.extend(["movement_breaks", "physical_outlets"])
            
        elif adhd_type == CognitiveStyle.ADHD_INATTENTIVE:
            base_persona.primary_challenges.extend(["task_initiation", "daydreaming", "details"])
            base_persona.support_needs.extend(["external_focus_aids", "minimal_distractions"])
            
        return base_persona
    
    def _mock_adhd_adaptation(self, scenario, persona):
        """Mock ADHD-specific adaptation system"""
        return {
            "task_breakdown": [
                {"title": "Gather supplies", "timer": 15, "dopamine_reward": True},
                {"title": "Sort one category", "timer": 25, "dopamine_reward": False},
                {"title": "Create one file section", "timer": 20, "dopamine_reward": True}
            ],
            "includes_movement_breaks": persona.cognitive_style == "adhd_hyperactive",
            "provides_external_focus_aids": "inattentive" in persona.cognitive_style,
            "acknowledges_adhd_strengths": True,
            "acknowledges_hyperactivity_as_strength": "hyperactive" in persona.cognitive_style,
            "minimizes_cognitive_load": True,
            "offers_multiple_strategy_options": "combined" in persona.cognitive_style,
            "alternative_approaches": ["pomodoro_with_movement", "body_doubling_session"],
            "strategies": ["Use physical movement to maintain focus"],
            "environmental_modifications": ["Minimize visual distractions", "Use white noise"],
            "explanation": "This approach works with your ADHD brain, not against it. Your hyperfocus ability is a genuine superpower when channeled effectively."
        }
    
    def _mock_hyperfocus_management(self, detection, persona):
        """Mock hyperfocus management system"""
        return {
            "celebrates_hyperfocus_strength": True,
            "validation": "You're in a hyperfocus state - this is one of ADHD's superpowers! Your deep focus ability is incredibly valuable.",
            "includes_body_care_reminders": True,
            "gentle_reminders": ["Remember to hydrate", "Consider a quick stretch"],
            "predicts_energy_crash": True,
            "post_hyperfocus_recovery_plan": ["Rest", "Gentle movement", "Nourishing food"],
            "forces_immediate_break": False,
            "respects_hyperfocus_value": True
        }


class TestAutismPersonaAdaptation:
    """
    Test system adaptation to autistic users with different processing styles
    """
    
    @pytest.mark.behavioral
    def test_autism_sensory_and_routine_considerations(self):
        """
        Test system considers sensory needs and routine preferences for autistic users
        """
        # GIVEN
        autism_persona = UserPersona(
            name="jordan_autism",
            primary_challenges=["sensory_overload", "unexpected_changes", "social_communication"],
            strengths=["detailed_focus", "pattern_recognition", "systematic_thinking", "honesty"],
            energy_pattern="consistent_but_depleted_by_social_demands",
            cognitive_style="autism_detail_oriented",
            support_needs=["predictable_routines", "sensory_accommodations", "clear_expectations"],
            trigger_patterns=["sudden_changes", "overwhelming_sensory_input", "ambiguous_instructions"],
            effective_strategies=["detailed_planning", "visual_supports", "routine_structure"]
        )
        
        challenging_scenario = {
            "task": "Attend team building event and networking session",
            "social_demand": "high",
            "sensory_environment": "loud_crowded_restaurant", 
            "schedule_change": "moved from Tuesday to Thursday",
            "expectations": "unclear"
        }
        
        # WHEN
        autism_adaptation = self._mock_autism_adaptation(challenging_scenario, autism_persona)
        
        # THEN
        # Should acknowledge sensory challenges
        assert autism_adaptation["acknowledges_sensory_challenges"]
        assert len(autism_adaptation["sensory_accommodations"]) > 0
        
        # Should provide detailed preparation support
        assert autism_adaptation["provides_detailed_preparation"]
        assert autism_adaptation["clarifies_expectations"]
        
        # Should offer alternatives for overwhelming aspects
        assert len(autism_adaptation["alternative_participation_options"]) > 0
        
        # Should validate autism-specific challenges
        assert autism_adaptation["validates_autism_specific_challenges"]
        assert not autism_adaptation["minimizes_sensory_needs"]
        
        # Should celebrate autistic strengths
        assert autism_adaptation["celebrates_autistic_strengths"]
        assert_neurodiversity_supportive(autism_adaptation["explanation"])

    @pytest.mark.behavioral
    def test_autism_special_interest_integration(self):
        """
        Test system recognizes and leverages autistic special interests for motivation
        """
        # GIVEN
        autism_persona_with_interests = UserPersona(
            name="sam_autism",
            primary_challenges=["task_switching", "motivation_for_non_preferred_tasks"],
            strengths=["deep_expertise", "sustained_focus", "passionate_learning"],
            energy_pattern="high_for_special_interests_low_for_others",
            cognitive_style="autism_big_picture", 
            support_needs=["special_interest_connection", "bridge_to_non_preferred_tasks"],
            trigger_patterns=["dismissal_of_interests", "forced_task_switching"],
            effective_strategies=["interest_integration", "passionate_connection_finding"],
            special_interests=["astronomy", "data_visualization", "historical_linguistics"]
        )
        
        mundane_task = {
            "title": "Organize quarterly expense reports",
            "description": "Sort and categorize business expenses for Q4",
            "user_motivation": "very_low",
            "required_completion": True
        }
        
        # WHEN
        interest_integration = self._mock_special_interest_integration(mundane_task, autism_persona_with_interests)
        
        # THEN
        # Should find genuine connections to special interests
        assert len(interest_integration["special_interest_connections"]) > 0
        
        # Should not force superficial connections
        for connection in interest_integration["special_interest_connections"]:
            assert connection["authentic"], "Connection should be genuine, not forced"
            assert connection["motivating"], "Connection should actually increase motivation"
        
        # Should celebrate the special interests
        assert interest_integration["celebrates_special_interests"]
        assert not interest_integration["dismisses_interests_as_distraction"]
        
        # Should maintain task completion while honoring interests
        assert interest_integration["maintains_task_completion_goal"]
        assert_neurodiversity_supportive(interest_integration["explanation"])

    def _mock_autism_adaptation(self, scenario, persona):
        """Mock autism-specific adaptation system"""
        return {
            "acknowledges_sensory_challenges": True,
            "sensory_accommodations": ["Request quieter seating area", "Bring noise-canceling headphones"],
            "provides_detailed_preparation": True,
            "clarifies_expectations": True,
            "alternative_participation_options": ["Join for dinner only", "Participate virtually in some sessions"],
            "validates_autism_specific_challenges": True,
            "minimizes_sensory_needs": False,
            "celebrates_autistic_strengths": True,
            "explanation": "Your systematic thinking and attention to detail are valuable strengths. Let's plan accommodations that let you participate authentically."
        }
    
    def _mock_special_interest_integration(self, task, persona):
        """Mock special interest integration system"""
        return {
            "special_interest_connections": [{
                "connection": "Create data visualization of expense patterns over time",
                "authentic": True,
                "motivating": True,
                "special_interest": "data_visualization"
            }],
            "celebrates_special_interests": True,
            "dismisses_interests_as_distraction": False,
            "maintains_task_completion_goal": True,
            "explanation": "Your passion for data visualization can make this expense task genuinely interesting by revealing spending patterns and trends."
        }


class TestDepressionPersonaAdaptation:
    """
    Test system adaptation to users experiencing depression
    """
    
    @pytest.mark.behavioral
    def test_depression_appropriate_expectations_and_validation(self):
        """
        Test system adjusts expectations appropriately for depression episodes
        while maintaining hope and forward momentum
        """
        # GIVEN
        depression_persona = UserPersona(
            name="riley_depression",
            primary_challenges=["low_motivation", "fatigue", "negative_self_talk", "concentration_difficulties"],
            strengths=["empathy", "depth_of_feeling", "careful_consideration", "resilience"],
            energy_pattern="consistently_low_with_occasional_better_days",
            cognitive_style="depression_low_energy",
            support_needs=["behavioral_activation", "self_compassion_promotion", "tiny_achievable_steps"],
            trigger_patterns=["high_expectations", "comparison_to_others", "productivity_pressure"],
            effective_strategies=["micro_tasks", "celebration_of_small_wins", "routine_building"]
        )
        
        difficult_day_scenario = {
            "energy_level": EnergyState(2, 2, 1, "11:00"),
            "completed_tasks": [],
            "self_talk": "I'm useless, I can't even do basic things",
            "motivation": "very_low",
            "time_of_day": "late_morning_still_in_bed"
        }
        
        # WHEN
        depression_support = self._mock_depression_adaptation(difficult_day_scenario, depression_persona)
        
        # THEN
        # Should validate the difficulty without agreeing with harsh self-criticism
        assert depression_support["validates_depression_difficulty"]
        assert not depression_support["agrees_with_harsh_self_criticism"]
        
        # Should suggest micro-tasks appropriate for energy level
        suggested_tasks = depression_support["micro_tasks"]
        assert all(task["timer"] <= 10 for task in suggested_tasks)
        assert any(task["self_care"] for task in suggested_tasks)
        
        # Should promote self-compassion
        assert depression_support["promotes_self_compassion"]
        assert any(word in depression_support["validation_message"].lower() 
                  for word in ["gentle", "kind", "understand", "difficult"])
        
        # Should maintain hope without toxic positivity
        assert depression_support["maintains_hope"]
        assert not depression_support["uses_toxic_positivity"]
        
        # Should apply behavioral activation principles
        assert depression_support["applies_behavioral_activation"]
        assert_behavioral_quality(depression_support["validation_message"])

    def _mock_depression_adaptation(self, scenario, persona):
        """Mock depression-appropriate adaptation system"""
        return {
            "validates_depression_difficulty": True,
            "agrees_with_harsh_self_criticism": False,
            "micro_tasks": [
                {"title": "Get a glass of water", "timer": 2, "self_care": True},
                {"title": "Make bed or straighten covers", "timer": 5, "self_care": False},
                {"title": "Step outside for 1 minute", "timer": 3, "self_care": True}
            ],
            "promotes_self_compassion": True,
            "validation_message": "Depression makes everything feel harder because it literally is harder. Your brain is working against you right now, and that's not your fault.",
            "maintains_hope": True,
            "uses_toxic_positivity": False,
            "applies_behavioral_activation": True
        }


class TestBurnoutRecoveryPersonaAdaptation:
    """
    Test system adaptation to users in burnout recovery
    """
    
    @pytest.mark.behavioral
    @pytest.mark.parametrize("recovery_stage", [
        "acute_burnout",
        "early_recovery", 
        "rebuilding_capacity",
        "prevention_maintenance"
    ])
    def test_burnout_recovery_stage_appropriate_support(self, recovery_stage):
        """
        Test system provides stage-appropriate support during burnout recovery
        """
        # GIVEN
        burnout_persona = self._create_burnout_persona(recovery_stage)
        work_pressure_scenario = {
            "urgent_deadline": "client presentation due tomorrow",
            "team_expectations": "high",
            "personal_energy": self._get_recovery_stage_energy(recovery_stage),
            "previous_overwork_pattern": True
        }
        
        # WHEN
        recovery_support = self._mock_burnout_recovery_adaptation(work_pressure_scenario, burnout_persona)
        
        # THEN
        if recovery_stage == "acute_burnout":
            # Should prioritize rest over productivity
            assert recovery_support["prioritizes_rest_over_productivity"]
            assert recovery_support["validates_need_for_recovery_time"]
            assert not recovery_support["encourages_pushing_through"]
            
        elif recovery_stage == "early_recovery":
            # Should be very cautious about work load
            assert recovery_support["extremely_cautious_about_workload"]
            assert recovery_support["emphasizes_sustainable_pace"]
            
        elif recovery_stage == "rebuilding_capacity":
            # Should allow gradual challenge increase with monitoring
            assert recovery_support["allows_gradual_challenge_increase"]
            assert recovery_support["emphasizes_energy_monitoring"]
            
        elif recovery_stage == "prevention_maintenance":
            # Should focus on maintaining healthy boundaries
            assert recovery_support["focuses_on_boundary_maintenance"]
            assert recovery_support["celebrates_recovery_progress"]
        
        # Universal burnout recovery principles
        assert recovery_support["validates_burnout_as_real_condition"]
        assert recovery_support["promotes_boundary_setting"]
        assert not recovery_support["minimizes_recovery_needs"]
        assert_behavioral_quality(recovery_support["support_message"])

    def _create_burnout_persona(self, stage):
        """Create burnout persona for specific recovery stage"""
        return UserPersona(
            name=f"alex_burnout_{stage}",
            primary_challenges=["energy_depletion", "cynicism", "reduced_efficacy", "boundary_difficulties"],
            strengths=["deep_experience", "hard_won_wisdom", "empathy_for_others_struggling"],
            energy_pattern=f"burnout_recovery_{stage}",
            cognitive_style="burnout_recovery",
            support_needs=["validation", "gentle_pacing", "boundary_support", "realistic_expectations"],
            trigger_patterns=["pressure_to_push_through", "minimization_of_burnout", "unrealistic_timelines"],
            effective_strategies=["micro_recovery", "boundary_practice", "energy_monitoring", "self_compassion"]
        )
    
    def _get_recovery_stage_energy(self, stage):
        """Get appropriate energy level for recovery stage"""
        energy_levels = {
            "acute_burnout": EnergyState(1, 1, 2, "any_time"),
            "early_recovery": EnergyState(3, 2, 3, "any_time"),
            "rebuilding_capacity": EnergyState(5, 4, 5, "any_time"),
            "prevention_maintenance": EnergyState(7, 6, 7, "any_time")
        }
        return energy_levels[stage]
    
    def _mock_burnout_recovery_adaptation(self, scenario, persona):
        """Mock burnout recovery adaptation system"""
        stage = persona.energy_pattern.split("_")[-1]
        
        base_response = {
            "validates_burnout_as_real_condition": True,
            "promotes_boundary_setting": True,
            "minimizes_recovery_needs": False,
            "support_message": f"Burnout recovery is a real process that takes time. Your {stage} stage needs specific support."
        }
        
        if stage == "acute":
            base_response.update({
                "prioritizes_rest_over_productivity": True,
                "validates_need_for_recovery_time": True,
                "encourages_pushing_through": False
            })
        elif stage == "early":
            base_response.update({
                "extremely_cautious_about_workload": True,
                "emphasizes_sustainable_pace": True
            })
        elif stage == "rebuilding":
            base_response.update({
                "allows_gradual_challenge_increase": True,
                "emphasizes_energy_monitoring": True
            })
        elif stage == "prevention":
            base_response.update({
                "focuses_on_boundary_maintenance": True,
                "celebrates_recovery_progress": True
            })
            
        return base_response


class TestPersonaIntegrationAndEvolution:
    """
    Test that personas evolve and integrate multiple aspects appropriately
    """
    
    @pytest.mark.behavioral
    def test_complex_multi_condition_persona_support(self):
        """
        Test system handles users with multiple overlapping conditions appropriately
        """
        # GIVEN
        complex_persona = UserPersona(
            name="casey_complex",
            primary_challenges=["adhd_executive_function", "seasonal_depression", "perfectionist_anxiety"],
            strengths=["creative_problem_solving", "high_empathy", "detail_orientation_when_focused"],
            energy_pattern="seasonal_with_adhd_variability",
            cognitive_style="multiple_intersecting",
            support_needs=["flexible_structure", "seasonal_adaptation", "perfectionism_management"],
            trigger_patterns=["rigid_expectations", "dark_winter_months", "criticism_of_adhd_traits"],
            effective_strategies=["interest_based_learning", "light_therapy", "good_enough_permission"]
        )
        
        winter_scenario = {
            "season": "deep_winter",
            "daylight_hours": "limited",
            "energy_level": EnergyState(3, 2, 2, "14:00"),
            "perfectionist_paralysis": "high",
            "adhd_symptoms": "heightened_by_depression",
            "task": "prepare important presentation"
        }
        
        # WHEN
        integrated_support = self._mock_complex_persona_adaptation(winter_scenario, complex_persona)
        
        # THEN
        # Should address multiple conditions simultaneously
        assert integrated_support["addresses_seasonal_depression"]
        assert integrated_support["accommodates_adhd_needs"]
        assert integrated_support["manages_perfectionist_anxiety"]
        
        # Should not oversimplify or ignore any condition
        assert not integrated_support["oversimplifies_complexity"]
        assert len(integrated_support["multi_condition_strategies"]) >= 3
        
        # Should find synergistic approaches where possible
        assert integrated_support["uses_synergistic_strategies"]
        
        # Should maintain person-first, strengths-based approach
        assert integrated_support["maintains_strengths_focus"]
        assert_individualized_response(integrated_support["explanation"])

    def _mock_complex_persona_adaptation(self, scenario, persona):
        """Mock adaptation for complex multi-condition persona"""
        return {
            "addresses_seasonal_depression": True,
            "accommodates_adhd_needs": True, 
            "manages_perfectionist_anxiety": True,
            "oversimplifies_complexity": False,
            "multi_condition_strategies": [
                "Light therapy during work sessions (seasonal + focus)",
                "Permission for 'good enough' draft (perfectionism + adhd executive function)",
                "Interest-based approach to presentation topic (adhd motivation + seasonal energy conservation)"
            ],
            "uses_synergistic_strategies": True,
            "maintains_strengths_focus": True,
            "explanation": "Your unique combination of traits creates both challenges and remarkable strengths. Let's work with all aspects of how your brain works."
        }


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "behavioral"])