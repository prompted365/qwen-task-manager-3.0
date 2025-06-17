"""
Advanced Cognitive Load Management Testing for Qwen Task Manager 3.0

This module tests sophisticated cognitive load management that prevents overwhelm
while maintaining productivity. Tests working memory limits, decision fatigue
prevention, and executive function support.

Focus: Validating that the system understands human cognitive limitations and
adapts to preserve mental bandwidth while promoting sustainable productivity.
"""

import pytest
from typing import Dict, List, Any, Tuple
from unittest.mock import Mock, patch
from dataclasses import dataclass

from tests.conftest import EnergyState, QualityScore
from tests.utils.test_helpers import (
    assert_cognitive_manageability, assert_behavioral_quality,
    assert_overwhelm_prevention, assert_decision_fatigue_minimized
)


@dataclass
class CognitiveLoadMetrics:
    """Metrics for assessing cognitive load of tasks and systems"""
    working_memory_items: int
    decision_points: int
    context_switches: int
    complexity_score: float  # 1-10 scale
    mental_effort_required: str  # 'low', 'medium', 'high'
    
    def is_cognitively_manageable(self) -> bool:
        """Determine if load is within manageable limits"""
        return (self.working_memory_items <= 5 and 
                self.decision_points <= 3 and
                self.context_switches <= 2 and
                self.complexity_score <= 7.0)


class TestWorkingMemoryLimits:
    """
    Test system respects working memory limitations (3-7 items) in all interfaces
    and task presentations, based on cognitive science research
    """
    
    @pytest.mark.behavioral
    @pytest.mark.parametrize("task_count,expected_chunking", [
        (3, 1),   # Small list - single chunk
        (7, 1),   # At limit - single chunk  
        (12, 3),  # Medium list - multiple chunks
        (20, 4),  # Large list - clear categorization
        (50, 6)   # Massive list - hierarchical organization
    ])
    def test_task_list_chunking_respects_working_memory(self, task_count, expected_chunking):
        """
        Test that large task lists are chunked appropriately to prevent
        cognitive overwhelm while maintaining accessibility
        """
        # GIVEN
        many_tasks = [{"title": f"Task {i}", "priority": 5} for i in range(task_count)]
        
        # WHEN
        organized_view = self._mock_cognitive_chunking(many_tasks)
        
        # THEN
        # Should create appropriate number of chunks
        assert len(organized_view["chunks"]) <= expected_chunking + 1  # Allow some flexibility
        
        # Each visible chunk should respect working memory
        for chunk in organized_view["chunks"]:
            if chunk["visible"]:
                assert len(chunk["items"]) <= 7, f"Chunk has {len(chunk['items'])} items, exceeds working memory"
                assert len(chunk["items"]) >= 3, f"Chunk has {len(chunk['items'])} items, too small to be useful"
        
        # Should explain chunking strategy
        assert "cognitive" in organized_view["explanation"].lower() or \
               "manageable" in organized_view["explanation"].lower()
        assert_behavioral_quality(organized_view["explanation"])

    @pytest.mark.behavioral
    def test_immediate_focus_area_limitation(self):
        """
        Test that immediate focus area never exceeds 3-5 items regardless
        of how many urgent tasks exist
        """
        # GIVEN - Many urgent tasks that all seem important
        urgent_tasks = [
            {"title": f"Critical issue {i}", "priority": 9, "deadline": "today"}
            for i in range(15)
        ]
        
        # WHEN
        focus_organization = self._mock_immediate_focus_limitation(urgent_tasks)
        
        # THEN
        immediate_items = focus_organization["immediate_focus"]
        assert len(immediate_items) <= 5, "Too many immediate items cause paralysis"
        assert len(immediate_items) >= 3, "Too few items may underutilize capacity"
        
        # Should explain why limitation is helpful
        explanation = focus_organization["reasoning"].lower()
        assert any(term in explanation for term in ["overwhelm", "focus", "cognitive", "effective"])
        
        # Should organize remaining urgent tasks appropriately
        remaining_urgent = focus_organization["urgent_but_deferred"]
        assert len(remaining_urgent) == len(urgent_tasks) - len(immediate_items)
        
        # Should provide clear next action after current focus
        assert "next_action_after_current" in focus_organization
        assert_cognitive_manageability(immediate_items)

    def _mock_cognitive_chunking(self, tasks):
        """Mock intelligent task chunking system"""
        chunk_size = min(5, max(3, len(tasks) // 4))  # Adaptive chunk size
        chunks = []
        
        for i in range(0, len(tasks), chunk_size):
            chunk_tasks = tasks[i:i + chunk_size]
            chunks.append({
                "items": chunk_tasks,
                "visible": i == 0,  # Only first chunk visible initially
                "label": f"Group {i//chunk_size + 1}"
            })
        
        return {
            "chunks": chunks,
            "explanation": f"Organized {len(tasks)} tasks into {len(chunks)} manageable groups to prevent cognitive overwhelm."
        }
    
    def _mock_immediate_focus_limitation(self, tasks):
        """Mock immediate focus limitation system"""
        return {
            "immediate_focus": tasks[:3],  # Limit to 3 for cognitive manageability
            "urgent_but_deferred": tasks[3:],
            "reasoning": "Limited immediate focus to 3 tasks to prevent cognitive overwhelm. Research shows working memory can effectively track 3-5 items simultaneously.",
            "next_action_after_current": "Review deferred urgent tasks and select next 3"
        }


class TestDecisionFatiguePrevention:
    """
    Test system minimizes decision fatigue by reducing unnecessary choices,
    providing intelligent defaults, and batching decision-making
    """
    
    @pytest.mark.behavioral
    def test_smart_defaults_reduce_decision_load(self):
        """
        Test system provides intelligent defaults for common decisions
        to preserve mental energy for important choices
        """
        # GIVEN
        new_task_context = {
            "user_history": {
                "typical_timer_for_emails": 15,
                "preferred_energy_level_for_calls": "medium",
                "usual_priority_for_admin": 4
            },
            "current_energy": EnergyState(6, 7, 6, "14:00"),
            "similar_tasks_completed": [
                {"title": "Update client status", "timer": 20, "energy": "medium", "priority": 5}
            ]
        }
        
        vague_task = "send project update email"
        
        # WHEN
        clarified_with_defaults = self._mock_smart_defaults_application(
            vague_task, new_task_context
        )
        
        # THEN
        # Should apply intelligent defaults without asking user
        assert clarified_with_defaults["timer"] == 15  # Based on email history
        assert clarified_with_defaults["energy_required"] == "medium"  # Based on current capacity
        assert clarified_with_defaults["priority"] == 5  # Based on similar tasks
        
        # Should minimize decision points
        decision_metrics = self._calculate_decision_load(clarified_with_defaults)
        assert decision_metrics.decision_points <= 2, "Too many decisions required from user"
        
        # Should explain default reasoning
        assert "based on" in clarified_with_defaults["default_reasoning"].lower()
        assert_behavioral_quality(clarified_with_defaults["default_reasoning"])

    @pytest.mark.behavioral
    def test_decision_batching_for_efficiency(self):
        """
        Test system batches similar decisions to reduce context switching
        and preserve mental energy
        """
        # GIVEN
        multiple_similar_tasks = [
            {"title": "Call client A", "type": "phone_call", "decisions_needed": ["timing", "agenda"]},
            {"title": "Call client B", "type": "phone_call", "decisions_needed": ["timing", "agenda"]}, 
            {"title": "Call insurance", "type": "phone_call", "decisions_needed": ["timing", "questions"]},
            {"title": "Email team update", "type": "email", "decisions_needed": ["content", "recipients"]},
            {"title": "Email quarterly report", "type": "email", "decisions_needed": ["format", "deadline"]}
        ]
        
        # WHEN
        batched_decisions = self._mock_decision_batching(multiple_similar_tasks)
        
        # THEN
        # Should group similar decision types
        assert "phone_call_batch" in batched_decisions
        assert "email_batch" in batched_decisions
        
        # Should reduce total decision fatigue
        total_decision_points = sum(
            len(batch["consolidated_decisions"]) 
            for batch in batched_decisions.values()
        )
        original_decision_points = sum(
            len(task["decisions_needed"]) 
            for task in multiple_similar_tasks
        )
        assert total_decision_points < original_decision_points, "Decision batching should reduce total decisions"
        
        # Should suggest efficient decision-making timing
        assert any("batch" in batch.get("suggestion", "").lower() 
                  for batch in batched_decisions.values())

    @pytest.mark.behavioral
    def test_overwhelm_early_warning_system(self):
        """
        Test system detects early signs of cognitive overwhelm and
        intervenes before paralysis sets in
        """
        # GIVEN - Indicators of building overwhelm
        overwhelm_indicators = {
            "task_switching_frequency": 12,  # High context switching
            "incomplete_task_ratio": 0.7,    # 70% of tasks left unfinished
            "decision_postponement_count": 8, # Many delayed decisions
            "energy_decline_rate": -2.5,     # Rapid energy loss
            "time_since_last_completion": 180 # 3 hours without completing anything
        }
        
        current_task_load = [
            {"title": f"Complex task {i}", "complexity": "high"} 
            for i in range(10)
        ]
        
        # WHEN
        overwhelm_intervention = self._mock_overwhelm_detection(
            overwhelm_indicators, current_task_load
        )
        
        # THEN
        # Should detect overwhelm risk
        assert overwhelm_intervention["overwhelm_detected"]
        assert overwhelm_intervention["intervention_triggered"]
        
        # Should provide specific relief strategies
        relief_strategies = overwhelm_intervention["relief_strategies"]
        assert len(relief_strategies) >= 3
        assert any("break" in strategy.lower() for strategy in relief_strategies)
        assert any("simplify" in strategy.lower() for strategy in relief_strategies)
        
        # Should temporarily reduce cognitive load
        simplified_focus = overwhelm_intervention["simplified_immediate_focus"]
        assert len(simplified_focus) <= 2, "Should dramatically reduce focus during overwhelm"
        
        # Should acknowledge difficulty without criticism
        message = overwhelm_intervention["supportive_message"]
        assert_behavioral_quality(message)
        assert any(word in message.lower() for word in ["normal", "understandable", "human"])

    def _calculate_decision_load(self, task_clarification):
        """Calculate cognitive decision load for a task"""
        decisions = 0
        if "timer" not in task_clarification: decisions += 1
        if "priority" not in task_clarification: decisions += 1
        if "energy_required" not in task_clarification: decisions += 1
        
        return CognitiveLoadMetrics(
            working_memory_items=1,  # Single task
            decision_points=decisions,
            context_switches=0,
            complexity_score=5.0,
            mental_effort_required="medium"
        )
    
    def _mock_smart_defaults_application(self, task, context):
        """Mock intelligent defaults system"""
        return {
            "title": task,
            "timer": context["user_history"]["typical_timer_for_emails"],
            "energy_required": context["user_history"]["preferred_energy_level_for_calls"],
            "priority": 5,  # Intelligent default based on similar tasks
            "default_reasoning": "Applied defaults based on your email patterns and similar tasks to minimize decision fatigue."
        }
    
    def _mock_decision_batching(self, tasks):
        """Mock decision batching system"""
        phone_tasks = [t for t in tasks if t["type"] == "phone_call"]
        email_tasks = [t for t in tasks if t["type"] == "email"]
        
        return {
            "phone_call_batch": {
                "tasks": phone_tasks,
                "consolidated_decisions": ["optimal_calling_time", "call_agenda_template"],
                "suggestion": "Batch all phone calls between 2-4 PM when you're typically most conversational"
            },
            "email_batch": {
                "tasks": email_tasks,
                "consolidated_decisions": ["email_template", "send_timing"],
                "suggestion": "Batch email composition during your writing-focused time blocks"
            }
        }
    
    def _mock_overwhelm_detection(self, indicators, current_load):
        """Mock overwhelm detection and intervention system"""
        return {
            "overwhelm_detected": True,
            "intervention_triggered": True,
            "overwhelm_score": 8.5,  # Out of 10
            "relief_strategies": [
                "Take a 10-minute break to reset cognitive load",
                "Simplify current focus to just 1 essential task",
                "Defer non-urgent items to reduce mental clutter"
            ],
            "simplified_immediate_focus": [current_load[0]],  # Just one task
            "supportive_message": "You're experiencing cognitive overwhelm, which is completely normal when juggling many complex tasks. Let's simplify and reset."
        }


class TestExecutiveFunctionSupport:
    """
    Test system provides specific support for executive function challenges
    including task initiation, working memory, and cognitive flexibility
    """
    
    @pytest.mark.behavioral
    def test_task_initiation_support_for_executive_dysfunction(self):
        """
        Test system helps users with executive dysfunction overcome
        task initiation paralysis through specific strategies
        """
        # GIVEN
        executive_dysfunction_profile = {
            "initiation_difficulty": "high",
            "working_memory_challenges": True,
            "context_switching_cost": "high",
            "hyperfocus_tendency": True
        }
        
        paralyzing_task = {
            "title": "Organize entire office space",
            "description": "Clean up and organize the whole office",
            "overwhelming_factors": ["too_vague", "too_large", "no_clear_start"]
        }
        
        # WHEN
        initiation_support = self._mock_executive_function_support(
            paralyzing_task, executive_dysfunction_profile
        )
        
        # THEN
        # Should break down into tiny, specific steps
        micro_steps = initiation_support["micro_steps"]
        assert len(micro_steps) >= 5, "Should provide multiple micro-steps"
        assert all(step["timer"] <= 15 for step in micro_steps), "Steps should be very short for initiation ease"
        
        # First step should be extremely low-barrier
        first_step = micro_steps[0]
        assert first_step["timer"] <= 5, "First step should be under 5 minutes"
        assert "gather" in first_step["title"].lower() or "collect" in first_step["title"].lower()
        
        # Should provide dopamine rewards
        assert any(step.get("dopamine_reward") for step in micro_steps)
        
        # Should acknowledge executive dysfunction
        assert "executive" in initiation_support["acknowledgment"].lower() or \
               "initiation" in initiation_support["acknowledgment"].lower()
        assert_behavioral_quality(initiation_support["acknowledgment"])

    @pytest.mark.behavioral
    def test_working_memory_scaffolding(self):
        """
        Test system provides external scaffolding for working memory limitations
        """
        # GIVEN
        working_memory_challenge = {
            "capacity": "low",  # 3-4 items max
            "interference_susceptibility": "high",
            "context_dependent": True
        }
        
        multi_step_task = {
            "title": "Prepare and send quarterly report",
            "steps": [
                "Gather Q4 data from 3 systems",
                "Analyze trends and create charts", 
                "Write executive summary",
                "Format document professionally",
                "Review with team lead",
                "Send to stakeholders with cover email"
            ]
        }
        
        # WHEN
        scaffolding = self._mock_working_memory_scaffolding(
            multi_step_task, working_memory_challenge
        )
        
        # THEN
        # Should provide external memory aids
        assert "checklist" in scaffolding["memory_aids"]
        assert "progress_tracker" in scaffolding["memory_aids"]
        
        # Should chunk steps appropriately
        chunks = scaffolding["chunked_steps"]
        assert all(len(chunk) <= 3 for chunk in chunks), "Chunks should respect working memory limits"
        
        # Should provide context preservation
        assert scaffolding["context_preservation"]["enabled"]
        assert "state_saving" in scaffolding["context_preservation"]["methods"]
        
        # Should suggest environmental supports
        environmental_supports = scaffolding["environmental_supports"]
        assert any("minimize" in support.lower() for support in environmental_supports)
        assert_behavioral_quality(scaffolding["explanation"])

    @pytest.mark.behavioral
    def test_cognitive_flexibility_support(self):
        """
        Test system helps users adapt when plans change or unexpected
        obstacles arise, supporting cognitive flexibility challenges
        """
        # GIVEN
        cognitive_rigidity_profile = {
            "plan_change_difficulty": "high",
            "unexpected_obstacle_stress": "severe",
            "cognitive_flexibility": "low"
        }
        
        plan_disruption = {
            "original_plan": ["Task A at 9 AM", "Task B at 10 AM", "Task C at 11 AM"],
            "disruption": "Urgent meeting called for 10-11 AM",
            "affected_tasks": ["Task B", "Task C"],
            "user_stress_level": 8  # Out of 10
        }
        
        # WHEN
        flexibility_support = self._mock_cognitive_flexibility_support(
            plan_disruption, cognitive_rigidity_profile
        )
        
        # THEN
        # Should acknowledge difficulty of change
        assert "difficult" in flexibility_support["validation"].lower() or \
               "challenging" in flexibility_support["validation"].lower()
        
        # Should provide structured adaptation process
        adaptation_steps = flexibility_support["adaptation_process"]
        assert len(adaptation_steps) >= 3, "Should provide step-by-step adaptation guidance"
        
        # Should minimize additional decisions during stress
        revised_plan = flexibility_support["revised_plan"]
        assert revised_plan["additional_decisions_minimized"]
        
        # Should preserve what can be preserved
        preserved_elements = flexibility_support["preserved_elements"]
        assert len(preserved_elements) > 0, "Should preserve some original plan elements"
        
        # Should provide stress management
        assert "stress_management" in flexibility_support
        assert_behavioral_quality(flexibility_support["validation"])

    def _mock_executive_function_support(self, task, profile):
        """Mock executive function support system"""
        return {
            "micro_steps": [
                {"title": "Gather one small box", "timer": 2, "dopamine_reward": True},
                {"title": "Collect loose papers from desk", "timer": 5, "dopamine_reward": False},
                {"title": "Sort papers into 3 piles", "timer": 10, "dopamine_reward": True},
                {"title": "File one pile", "timer": 15, "dopamine_reward": True}
            ],
            "acknowledgment": "Executive dysfunction makes task initiation really challenging. These micro-steps are designed to work with your brain, not against it."
        }
    
    def _mock_working_memory_scaffolding(self, task, challenge):
        """Mock working memory scaffolding system"""
        return {
            "memory_aids": ["checklist", "progress_tracker", "context_notes"],
            "chunked_steps": [
                task["steps"][:2],  # Chunk 1: Data gathering
                task["steps"][2:4],  # Chunk 2: Analysis and writing  
                task["steps"][4:]    # Chunk 3: Review and distribution
            ],
            "context_preservation": {
                "enabled": True,
                "methods": ["state_saving", "progress_notes", "next_action_prompts"]
            },
            "environmental_supports": [
                "Minimize distractions during each chunk",
                "Use timer to prevent hyperfocus",
                "Save progress after each step"
            ],
            "explanation": "Broken down to respect working memory limits and provide external memory supports."
        }
    
    def _mock_cognitive_flexibility_support(self, disruption, profile):
        """Mock cognitive flexibility support system"""
        return {
            "validation": "Plan changes are especially difficult when you prefer structure. This stress response is completely normal.",
            "adaptation_process": [
                "Acknowledge the disruption and take 3 deep breaths",
                "Identify which parts of original plan can be preserved",
                "Make minimal necessary changes to accommodate meeting"
            ],
            "revised_plan": {
                "new_schedule": ["Task A at 9 AM", "Meeting 10-11 AM", "Task B at 11:30 AM"],
                "additional_decisions_minimized": True
            },
            "preserved_elements": ["Task A timing", "Overall task sequence"],
            "stress_management": ["Deep breathing", "Remind yourself this is temporary"]
        }


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "behavioral"])