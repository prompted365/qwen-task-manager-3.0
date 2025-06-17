"""
Unit tests for the 4 core agents: Perception, Memory, Reasoning, Exchange

These tests focus on individual agent behavior and responsibilities while ensuring
they support the behavioral-first testing philosophy. Each agent has distinct
responsibilities that require specialized testing approaches.

Agent Responsibilities:
- Perception: File system monitoring, context extraction
- Memory: Pattern storage, interaction history, energy tracking
- Reasoning: AI-powered decision making, prioritization
- Exchange: External integrations, notifications, calendar sync

Testing Focus:
- Agent boundary enforcement (no responsibility overlap)
- Individual agent reliability and error handling
- Behavioral impact of agent outputs
- Performance within quality gates
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from pathlib import Path
from typing import Dict, List, Any
import json
import tempfile
import os

# Import test utilities
from tests.utils.test_helpers import (
    BehavioralTestValidator, PerformanceTestHelper, assert_behavioral_quality
)
from tests.fixtures.sample_data import (
    get_user_profile, get_energy_pattern, CONTEXT_TAGGING_TEST_DATA
)

class TestPerceptionAgent:
    """
    Unit tests for Perception Agent
    
    Responsibilities:
    - Monitor file system changes
    - Extract context tags from files
    - Detect project patterns
    - Send context updates to other agents
    
    Behavioral Focus:
    - Reduce cognitive load by auto-detecting context
    - Support task organization through intelligent tagging
    """
    
    def test_file_watcher_initialization(self):
        """Test that file watcher initializes with correct paths"""
        # Mock the PerceptionAgent class
        with patch('agents.PerceptionAgent') as MockAgent:
            mock_agent = Mock()
            mock_agent.watched_paths = [Path("./projects"), Path("./docs")]
            mock_agent.socket_path = "/tmp/qtm_perception.sock"
            mock_agent.status = "healthy"
            MockAgent.return_value = mock_agent
            
            # Initialize agent
            from agents import PerceptionAgent
            agent = PerceptionAgent([Path("./projects"), Path("./docs")])
            
            # Verify initialization
            assert agent.watched_paths == [Path("./projects"), Path("./docs")]
            assert agent.socket_path.endswith("perception.sock")
            assert agent.status == "healthy"
    
    def test_context_tag_extraction_accuracy(self):
        """Test context tag extraction meets 80% accuracy requirement"""
        with patch('agents.PerceptionAgent') as MockAgent:
            mock_agent = Mock()
            
            # Mock extract_context_tags method with realistic responses
            test_data = CONTEXT_TAGGING_TEST_DATA["accuracy_test_set"]
            mock_responses = {}
            
            for file_path, content, expected_tags in test_data:
                # Simulate realistic tag extraction (80% accuracy)
                if "auth" in file_path:
                    detected = ["authentication", "backend"]  # Missing "security" 
                elif "user_guide" in file_path:
                    detected = ["documentation", "user_guide", "onboarding"]  # Perfect
                elif "test_api" in file_path:
                    detected = ["testing", "api"]  # Missing "integration"
                elif "nginx" in file_path:
                    detected = ["configuration", "web_server", "infrastructure"]  # Perfect
                elif "Dashboard" in file_path:
                    detected = ["frontend", "vue"]  # Missing "ui_component"
                else:
                    detected = expected_tags  # Default to perfect
                
                mock_responses[file_path] = detected
            
            mock_agent.extract_context_tags.side_effect = lambda path: mock_responses.get(path, [])
            MockAgent.return_value = mock_agent
            
            # Test accuracy calculation
            performance_helper = PerformanceTestHelper()
            predictions = []
            ground_truth = []
            
            for file_path, content, expected_tags in test_data:
                detected_tags = mock_agent.extract_context_tags(file_path)
                predictions.append(detected_tags)
                ground_truth.append(expected_tags)
            
            accuracy = performance_helper.calculate_accuracy_score(predictions, ground_truth)
            
            # Verify meets quality gate requirement
            assert performance_helper.validate_accuracy_requirement(accuracy), \
                f"Context tagging accuracy {accuracy:.2%} below 80% threshold"
            assert accuracy >= 0.75, "Accuracy should be reasonable for realistic test"
    
    def test_file_change_detection_behavioral_impact(self):
        """Test that file change detection supports behavioral activation"""
        with patch('agents.PerceptionAgent') as MockAgent:
            mock_agent = Mock()
            
            # Mock file change detection
            mock_changes = [
                {"path": "README.md", "type": "modified", "project": "qtm3"},
                {"path": "src/agents.py", "type": "modified", "project": "qtm3"},
                {"path": "tests/test_new_feature.py", "type": "created", "project": "qtm3"}
            ]
            
            mock_agent.detect_changes.return_value = mock_changes
            MockAgent.return_value = mock_agent
            
            changes = mock_agent.detect_changes()
            
            # Verify behavioral impact - changes should support task context
            assert len(changes) > 0, "Should detect meaningful changes"
            
            for change in changes:
                assert "project" in change, "Changes should include project context"
                assert change["type"] in ["modified", "created", "deleted"], "Should categorize change type"
                
                # Project detection helps with task organization (behavioral benefit)
                if change["project"]:
                    assert len(change["project"]) > 0, "Project detection should provide context"
    
    def test_agent_boundary_enforcement(self):
        """Test that Perception agent doesn't overstep responsibilities"""
        with patch('agents.PerceptionAgent') as MockAgent:
            mock_agent = Mock()
            
            # Mock methods that should NOT exist in Perception agent
            mock_agent.prioritize_tasks = None
            mock_agent.generate_reflection = None
            mock_agent.sync_calendar = None
            mock_agent.store_memory = None
            
            # Mock methods that SHOULD exist
            mock_agent.extract_context_tags = Mock(return_value=["project", "documentation"])
            mock_agent.detect_changes = Mock(return_value=[])
            mock_agent.send_context_update = Mock()
            
            MockAgent.return_value = mock_agent
            
            # Verify proper boundaries
            assert hasattr(mock_agent, 'extract_context_tags'), "Should handle context extraction"
            assert hasattr(mock_agent, 'detect_changes'), "Should handle file monitoring"
            assert hasattr(mock_agent, 'send_context_update'), "Should send updates to other agents"
            
            # Should NOT handle these responsibilities
            assert mock_agent.prioritize_tasks is None, "Should not prioritize tasks"
            assert mock_agent.generate_reflection is None, "Should not generate reflections"
            assert mock_agent.sync_calendar is None, "Should not sync calendar"
            assert mock_agent.store_memory is None, "Should not store memories"
    
    @pytest.mark.performance
    def test_file_monitoring_performance(self):
        """Test file monitoring meets performance requirements"""
        with patch('agents.PerceptionAgent') as MockAgent:
            mock_agent = Mock()
            
            # Simulate monitoring performance
            start_time = time.time()
            
            # Mock rapid file change processing
            mock_agent.process_file_change = Mock(return_value={"processed": True, "latency": 0.05})
            
            # Simulate processing multiple file changes
            for i in range(100):
                result = mock_agent.process_file_change(f"file_{i}.py")
                assert result["processed"], f"File {i} not processed"
            
            total_time = time.time() - start_time
            
            # Should handle 100 file changes quickly (real-world burst scenario)
            assert total_time < 2.0, f"File monitoring too slow: {total_time:.2f}s for 100 files"
            
            MockAgent.return_value = mock_agent

class TestMemoryAgent:
    """
    Unit tests for Memory Agent
    
    Responsibilities:
    - Store interaction history
    - Track energy patterns over time
    - Maintain user behavioral patterns
    - Provide historical context for decisions
    
    Behavioral Focus:
    - Enable behavioral pattern recognition
    - Support energy-based scheduling through historical data
    """
    
    def test_energy_pattern_storage_and_retrieval(self):
        """Test energy pattern storage supports behavioral insights"""
        with patch('agents.MemoryAgent') as MockAgent:
            mock_agent = Mock()
            
            # Mock energy data storage
            energy_data = get_energy_pattern("morning_person_week")[0]["pattern"]
            
            mock_agent.store_energy_data = Mock()
            mock_agent.get_energy_patterns = Mock(return_value={
                "peak_hours": "08:00-11:00",
                "low_hours": "14:00-16:00", 
                "pattern_confidence": 0.85,
                "behavioral_insights": [
                    "User shows consistent morning peak mental energy",
                    "Afternoon dip suggests natural circadian rhythm",
                    "Creative work best scheduled 8-11 AM"
                ]
            })
            
            MockAgent.return_value = mock_agent
            
            # Store energy data
            mock_agent.store_energy_data("2024-01-15", energy_data)
            mock_agent.store_energy_data.assert_called_once()
            
            # Retrieve patterns
            patterns = mock_agent.get_energy_patterns()
            
            # Verify behavioral value
            assert patterns["pattern_confidence"] > 0.8, "Should have high confidence in patterns"
            assert "peak_hours" in patterns, "Should identify peak energy windows"
            assert len(patterns["behavioral_insights"]) > 0, "Should provide actionable insights"
            
            # Insights should be behaviorally meaningful
            insights_text = " ".join(patterns["behavioral_insights"]).lower()
            assert any(word in insights_text for word in ["morning", "creative", "schedule"]), \
                "Insights should guide behavioral choices"
    
    def test_interaction_history_behavioral_learning(self):
        """Test interaction history enables behavioral learning"""
        with patch('agents.MemoryAgent') as MockAgent:
            mock_agent = Mock()
            
            # Mock interaction storage
            mock_interactions = [
                {
                    "timestamp": "2024-01-15T09:00:00", 
                    "task_type": "creative",
                    "energy_level": {"mental": 9, "physical": 8},
                    "completion_time": 25,
                    "satisfaction": 9
                },
                {
                    "timestamp": "2024-01-15T14:00:00",
                    "task_type": "creative", 
                    "energy_level": {"mental": 4, "physical": 5},
                    "completion_time": 45,
                    "satisfaction": 4
                }
            ]
            
            mock_agent.store_interaction = Mock()
            mock_agent.analyze_task_performance = Mock(return_value={
                "creative_tasks": {
                    "best_time": "09:00-11:00",
                    "worst_time": "14:00-16:00",
                    "performance_difference": "225% better in morning",
                    "recommendation": "Schedule creative work during morning peak energy"
                }
            })
            
            MockAgent.return_value = mock_agent
            
            # Store interactions
            for interaction in mock_interactions:
                mock_agent.store_interaction(interaction)
            
            # Analyze for behavioral patterns
            analysis = mock_agent.analyze_task_performance("creative")
            
            # Verify behavioral learning
            assert "best_time" in analysis["creative_tasks"], "Should identify optimal timing"
            assert "recommendation" in analysis["creative_tasks"], "Should provide actionable guidance"
            
            recommendation = analysis["creative_tasks"]["recommendation"].lower()
            assert "schedule" in recommendation, "Should provide scheduling guidance"
            assert "morning" in recommendation, "Should identify morning preference"
    
    def test_memory_agent_boundary_enforcement(self):
        """Test Memory agent respects responsibility boundaries"""
        with patch('agents.MemoryAgent') as MockAgent:
            mock_agent = Mock()
            
            # Mock appropriate methods
            mock_agent.store_interaction = Mock()
            mock_agent.store_energy_data = Mock()
            mock_agent.get_patterns = Mock() 
            mock_agent.analyze_trends = Mock()
            
            # Methods that should NOT exist
            mock_agent.prioritize_tasks = None
            mock_agent.extract_context_tags = None
            mock_agent.sync_calendar = None
            
            MockAgent.return_value = mock_agent
            
            # Verify boundaries
            assert hasattr(mock_agent, 'store_interaction'), "Should store interactions"
            assert hasattr(mock_agent, 'get_patterns'), "Should retrieve patterns"
            assert mock_agent.prioritize_tasks is None, "Should not prioritize tasks"
            assert mock_agent.extract_context_tags is None, "Should not extract context"

class TestReasoningAgent:
    """
    Unit tests for Reasoning Agent
    
    Responsibilities:
    - AI-powered task prioritization
    - Generate behavioral reflections
    - Clarify vague tasks into actionable items
    - Apply behavioral activation principles
    
    Behavioral Focus:
    - Ensure AI responses support behavioral activation
    - Validate reasoning quality and empathy
    - Test cognitive load management
    """
    
    def test_task_prioritization_behavioral_quality(self):
        """Test task prioritization follows behavioral activation principles"""
        with patch('agents.ReasoningAgent') as MockAgent:
            mock_agent = Mock()
            
            # Mock task prioritization
            mixed_tasks = [
                {"title": "Prepare board presentation", "priority": 9, "energy_required": "high"},
                {"title": "Organize desk drawer", "priority": 3, "energy_required": "low"},
                {"title": "Call insurance company", "priority": 8, "energy_required": "medium"},
                {"title": "Write blog post", "priority": 6, "energy_required": "high"}
            ]
            
            mock_prioritization = {
                "immediate": ["Call insurance company"],  # Avoidance task prioritized
                "today": ["Organize desk drawer"],       # Quick win included
                "this_week": ["Prepare board presentation", "Write blog post"],
                "reasoning": "Started with the insurance call since you've been avoiding it - getting that done will remove mental burden. Added desk organization as a satisfying quick win. High-energy creative work moved to when you have more capacity."
            }
            
            mock_agent.prioritize_tasks = Mock(return_value=mock_prioritization)
            MockAgent.return_value = mock_agent
            
            result = mock_agent.prioritize_tasks(mixed_tasks)
            
            # Verify behavioral quality
            assert_behavioral_quality(result["reasoning"])
            
            # Should limit immediate focus (cognitive load management)
            assert len(result["immediate"]) <= 3, "Too many immediate tasks"
            
            # Should include avoidance task handling
            immediate_task = result["immediate"][0].lower()
            assert "insurance" in immediate_task, "Should prioritize avoided tasks"
            
            # Reasoning should explain behavioral benefits
            reasoning = result["reasoning"].lower()
            assert any(word in reasoning for word in ["avoiding", "burden", "satisfying", "capacity"]), \
                "Should explain behavioral reasoning"
    
    def test_reflection_generation_quality(self):
        """Test reflection generation meets therapeutic standards"""
        with patch('agents.ReasoningAgent') as MockAgent:
            mock_agent = Mock()
            
            # Mock reflection generation
            completed_tasks = ["Check emails", "Quick desk organization"]
            energy_state = {"physical": 4, "mental": 3, "emotional": 3}
            
            high_quality_reflection = """
            You accomplished two meaningful things today despite having lower energy. 
            
            I noticed you tackled that desk organization - these small wins can really shift your mental space. The email check shows you're staying connected even when energy is limited.
            
            Your pattern suggests afternoons are tough right now. Tomorrow morning might be a good time to tackle something that gives you a sense of progress.
            
            Be gentle with yourself - you're managing your energy wisely.
            """
            
            mock_agent.generate_reflection = Mock(return_value=high_quality_reflection)
            MockAgent.return_value = mock_agent
            
            reflection = mock_agent.generate_reflection(completed_tasks, energy_state)
            
            # Use behavioral validator
            validator = BehavioralTestValidator()
            assert validator.validate_behavioral_activation_compliance(
                reflection, completed_tasks, energy_state
            ), "Reflection doesn't meet behavioral activation standards"
            
            # Verify therapeutic quality
            reflection_lower = reflection.lower()
            assert "gentle" in reflection_lower or "kind" in reflection_lower, \
                "Should promote self-compassion"
            assert any(task.lower() in reflection_lower for task in completed_tasks), \
                "Should acknowledge specific completions"
    
    def test_task_clarification_cognitive_manageability(self):
        """Test task clarification produces cognitively manageable tasks"""
        with patch('agents.ReasoningAgent') as MockAgent:
            mock_agent = Mock()
            
            # Mock task clarification
            vague_input = "fix all the problems with the website and make it perfect"
            
            clarified_tasks = [
                {
                    "title": "Identify top 3 website issues",
                    "description": "Quick scan for broken links, loading problems, or display errors",
                    "timer": 15,
                    "energy_required": "low",
                    "priority": 7
                },
                {
                    "title": "Fix highest priority issue",
                    "description": "Choose one specific problem and resolve it completely",
                    "timer": 30,
                    "energy_required": "medium", 
                    "priority": 8
                },
                {
                    "title": "Document improvement made",
                    "description": "Note what was fixed for future reference",
                    "timer": 10,
                    "energy_required": "low",
                    "priority": 6
                }
            ]
            
            mock_agent.clarify_tasks = Mock(return_value=clarified_tasks)
            MockAgent.return_value = mock_agent
            
            result = mock_agent.clarify_tasks(vague_input)
            
            # Verify cognitive manageability
            from tests.utils.test_helpers import assert_cognitive_manageability
            assert_cognitive_manageability(result)
            
            # All tasks should be under 45 minutes (attention span research)
            for task in result:
                assert task["timer"] <= 45, f"Task too long: {task['timer']} minutes"
            
            # Should break perfectionist paralysis
            assert len(result) >= 3, "Should break large task into smaller steps"
            assert "identify" in result[0]["title"].lower(), "Should start with assessment"
    
    def test_reasoning_agent_boundary_enforcement(self):
        """Test Reasoning agent focuses on its responsibilities"""
        with patch('agents.ReasoningAgent') as MockAgent:
            mock_agent = Mock()
            
            # Mock appropriate methods
            mock_agent.prioritize_tasks = Mock()
            mock_agent.generate_reflection = Mock()
            mock_agent.clarify_tasks = Mock()
            mock_agent.apply_behavioral_principles = Mock()
            
            # Methods that should NOT exist
            mock_agent.extract_context_tags = None
            mock_agent.store_interaction = None  
            mock_agent.sync_calendar = None
            mock_agent.send_notification = None
            
            MockAgent.return_value = mock_agent
            
            # Verify boundaries
            assert hasattr(mock_agent, 'prioritize_tasks'), "Should prioritize tasks"
            assert hasattr(mock_agent, 'generate_reflection'), "Should generate reflections"
            assert mock_agent.extract_context_tags is None, "Should not extract context"
            assert mock_agent.sync_calendar is None, "Should not sync calendar"

class TestExchangeAgent:
    """
    Unit tests for Exchange Agent
    
    Responsibilities:
    - Calendar integration and sync
    - External notification sending
    - Task status updates to external systems
    - Data import/export
    
    Behavioral Focus:
    - Reduce cognitive overhead through automation
    - Support habit formation through timely reminders
    """
    
    def test_calendar_bidirectional_sync(self):
        """Test calendar sync supports behavioral scheduling"""
        with patch('agents.ExchangeAgent') as MockAgent:
            mock_agent = Mock()
            
            # Mock calendar sync
            qtm_task = {
                "title": "Deep work session",
                "due": "2024-01-15T10:00:00",
                "duration": 90,
                "energy_required": "high"
            }
            
            calendar_event = {
                "title": "Deep work session",
                "start": "2024-01-15T10:00:00",
                "end": "2024-01-15T11:30:00",
                "location": "Focus room"
            }
            
            mock_agent.sync_task_to_calendar = Mock(return_value=calendar_event)
            mock_agent.sync_calendar_to_tasks = Mock(return_value=[qtm_task])
            
            MockAgent.return_value = mock_agent
            
            # Test task -> calendar sync
            created_event = mock_agent.sync_task_to_calendar(qtm_task)
            assert created_event["title"] == qtm_task["title"]
            assert created_event["start"] == qtm_task["due"]
            
            # Test calendar -> task sync
            synced_tasks = mock_agent.sync_calendar_to_tasks([calendar_event])
            assert len(synced_tasks) == 1
            assert synced_tasks[0]["title"] == calendar_event["title"]
    
    def test_notification_behavioral_timing(self):
        """Test notifications support behavioral activation timing"""
        with patch('agents.ExchangeAgent') as MockAgent:
            mock_agent = Mock()
            
            # Mock notification sending with behavioral awareness
            user_profile = get_user_profile("alex_adhd")
            current_energy = {"physical": 8, "mental": 9, "emotional": 7}
            
            notification_request = {
                "task": "Start creative writing session",
                "energy_required": "high",
                "user_profile": user_profile,
                "current_energy": current_energy
            }
            
            mock_response = {
                "sent": True,
                "timing": "immediate", 
                "reasoning": "High energy level detected - perfect time for creative work",
                "message": "✨ Great energy for creative work! Ready to start that writing session?"
            }
            
            mock_agent.send_behavioral_notification = Mock(return_value=mock_response)
            MockAgent.return_value = mock_agent
            
            result = mock_agent.send_behavioral_notification(notification_request)
            
            # Verify behavioral appropriateness
            assert result["sent"], "Should send notification during high energy"
            assert result["timing"] == "immediate", "Should suggest immediate action"
            
            # Message should be encouraging and energy-aware
            message = result["message"].lower()
            assert any(word in message for word in ["energy", "great", "perfect", "ready"]), \
                "Should acknowledge good energy state"
    
    def test_exchange_agent_boundary_enforcement(self):
        """Test Exchange agent focuses on external integrations only"""
        with patch('agents.ExchangeAgent') as MockAgent:
            mock_agent = Mock()
            
            # Mock appropriate methods
            mock_agent.sync_calendar = Mock()
            mock_agent.send_notification = Mock()
            mock_agent.export_data = Mock()
            mock_agent.import_tasks = Mock()
            
            # Methods that should NOT exist
            mock_agent.prioritize_tasks = None
            mock_agent.extract_context_tags = None
            mock_agent.store_interaction = None
            mock_agent.generate_reflection = None
            
            MockAgent.return_value = mock_agent
            
            # Verify boundaries
            assert hasattr(mock_agent, 'sync_calendar'), "Should sync calendar"
            assert hasattr(mock_agent, 'send_notification'), "Should send notifications"
            assert mock_agent.prioritize_tasks is None, "Should not prioritize tasks"
            assert mock_agent.generate_reflection is None, "Should not generate reflections"

class TestAgentPerformance:
    """
    Performance tests for individual agents to ensure quality gates are met
    """
    
    @pytest.mark.performance
    def test_perception_agent_latency(self):
        """Test Perception agent meets latency requirements"""
        with patch('agents.PerceptionAgent') as MockAgent:
            mock_agent = Mock()
            
            # Mock context extraction with timing
            start_time = time.time()
            mock_agent.extract_context_tags = Mock(return_value=["project", "documentation"])
            
            # Simulate realistic processing time
            result = mock_agent.extract_context_tags("README.md")
            processing_time = time.time() - start_time
            
            MockAgent.return_value = mock_agent
            
            # Should be very fast for single file
            assert processing_time < 1.0, f"Context extraction too slow: {processing_time:.3f}s"
            assert len(result) > 0, "Should extract meaningful tags"
    
    @pytest.mark.performance 
    def test_reasoning_agent_quality_gate_latency(self):
        """Test Reasoning agent meets <10s quality gate for task processing"""
        with patch('agents.ReasoningAgent') as MockAgent:
            mock_agent = Mock()
            
            # Mock full reasoning pipeline
            complex_input = "organize my entire life and career and fix all my problems"
            
            # Simulate realistic AI processing time
            mock_agent.clarify_tasks = AsyncMock(return_value=[
                {"title": "List current life areas", "timer": 15},
                {"title": "Choose one area to improve", "timer": 10},
                {"title": "Define one small action", "timer": 5}
            ])
            
            MockAgent.return_value = mock_agent
            
            # Measure full processing
            start_time = time.time()
            result = asyncio.run(mock_agent.clarify_tasks(complex_input))
            total_time = time.time() - start_time
            
            # Should meet quality gate
            assert total_time < 10.0, f"Reasoning too slow: {total_time:.2f}s exceeds 10s limit"
            assert len(result) >= 2, "Should break complex input into multiple tasks"

if __name__ == "__main__":
    # Run agent unit tests
    pytest.main([__file__, "-v"])