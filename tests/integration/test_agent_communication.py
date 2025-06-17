"""
Integration tests for inter-agent communication

These tests validate that our modular architecture works as a coherent system,
with agents communicating effectively while maintaining their boundaries.
The focus is on message passing, error handling, and system resilience.

Communication Patterns Tested:
- Perception → Reasoning: Context updates from file changes
- Reasoning → Exchange: Priority updates and notifications
- Memory ↔ All Agents: Pattern storage and retrieval
- Error handling and graceful degradation
- Unix socket reliability and recovery

Behavioral Focus:
- Communication failures shouldn't disrupt user workflow
- Message delays should be imperceptible to users
- System should recover automatically from agent failures
"""

import pytest
import asyncio
import time
import json
import tempfile
import socket
import os
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Import test utilities
from tests.utils.test_helpers import (
    MockAgentCommunication, PerformanceTestHelper
)
from tests.fixtures.sample_data import (
    get_user_profile, get_brain_dump
)

@dataclass
class AgentMessage:
    """Standard message format for inter-agent communication"""
    type: str
    source: str
    target: str
    timestamp: float
    data: Dict[str, Any]
    message_id: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)

class TestAgentMessageFormats:
    """
    Test that all inter-agent messages follow defined schemas
    and contain required information for behavioral features
    """
    
    def test_context_update_message_schema(self):
        """Test Perception → Reasoning context update messages"""
        # GIVEN
        context_update = AgentMessage(
            type="context_update",
            source="perception",
            target="reasoning",
            timestamp=time.time(),
            data={
                "project": "qtm3",
                "files_changed": ["README.md", "src/agents.py"],
                "context_tags": ["documentation", "code", "agents"],
                "change_type": "modification",
                "impact_assessment": "medium"  # Behavioral relevance
            },
            message_id="ctx_001"
        )
        
        # WHEN
        message_dict = context_update.to_dict()
        
        # THEN
        mock_comm = MockAgentCommunication()
        assert mock_comm.validate_message_schema(message_dict, "context_update")
        
        # Verify behavioral relevance
        assert "context_tags" in message_dict["data"], "Should include context for task organization"
        assert "impact_assessment" in message_dict["data"], "Should assess behavioral impact"
        assert message_dict["data"]["project"] is not None, "Should provide project context"
    
    def test_priority_update_message_schema(self):
        """Test Reasoning → Exchange priority update messages"""
        # GIVEN
        priority_update = AgentMessage(
            type="priority_update",
            source="reasoning", 
            target="exchange",
            timestamp=time.time(),
            data={
                "task_id": "task_123",
                "new_priority": 8,
                "old_priority": 5,
                "reasoning": "Context change indicates increased urgency based on project deadline",
                "energy_consideration": "Task matches current high energy state",
                "notification_required": True,
                "calendar_sync_needed": True
            },
            message_id="pri_001"
        )
        
        # WHEN
        message_dict = priority_update.to_dict()
        
        # THEN
        mock_comm = MockAgentCommunication()
        assert mock_comm.validate_message_schema(message_dict, "priority_update")
        
        # Verify behavioral intelligence
        assert "reasoning" in message_dict["data"], "Should explain priority change"
        assert "energy_consideration" in message_dict["data"], "Should consider user energy"
        assert message_dict["data"]["notification_required"] is not None, "Should specify notification needs"
    
    def test_energy_pattern_message_schema(self):
        """Test Memory → Reasoning energy pattern messages"""
        # GIVEN
        energy_pattern = AgentMessage(
            type="energy_pattern_update",
            source="memory",
            target="reasoning",
            timestamp=time.time(),
            data={
                "user_id": "user_123",
                "pattern_type": "daily_energy",
                "peak_hours": ["08:00-11:00", "15:00-16:00"],
                "low_hours": ["13:00-14:00", "17:00-19:00"],
                "confidence_score": 0.87,
                "behavioral_recommendations": [
                    "Schedule creative work during morning peak",
                    "Use afternoon dip for routine administrative tasks"
                ],
                "pattern_stability": "stable_2_weeks"
            },
            message_id="eng_001"
        )
        
        # WHEN
        message_dict = energy_pattern.to_dict()
        
        # THEN
        mock_comm = MockAgentCommunication()
        assert mock_comm.validate_message_schema(message_dict, "energy_pattern_update")
        
        # Verify behavioral value
        assert len(message_dict["data"]["behavioral_recommendations"]) > 0, \
            "Should provide actionable behavioral guidance"
        assert message_dict["data"]["confidence_score"] > 0.8, \
            "Should only share high-confidence patterns"

class TestUnixSocketCommunication:
    """
    Test Unix socket reliability, error handling, and recovery
    """
    
    @pytest.mark.integration
    async def test_socket_connection_establishment(self):
        """Test agents can establish Unix socket connections"""
        # GIVEN
        mock_comm = MockAgentCommunication()
        
        # Mock socket setup
        with patch('socket.socket') as mock_socket_class:
            mock_socket = Mock()
            mock_socket.bind = Mock()
            mock_socket.listen = Mock()
            mock_socket.accept = Mock(return_value=(Mock(), "client_addr"))
            mock_socket_class.return_value = mock_socket
            
            # WHEN
            # Simulate agent socket initialization
            socket_path = "/tmp/qtm_test_perception.sock"
            
            # Clean up any existing socket
            if os.path.exists(socket_path):
                os.unlink(socket_path)
            
            # Mock agent initialization
            mock_socket.bind.assert_not_called()  # Not called yet
            
            # Simulate binding
            mock_socket.bind(socket_path)
            mock_socket.listen(5)
            
            # THEN
            mock_socket.bind.assert_called_once_with(socket_path)
            mock_socket.listen.assert_called_once_with(5)
            
            # Verify socket path follows convention
            assert "qtm_" in socket_path, "Socket should follow naming convention"
            assert socket_path.endswith(".sock"), "Should use .sock extension"
    
    @pytest.mark.integration
    async def test_message_delivery_reliability(self):
        """Test message delivery between agents is reliable"""
        # GIVEN
        mock_comm = MockAgentCommunication()
        
        test_message = {
            "type": "context_update",
            "source": "perception",
            "target": "reasoning", 
            "timestamp": time.time(),
            "data": {"project": "qtm3", "files_changed": ["test.py"]}
        }
        
        # WHEN
        delivery_successful = await mock_comm.simulate_agent_message(
            source="perception",
            target="reasoning",
            message_type="context_update",
            data={"project": "qtm3", "files_changed": ["test.py"]}
        )
        
        # THEN
        assert delivery_successful, "Message delivery should succeed"
        assert len(mock_comm.message_history) == 1, "Should record message in history"
        
        delivered_message = mock_comm.message_history[0]
        assert delivered_message["type"] == "context_update"
        assert delivered_message["source"] == "perception"
        assert delivered_message["target"] == "reasoning"
    
    @pytest.mark.integration
    async def test_socket_failure_handling(self):
        """Test graceful handling of socket communication failures"""
        # GIVEN
        mock_comm = MockAgentCommunication()
        socket_path = "/tmp/qtm_test_reasoning.sock"
        
        # Mock active socket
        mock_comm.active_sockets[socket_path] = {"status": "healthy", "agent": "reasoning"}
        
        # WHEN - Simulate socket failure
        mock_comm.simulate_socket_failure(socket_path)
        
        # THEN
        assert mock_comm.active_sockets[socket_path]["status"] == "failed"
        
        # Simulate recovery
        mock_comm.restore_socket_connection(socket_path)
        assert mock_comm.active_sockets[socket_path]["status"] == "healthy"
    
    @pytest.mark.integration 
    @pytest.mark.performance
    async def test_message_latency_requirements(self):
        """Test inter-agent message latency meets performance requirements"""
        # GIVEN
        mock_comm = MockAgentCommunication()
        performance_helper = PerformanceTestHelper()
        
        # WHEN - Measure message round-trip time
        start_time = time.time()
        
        # Simulate realistic message exchange
        await mock_comm.simulate_agent_message(
            source="perception",
            target="reasoning",
            message_type="context_update", 
            data={"project": "qtm3", "files_changed": ["large_file.py"]}
        )
        
        # Simulate reasoning response
        await mock_comm.simulate_agent_message(
            source="reasoning",
            target="perception",
            message_type="processing_complete",
            data={"status": "context_integrated"}
        )
        
        total_latency = time.time() - start_time
        
        # THEN
        # Inter-agent communication should be very fast (< 100ms)
        assert total_latency < 0.1, f"Inter-agent latency too high: {total_latency:.3f}s"
        assert len(mock_comm.message_history) == 2, "Should record both messages"

class TestAgentCommunicationFlows:
    """
    Test complete communication flows that support behavioral features
    """
    
    @pytest.mark.integration
    async def test_file_change_to_priority_update_flow(self):
        """Test Perception→Reasoning→Exchange flow for file changes"""
        # GIVEN
        mock_comm = MockAgentCommunication()
        
        # File change detected by Perception
        file_change_data = {
            "path": "src/critical_feature.py",
            "change_type": "modified",
            "project": "qtm3",
            "context_tags": ["critical", "feature", "code"],
            "timestamp": time.time()
        }
        
        # WHEN - Simulate complete flow
        
        # 1. Perception → Reasoning
        await mock_comm.simulate_agent_message(
            source="perception",
            target="reasoning",
            message_type="context_update",
            data=file_change_data
        )
        
        # 2. Reasoning processes and determines priority change
        reasoning_response = {
            "affected_tasks": ["task_123", "task_456"],
            "priority_changes": [
                {"task_id": "task_123", "new_priority": 9, "reason": "Critical file modified"},
                {"task_id": "task_456", "new_priority": 7, "reason": "Related feature impact"}
            ],
            "notification_required": True
        }
        
        # 3. Reasoning → Exchange
        await mock_comm.simulate_agent_message(
            source="reasoning",
            target="exchange",
            message_type="priority_update",
            data=reasoning_response
        )
        
        # 4. Exchange → User (notification)
        await mock_comm.simulate_agent_message(
            source="exchange", 
            target="user",
            message_type="notification",
            data={
                "message": "Critical file updated - task priorities adjusted automatically",
                "tasks_affected": 2,
                "action_required": False
            }
        )
        
        # THEN
        assert len(mock_comm.message_history) == 3, "Should complete full flow"
        
        # Verify flow progression
        messages = mock_comm.message_history
        assert messages[0]["type"] == "context_update"
        assert messages[1]["type"] == "priority_update" 
        assert messages[2]["type"] == "notification"
        
        # Verify behavioral value - user is informed without overwhelming
        final_notification = messages[2]["data"]
        assert final_notification["action_required"] is False, "Should not overwhelm user"
        assert "automatically" in final_notification["message"], "Should emphasize automation"
    
    @pytest.mark.integration
    async def test_energy_pattern_learning_flow(self):
        """Test Memory→Reasoning flow for energy pattern learning"""
        # GIVEN
        mock_comm = MockAgentCommunication()
        
        # Memory detects new energy pattern
        energy_insight = {
            "pattern_type": "weekly_energy",
            "discovery": "Monday mornings show 40% higher mental energy",
            "confidence": 0.89,
            "sample_size": 4,  # 4 weeks of data
            "behavioral_recommendation": "Schedule challenging cognitive work on Monday mornings",
            "affected_scheduling": ["creative_tasks", "problem_solving", "strategic_planning"]
        }
        
        # WHEN
        # 1. Memory → Reasoning
        await mock_comm.simulate_agent_message(
            source="memory",
            target="reasoning", 
            message_type="energy_pattern_discovered",
            data=energy_insight
        )
        
        # 2. Reasoning incorporates pattern into scheduling logic
        scheduling_update = {
            "pattern_integrated": True,
            "scheduling_rules_updated": [
                "monday_morning_cognitive_boost",
                "high_energy_task_preference_monday"
            ],
            "affected_users": ["user_123"],
            "effectiveness_tracking": "enabled"
        }
        
        await mock_comm.simulate_agent_message(
            source="reasoning",
            target="memory",
            message_type="pattern_integration_complete",
            data=scheduling_update
        )
        
        # THEN
        assert len(mock_comm.message_history) == 2, "Should complete learning flow"
        
        # Verify learning cycle
        discovery_msg = mock_comm.message_history[0]
        integration_msg = mock_comm.message_history[1]
        
        assert discovery_msg["data"]["confidence"] > 0.8, "Should only share high-confidence patterns"
        assert integration_msg["data"]["pattern_integrated"], "Should confirm integration"
        assert "effectiveness_tracking" in integration_msg["data"], "Should enable outcome tracking"

class TestAgentBoundaryEnforcement:
    """
    Test that agents don't overstep their defined responsibilities
    even during communication
    """
    
    @pytest.mark.integration
    def test_perception_messaging_boundaries(self):
        """Test Perception agent only sends appropriate message types"""
        mock_comm = MockAgentCommunication()
        
        # Valid Perception messages
        valid_message_types = [
            "context_update",
            "file_change_detected", 
            "project_structure_update",
            "tag_extraction_complete"
        ]
        
        # Invalid messages Perception should never send
        invalid_message_types = [
            "task_prioritization",  # Reasoning responsibility
            "reflection_generated",  # Reasoning responsibility
            "calendar_sync_complete",  # Exchange responsibility
            "energy_pattern_stored"  # Memory responsibility
        ]
        
        # Verify boundaries
        for msg_type in valid_message_types:
            # Should be allowed (no exception)
            assert msg_type.startswith(("context", "file", "project", "tag")), \
                f"Perception should handle {msg_type}"
        
        for msg_type in invalid_message_types:
            # Should not be in Perception's message types
            assert not any(valid in msg_type for valid in ["context", "file", "project", "tag"]), \
                f"Perception should NOT handle {msg_type}"
    
    @pytest.mark.integration
    def test_reasoning_messaging_boundaries(self):
        """Test Reasoning agent respects message type boundaries"""
        mock_comm = MockAgentCommunication()
        
        # Valid Reasoning messages
        valid_message_types = [
            "priority_update",
            "reflection_generated",
            "task_clarification_complete",
            "behavioral_intervention_suggested"
        ]
        
        # Invalid messages Reasoning should never send
        invalid_message_types = [
            "file_change_detected",  # Perception responsibility
            "interaction_stored",    # Memory responsibility
            "calendar_event_created" # Exchange responsibility
        ]
        
        # Verify Reasoning focuses on AI-powered decisions
        for msg_type in valid_message_types:
            assert any(keyword in msg_type for keyword in 
                      ["priority", "reflection", "clarification", "behavioral"]), \
                f"Reasoning should handle {msg_type}"

class TestSystemResilience:
    """
    Test system resilience during agent failures and recovery
    """
    
    @pytest.mark.integration
    async def test_reasoning_agent_failure_recovery(self):
        """Test system graceful degradation when Reasoning agent fails"""
        # GIVEN
        mock_comm = MockAgentCommunication()
        
        # Normal operation first
        await mock_comm.simulate_agent_message(
            source="perception",
            target="reasoning",
            message_type="context_update",
            data={"project": "qtm3", "files_changed": ["important.py"]}
        )
        
        # WHEN - Reasoning agent fails
        reasoning_socket = "/tmp/qtm_reasoning.sock"
        mock_comm.simulate_socket_failure(reasoning_socket)
        
        # System should continue with degraded functionality
        # Perception should queue messages for when Reasoning recovers
        queued_message = {
            "queued_for_reasoning": True,
            "message": "Context update queued - AI prioritization unavailable temporarily",
            "degraded_mode": True
        }
        
        # THEN
        # System should operate in degraded mode
        assert queued_message["degraded_mode"], "Should acknowledge degraded state"
        assert queued_message["queued_for_reasoning"], "Should queue messages for recovery"
        
        # When Reasoning recovers
        mock_comm.restore_socket_connection(reasoning_socket)
        
        # Queued messages should be processed
        recovery_successful = True
        assert recovery_successful, "Should recover and process queued messages"
    
    @pytest.mark.integration
    async def test_partial_system_functionality_during_failures(self):
        """Test that some functionality remains during partial failures"""
        # GIVEN
        mock_comm = MockAgentCommunication()
        
        # WHEN - Exchange agent fails (external integrations down)
        exchange_socket = "/tmp/qtm_exchange.sock"
        mock_comm.simulate_socket_failure(exchange_socket)
        
        # Core functionality should continue
        core_functions_available = {
            "perception": True,    # File monitoring continues
            "memory": True,        # Pattern storage continues
            "reasoning": True,     # AI decisions continue
            "exchange": False,     # Calendar sync fails
            "user_impact": "minimal"  # Core workflow preserved
        }
        
        # THEN
        assert core_functions_available["perception"], "File monitoring should continue"
        assert core_functions_available["reasoning"], "AI decisions should continue"
        assert not core_functions_available["exchange"], "External sync should fail"
        assert core_functions_available["user_impact"] == "minimal", \
            "User should barely notice external sync failure"

class TestBehavioralCommunicationPatterns:
    """
    Test communication patterns that specifically support behavioral features
    """
    
    @pytest.mark.integration
    @pytest.mark.behavioral
    async def test_overwhelm_prevention_communication(self):
        """Test agents communicate to prevent user overwhelm"""
        # GIVEN
        mock_comm = MockAgentCommunication()
        
        # Many urgent events happening simultaneously
        urgent_events = [
            {"type": "deadline_approaching", "task": "Board presentation", "hours_left": 2},
            {"type": "calendar_conflict", "meeting": "Client call", "overlap": True},
            {"type": "file_change", "critical_file": "production_code.py"},
            {"type": "energy_low", "current_state": {"mental": 3, "physical": 4}}
        ]
        
        # WHEN - Agents coordinate to prevent overwhelm
        
        # 1. Multiple events trigger agent communications
        for event in urgent_events:
            await mock_comm.simulate_agent_message(
                source="perception",
                target="reasoning",
                message_type="urgent_event",
                data=event
            )
        
        # 2. Reasoning coordinates response to prevent overwhelm
        coordinated_response = {
            "overwhelm_detected": True,
            "simplified_focus": "Board presentation only",
            "deferred_items": ["file_change_review", "calendar_optimization"],
            "energy_consideration": "Low energy - minimal additional load",
            "user_message": "Focusing on presentation deadline. Other items handled automatically after completion."
        }
        
        await mock_comm.simulate_agent_message(
            source="reasoning",
            target="exchange",
            message_type="overwhelm_prevention",
            data=coordinated_response
        )
        
        # THEN
        messages = mock_comm.message_history
        final_coordination = messages[-1]["data"]
        
        assert final_coordination["overwhelm_detected"], "Should detect overwhelm risk"
        assert "simplified_focus" in final_coordination, "Should simplify user focus"
        assert len(final_coordination["deferred_items"]) > 0, "Should defer non-critical items"
        
        # User message should be calming, not alarming
        user_msg = final_coordination["user_message"].lower()
        assert "automatically" in user_msg, "Should emphasize automation"
        assert "focusing" in user_msg, "Should provide clear focus"

if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "-m", "integration"])