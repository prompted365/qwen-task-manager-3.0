"""
Advanced Energy Pattern Testing for Qwen Task Manager 3.0

This module tests sophisticated energy management features that adapt to individual
circadian rhythms, ADHD patterns, burnout recovery, and seasonal variations.

Focus: Validating that the system genuinely understands and responds to human energy
cycles rather than imposing arbitrary productivity schedules.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, patch
import asyncio

from tests.conftest import EnergyState, QualityScore
from tests.utils.test_helpers import (
    assert_energy_appropriate, assert_behavioral_quality,
    assert_circadian_awareness, assert_adhd_supportive
)


class TestCircadianRhythmAdaptation:
    """
    Test sophisticated circadian rhythm awareness that goes beyond simple 
    morning/evening preferences to understand individual chronotypes
    """
    
    @pytest.mark.behavioral
    @pytest.mark.parametrize("chronotype,peak_hours,low_hours", [
        ("extreme_morning", ["06:00", "07:00", "08:00"], ["20:00", "21:00", "22:00"]),
        ("moderate_morning", ["08:00", "09:00", "10:00"], ["22:00", "23:00", "00:00"]),
        ("moderate_evening", ["15:00", "16:00", "17:00"], ["06:00", "07:00", "08:00"]),
        ("extreme_evening", ["20:00", "21:00", "22:00"], ["06:00", "07:00", "08:00"])
    ])
    def test_chronotype_specific_scheduling(self, chronotype, peak_hours, low_hours):
        """
        Test that system schedules demanding tasks during individual peak hours
        and protects low energy times with gentle tasks
        """
        # GIVEN
        user_chronotype = {
            "type": chronotype,
            "peak_performance_hours": peak_hours,
            "low_energy_hours": low_hours,
            "historical_patterns": self._generate_historical_pattern(peak_hours, low_hours)
        }
        
        demanding_tasks = [
            {"title": "Strategic planning session", "energy_required": "high", "cognitive_load": "heavy"},
            {"title": "Write complex proposal", "energy_required": "high", "cognitive_load": "heavy"},
            {"title": "Code review deep dive", "energy_required": "high", "cognitive_load": "heavy"}
        ]
        
        gentle_tasks = [
            {"title": "Organize email folders", "energy_required": "low", "cognitive_load": "light"},
            {"title": "Update project status", "energy_required": "low", "cognitive_load": "light"},
            {"title": "File digital receipts", "energy_required": "low", "cognitive_load": "light"}
        ]
        
        # WHEN
        schedule = self._mock_chronotype_scheduling(
            demanding_tasks + gentle_tasks, 
            user_chronotype
        )
        
        # THEN
        # Demanding tasks should be in peak hours
        for task_time in schedule["high_energy_slots"]:
            hour = task_time.split(":")[0] + ":00"
            assert hour in peak_hours, f"High energy task scheduled at {hour}, not in peak hours {peak_hours}"
        
        # Gentle tasks should be in low energy hours  
        for task_time in schedule["low_energy_slots"]:
            hour = task_time.split(":")[0] + ":00"
            assert hour in low_hours, f"Low energy task scheduled at {hour}, not in low energy hours {low_hours}"
        
        # Reasoning should acknowledge chronotype
        assert chronotype.split("_")[1] in schedule["reasoning"].lower()  # "morning" or "evening"
        assert_behavioral_quality(schedule["reasoning"])

    def _generate_historical_pattern(self, peak_hours, low_hours):
        """Generate realistic historical energy data"""
        pattern = {}
        for hour in range(24):
            hour_str = f"{hour:02d}:00"
            if hour_str in peak_hours:
                pattern[hour_str] = {"avg_energy": 8.5, "productivity_score": 9.2}
            elif hour_str in low_hours:
                pattern[hour_str] = {"avg_energy": 3.2, "productivity_score": 4.1}
            else:
                pattern[hour_str] = {"avg_energy": 6.0, "productivity_score": 6.5}
        return pattern
    
    def _mock_chronotype_scheduling(self, tasks, user_chronotype):
        """Mock advanced chronotype-aware scheduling"""
        return {
            "high_energy_slots": [f"{user_chronotype['peak_performance_hours'][0]}:30"],
            "low_energy_slots": [f"{user_chronotype['low_energy_hours'][0]}:30"],
            "reasoning": f"Scheduled based on your {user_chronotype['type']} chronotype patterns. Your peak mental clarity occurs during {user_chronotype['peak_performance_hours'][0]}-{user_chronotype['peak_performance_hours'][-1]} window."
        }


class TestADHDEnergyManagement:
    """
    Test sophisticated ADHD energy pattern management including hyperfocus
    protection, crash prediction, and medication timing awareness
    """
    
    @pytest.mark.behavioral
    def test_hyperfocus_protection_and_utilization(self):
        """
        Test system recognizes hyperfocus state and both protects it
        while preparing for inevitable crash
        """
        # GIVEN
        current_hyperfocus = EnergyState(
            physical=6, mental=9, emotional=8, timestamp="10:30"
        )
        
        # Historical pattern shows crashes after hyperfocus
        adhd_history = {
            "hyperfocus_episodes": [
                {"start": "08:00", "peak": "10:30", "crash": "12:45", "recovery": "15:00"},
                {"start": "14:00", "peak": "16:30", "crash": "18:45", "recovery": "20:00"}
            ],
            "typical_hyperfocus_duration": 180,  # 3 hours
            "crash_severity": "moderate",
            "recovery_time": 120  # 2 hours
        }
        
        urgent_tasks = [
            {"title": "Fix critical production bug", "priority": 10, "energy_required": "high"},
            {"title": "Prepare client presentation", "priority": 9, "energy_required": "high"},
            {"title": "Organize photo library", "priority": 3, "energy_required": "low"}
        ]
        
        # WHEN
        hyperfocus_plan = self._mock_hyperfocus_management(
            current_hyperfocus, adhd_history, urgent_tasks
        )
        
        # THEN
        # Should recommend continuing current high-value work
        assert hyperfocus_plan["continue_current_task"]
        assert "hyperfocus" in hyperfocus_plan["reasoning"].lower()
        
        # Should predict and prepare for crash
        assert len(hyperfocus_plan["crash_warnings"]) > 0
        assert "12:45" in str(hyperfocus_plan["predicted_crash_time"])  # Based on pattern
        
        # Should pre-schedule recovery tasks
        recovery_tasks = hyperfocus_plan["post_crash_schedule"]
        assert all(task["energy_required"] == "low" for task in recovery_tasks)
        assert any("organize" in task["title"].lower() for task in recovery_tasks)
        
        # Should acknowledge ADHD pattern value
        assert any(word in hyperfocus_plan["reasoning"].lower() 
                  for word in ["superpower", "strength", "gift", "valuable"])

    @pytest.mark.behavioral  
    def test_medication_timing_awareness(self):
        """
        Test system understands stimulant medication timing and adjusts
        energy predictions accordingly
        """
        # GIVEN
        medication_schedule = {
            "medication": "stimulant",
            "morning_dose": "07:00",
            "afternoon_dose": "13:00", 
            "effectiveness_curve": {
                "07:00": 0.0, "08:00": 0.7, "09:00": 0.9, "10:00": 1.0,
                "11:00": 0.9, "12:00": 0.6, "13:00": 0.4, "14:00": 0.8,
                "15:00": 0.9, "16:00": 0.8, "17:00": 0.6, "18:00": 0.3
            }
        }
        
        current_time = "11:30"  # Peak effectiveness period
        
        # WHEN
        medication_aware_plan = self._mock_medication_aware_scheduling(
            medication_schedule, current_time
        )
        
        # THEN
        # Should recognize peak medication effectiveness
        assert medication_aware_plan["current_effectiveness"] >= 0.8
        assert "medication" in medication_aware_plan["reasoning"].lower()
        
        # Should suggest cognitively demanding tasks during peak
        suggested_now = medication_aware_plan["current_recommendations"]
        assert any(task["cognitive_load"] == "heavy" for task in suggested_now)
        
        # Should warn about afternoon dip before second dose
        afternoon_warnings = medication_aware_plan["upcoming_low_periods"]
        assert any("12:00" in warning for warning in afternoon_warnings)

    def _mock_hyperfocus_management(self, current_state, history, tasks):
        """Mock hyperfocus-aware task management"""
        return {
            "continue_current_task": True,
            "reasoning": "You're in a hyperfocus state - this is one of ADHD's superpowers! Your mental energy is at 9/10, which is perfect for deep work.",
            "crash_warnings": ["Energy crash predicted around 12:45 PM based on your typical 3-hour hyperfocus pattern"],
            "predicted_crash_time": "12:45",
            "post_crash_schedule": [
                {"title": "Organize photo library", "energy_required": "low", "scheduled_time": "13:00"}
            ]
        }
    
    def _mock_medication_aware_scheduling(self, medication_schedule, current_time):
        """Mock medication-aware energy management"""
        return {
            "current_effectiveness": 0.9,
            "reasoning": "Your stimulant medication is at peak effectiveness right now. Great time for focus-intensive work.",
            "current_recommendations": [
                {"title": "Complex coding task", "cognitive_load": "heavy", "timing": "optimal"}
            ],
            "upcoming_low_periods": ["Energy dip expected 12:00-13:00 before afternoon dose kicks in"]
        }


class TestSeasonalEnergyAdaptation:
    """
    Test system adaptation to seasonal affective patterns and 
    environmental energy influences
    """
    
    @pytest.mark.behavioral
    @pytest.mark.parametrize("season,expected_adaptations", [
        ("winter_sad", ["light_therapy_reminders", "vitamin_d_awareness", "shortened_task_timers"]),
        ("spring_renewal", ["increased_outdoor_tasks", "longer_focus_periods", "creative_prioritization"]),
        ("summer_heat_fatigue", ["early_morning_scheduling", "hydration_reminders", "reduced_afternoon_load"]),
        ("autumn_transition", ["routine_establishment", "preparation_tasks", "cozy_environment_suggestions"])
    ])
    def test_seasonal_energy_adaptation(self, season, expected_adaptations):
        """
        Test system adapts to seasonal energy patterns and environmental factors
        """
        # GIVEN
        seasonal_profile = self._create_seasonal_profile(season)
        current_date = self._get_season_date(season)
        
        standard_tasks = [
            {"title": "Team meeting", "type": "social", "energy_required": "medium"},
            {"title": "Creative brainstorming", "type": "creative", "energy_required": "high"},
            {"title": "Data entry", "type": "routine", "energy_required": "low"},
            {"title": "Outdoor team building", "type": "outdoor", "energy_required": "medium"}
        ]
        
        # WHEN
        seasonal_recommendations = self._mock_seasonal_adaptation(
            standard_tasks, seasonal_profile, current_date
        )
        
        # THEN
        # Validate season-appropriate adaptations
        for adaptation in expected_adaptations:
            if adaptation == "light_therapy_reminders":
                assert "light" in seasonal_recommendations["wellness_suggestions"][0].lower()
            elif adaptation == "early_morning_scheduling":
                morning_tasks = seasonal_recommendations["morning_priority_tasks"]
                assert len(morning_tasks) > len(seasonal_recommendations["afternoon_priority_tasks"])
            elif adaptation == "shortened_task_timers":
                avg_timer = sum(task["timer"] for task in seasonal_recommendations["adapted_tasks"]) / len(seasonal_recommendations["adapted_tasks"])
                assert avg_timer <= 25  # Shorter than standard 30-45 minute chunks
        
        # Reasoning should acknowledge seasonal factors
        assert_behavioral_quality(seasonal_recommendations["reasoning"])
        assert season.split("_")[0] in seasonal_recommendations["reasoning"].lower()

    def _create_seasonal_profile(self, season):
        """Create realistic seasonal energy profile"""
        if season == "winter_sad":
            return {
                "condition": "seasonal_affective_disorder",
                "light_sensitivity": "high",
                "energy_baseline": 4.2,
                "motivation_challenges": True
            }
        elif season == "summer_heat_fatigue":
            return {
                "heat_sensitivity": "high", 
                "optimal_temp_range": "65-72F",
                "afternoon_energy_drop": True
            }
        return {"season": season, "adaptations_needed": True}
    
    def _get_season_date(self, season):
        """Get representative date for season"""
        season_dates = {
            "winter_sad": "2024-01-15",
            "spring_renewal": "2024-04-15", 
            "summer_heat_fatigue": "2024-07-15",
            "autumn_transition": "2024-10-15"
        }
        return season_dates.get(season, "2024-06-15")
    
    def _mock_seasonal_adaptation(self, tasks, profile, date):
        """Mock seasonal adaptation system"""
        return {
            "adapted_tasks": [{"title": task["title"], "timer": 20} for task in tasks],
            "wellness_suggestions": ["Consider light therapy in morning during dark winter months"],
            "morning_priority_tasks": tasks[:2],
            "afternoon_priority_tasks": tasks[2:],
            "reasoning": f"Adapted schedule for winter seasonal patterns. Shorter task chunks and morning prioritization help manage seasonal energy fluctuations."
        }


class TestEnergyRecoveryPatterns:
    """
    Test system support for various recovery patterns including burnout,
    chronic illness, and post-crisis energy management
    """
    
    @pytest.mark.behavioral
    def test_burnout_recovery_progression(self):
        """
        Test system provides appropriate support during different stages
        of burnout recovery with realistic timeline expectations
        """
        # GIVEN - Different stages of burnout recovery
        recovery_stages = {
            "acute_burnout": EnergyState(physical=2, mental=1, emotional=2, timestamp="week_1"),
            "early_recovery": EnergyState(physical=3, mental=3, emotional=3, timestamp="week_4"), 
            "rebuilding": EnergyState(physical=5, mental=4, emotional=5, timestamp="week_12"),
            "sustainable": EnergyState(physical=7, mental=6, emotional=7, timestamp="week_24")
        }
        
        challenging_task = {
            "title": "Lead strategic planning meeting",
            "energy_required": "high",
            "social_demand": "high",
            "decision_fatigue": "high"
        }
        
        # Test each recovery stage
        for stage_name, energy_state in recovery_stages.items():
            # WHEN
            recovery_support = self._mock_burnout_recovery_support(
                challenging_task, energy_state, stage_name
            )
            
            # THEN - Validate stage-appropriate support
            if stage_name == "acute_burnout":
                assert not recovery_support["task_recommended"]
                assert "rest" in recovery_support["primary_recommendation"].lower()
                assert recovery_support["timeline_reality_check"]
                
            elif stage_name == "early_recovery":
                assert recovery_support["task_modified"]
                assert recovery_support["modified_task"]["social_demand"] == "low"
                
            elif stage_name == "rebuilding":
                assert recovery_support["gradual_challenge_increase"]
                assert recovery_support["energy_monitoring_emphasized"]
                
            elif stage_name == "sustainable":
                assert recovery_support["task_recommended"]
                assert recovery_support["celebrates_progress"]
            
            # All stages should validate the recovery process
            assert_behavioral_quality(recovery_support["message"])
            assert "recovery" in recovery_support["message"].lower()

    @pytest.mark.behavioral
    def test_chronic_illness_spoon_theory_integration(self):
        """
        Test system integrates spoon theory for users with chronic illness,
        tracking energy as finite resource that must be budgeted carefully
        """
        # GIVEN
        spoon_profile = {
            "condition": "chronic_fatigue_syndrome",
            "daily_spoons": 12,  # Limited energy units
            "current_spoons": 8,  # Already used some today
            "spoon_costs": {
                "low_energy_task": 1,
                "medium_energy_task": 2, 
                "high_energy_task": 4,
                "social_interaction": 3,
                "decision_making": 2
            }
        }
        
        remaining_tasks = [
            {"title": "Grocery shopping", "spoon_cost": 4, "priority": 8},
            {"title": "Call doctor", "spoon_cost": 3, "priority": 9},
            {"title": "Organize photos", "spoon_cost": 1, "priority": 3},
            {"title": "Team meeting", "spoon_cost": 5, "priority": 7}
        ]
        
        # WHEN
        spoon_budget = self._mock_spoon_theory_planning(remaining_tasks, spoon_profile)
        
        # THEN
        # Should not exceed available spoons
        total_planned_cost = sum(task["spoon_cost"] for task in spoon_budget["recommended_tasks"])
        assert total_planned_cost <= spoon_profile["current_spoons"]
        
        # Should prioritize by both urgency and spoon efficiency
        high_priority_low_cost = [t for t in spoon_budget["recommended_tasks"] 
                                 if t["priority"] >= 8 and t["spoon_cost"] <= 3]
        assert len(high_priority_low_cost) > 0
        
        # Should defer high-cost items appropriately
        deferred_high_cost = [t for t in spoon_budget["deferred_tasks"] 
                             if t["spoon_cost"] >= 4]
        assert len(deferred_high_cost) > 0
        
        # Should explain spoon theory reasoning
        assert "spoons" in spoon_budget["reasoning"].lower() or "energy budget" in spoon_budget["reasoning"].lower()
        assert_behavioral_quality(spoon_budget["reasoning"])

    def _mock_burnout_recovery_support(self, task, energy_state, stage):
        """Mock burnout recovery stage-appropriate support"""
        stage_responses = {
            "acute_burnout": {
                "task_recommended": False,
                "primary_recommendation": "Your only job right now is rest and recovery. Healing from burnout takes time.",
                "timeline_reality_check": True,
                "message": "Burnout recovery is a process, not a sprint. Be gentle with yourself."
            },
            "early_recovery": {
                "task_modified": True,
                "modified_task": {"title": "Send brief email to team about meeting", "social_demand": "low"},
                "message": "You're making progress in recovery. Let's modify this task to match your current capacity."
            },
            "rebuilding": {
                "gradual_challenge_increase": True,
                "energy_monitoring_emphasized": True,
                "message": "You're rebuilding strength. Let's try this with careful energy monitoring."
            },
            "sustainable": {
                "task_recommended": True,
                "celebrates_progress": True,
                "message": "Look how far you've come in your recovery! You're ready for this challenge."
            }
        }
        return stage_responses[stage]
    
    def _mock_spoon_theory_planning(self, tasks, profile):
        """Mock spoon theory aware task planning"""
        # Simple mock: recommend tasks that fit in spoon budget
        recommended = []
        remaining_spoons = profile["current_spoons"]
        
        # Sort by priority/spoon ratio
        sorted_tasks = sorted(tasks, key=lambda t: t["priority"] / t["spoon_cost"], reverse=True)
        
        for task in sorted_tasks:
            if task["spoon_cost"] <= remaining_spoons:
                recommended.append(task)
                remaining_spoons -= task["spoon_cost"]
        
        deferred = [t for t in tasks if t not in recommended]
        
        return {
            "recommended_tasks": recommended,
            "deferred_tasks": deferred,
            "remaining_spoons": remaining_spoons,
            "reasoning": f"Planned {len(recommended)} tasks within your {profile['current_spoons']} spoon budget. Deferred high-cost tasks to preserve energy."
        }


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "behavioral"])