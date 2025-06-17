"""
Pytest configuration for Qwen Task Manager 3.0

This configuration supports behavioral-first testing that validates human psychology
alongside code execution. We test whether our system genuinely helps users with
executive function and behavioral activation, not just technical functionality.

Key Testing Philosophy:
- Behavioral-First: Every test considers the human element
- AI-Aware: Validates reasoning quality over exact output matching
- Agent-Centric: Specialized testing for each agent's responsibilities
- Continuous Behavioral Validation: Psychological outcomes evolve over time
"""

import pytest
import asyncio
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import json

# Import core modules (these will be implemented)
# from qtm3_core import TaskManagerCore
# from agents import PerceptionAgent, MemoryAgent, ReasoningAgent, ExchangeAgent

@dataclass
class EnergyState:
    """Represents user energy levels for behavioral testing"""
    physical: int  # 1-10 scale
    mental: int    # 1-10 scale  
    emotional: int # 1-10 scale
    timestamp: str
    
    def is_high_energy(self) -> bool:
        return (self.physical + self.mental + self.emotional) / 3 >= 7
    
    def is_low_energy(self) -> bool:
        return (self.physical + self.mental + self.emotional) / 3 <= 4

@dataclass
class QualityScore:
    """Assessment framework for AI response quality"""
    compassion: bool = False
    encouragement: bool = False
    criticism_avoidance: bool = False
    specific_acknowledgment: bool = False
    pattern_recognition: bool = False
    forward_focus: bool = False
    
    @property
    def overall_score(self) -> float:
        """Calculate overall quality score (0-10 scale)"""
        attributes = [
            self.compassion, self.encouragement, self.criticism_avoidance,
            self.specific_acknowledgment, self.pattern_recognition, self.forward_focus
        ]
        return (sum(attributes) / len(attributes)) * 10

@dataclass
class TaskExample:
    """Realistic task examples for behavioral testing"""
    title: str
    description: str
    energy_required: str  # 'low', 'medium', 'high'
    timer: int  # minutes
    priority: int  # 1-10
    context_tags: List[str]
    completion_probability: float  # 0-1 based on behavioral research

# Behavioral Testing Fixtures
@pytest.fixture
def sample_energy_states():
    """Realistic energy patterns for testing behavioral activation"""
    return {
        'morning_person': [
            EnergyState(8, 9, 7, "08:00"),
            EnergyState(7, 8, 6, "10:00"),
            EnergyState(5, 6, 5, "14:00"),
            EnergyState(4, 5, 4, "18:00")
        ],
        'night_owl': [
            EnergyState(3, 4, 4, "08:00"),
            EnergyState(5, 6, 5, "10:00"),
            EnergyState(7, 8, 7, "14:00"),
            EnergyState(8, 9, 8, "20:00")
        ],
        'adhd_pattern': [
            EnergyState(2, 3, 3, "08:00"),
            EnergyState(8, 9, 6, "10:00"),  # Hyperfocus period
            EnergyState(3, 2, 4, "12:00"),  # Crash
            EnergyState(6, 7, 5, "15:00")   # Recovery
        ],
        'burnout_recovery': [
            EnergyState(3, 2, 2, "08:00"),
            EnergyState(4, 3, 3, "10:00"),
            EnergyState(3, 3, 4, "14:00"),
            EnergyState(2, 2, 3, "18:00")
        ]
    }

@pytest.fixture
def realistic_task_examples():
    """Task examples based on actual user scenarios"""
    return [
        TaskExample(
            "Update project documentation",
            "Review and update README with recent changes",
            "medium", 25, 6, ["documentation", "project"],
            0.7
        ),
        TaskExample(
            "Call insurance about claim",
            "Follow up on pending claim #12345, get status update",
            "low", 15, 8, ["admin", "phone"],
            0.4  # High avoidance factor
        ),
        TaskExample(
            "Design new feature wireframes", 
            "Create wireframes for user dashboard improvements",
            "high", 45, 5, ["design", "creative"],
            0.8
        ),
        TaskExample(
            "Organize digital photos",
            "Sort and tag photos from last vacation",
            "low", 30, 3, ["organization", "personal"],
            0.9  # Easy win
        ),
        TaskExample(
            "Prepare presentation for client",
            "Create slides for quarterly review meeting",
            "high", 60, 9, ["presentation", "client"],
            0.6
        )
    ]

@pytest.fixture
def mock_qwen_responses():
    """Deterministic mock responses for testing AI interactions"""
    return {
        'task_clarification': {
            "fix the website": [
                {
                    "title": "Identify website issues",
                    "description": "Run through site manually, document broken links and display issues",
                    "timer": 20,
                    "energy_required": "medium",
                    "priority": 8
                },
                {
                    "title": "Fix critical bugs",
                    "description": "Address any security or functionality issues found",
                    "timer": 45,
                    "energy_required": "high", 
                    "priority": 9
                }
            ]
        },
        'prioritization': {
            "reasoning": "Prioritized based on urgency and energy requirements. High-energy creative tasks scheduled for your peak mental energy window (10-11 AM based on your patterns).",
            "immediate": ["Call insurance about claim", "Update project documentation"],
            "today": ["Organize digital photos"],
            "this_week": ["Design new feature wireframes", "Prepare presentation for client"]
        },
        'reflection_high_quality': """
        You completed two meaningful tasks today despite having lower energy levels. 
        
        The insurance call you've been avoiding got done - that's huge! Administrative tasks like that often feel harder than they are. Notice how you felt relief after completing it.
        
        Your pattern shows you're most productive with documentation in the afternoon. Consider scheduling similar tasks during that 2-3 PM window.
        
        For tomorrow: Start with something small and energy-giving. Maybe organize those photos since you mentioned it feels satisfying.
        """,
        'reflection_low_quality': """
        Good job today. You did some tasks. Keep it up tomorrow.
        """
    }

@pytest.fixture
def mock_agents():
    """Mock agent instances for testing inter-agent communication"""
    perception = Mock()
    perception.socket_path = "/tmp/qtm_perception.sock"
    perception.status = "healthy"
    perception.extract_context_tags = Mock(return_value=["project", "documentation"])
    
    memory = Mock()
    memory.socket_path = "/tmp/qtm_memory.sock" 
    memory.status = "healthy"
    memory.store_interaction = Mock()
    memory.retrieve_patterns = Mock(return_value={"energy_peak": "10:00-11:00"})
    
    reasoning = Mock()
    reasoning.socket_path = "/tmp/qtm_reasoning.sock"
    reasoning.status = "healthy"
    reasoning.prioritize_tasks = Mock()
    reasoning.generate_reflection = Mock()
    
    exchange = Mock()
    exchange.socket_path = "/tmp/qtm_exchange.sock"
    exchange.status = "healthy"
    exchange.sync_calendar = Mock()
    exchange.send_notifications = Mock()
    
    return {
        'perception': perception,
        'memory': memory, 
        'reasoning': reasoning,
        'exchange': exchange
    }

# Performance Testing Fixtures
@pytest.fixture
def performance_timer():
    """Context manager for measuring execution time"""
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            
        def __enter__(self):
            self.start_time = time.time()
            return self
            
        def __exit__(self, *args):
            self.end_time = time.time()
            
        @property
        def elapsed(self):
            return self.end_time - self.start_time if self.end_time else None
    
    return Timer

# AI Quality Assessment Fixtures
@pytest.fixture 
def quality_assessor():
    """Tools for assessing AI response quality"""
    class QualityAssessor:
        
        def assess_reflection_quality(self, reflection_text: str) -> QualityScore:
            """Assess reflection quality against behavioral activation standards"""
            score = QualityScore()
            
            # Emotional tone assessment
            compassionate_words = ['understand', 'gentle', 'progress', 'effort', 'celebrate']
            score.compassion = any(word in reflection_text.lower() for word in compassionate_words)
            
            encouraging_words = ['great', 'well done', 'proud', 'achievement', 'success']
            score.encouragement = any(word in reflection_text.lower() for word in encouraging_words)
            
            critical_words = ['should have', 'failed', 'behind', 'not enough', 'disappointing']
            score.criticism_avoidance = not any(word in reflection_text.lower() for word in critical_words)
            
            # Content quality  
            score.specific_acknowledgment = len(reflection_text) > 50  # Meaningful length
            score.pattern_recognition = 'pattern' in reflection_text.lower() or 'notice' in reflection_text.lower()
            score.forward_focus = 'tomorrow' in reflection_text.lower() or 'next' in reflection_text.lower()
            
            return score
        
        def validate_smart_criteria(self, task_dict: dict) -> bool:
            """Validate that clarified task meets SMART criteria"""
            has_specific_title = len(task_dict.get('title', '').split()) >= 3
            has_measurable_desc = len(task_dict.get('description', '')) > 20
            has_time_estimate = 'timer' in task_dict and task_dict['timer'] > 0
            has_energy_assessment = task_dict.get('energy_required') in ['low', 'medium', 'high']
            
            return all([has_specific_title, has_measurable_desc, has_time_estimate, has_energy_assessment])
        
        def assess_cognitive_load(self, task_title: str) -> bool:
            """Assess if task title is cognitively manageable"""
            word_count = len(task_title.split())
            return word_count <= 8  # Research-based cognitive limit
    
    return QualityAssessor()

# Behavioral Validation Fixtures
@pytest.fixture
def behavioral_validator():
    """Validators for behavioral activation principles"""
    class BehavioralValidator:
        
        def promotes_self_compassion(self, text: str) -> bool:
            """Check if text promotes self-compassion vs self-criticism"""
            compassion_indicators = [
                'you did well', 'progress', 'effort', 'gentle', 'understand',
                'it\'s okay', 'normal', 'human', 'be kind'
            ]
            
            criticism_indicators = [
                'should have', 'failed', 'not good enough', 'behind',
                'disappointing', 'waste', 'lazy', 'procrastinating'
            ]
            
            text_lower = text.lower()
            has_compassion = any(phrase in text_lower for phrase in compassion_indicators)
            has_criticism = any(phrase in text_lower for phrase in criticism_indicators)
            
            return has_compassion and not has_criticism
        
        def suggests_appropriate_next_steps(self, text: str, current_energy: EnergyState) -> bool:
            """Validate that suggested next steps match energy state"""
            text_lower = text.lower()
            
            if current_energy.is_low_energy():
                # Should suggest gentle, small tasks
                gentle_suggestions = ['small', 'easy', 'gentle', 'light', 'simple']
                return any(word in text_lower for word in gentle_suggestions)
            elif current_energy.is_high_energy():
                # Can suggest more demanding tasks
                return True  # High energy can handle any suggestion
            else:
                # Medium energy - should be reasonable
                return 'overwhelming' not in text_lower
        
        def validates_effort(self, text: str, completed_tasks: List[str]) -> bool:
            """Check if reflection appropriately validates effort"""
            if not completed_tasks:
                return 'it\'s okay' in text.lower() or 'tomorrow' in text.lower()
            
            # Should acknowledge specific completions
            return any(task.lower() in text.lower() for task in completed_tasks[:2])
    
    return BehavioralValidator()

# Test Configuration
@pytest.fixture(scope="session", autouse=True)
def configure_behavioral_testing():
    """Configure pytest for behavioral testing patterns"""
    # Set up logging for behavioral test insights
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Configure async event loop for agent testing
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

# Pytest markers for test categorization
def pytest_configure(config):
    """Register custom pytest markers for test categorization"""
    config.addinivalue_line("markers", "behavioral: Tests that validate psychological outcomes")
    config.addinivalue_line("markers", "ai_quality: Tests that assess AI response quality")
    config.addinivalue_line("markers", "ai_consistency: Tests that validate AI consistency across sessions")
    config.addinivalue_line("markers", "integration: Tests that validate agent communication")
    config.addinivalue_line("markers", "performance: Tests that validate quality gates")
    config.addinivalue_line("markers", "phase0: Tests required for Phase 0 deployment")
    config.addinivalue_line("markers", "phase1: Tests required for Phase 1 deployment")
    config.addinivalue_line("markers", "phase2: Tests required for Phase 2 deployment")

# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_test_artifacts(tmp_path):
    """Ensure clean state between tests"""
    yield
    # Clean up any test sockets, temp files, etc.
    import glob
    for socket_file in glob.glob("/tmp/qtm_test_*.sock"):
        try:
            Path(socket_file).unlink()
        except FileNotFoundError:
            pass