"""
Testing utilities for AI and behavioral validation

This module provides specialized helpers for testing psychological and AI systems.
Unlike traditional testing utilities, these focus on validating human impact
and reasoning quality over deterministic outputs.

Key Testing Approaches:
- Quality Pattern Recognition: Assess response patterns vs exact matches
- Behavioral Impact Validation: Verify psychological benefits
- AI Reasoning Assessment: Evaluate decision-making quality
- Energy-Context Matching: Validate energy-appropriate suggestions
"""

import re
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import time
from unittest.mock import Mock

@dataclass
class AIResponseAnalysis:
    """Comprehensive analysis of AI response quality"""
    clarity_score: float      # 0-1: How clear is the response?
    specificity_score: float  # 0-1: How specific and actionable?
    empathy_score: float     # 0-1: Emotional appropriateness
    consistency_score: float # 0-1: Consistency with previous responses
    behavioral_support: bool # Does it support behavioral activation?
    
    @property
    def overall_quality(self) -> float:
        """Calculate weighted overall quality score"""
        return (
            self.clarity_score * 0.2 +
            self.specificity_score * 0.25 +
            self.empathy_score * 0.3 +  # Empathy weighted higher for behavioral system
            self.consistency_score * 0.15 +
            (1.0 if self.behavioral_support else 0.0) * 0.1
        )

class AIQualityValidator:
    """Specialized validator for AI response quality in behavioral contexts"""
    
    def __init__(self):
        self.empathy_indicators = [
            'understand', 'feel', 'sounds like', 'I hear', 'that makes sense',
            'it\'s natural', 'many people', 'common experience', 'validate'
        ]
        
        self.action_indicators = [
            'try', 'consider', 'might', 'could', 'what if', 'perhaps',
            'one option', 'you might find', 'it could help'
        ]
        
        self.harsh_language = [
            'must', 'should', 'need to', 'have to', 'required',
            'failed', 'wrong', 'bad', 'terrible', 'awful'
        ]
        
        self.vague_responses = [
            'good job', 'keep it up', 'nice work', 'well done',
            'continue', 'maintain', 'stay positive'
        ]
    
    def analyze_response(self, response_text: str, context: Dict[str, Any] = None) -> AIResponseAnalysis:
        """Comprehensive analysis of AI response quality"""
        response_lower = response_text.lower()
        
        # Clarity: Is the response specific and understandable?
        clarity = self._assess_clarity(response_text)
        
        # Specificity: Does it provide actionable guidance?
        specificity = self._assess_specificity(response_text)
        
        # Empathy: Is the tone appropriate and supportive?
        empathy = self._assess_empathy(response_lower)
        
        # Consistency: Does it align with expected patterns?
        consistency = self._assess_consistency(response_text, context or {})
        
        # Behavioral support: Does it follow behavioral activation principles?
        behavioral_support = self._assess_behavioral_support(response_lower)
        
        return AIResponseAnalysis(
            clarity_score=clarity,
            specificity_score=specificity,
            empathy_score=empathy,
            consistency_score=consistency,
            behavioral_support=behavioral_support
        )
    
    def _assess_clarity(self, text: str) -> float:
        """Assess response clarity (0-1 scale)"""
        # Penalize overly vague responses
        vague_count = sum(1 for phrase in self.vague_responses if phrase in text.lower())
        if vague_count > 2:
            return 0.3
        
        # Reward specific language
        sentence_count = len([s for s in text.split('.') if s.strip()])
        avg_sentence_length = len(text.split()) / max(sentence_count, 1)
        
        # Optimal sentence length for clarity (research-based)
        if 10 <= avg_sentence_length <= 20:
            return 0.9
        elif 8 <= avg_sentence_length <= 25:
            return 0.7
        else:
            return 0.5
    
    def _assess_specificity(self, text: str) -> float:
        """Assess actionability and specificity (0-1 scale)"""
        action_count = sum(1 for phrase in self.action_indicators if phrase in text.lower())
        specificity_indicators = ['when', 'where', 'how', 'what', 'why', 'minutes', 'time', 'step']
        specific_count = sum(1 for word in specificity_indicators if word in text.lower())
        
        # Higher score for more specific, actionable language
        total_indicators = action_count + specific_count
        word_count = len(text.split())
        
        if word_count > 0:
            indicator_ratio = total_indicators / (word_count / 10)  # Per 10 words
            return min(indicator_ratio, 1.0)
        
        return 0.0
    
    def _assess_empathy(self, text_lower: str) -> float:
        """Assess emotional appropriateness and empathy (0-1 scale)"""
        empathy_count = sum(1 for phrase in self.empathy_indicators if phrase in text_lower)
        harsh_count = sum(1 for phrase in self.harsh_language if phrase in text_lower)
        
        # Penalize harsh language heavily
        if harsh_count > 0:
            return max(0.0, 0.5 - (harsh_count * 0.2))
        
        # Reward empathetic language
        if empathy_count >= 2:
            return 1.0
        elif empathy_count == 1:
            return 0.8
        else:
            return 0.6  # Neutral is acceptable
    
    def _assess_consistency(self, text: str, context: Dict[str, Any]) -> float:
        """Assess consistency with user context and previous responses"""
        # Without historical data, check internal consistency
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) < 2:
            return 0.8  # Single sentence, assume consistent
        
        # Check for contradictory statements (basic heuristic)
        contradictory_pairs = [
            ('should', 'might'), ('must', 'could'), ('always', 'sometimes'),
            ('never', 'occasionally'), ('easy', 'difficult')
        ]
        
        for word1, word2 in contradictory_pairs:
            if word1 in text.lower() and word2 in text.lower():
                return 0.6  # Some inconsistency detected
        
        return 0.9  # Appears consistent
    
    def _assess_behavioral_support(self, text_lower: str) -> bool:
        """Assess if response supports behavioral activation principles"""
        # Key behavioral activation principles
        supports_self_compassion = any(phrase in text_lower for phrase in [
            'be kind', 'gentle', 'progress', 'effort', 'it\'s okay'
        ])
        
        avoids_overwhelming = 'overwhelming' not in text_lower and 'too much' not in text_lower
        
        suggests_small_steps = any(phrase in text_lower for phrase in [
            'small', 'little', 'one step', 'start with', 'begin by'
        ])
        
        acknowledges_difficulty = any(phrase in text_lower for phrase in [
            'difficult', 'hard', 'challenging', 'understand', 'tough'
        ])
        
        # Must have at least 2 of these principles
        principles_count = sum([
            supports_self_compassion, avoids_overwhelming, 
            suggests_small_steps, acknowledges_difficulty
        ])
        
        return principles_count >= 2

class BehavioralTestValidator:
    """Specialized validator for behavioral activation testing"""
    
    def validate_energy_appropriate_suggestions(self, suggestions: List[Dict], energy_state: Dict) -> bool:
        """Validate that task suggestions match user's energy state"""
        avg_energy = (energy_state['physical'] + energy_state['mental'] + energy_state['emotional']) / 3
        
        for suggestion in suggestions:
            required_energy = suggestion.get('energy_required', 'medium')
            
            if avg_energy <= 4 and required_energy == 'high':
                return False  # High-energy task suggested during low energy
            
            if avg_energy >= 8 and all(s.get('energy_required') == 'low' for s in suggestions):
                return False  # Only low-energy tasks during high energy (missed opportunity)
        
        return True
    
    def validate_cognitive_load_management(self, tasks: List[Dict]) -> bool:
        """Ensure tasks don't create cognitive overload"""
        # Research: Maximum 3-5 items in working memory
        immediate_tasks = [t for t in tasks if t.get('priority', 0) >= 8]
        
        if len(immediate_tasks) > 3:
            return False  # Too many high-priority items
        
        # Check individual task complexity
        for task in tasks:
            title_words = len(task.get('title', '').split())
            if title_words > 8:  # Cognitive complexity limit
                return False
        
        return True
    
    def validate_behavioral_activation_compliance(self, reflection: str, completed_tasks: List[str], energy: Dict) -> bool:
        """Validate reflection follows behavioral activation principles"""
        reflection_lower = reflection.lower()
        
        # Principle 1: Acknowledge effort, no matter how small
        if completed_tasks and not any(task.lower() in reflection_lower for task in completed_tasks[:2]):
            return False
        
        # Principle 2: Avoid self-criticism
        critical_phrases = ['should have', 'not enough', 'failed', 'behind', 'disappointing']
        if any(phrase in reflection_lower for phrase in critical_phrases):
            return False
        
        # Principle 3: Validate emotional experience
        if energy['emotional'] <= 4:  # Low emotional energy
            validation_phrases = ['understand', 'difficult', 'tough', 'it\'s okay', 'normal']
            if not any(phrase in reflection_lower for phrase in validation_phrases):
                return False
        
        # Principle 4: Suggest manageable next steps
        if 'tomorrow' in reflection_lower or 'next' in reflection_lower:
            # Should suggest appropriate difficulty level
            if energy['mental'] <= 4:  # Low mental energy
                overwhelming_words = ['ambitious', 'challenging', 'complex', 'difficult']
                if any(word in reflection_lower for word in overwhelming_words):
                    return False
        
        return True

class PerformanceTestHelper:
    """Helper for performance and quality gate testing"""
    
    def __init__(self):
        self.latency_threshold = 10.0  # seconds
        self.accuracy_threshold = 0.8  # 80%
    
    async def measure_task_capture_latency(self, task_input: str, mock_qwen=None) -> float:
        """Measure full task capture and processing latency"""
        start_time = time.time()
        
        # Simulate full capture flow (would be real implementation in actual tests)
        if mock_qwen:
            # Mock flow for testing
            await asyncio.sleep(0.1)  # Simulate processing time
            clarified = mock_qwen.clarify_tasks(task_input)
            prioritized = mock_qwen.prioritize_tasks(clarified)
        else:
            # Would call real implementation
            await asyncio.sleep(2.0)  # Simulate realistic processing time
        
        return time.time() - start_time
    
    def validate_latency_requirement(self, measured_latency: float) -> bool:
        """Validate latency meets quality gate requirement"""
        return measured_latency < self.latency_threshold
    
    def calculate_accuracy_score(self, predictions: List[Any], ground_truth: List[Any]) -> float:
        """Calculate accuracy for auto-tagging and other prediction tasks"""
        if not predictions or not ground_truth:
            return 0.0
        
        # For set-based comparisons (e.g., context tags)
        if isinstance(predictions[0], (list, set)):
            correct = 0
            total = 0
            
            for pred, truth in zip(predictions, ground_truth):
                pred_set = set(pred)
                truth_set = set(truth)
                
                intersection = len(pred_set & truth_set)
                union = len(pred_set | truth_set)
                
                if union > 0:
                    correct += intersection
                    total += union
            
            return correct / total if total > 0 else 0.0
        
        # For exact matches
        matches = sum(1 for p, t in zip(predictions, ground_truth) if p == t)
        return matches / len(predictions)
    
    def validate_accuracy_requirement(self, accuracy_score: float) -> bool:
        """Validate accuracy meets quality gate requirement"""
        return accuracy_score >= self.accuracy_threshold

class MockAgentCommunication:
    """Helper for testing inter-agent communication"""
    
    def __init__(self):
        self.message_history = []
        self.active_sockets = {}
    
    async def simulate_agent_message(self, source: str, target: str, message_type: str, data: Dict) -> bool:
        """Simulate inter-agent message passing"""
        message = {
            "type": message_type,
            "source": source,
            "target": target,
            "timestamp": time.time(),
            "data": data
        }
        
        self.message_history.append(message)
        
        # Simulate processing delay
        await asyncio.sleep(0.01)
        
        return True
    
    def validate_message_schema(self, message: Dict, expected_type: str) -> bool:
        """Validate message follows expected schema"""
        required_fields = ["type", "source", "timestamp", "data"]
        
        # Check required fields
        for field in required_fields:
            if field not in message:
                return False
        
        # Check message type
        if message["type"] != expected_type:
            return False
        
        # Validate timestamp format
        if not isinstance(message["timestamp"], (int, float, str)):
            return False
        
        return True
    
    def simulate_socket_failure(self, socket_path: str):
        """Simulate Unix socket communication failure"""
        if socket_path in self.active_sockets:
            self.active_sockets[socket_path]["status"] = "failed"
    
    def restore_socket_connection(self, socket_path: str):
        """Restore Unix socket communication"""
        if socket_path in self.active_sockets:
            self.active_sockets[socket_path]["status"] = "healthy"

# Utility functions for common test patterns
def create_realistic_task_input() -> str:
    """Generate realistic messy task input for testing"""
    messy_inputs = [
        "need to fix website bugs update docs call sarah about project",
        "prepare presentation review quarterly numbers schedule team meeting",
        "organize files backup computer clean desk write blog post",
        "research competitor pricing update linkedin profile call dentist"
    ]
    
    import random
    return random.choice(messy_inputs)

def assert_behavioral_quality(response: str, context: Dict = None) -> None:
    """Assert that response meets behavioral activation standards"""
    validator = AIQualityValidator()
    analysis = validator.analyze_response(response, context)
    
    assert analysis.overall_quality >= 0.7, f"Response quality {analysis.overall_quality:.2f} below threshold"
    assert analysis.behavioral_support, "Response does not support behavioral activation principles"
    assert analysis.empathy_score >= 0.6, f"Empathy score {analysis.empathy_score:.2f} too low"

def assert_cognitive_manageability(tasks: List[Dict]) -> None:
    """Assert that tasks are cognitively manageable"""
    validator = BehavioralTestValidator()
    
    assert validator.validate_cognitive_load_management(tasks), "Tasks create cognitive overload"
    
    for task in tasks:
        title_length = len(task.get('title', '').split())
        assert title_length <= 8, f"Task title '{task.get('title')}' too complex ({title_length} words)"

def assert_energy_appropriate(suggestions: List[Dict], energy_state: Dict) -> None:
    """Assert that suggestions are appropriate for energy state"""
    validator = BehavioralTestValidator()
    
    assert validator.validate_energy_appropriate_suggestions(suggestions, energy_state), \
        f"Suggestions not appropriate for energy state {energy_state}"