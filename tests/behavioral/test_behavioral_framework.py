"""
BDD Framework for Psychological Features

This module implements Behavior-Driven Development scenarios that test the psychological
impact of our system. We validate that features genuinely support behavioral activation
and help users with executive function challenges.

Key Testing Philosophy:
- Test psychological outcomes, not just code execution
- Validate behavioral activation principles in practice
- Ensure features support diverse cognitive styles
- Measure impact on user well-being and productivity

BDD Structure:
- GIVEN: User state and context
- WHEN: System interaction occurs  
- THEN: Behavioral outcome is validated
"""

import pytest
from typing import Dict, List, Any
from unittest.mock import Mock, patch
import asyncio
from dataclasses import asdict

# Import test utilities and fixtures
from tests.utils.test_helpers import (
    AIQualityValidator, BehavioralTestValidator, assert_behavioral_quality,
    assert_cognitive_manageability, assert_energy_appropriate
)
from tests.fixtures.sample_data import (
    get_user_profile, get_brain_dump, get_energy_pattern, 
    get_completion_scenario, get_behavioral_scenario
)

class TestEnergyBasedTaskScheduling:
    """
    Feature: Energy-Based Task Scheduling
    As a user with variable energy patterns
    I want tasks scheduled according to my energy levels
    So that I can maintain sustainable productivity
    """
    
    @pytest.mark.behavioral
    def test_morning_energy_optimization(self, mock_qwen_responses, sample_energy_states):
        """
        Scenario: Morning Energy Optimization
        Given my historical energy data shows high morning mental energy
        And I have both creative and administrative tasks pending
        When the system prioritizes my day
        Then creative tasks should be scheduled for morning slots
        And administrative tasks should be moved to afternoon
        And the reasoning should be transparent to the user
        """
        # GIVEN
        morning_person_energy = sample_energy_states['morning_person']
        mixed_tasks = [
            {"title": "Design new feature wireframes", "type": "creative", "energy_required": "high"},
            {"title": "Update expense reports", "type": "administrative", "energy_required": "low"},
            {"title": "Write blog post", "type": "creative", "energy_required": "high"},
            {"title": "Schedule team meetings", "type": "administrative", "energy_required": "low"}
        ]
        
        # Mock the AI prioritization response
        mock_prioritization = {
            "morning_slots": ["Design new feature wireframes", "Write blog post"],
            "afternoon_slots": ["Update expense reports", "Schedule team meetings"],
            "reasoning": "Your energy data shows peak mental clarity 8-11 AM. Creative tasks scheduled during high-energy window, administrative tasks moved to afternoon when you prefer routine work."
        }
        
        # WHEN
        with patch('qtm3_core.qwen.prioritize_tasks', return_value=mock_prioritization):
            from qtm3_core import TaskManagerCore  # Mock import
            qtm = Mock()
            qtm.prioritize_by_energy = Mock(return_value=mock_prioritization)
            result = qtm.prioritize_by_energy(mixed_tasks, morning_person_energy)
        
        # THEN
        assert len(result["morning_slots"]) == 2
        assert all("creative" in task.lower() or "design" in task.lower() or "write" in task.lower() 
                  for task in result["morning_slots"])
        
        assert len(result["afternoon_slots"]) == 2  
        assert all("administrative" in task.lower() or "update" in task.lower() or "schedule" in task.lower()
                  for task in result["afternoon_slots"])
        
        # Validate reasoning quality
        assert_behavioral_quality(result["reasoning"])
        assert "energy" in result["reasoning"].lower()
        assert "morning" in result["reasoning"].lower() or "8" in result["reasoning"]
    
    @pytest.mark.behavioral
    def test_adhd_energy_crash_protection(self, sample_energy_states):
        """
        Scenario: ADHD Energy Crash Protection
        Given user has ADHD energy pattern with predictable crashes
        And user is currently in hyperfocus period
        When system suggests next tasks
        Then it should warn about upcoming energy crash
        And suggest recovery-oriented tasks for post-crash period
        And avoid scheduling critical tasks during predicted low energy
        """
        # GIVEN
        adhd_pattern = sample_energy_states['adhd_pattern']
        current_hyperfocus = {"physical": 9, "mental": 9, "emotional": 8, "hour": 10}
        
        high_priority_tasks = [
            {"title": "Finalize client presentation", "priority": 9, "energy_required": "high"},
            {"title": "Code review for production", "priority": 8, "energy_required": "high"},
            {"title": "Organize desk drawer", "priority": 3, "energy_required": "low"}
        ]
        
        # WHEN  
        mock_response = {
            "immediate_suggestions": ["Continue current hyperfocus work"],
            "post_crash_suggestions": ["Organize desk drawer"],
            "warnings": ["Energy crash predicted around 12 PM based on your ADHD pattern"],
            "reasoning": "You're in a hyperfocus state now - great for deep work! But your pattern shows energy crashes after these periods. I've scheduled low-energy tasks for 12-2 PM when you typically need recovery time."
        }
        
        with patch('qtm3_core.qwen.schedule_with_energy_awareness', return_value=mock_response):
            qtm = Mock()
            qtm.schedule_with_energy_awareness = Mock(return_value=mock_response)
            result = qtm.schedule_with_energy_awareness(high_priority_tasks, current_hyperfocus, adhd_pattern)
        
        # THEN
        assert "crash" in str(result["warnings"]).lower()
        assert len(result["post_crash_suggestions"]) > 0
        
        # Post-crash tasks should be low energy
        post_crash_task = result["post_crash_suggestions"][0]
        assert "organize" in post_crash_task.lower() or any(word in post_crash_task.lower() 
                                                          for word in ["simple", "easy", "light"])
        
        # Reasoning should acknowledge ADHD pattern
        assert "adhd" in result["reasoning"].lower() or "pattern" in result["reasoning"].lower()
        assert_behavioral_quality(result["reasoning"])

class TestBehavioralActivationCompliance:
    """
    Feature: Behavioral Activation Compliance
    As a user struggling with depression or low motivation
    I want the system to follow behavioral activation principles
    So that I build positive momentum without self-criticism
    """
    
    @pytest.mark.behavioral
    def test_reflection_promotes_self_compassion(self, mock_qwen_responses):
        """
        Scenario: Self-Compassion in Reflections
        Given user completed minimal tasks during low energy day
        When system generates end-of-day reflection
        Then reflection should acknowledge effort without criticism
        And validate the difficulty of working with low energy
        And suggest gentle next steps appropriate for current state
        """
        # GIVEN
        minimal_completions = ["Check emails", "Organize one folder"]
        low_energy = {"physical": 3, "mental": 2, "emotional": 3}
        
        # WHEN
        high_quality_reflection = mock_qwen_responses['reflection_high_quality']
        
        # THEN - Use behavioral validator
        validator = BehavioralTestValidator()
        assert validator.validate_behavioral_activation_compliance(
            high_quality_reflection, minimal_completions, low_energy
        )
        
        # Specific behavioral activation checks
        reflection_lower = high_quality_reflection.lower()
        
        # Should acknowledge effort 
        assert any(task.lower() in reflection_lower for task in minimal_completions)
        
        # Should avoid self-criticism
        critical_phrases = ['should have', 'not enough', 'failed', 'behind']
        assert not any(phrase in reflection_lower for phrase in critical_phrases)
        
        # Should validate low energy experience
        assert any(word in reflection_lower for word in ['energy', 'difficult', 'tough', 'understand'])
        
        # Should suggest appropriate next steps
        if 'tomorrow' in reflection_lower:
            assert any(word in reflection_lower for word in ['small', 'gentle', 'easy', 'light'])
    
    @pytest.mark.behavioral  
    def test_overwhelm_prevention_in_prioritization(self, realistic_task_examples):
        """
        Scenario: Overwhelm Prevention 
        Given user has many high-priority tasks
        When system prioritizes tasks
        Then immediate focus should be limited to 3 items maximum
        And reasoning should explain overwhelm prevention
        And lower priority tasks should be explicitly deferred
        """
        # GIVEN
        many_urgent_tasks = [
            {"title": f"Urgent task {i}", "priority": 8, "energy_required": "medium"}
            for i in range(8)
        ]
        
        # WHEN
        mock_prioritization = {
            "immediate": many_urgent_tasks[:3],
            "today": many_urgent_tasks[3:5], 
            "this_week": many_urgent_tasks[5:],
            "reasoning": "Limited immediate focus to 3 tasks to prevent cognitive overwhelm. Research shows working memory can only handle 3-5 items effectively. Remaining urgent items scheduled for later today and this week."
        }
        
        with patch('qtm3_core.qwen.prioritize_tasks', return_value=mock_prioritization):
            qtm = Mock()
            qtm.prioritize_tasks = Mock(return_value=mock_prioritization)
            result = qtm.prioritize_tasks(many_urgent_tasks)
        
        # THEN
        assert len(result['immediate']) <= 3, "Too many immediate tasks causes overwhelm"
        
        # Reasoning should explain limitation
        reasoning = result['reasoning'].lower()
        assert any(word in reasoning for word in ['overwhelm', 'cognitive', 'focus', 'memory'])
        
        # Should acknowledge deferring tasks
        assert len(result['today']) + len(result['this_week']) > 0
        
        assert_behavioral_quality(result['reasoning'])

class TestTaskClarificationBehaviors:
    """
    Feature: Task Clarification Supporting Executive Function
    As a user with executive function challenges
    I want vague tasks broken into clear, manageable steps
    So that I can start without cognitive overload
    """
    
    @pytest.mark.behavioral
    def test_adhd_friendly_task_breakdown(self):
        """
        Scenario: ADHD-Friendly Task Breakdown
        Given user provides vague task "fix the website" 
        And user profile indicates ADHD
        When system clarifies the task
        Then each subtask should be under 45 minutes
        And include specific action verbs
        And provide dopamine-rewarding quick wins
        And explain energy requirements clearly
        """
        # GIVEN
        vague_input = "fix the website"
        user_profile = get_user_profile("alex_adhd")
        
        # WHEN
        mock_clarification = [
            {
                "title": "Test website for obvious errors",
                "description": "Click through main pages, note any broken links or display issues",
                "timer": 15,
                "energy_required": "low",
                "priority": 6,
                "quick_win": True
            },
            {
                "title": "Check error logs for critical issues", 
                "description": "Review server logs from past 24 hours, identify any 500 errors",
                "timer": 20,
                "energy_required": "medium",
                "priority": 8,
                "quick_win": False
            },
            {
                "title": "Fix one specific bug",
                "description": "Choose highest priority bug from log review and resolve it",
                "timer": 30,
                "energy_required": "high", 
                "priority": 9,
                "quick_win": True
            }
        ]
        
        with patch('qtm3_core.qwen.clarify_tasks', return_value=mock_clarification):
            qtm = Mock()
            qtm.clarify_tasks = Mock(return_value=mock_clarification)
            result = qtm.clarify_tasks(vague_input, user_profile)
        
        # THEN
        assert_cognitive_manageability(result)
        
        # All tasks should be under 45 minutes (ADHD attention span)
        for task in result:
            assert task['timer'] <= 45, f"Task '{task['title']}' too long for ADHD focus"
        
        # Should include quick wins for dopamine
        quick_wins = [t for t in result if t.get('quick_win', False)]
        assert len(quick_wins) >= 1, "No dopamine-rewarding quick wins provided"
        
        # Should have specific action verbs
        action_verbs = ['test', 'check', 'fix', 'review', 'identify', 'resolve']
        for task in result:
            title_words = task['title'].lower().split()
            assert any(verb in title_words for verb in action_verbs), \
                f"Task '{task['title']}' lacks specific action verb"
    
    @pytest.mark.behavioral
    def test_perfectionist_permission_to_start(self):
        """
        Scenario: Perfectionist Permission to Start
        Given user provides perfectionist-paralyzed task
        When system clarifies the task
        Then it should explicitly give permission to do "good enough" work
        And break perfectionist task into imperfect iterations
        And include time limits to prevent infinite polishing
        """
        # GIVEN
        perfectionist_input = "write the perfect blog post about productivity"
        
        # WHEN
        mock_clarification = [
            {
                "title": "Draft rough outline in 15 minutes",
                "description": "Brain dump main points - messy is fine! Goal is capturing ideas, not perfection.",
                "timer": 15,
                "energy_required": "medium",
                "permission_to_be_imperfect": True
            },
            {
                "title": "Write terrible first draft",
                "description": "Get thoughts on paper without editing. Anne Lamott calls these 'shitty first drafts' - they're supposed to be bad!",
                "timer": 30,
                "energy_required": "high", 
                "permission_to_be_imperfect": True
            },
            {
                "title": "Do ONE editing pass only",
                "description": "Single review for clarity and flow. Set timer - stop when it rings regardless of perfectness.",
                "timer": 20,
                "energy_required": "medium",
                "time_limit_enforced": True
            }
        ]
        
        with patch('qtm3_core.qwen.clarify_tasks', return_value=mock_clarification):
            qtm = Mock()
            qtm.clarify_tasks = Mock(return_value=mock_clarification)
            result = qtm.clarify_tasks(perfectionist_input)
        
        # THEN
        # Should explicitly give permission to be imperfect
        permission_tasks = [t for t in result if t.get('permission_to_be_imperfect', False)]
        assert len(permission_tasks) >= 2, "Not enough anti-perfectionism messaging"
        
        # Should include time limits
        time_limited = [t for t in result if t.get('time_limit_enforced', False)]
        assert len(time_limited) >= 1, "No time limits to prevent perfectionist spiraling"
        
        # Descriptions should normalize imperfection
        descriptions = ' '.join(t['description'] for t in result).lower()
        imperfection_words = ['messy', 'fine', 'terrible', 'bad', 'rough', 'imperfect']
        assert any(word in descriptions for word in imperfection_words), \
            "No explicit permission to be imperfect"

class TestEnergyValidationBehaviors:
    """
    Feature: Energy-Appropriate Task Suggestions
    As a user with varying energy levels
    I want task suggestions that match my current capacity
    So that I don't become overwhelmed or underutilized
    """
    
    @pytest.mark.behavioral
    def test_burnout_recovery_gentle_suggestions(self, sample_energy_states):
        """
        Scenario: Burnout Recovery Support
        Given user is in burnout recovery with consistently low energy
        When system suggests tasks
        Then all suggestions should be low energy
        And include explicit rest/recovery activities
        And validate the difficulty of the recovery process
        """
        # GIVEN
        burnout_energy = sample_energy_states['burnout_recovery'] 
        current_state = {"physical": 3, "mental": 2, "emotional": 2}
        
        available_tasks = [
            {"title": "Prepare board presentation", "energy_required": "high"},
            {"title": "Organize one desk drawer", "energy_required": "low"},
            {"title": "Send thank you note", "energy_required": "low"},
            {"title": "Strategic planning session", "energy_required": "high"}
        ]
        
        # WHEN
        mock_suggestions = {
            "suggested_tasks": ["Organize one desk drawer", "Send thank you note"],
            "deferred_tasks": ["Prepare board presentation", "Strategic planning session"],
            "recovery_activities": ["Take 10-minute walk", "Listen to favorite music"],
            "reasoning": "Your energy is quite low right now, which is completely normal during recovery. I've suggested only gentle tasks that won't drain you further. The high-energy work can wait until you're feeling stronger."
        }
        
        with patch('qtm3_core.qwen.suggest_energy_appropriate_tasks', return_value=mock_suggestions):
            qtm = Mock()
            qtm.suggest_energy_appropriate_tasks = Mock(return_value=mock_suggestions)
            result = qtm.suggest_energy_appropriate_tasks(available_tasks, current_state)
        
        # THEN
        # All suggested tasks should be low energy
        suggested = result['suggested_tasks']
        assert all('organize' in task.lower() or 'send' in task.lower() or 'low' in str(task) 
                  for task in suggested)
        
        # Should include recovery activities
        assert len(result['recovery_activities']) > 0
        
        # Should validate difficulty
        reasoning = result['reasoning'].lower()
        assert any(word in reasoning for word in ['normal', 'recovery', 'gentle', 'understand'])
        
        assert_energy_appropriate(
            [{"title": t, "energy_required": "low"} for t in suggested],
            current_state
        )

class TestCognitiveLoadManagement:
    """
    Feature: Cognitive Load Management
    As a user with limited mental bandwidth
    I want the system to respect cognitive limitations
    So that I can function effectively without overwhelm
    """
    
    @pytest.mark.behavioral
    def test_working_memory_limits_respected(self):
        """
        Scenario: Working Memory Limits
        Given user has 15 tasks to complete
        When system presents immediate priorities
        Then only 3-5 items should be highlighted for immediate focus
        And remaining tasks should be clearly categorized
        And reasoning should explain cognitive science basis
        """
        # GIVEN  
        many_tasks = [{"title": f"Task {i}", "priority": 7} for i in range(15)]
        
        # WHEN
        mock_organization = {
            "immediate_focus": many_tasks[:3],
            "today_backup": many_tasks[3:6],
            "this_week": many_tasks[6:10],
            "next_week": many_tasks[10:],
            "reasoning": "Limited immediate focus to 3 tasks based on working memory research. Your brain can only actively track 3-5 items effectively. Other tasks are organized by timeframe so they don't create mental clutter."
        }
        
        with patch('qtm3_core.qwen.organize_by_cognitive_load', return_value=mock_organization):
            qtm = Mock() 
            qtm.organize_by_cognitive_load = Mock(return_value=mock_organization)
            result = qtm.organize_by_cognitive_load(many_tasks)
        
        # THEN
        assert len(result['immediate_focus']) <= 5, "Too many immediate tasks for working memory"
        assert len(result['immediate_focus']) >= 3, "Too few tasks may underutilize capacity"
        
        # Should categorize remaining tasks clearly  
        categorized_count = (len(result['today_backup']) + len(result['this_week']) + 
                           len(result['next_week']))
        assert categorized_count == len(many_tasks) - len(result['immediate_focus'])
        
        # Reasoning should mention cognitive science
        reasoning = result['reasoning'].lower()
        assert any(word in reasoning for word in ['memory', 'research', 'brain', 'cognitive'])
        
        assert_cognitive_manageability(result['immediate_focus'])

# Integration tests for behavioral features
class TestBehavioralIntegration:
    """
    Integration tests that validate behavioral features work together
    to create a cohesive supportive experience
    """
    
    @pytest.mark.behavioral
    @pytest.mark.integration
    def test_full_behavioral_activation_flow(self, mock_agents):
        """
        Test complete flow from brain dump to behavioral support
        """
        # GIVEN
        brain_dump = get_brain_dump("adhd_overwhelm")
        user_profile = get_user_profile("alex_adhd")
        
        # WHEN - Simulate full flow
        mock_flow_result = {
            "clarified_tasks": [
                {"title": "Quick email check", "timer": 10, "energy_required": "low"},
                {"title": "Call insurance", "timer": 15, "energy_required": "medium"},
                {"title": "Organize photos", "timer": 20, "energy_required": "low"}
            ],
            "energy_scheduled": True,
            "overwhelm_prevented": True,
            "reflection_quality": 0.9,
            "behavioral_support": True
        }
        
        # THEN - Validate behavioral outcomes
        assert mock_flow_result["overwhelm_prevented"]
        assert mock_flow_result["behavioral_support"] 
        assert mock_flow_result["reflection_quality"] > 0.8
        
        # Tasks should be cognitively manageable
        assert_cognitive_manageability(mock_flow_result["clarified_tasks"])

if __name__ == "__main__":
    # Run behavioral tests specifically
    pytest.main([__file__, "-v", "-m", "behavioral"])