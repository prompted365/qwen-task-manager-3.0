"""
AI Reasoning Quality Tests for Qwen Interactions

These tests validate the quality of AI reasoning and responses in Qwen Task Manager 3.0.
Unlike traditional unit tests that check exact outputs, these tests validate:

- Therapeutic appropriateness of AI responses
- Empathy and emotional intelligence in interactions
- Behavioral activation compliance in suggestions
- Prompt engineering effectiveness for different user states
- Response consistency while allowing natural language variation
- Context-aware reasoning that considers user psychology

Behavioral Focus:
- AI should support, not overwhelm, users with diverse needs
- Responses should demonstrate understanding of cognitive load
- Suggestions should align with energy-based scheduling principles
- Language should be encouraging and non-judgmental
"""

import pytest
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import dataclass

# Import test utilities  
from tests.utils.test_helpers import (
    AIQualityValidator, BehavioralValidator, PerformanceTestHelper
)
from tests.fixtures.sample_data import (
    get_user_profile, get_brain_dump, get_energy_pattern,
    get_behavioral_scenario
)

@dataclass
class QwenResponse:
    """Structure for Qwen AI response evaluation"""
    content: str
    reasoning_quality: float
    empathy_score: float
    behavioral_appropriateness: float
    context_awareness: float
    response_time: float
    
    def overall_score(self) -> float:
        """Calculate weighted overall quality score"""
        weights = {
            'reasoning_quality': 0.25,
            'empathy_score': 0.30,
            'behavioral_appropriateness': 0.25,
            'context_awareness': 0.20
        }
        
        return (
            self.reasoning_quality * weights['reasoning_quality'] +
            self.empathy_score * weights['empathy_score'] +
            self.behavioral_appropriateness * weights['behavioral_appropriateness'] +
            self.context_awareness * weights['context_awareness']
        )

class MockQwenModel:
    """Mock Qwen model for testing AI interactions"""
    
    def __init__(self):
        self.response_templates = {
            "task_breakdown": self._task_breakdown_responses(),
            "energy_coaching": self._energy_coaching_responses(),
            "overwhelm_support": self._overwhelm_support_responses(),
            "reflection_prompts": self._reflection_prompt_responses(),
            "priority_reasoning": self._priority_reasoning_responses()
        }
    
    async def generate_response(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate contextually appropriate response"""
        # Analyze prompt to determine response type
        response_type = self._classify_prompt(prompt)
        
        # Select appropriate template based on user context
        user_state = context.get('user_state', {})
        energy_level = user_state.get('energy_level', 'medium')
        stress_level = user_state.get('stress_level', 'normal')
        
        template_key = f"{response_type}_{energy_level}_{stress_level}"
        if template_key in self.response_templates[response_type]:
            return self.response_templates[response_type][template_key]
        else:
            # Fallback to basic template
            return self.response_templates[response_type][f"{response_type}_medium_normal"]
    
    def _classify_prompt(self, prompt: str) -> str:
        """Classify prompt to determine response strategy"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['break down', 'breakdown', 'steps']):
            return 'task_breakdown'
        elif any(word in prompt_lower for word in ['energy', 'tired', 'fatigue']):
            return 'energy_coaching'
        elif any(word in prompt_lower for word in ['overwhelmed', 'stressed', 'too much']):
            return 'overwhelm_support'
        elif any(word in prompt_lower for word in ['reflect', 'think about', 'journal']):
            return 'reflection_prompts'
        elif any(word in prompt_lower for word in ['priority', 'important', 'urgent']):
            return 'priority_reasoning'
        else:
            return 'task_breakdown'  # Default
    
    def _task_breakdown_responses(self) -> Dict[str, str]:
        return {
            "task_breakdown_high_normal": 
                "I can see you're ready to tackle this! Let's break this down into energizing steps:\n\n"
                "1. **Quick win first**: Start with the easiest piece to build momentum\n"
                "2. **Core work**: Dive into the main challenge while your energy is strong\n"
                "3. **Wrap-up tasks**: Save administrative items for later\n\n"
                "This approach will help you maintain that great energy throughout the process.",
                
            "task_breakdown_medium_normal":
                "Let's make this manageable by breaking it into clear steps:\n\n"
                "1. **Start small**: Pick one piece that feels achievable right now\n"
                "2. **Build progressively**: Each step should feel like a natural next move\n"
                "3. **Celebrate progress**: Acknowledge each completed step\n\n"
                "Remember, progress over perfection - you've got this!",
                
            "task_breakdown_low_normal":
                "I understand your energy feels limited right now. Let's be gentle with this:\n\n"
                "1. **Micro-step first**: What's the tiniest meaningful action you could take?\n"
                "2. **Rest if needed**: Honor your energy - small progress counts\n"
                "3. **Save complexity**: Keep demanding work for when you're refreshed\n\n"
                "Even small movement forward is valuable. Be kind to yourself today.",
                
            "task_breakdown_medium_high":
                "I notice you might be feeling stressed. Let's approach this calmly:\n\n"
                "1. **Breathe first**: Take a moment to center yourself\n"
                "2. **One thing only**: Focus on just the next single step\n"
                "3. **Permission to pause**: You can always take breaks between steps\n\n"
                "Stress doesn't define your capability. You're handling this well."
        }
    
    def _energy_coaching_responses(self) -> Dict[str, str]:
        return {
            "energy_coaching_high_normal":
                "Your energy feels strong right now - that's wonderful! Here's how to make the most of it:\n\n"
                "• **Tackle your most challenging work first** while this clarity lasts\n"
                "• **Protect this energy** by minimizing distractions\n"
                "• **Plan for the transition** when your energy naturally shifts\n\n"
                "High-energy moments are gifts - use yours wisely!",
                
            "energy_coaching_low_normal":
                "Low energy is completely natural and temporary. Let's work with it, not against it:\n\n"
                "• **Gentle activities only**: Administrative tasks, organizing, light planning\n"
                "• **Rest is productive**: Your brain processes and recovers during downtime\n"
                "• **Trust your rhythms**: This energy will return\n\n"
                "Honoring low energy prevents burnout and supports sustainable productivity.",
                
            "energy_coaching_medium_high":
                "I sense you're pushing through stress fatigue. Let's recalibrate:\n\n"
                "• **Stress masquerades as productivity**: Real progress needs sustainable energy\n"
                "• **Pause, don't push**: What your system needs most right now is gentleness\n"
                "• **Small wins count**: Progress doesn't require high intensity\n\n"
                "Your worth isn't measured by your energy output. You're doing enough."
        }
    
    def _overwhelm_support_responses(self) -> Dict[str, str]:
        return {
            "overwhelm_support_high_normal":
                "Feeling overwhelmed despite good energy is so common. Let's simplify:\n\n"
                "**Right now, you only need to focus on ONE thing.** Everything else can wait.\n\n"
                "• Choose the single most important item\n"
                "• Give yourself permission to ignore the rest temporarily\n"
                "• Remember: You can't do everything at once, and that's perfectly okay\n\n"
                "Overwhelm is about perception, not capability. You're more capable than this moment feels.",
                
            "overwhelm_support_low_normal":
                "Overwhelm on low energy feels especially heavy. You're not alone in this:\n\n"
                "**The gentlest possible approach right now:**\n\n"
                "• Pick the easiest task on your list (not the most important)\n"
                "• Do just that one thing\n"
                "• Rest afterwards without guilt\n\n"
                "Overwhelm will pass. Your job right now is simply to be kind to yourself.",
                
            "overwhelm_support_medium_high":
                "Stress-overwhelm creates a cycle that's hard to break. Let's interrupt it gently:\n\n"
                "**Emergency self-compassion protocol:**\n\n"
                "• Acknowledge: 'This is a moment of suffering'\n"
                "• Normalize: 'Overwhelm is part of the human experience'\n"
                "• Kindness: 'May I be gentle with myself right now'\n\n"
                "Nothing on your list is more important than your wellbeing. You matter more than your tasks."
        }
    
    def _reflection_prompt_responses(self) -> Dict[str, str]:
        return {
            "reflection_prompts_medium_normal":
                "Reflection is such a powerful tool for understanding yourself. Here are some gentle prompts:\n\n"
                "**Today's Wins** (however small):\n"
                "• What felt good about today?\n"
                "• What choice am I proud of?\n\n"
                "**Energy Awareness**:\n"
                "• When did I feel most/least energized?\n"
                "• What activities align with my natural rhythms?\n\n"
                "**Tomorrow's Intention**:\n"
                "• How do I want to feel tomorrow?\n"
                "• What would make tomorrow feel successful?\n\n"
                "Remember: There are no wrong answers in reflection, only insights.",
                
            "reflection_prompts_low_normal":
                "When energy is low, reflection can be especially nourishing. Keep it simple:\n\n"
                "**Just for today:**\n"
                "• What did I handle well, even if it felt difficult?\n"
                "• What can I appreciate about how I took care of myself?\n"
                "• What do I need to feel supported right now?\n\n"
                "Low-energy days often reveal our resilience. You're stronger than you realize."
        }
    
    def _priority_reasoning_responses(self) -> Dict[str, str]:
        return {
            "priority_reasoning_medium_normal":
                "Priority decisions work best when they align with both logic and intuition:\n\n"
                "**Framework for clarity:**\n\n"
                "• **Impact vs. Energy**: What creates the biggest positive change for the least energy?\n"
                "• **Time sensitivity**: What has real deadlines vs. artificial urgency?\n"
                "• **Personal values**: What matters most to you beyond external expectations?\n\n"
                "Sometimes the 'right' priority is the one that feels sustainable, not just urgent.",
                
            "priority_reasoning_high_normal":
                "With strong energy, you can tackle meaningful priorities effectively:\n\n"
                "**Strategic approach:**\n\n"
                "• **Highest impact first**: Use this energy for work that creates lasting value\n"
                "• **Complex before simple**: Handle demanding decisions while clarity is high\n"
                "• **Future planning**: Set yourself up for success during lower-energy periods\n\n"
                "High energy is perfect for building momentum on what truly matters."
        }

class TestQwenResponseQuality:
    """
    Test that Qwen responses meet behavioral and therapeutic standards
    """
    
    @pytest.fixture
    def mock_qwen(self):
        return MockQwenModel()
    
    @pytest.fixture
    def ai_validator(self):
        return AIQualityValidator()
    
    @pytest.fixture
    def behavioral_validator(self):
        return BehavioralValidator()
    
    @pytest.mark.ai_reasoning
    async def test_task_breakdown_response_quality(self, mock_qwen, ai_validator):
        """Test AI provides helpful, encouraging task breakdowns"""
        # GIVEN
        user_context = {
            'user_state': {
                'energy_level': 'medium',
                'stress_level': 'normal',
                'cognitive_load': 'moderate'
            },
            'task_complexity': 'high',
            'user_profile': get_user_profile('adhd_creative')
        }
        
        prompt = "I need to break down this complex project into manageable steps. It feels overwhelming."
        
        # WHEN
        response = await mock_qwen.generate_response(prompt, user_context)
        
        # THEN
        quality_scores = ai_validator.evaluate_response_quality(response, 'task_breakdown')
        
        assert quality_scores['empathy_score'] >= 0.7, "Should show understanding of overwhelm"
        assert quality_scores['behavioral_appropriateness'] >= 0.8, "Should follow behavioral activation principles"
        assert quality_scores['reasoning_quality'] >= 0.7, "Should provide logical structure"
        
        # Verify specific therapeutic elements
        response_lower = response.lower()
        assert any(word in response_lower for word in ['manageable', 'break', 'steps']), \
            "Should emphasize manageability"
        assert any(word in response_lower for word in ['progress', 'momentum', 'celebrate']), \
            "Should encourage progress mindset"
        
        # Should NOT contain overwhelming language
        overwhelming_phrases = ['must', 'should have', 'need to', 'have to']
        assert not any(phrase in response_lower for phrase in overwhelming_phrases), \
            "Should avoid pressure language"
    
    @pytest.mark.ai_reasoning
    async def test_energy_coaching_adaptation(self, mock_qwen, ai_validator):
        """Test AI adapts coaching based on user energy levels"""
        energy_scenarios = [
            ('high', 'normal', 'challenge'),
            ('medium', 'normal', 'balance'),
            ('low', 'normal', 'gentle'),
            ('medium', 'high', 'support')
        ]
        
        for energy, stress, expected_tone in energy_scenarios:
            # GIVEN
            user_context = {
                'user_state': {
                    'energy_level': energy,
                    'stress_level': stress,
                    'cognitive_load': 'moderate'
                }
            }
            
            prompt = "I'm feeling tired and need some guidance on managing my energy today."
            
            # WHEN
            response = await mock_qwen.generate_response(prompt, user_context)
            
            # THEN
            quality_scores = ai_validator.evaluate_response_quality(response, 'energy_coaching')
            
            assert quality_scores['context_awareness'] >= 0.8, \
                f"Should adapt to {energy} energy, {stress} stress"
            
            # Verify tone matches energy level
            if expected_tone == 'challenge':
                assert any(word in response.lower() for word in ['tackle', 'strong', 'make the most']), \
                    "High energy should get encouraging challenge"
            elif expected_tone == 'gentle':
                assert any(word in response.lower() for word in ['gentle', 'kind', 'honor', 'rest']), \
                    "Low energy should get gentle support"
            elif expected_tone == 'support':
                assert any(word in response.lower() for word in ['understand', 'okay', 'enough']), \
                    "Stress should get supportive validation"
    
    @pytest.mark.ai_reasoning
    async def test_overwhelm_intervention_effectiveness(self, mock_qwen, behavioral_validator):
        """Test AI provides effective overwhelm interventions"""
        # GIVEN
        overwhelm_context = {
            'user_state': {
                'energy_level': 'low',
                'stress_level': 'high',
                'cognitive_load': 'overloaded',
                'emotional_state': 'overwhelmed'
            },
            'task_count': 15,
            'urgent_tasks': 8,
            'user_profile': get_user_profile('burnout_recovery')
        }
        
        prompt = "I have too many urgent tasks and I can't handle it all. Everything feels important and I'm paralyzed."
        
        # WHEN
        response = await mock_qwen.generate_response(prompt, overwhelm_context)
        
        # THEN
        is_behaviorally_appropriate = behavioral_validator.validate_overwhelm_response(response)
        assert is_behaviorally_appropriate, "Should follow overwhelm intervention best practices"
        
        # Specific overwhelm intervention elements
        response_lower = response.lower()
        
        # Should simplify focus
        assert any(phrase in response_lower for phrase in ['one thing', 'single', 'just']), \
            "Should narrow focus to prevent overwhelm"
        
        # Should validate feelings
        assert any(phrase in response_lower for phrase in ['understand', 'common', 'okay']), \
            "Should normalize overwhelming feelings"
        
        # Should provide permission to rest/pause
        assert any(phrase in response_lower for phrase in ['permission', 'okay to', 'can wait']), \
            "Should give permission to not do everything"
        
        # Should NOT add more pressure
        pressure_words = ['need to', 'must', 'should', 'have to', 'urgent', 'quickly']
        assert not any(word in response_lower for word in pressure_words), \
            "Should not add pressure during overwhelm"
    
    @pytest.mark.ai_reasoning
    async def test_response_consistency_across_sessions(self, mock_qwen, ai_validator):
        """Test AI maintains consistent therapeutic approach across multiple interactions"""
        # GIVEN
        user_context = {
            'user_state': {
                'energy_level': 'medium',
                'stress_level': 'normal'
            },
            'session_history': ['task_breakdown', 'reflection', 'priority_help']
        }
        
        # Same type of request multiple times
        prompts = [
            "Help me break down this project into steps",
            "I need to organize this big task into smaller pieces",
            "Can you help me make this complex work more manageable?"
        ]
        
        responses = []
        quality_scores = []
        
        # WHEN
        for prompt in prompts:
            response = await mock_qwen.generate_response(prompt, user_context)
            responses.append(response)
            scores = ai_validator.evaluate_response_quality(response, 'task_breakdown')
            quality_scores.append(scores)
        
        # THEN
        # All responses should meet quality thresholds
        for i, scores in enumerate(quality_scores):
            assert scores['empathy_score'] >= 0.7, f"Response {i+1} lacks empathy"
            assert scores['behavioral_appropriateness'] >= 0.8, f"Response {i+1} not behaviorally sound"
        
        # Responses should be consistent in tone but varied in content
        consistent_elements = []
        for response in responses:
            response_lower = response.lower()
            has_encouragement = any(word in response_lower for word in ['you', 'can', 'able', 'capable'])
            has_structure = any(word in response_lower for word in ['steps', 'break', 'manageable'])
            consistent_elements.append((has_encouragement, has_structure))
        
        # All should have consistent therapeutic elements
        assert all(elem[0] for elem in consistent_elements), "All responses should be encouraging"
        assert all(elem[1] for elem in consistent_elements), "All responses should provide structure"
    
    @pytest.mark.ai_reasoning
    @pytest.mark.performance
    async def test_response_time_requirements(self, mock_qwen):
        """Test AI response times meet user experience requirements"""
        # GIVEN
        performance_helper = PerformanceTestHelper()
        
        test_prompts = [
            "Quick task breakdown needed",
            "Help me prioritize these 5 tasks",
            "I'm feeling overwhelmed with my workload",
            "Generate a reflection prompt for today"
        ]
        
        user_context = {
            'user_state': {
                'energy_level': 'medium',
                'stress_level': 'normal'
            }
        }
        
        # WHEN
        response_times = []
        for prompt in test_prompts:
            start_time = performance_helper.start_timer()
            await mock_qwen.generate_response(prompt, user_context)
            response_time = performance_helper.end_timer(start_time)
            response_times.append(response_time)
        
        # THEN
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        # AI responses should be fast enough for real-time interaction
        assert avg_response_time < 2.0, f"Average response time too slow: {avg_response_time:.2f}s"
        assert max_response_time < 5.0, f"Max response time too slow: {max_response_time:.2f}s"
        
        # No response should take longer than user patience threshold
        for i, time in enumerate(response_times):
            assert time < 3.0, f"Response {i+1} took too long: {time:.2f}s"

class TestPromptEngineering:
    """
    Test prompt engineering effectiveness for different scenarios
    """
    
    @pytest.fixture
    def mock_qwen(self):
        return MockQwenModel()
    
    @pytest.mark.ai_reasoning
    async def test_context_aware_prompting(self, mock_qwen):
        """Test prompts effectively incorporate user context"""
        # Test different user profiles require different prompt approaches
        user_profiles = [
            ('adhd_creative', 'adhd'),
            ('burnout_recovery', 'burnout'),
            ('high_achiever', 'perfectionism')
        ]
        
        base_prompt = "Help me organize my tasks for today"
        
        for profile_key, challenge_type in user_profiles:
            # GIVEN
            user_profile = get_user_profile(profile_key)
            context = {
                'user_state': user_profile['typical_state'],
                'user_profile': user_profile,
                'challenge_type': challenge_type
            }
            
            # WHEN
            response = await mock_qwen.generate_response(base_prompt, context)
            
            # THEN
            response_lower = response.lower()
            
            if challenge_type == 'adhd':
                # Should acknowledge ADHD-specific needs
                assert any(phrase in response_lower for phrase in 
                          ['momentum', 'energy', 'focus', 'small steps']), \
                    "Should address ADHD-specific productivity challenges"
            
            elif challenge_type == 'burnout':
                # Should emphasize gentleness and recovery
                assert any(phrase in response_lower for phrase in 
                          ['gentle', 'rest', 'sustainable', 'energy']), \
                    "Should support burnout recovery approach"
            
            elif challenge_type == 'perfectionism':
                # Should address perfectionist tendencies
                assert any(phrase in response_lower for phrase in 
                          ['progress', 'good enough', 'perfect', 'done']), \
                    "Should counter perfectionist paralysis"
    
    @pytest.mark.ai_reasoning
    async def test_emotional_state_adaptation(self, mock_qwen):
        """Test AI adapts language based on detected emotional state"""
        emotional_scenarios = [
            {
                'state': 'anxious',
                'context': {'stress_level': 'high', 'cognitive_load': 'overloaded'},
                'expected_elements': ['calm', 'breathe', 'okay', 'gentle']
            },
            {
                'state': 'motivated',
                'context': {'energy_level': 'high', 'mood': 'positive'},
                'expected_elements': ['momentum', 'tackle', 'energy', 'great']
            },
            {
                'state': 'defeated',
                'context': {'energy_level': 'low', 'mood': 'discouraged'},
                'expected_elements': ['understand', 'small', 'enough', 'kind']
            }
        ]
        
        for scenario in emotional_scenarios:
            # GIVEN
            prompt = "I don't know where to start with my work today"
            context = {
                'user_state': scenario['context'],
                'emotional_state': scenario['state']
            }
            
            # WHEN
            response = await mock_qwen.generate_response(prompt, context)
            
            # THEN
            response_lower = response.lower()
            found_elements = [elem for elem in scenario['expected_elements'] 
                            if elem in response_lower]
            
            assert len(found_elements) >= 1, \
                f"Should include emotional support for {scenario['state']} state. Expected one of {scenario['expected_elements']}, got: {response}"

class TestBehavioralActivationCompliance:
    """
    Test AI responses comply with behavioral activation therapeutic principles
    """
    
    @pytest.fixture
    def behavioral_validator(self):
        return BehavioralValidator()
    
    @pytest.mark.ai_reasoning
    @pytest.mark.behavioral
    async def test_activity_scheduling_principles(self, behavioral_validator):
        """Test AI follows behavioral activation activity scheduling principles"""
        # GIVEN
        mock_qwen = MockQwenModel()
        
        scenario = get_behavioral_scenario('energy_based_scheduling')
        context = {
            'user_state': scenario['user_state'],
            'energy_pattern': scenario['energy_pattern'],
            'available_tasks': scenario['available_tasks']
        }
        
        prompt = "Help me schedule my tasks based on my energy levels"
        
        # WHEN
        response = await mock_qwen.generate_response(prompt, context)
        
        # THEN
        ba_compliance = behavioral_validator.validate_behavioral_activation_compliance(response)
        
        assert ba_compliance['activity_scheduling'] >= 0.8, \
            "Should demonstrate good activity scheduling principles"
        assert ba_compliance['energy_awareness'] >= 0.8, \
            "Should show awareness of energy-task matching"
        assert ba_compliance['self_compassion'] >= 0.7, \
            "Should include self-compassionate language"
    
    @pytest.mark.ai_reasoning
    @pytest.mark.behavioral  
    async def test_avoids_harmful_productivity_culture(self, behavioral_validator):
        """Test AI avoids harmful productivity culture messages"""
        # GIVEN
        mock_qwen = MockQwenModel()
        
        # Context simulating burnout risk
        context = {
            'user_state': {
                'energy_level': 'low',
                'stress_level': 'high',
                'recent_overwork': True,
                'sleep_quality': 'poor'
            },
            'user_profile': get_user_profile('burnout_recovery')
        }
        
        prompt = "I feel like I'm not productive enough. How can I get more done?"
        
        # WHEN
        response = await mock_qwen.generate_response(prompt, context)
        
        # THEN
        harmful_patterns = behavioral_validator.detect_harmful_productivity_messages(response)
        
        assert not harmful_patterns['hustle_culture'], \
            "Should not promote unsustainable work patterns"
        assert not harmful_patterns['productivity_shame'], \
            "Should not shame user for current productivity levels"
        assert not harmful_patterns['ignore_wellbeing'], \
            "Should not prioritize tasks over wellbeing"
        
        # Should actively counter productivity pressure
        response_lower = response.lower()
        supportive_elements = [
            'enough', 'sustainable', 'wellbeing', 'rest', 'balance', 'gentle'
        ]
        
        found_supportive = [elem for elem in supportive_elements if elem in response_lower]
        assert len(found_supportive) >= 2, \
            f"Should include supportive counter-messages. Found: {found_supportive}"

class TestContextualReasoning:
    """
    Test AI's ability to reason about complex, contextual situations
    """
    
    @pytest.mark.ai_reasoning
    async def test_multi_factor_decision_support(self):
        """Test AI can handle complex scenarios with multiple competing factors"""
        # GIVEN
        mock_qwen = MockQwenModel()
        
        complex_scenario = {
            'competing_deadlines': [
                {'task': 'Client presentation', 'deadline': '2 days', 'importance': 'high'},
                {'task': 'Team report', 'deadline': '3 days', 'importance': 'medium'},
                {'task': 'Personal project', 'deadline': '1 week', 'importance': 'personal'}
            ],
            'constraints': {
                'energy_level': 'medium',
                'available_time': '6 hours',
                'stress_level': 'elevated',
                'support_available': 'limited'
            },
            'user_values': ['quality work', 'work-life balance', 'team collaboration']
        }
        
        prompt = """I have multiple competing deadlines and limited time. Help me think through this:
        - Client presentation due in 2 days (high stakes)
        - Team report due in 3 days (affects colleagues) 
        - Personal passion project due in 1 week
        
        I'm already feeling stressed and only have about 6 hours total to work with."""
        
        # WHEN
        response = await mock_qwen.generate_response(prompt, complex_scenario)
        
        # THEN
        ai_validator = AIQualityValidator()
        reasoning_analysis = ai_validator.analyze_reasoning_quality(response, complex_scenario)
        
        assert reasoning_analysis['considers_constraints'] >= 0.8, \
            "Should acknowledge time and energy constraints"
        assert reasoning_analysis['balances_factors'] >= 0.7, \
            "Should balance competing priorities thoughtfully"
        assert reasoning_analysis['suggests_tradeoffs'] >= 0.7, \
            "Should help user understand necessary tradeoffs"
        
        # Should provide specific, actionable guidance
        response_lower = response.lower()
        assert any(word in response_lower for word in ['start with', 'focus on', 'prioritize']), \
            "Should provide specific starting point"
        assert any(phrase in response_lower for phrase in ['stress', 'energy', 'sustainable']), \
            "Should acknowledge user's constraints"

if __name__ == "__main__":
    # Run AI reasoning tests
    pytest.main([__file__, "-v", "-m", "ai_reasoning"])