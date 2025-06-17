#!/usr/bin/env python3
"""
User-Story Synthesiser Agent
Core USS agent responsible for analyzing components and generating user stories
"""

import json
import ast
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

# Import base Agent class
import sys
sys.path.append(str(Path(__file__).parent.parent))
from agents import Agent
from agents.component_registry import ComponentRegistry


@dataclass
class ComponentAnalysis:
    """Result of component structure analysis"""
    structure: Dict[str, Any]
    behavior: Dict[str, Any]  
    interactions: Dict[str, Any]
    relationships: Dict[str, Any]
    component_info: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'structure': self.structure,
            'behavior': self.behavior,
            'interactions': self.interactions,
            'relationships': self.relationships,
            'component_info': self.component_info
        }


@dataclass 
class QualityScore:
    """Quality assessment for generated user stories"""
    overall_score: float
    format_score: float
    clarity_score: float
    value_score: float
    touchpoint_score: float
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'overall_score': self.overall_score,
            'format_score': self.format_score,
            'clarity_score': self.clarity_score,
            'value_score': self.value_score,
            'touchpoint_score': self.touchpoint_score,
            'confidence': self.confidence
        }


class ComponentAnalyzer:
    """Analyzes components to understand their purpose and interfaces"""
    
    def __init__(self):
        self.logger = logging.getLogger("qtm3.component_analyzer")
    
    def analyze_component(self, component_info: Dict[str, Any]) -> ComponentAnalysis:
        """Comprehensive component analysis"""
        file_path = Path(component_info.get('file_path', ''))
        
        # Extract structural information
        structure = self._analyze_structure(file_path)
        
        # Extract behavioral patterns
        behavior = self._analyze_behavior(file_path)
        
        # Extract user interaction patterns
        interactions = self._analyze_interactions(file_path)
        
        # Extract dependencies and relationships
        relationships = self._analyze_relationships(file_path)
        
        return ComponentAnalysis(
            structure=structure,
            behavior=behavior,
            interactions=interactions,
            relationships=relationships,
            component_info=component_info
        )
    
    def _analyze_structure(self, file_path: Path) -> Dict[str, Any]:
        """Analyze component's structural elements"""
        if not file_path.exists():
            return {"classes": [], "functions": [], "interfaces": [], "data_structures": []}
        
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            
            classes = []
            functions = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    classes.append({
                        "name": node.name,
                        "methods": methods,
                        "docstring": ast.get_docstring(node),
                        "is_abstract": any(isinstance(n, ast.FunctionDef) and 
                                         any(isinstance(d, ast.Name) and d.id == 'abstractmethod' 
                                             for d in getattr(n, 'decorator_list', []))
                                         for n in node.body)
                    })
                elif isinstance(node, ast.FunctionDef) and not hasattr(node, 'parent_class'):
                    functions.append({
                        "name": node.name,
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node),
                        "is_private": node.name.startswith('_')
                    })
                elif isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    imports.extend([f"{module}.{alias.name}" for alias in node.names])
            
            return {
                "classes": classes,
                "functions": functions,
                "imports": imports,
                "total_lines": len(content.split('\n')) if content else 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze structure of {file_path}: {e}")
            return {"classes": [], "functions": [], "interfaces": [], "data_structures": []}
    
    def _analyze_behavior(self, file_path: Path) -> Dict[str, Any]:
        """Analyze component's behavioral patterns"""
        if not file_path.exists():
            return {"primary_behaviors": [], "side_effects": [], "state_changes": [], "event_handling": []}
        
        try:
            content = file_path.read_text()
            
            # Look for common behavioral patterns
            primary_behaviors = []
            side_effects = []
            state_changes = []
            event_handling = []
            
            # Detect CRUD operations
            if re.search(r'(create|insert|add)', content, re.IGNORECASE):
                primary_behaviors.append("create_operations")
            if re.search(r'(read|get|fetch|retrieve)', content, re.IGNORECASE):
                primary_behaviors.append("read_operations")
            if re.search(r'(update|modify|edit)', content, re.IGNORECASE):
                primary_behaviors.append("update_operations")
            if re.search(r'(delete|remove)', content, re.IGNORECASE):
                primary_behaviors.append("delete_operations")
            
            # Detect side effects
            if re.search(r'(logging|print|log)', content, re.IGNORECASE):
                side_effects.append("logging")
            if re.search(r'(notification|alert|email)', content, re.IGNORECASE):
                side_effects.append("notifications")
            if re.search(r'(file|write|save)', content, re.IGNORECASE):
                side_effects.append("file_operations")
            
            # Detect state changes
            if re.search(r'(self\.|state|status)', content):
                state_changes.append("internal_state")
            if re.search(r'(database|db|sql)', content, re.IGNORECASE):
                state_changes.append("persistent_state")
            
            # Detect event handling
            if re.search(r'(handle|process|on_|event)', content, re.IGNORECASE):
                event_handling.append("event_processing")
            if re.search(r'(message|signal|callback)', content, re.IGNORECASE):
                event_handling.append("message_handling")
            
            return {
                "primary_behaviors": primary_behaviors,
                "side_effects": side_effects,
                "state_changes": state_changes,
                "event_handling": event_handling
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze behavior of {file_path}: {e}")
            return {"primary_behaviors": [], "side_effects": [], "state_changes": [], "event_handling": []}
    
    def _analyze_interactions(self, file_path: Path) -> Dict[str, Any]:
        """Analyze how users interact with component"""
        if not file_path.exists():
            return {"input_methods": [], "output_formats": [], "user_touchpoints": [], "interaction_patterns": []}
        
        try:
            content = file_path.read_text()
            
            input_methods = []
            output_formats = []
            user_touchpoints = []
            interaction_patterns = []
            
            # Detect input methods
            if re.search(r'(input|stdin|raw_input)', content, re.IGNORECASE):
                input_methods.append("direct_input")
            if re.search(r'(command|cli|argv)', content, re.IGNORECASE):
                input_methods.append("command_line")
            if re.search(r'(json|dict|message)', content, re.IGNORECASE):
                input_methods.append("structured_data")
            if re.search(r'(file|path|read)', content, re.IGNORECASE):
                input_methods.append("file_input")
            
            # Detect output formats
            if re.search(r'(print|stdout|output)', content, re.IGNORECASE):
                output_formats.append("console_output")
            if re.search(r'(json|dumps)', content, re.IGNORECASE):
                output_formats.append("json_output")
            if re.search(r'(return|response)', content, re.IGNORECASE):
                output_formats.append("return_values")
            if re.search(r'(write|save|file)', content, re.IGNORECASE):
                output_formats.append("file_output")
            
            # Detect user touchpoints
            if re.search(r'(ui|interface|gui)', content, re.IGNORECASE):
                user_touchpoints.append("user_interface")
            if re.search(r'(api|endpoint|service)', content, re.IGNORECASE):
                user_touchpoints.append("api_interface")
            if re.search(r'(cli|command)', content, re.IGNORECASE):
                user_touchpoints.append("command_interface")
            if re.search(r'(config|settings)', content, re.IGNORECASE):
                user_touchpoints.append("configuration")
            
            # Detect interaction patterns
            if re.search(r'(async|await|thread)', content, re.IGNORECASE):
                interaction_patterns.append("asynchronous")
            if re.search(r'(request|response|http)', content, re.IGNORECASE):
                interaction_patterns.append("request_response")
            if re.search(r'(stream|flow|pipe)', content, re.IGNORECASE):
                interaction_patterns.append("streaming")
            
            return {
                "input_methods": input_methods,
                "output_formats": output_formats,
                "user_touchpoints": user_touchpoints,
                "interaction_patterns": interaction_patterns
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze interactions of {file_path}: {e}")
            return {"input_methods": [], "output_formats": [], "user_touchpoints": [], "interaction_patterns": []}
    
    def _analyze_relationships(self, file_path: Path) -> Dict[str, Any]:
        """Analyze dependencies and relationships"""
        if not file_path.exists():
            return {"dependencies": [], "collaborators": [], "inheritance": []}
        
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            
            dependencies = []
            collaborators = []
            inheritance = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    dependencies.extend([alias.name for alias in node.names])
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    dependencies.extend([f"{module}.{alias.name}" for alias in node.names])
                elif isinstance(node, ast.ClassDef):
                    # Check for inheritance
                    if node.bases:
                        inheritance.extend([base.id if isinstance(base, ast.Name) else str(base) 
                                          for base in node.bases])
                    
                    # Look for collaborating classes in method calls
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                            if isinstance(child.func.value, ast.Name):
                                collaborators.append(child.func.value.id)
            
            return {
                "dependencies": list(set(dependencies)),
                "collaborators": list(set(collaborators)),
                "inheritance": list(set(inheritance))
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze relationships of {file_path}: {e}")
            return {"dependencies": [], "collaborators": [], "inheritance": []}


class StoryGenerator:
    """Generates user stories using AI reasoning"""
    
    def __init__(self):
        self.logger = logging.getLogger("qtm3.story_generator")
    
    def generate_story(self, analysis: ComponentAnalysis) -> Dict[str, Any]:
        """Generate user story from component analysis"""
        # Prepare context for AI reasoning
        context = self._prepare_context(analysis)
        
        # Generate story using template-based approach (Phase 1 implementation)
        story_data = self._generate_template_story(context)
        
        return story_data
    
    def _prepare_context(self, analysis: ComponentAnalysis) -> Dict[str, Any]:
        """Prepare analysis context for story generation"""
        return {
            'component_name': analysis.component_info.get('name', 'Unknown'),
            'component_type': analysis.component_info.get('type', 'module'),
            'structure_summary': self._summarize_structure(analysis.structure),
            'behavior_summary': self._summarize_behavior(analysis.behavior),
            'interaction_summary': self._summarize_interactions(analysis.interactions),
            'complexity_score': self._calculate_complexity(analysis)
        }
    
    def _summarize_structure(self, structure: Dict[str, Any]) -> str:
        """Create readable summary of component structure"""
        parts = []
        
        if structure.get('classes'):
            class_count = len(structure['classes'])
            parts.append(f"{class_count} class{'es' if class_count > 1 else ''}")
        
        if structure.get('functions'):
            func_count = len(structure['functions'])
            parts.append(f"{func_count} function{'s' if func_count > 1 else ''}")
        
        if structure.get('total_lines'):
            parts.append(f"{structure['total_lines']} lines")
        
        return ", ".join(parts) if parts else "Simple module"
    
    def _summarize_behavior(self, behavior: Dict[str, Any]) -> str:
        """Create readable summary of component behavior"""
        behaviors = behavior.get('primary_behaviors', [])
        if not behaviors:
            return "No clear behavioral patterns"
        
        behavior_map = {
            'create_operations': 'creates data',
            'read_operations': 'reads/retrieves data', 
            'update_operations': 'updates data',
            'delete_operations': 'deletes data'
        }
        
        readable_behaviors = [behavior_map.get(b, b) for b in behaviors]
        return ", ".join(readable_behaviors)
    
    def _summarize_interactions(self, interactions: Dict[str, Any]) -> str:
        """Create readable summary of user interactions"""
        touchpoints = interactions.get('user_touchpoints', [])
        if not touchpoints:
            return "Internal component with no direct user interaction"
        
        touchpoint_map = {
            'user_interface': 'UI interface',
            'api_interface': 'API endpoints',
            'command_interface': 'command-line interface',
            'configuration': 'configuration files'
        }
        
        readable_touchpoints = [touchpoint_map.get(t, t) for t in touchpoints]
        return ", ".join(readable_touchpoints)
    
    def _calculate_complexity(self, analysis: ComponentAnalysis) -> float:
        """Calculate component complexity score (0.0 to 1.0)"""
        structure = analysis.structure
        behavior = analysis.behavior
        interactions = analysis.interactions
        
        # Base complexity on various factors
        complexity = 0.0
        
        # Structure complexity
        class_count = len(structure.get('classes', []))
        function_count = len(structure.get('functions', []))
        complexity += min((class_count + function_count) / 20, 0.3)
        
        # Behavioral complexity
        behavior_count = sum(len(behaviors) for behaviors in behavior.values())
        complexity += min(behavior_count / 15, 0.3)
        
        # Interaction complexity
        interaction_count = sum(len(interactions_list) for interactions_list in interactions.values())
        complexity += min(interaction_count / 10, 0.4)
        
        return min(complexity, 1.0)
    
    def _generate_template_story(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate user story using template-based approach"""
        component_name = context['component_name']
        component_type = context['component_type']
        interaction_summary = context['interaction_summary']
        behavior_summary = context['behavior_summary']
        complexity_score = context['complexity_score']
        
        # Determine engagement type
        if "UI interface" in interaction_summary or "command-line interface" in interaction_summary:
            engagement = "direct"
        else:
            engagement = "proxy"
        
        # Generate user story based on component type and behavior
        if component_type == "agent":
            user_story = f"As a user I want {component_name} to handle {behavior_summary} so that I can focus on higher-level tasks"
            primitive_value = "Task automation and cognitive load reduction"
            expression = "Seamless background processing with clear status feedback"
        elif "database" in behavior_summary or "persistent_state" in behavior_summary:
            user_story = f"As a user I want {component_name} to reliably store and retrieve my data so that my information is preserved and accessible"
            primitive_value = "Data persistence and reliability"
            expression = "Confident data storage with fast retrieval"
        elif "command" in interaction_summary:
            user_story = f"As a user I want {component_name} to provide clear command-line tools so that I can efficiently accomplish tasks"
            primitive_value = "Efficient task execution"
            expression = "Intuitive commands with helpful feedback"
        else:
            # Generic fallback
            user_story = f"As a user I want {component_name} to {behavior_summary} so that my workflow is enhanced"
            primitive_value = "Workflow enhancement"
            expression = "Smooth integration with existing processes"
        
        # Generate touch points based on interactions
        touch_points = []
        if "command_interface" in interaction_summary:
            touch_points.append("Command-line interface")
        if "api_interface" in interaction_summary:
            touch_points.append("API endpoints")
        if "user_interface" in interaction_summary:
            touch_points.append("User interface")
        if "configuration" in interaction_summary:
            touch_points.append("Configuration files")
        if not touch_points:
            touch_points.append("Internal interfaces")
        
        return {
            "user_story": user_story,
            "engagement": engagement,
            "touch_points": touch_points,
            "primitive_value": primitive_value,
            "expression": expression
        }


class StoryQualityAssessor:
    """Assesses quality of generated user stories"""
    
    def __init__(self):
        self.logger = logging.getLogger("qtm3.story_quality_assessor")
    
    def assess_quality(self, story_data: Dict[str, Any]) -> QualityScore:
        """Comprehensive quality assessment"""
        # Check story format compliance
        format_score = self._assess_format(story_data)
        
        # Check story clarity and specificity
        clarity_score = self._assess_clarity(story_data)
        
        # Check value proposition strength
        value_score = self._assess_value_proposition(story_data)
        
        # Check touchpoint relevance
        touchpoint_score = self._assess_touchpoints(story_data)
        
        overall_score = (
            format_score * 0.2 +
            clarity_score * 0.3 +
            value_score * 0.3 +
            touchpoint_score * 0.2
        )
        
        return QualityScore(
            overall_score=overall_score,
            format_score=format_score,
            clarity_score=clarity_score,
            value_score=value_score,
            touchpoint_score=touchpoint_score,
            confidence=min(overall_score, 0.95)  # Cap confidence
        )
    
    def _assess_format(self, story_data: Dict[str, Any]) -> float:
        """Assess user story format compliance"""
        user_story = story_data.get('user_story', '')
        
        # Check for required format elements
        has_as_a = 'As a' in user_story or 'As an' in user_story
        has_i_want = 'I want' in user_story
        has_so_that = 'so that' in user_story
        
        format_elements = sum([has_as_a, has_i_want, has_so_that])
        return format_elements / 3.0
    
    def _assess_clarity(self, story_data: Dict[str, Any]) -> float:
        """Assess story clarity and specificity"""
        user_story = story_data.get('user_story', '')
        primitive_value = story_data.get('primitive_value', '')
        
        # Check length and detail
        story_length_score = min(len(user_story.split()) / 15, 1.0)  # Optimal ~15 words
        value_clarity_score = min(len(primitive_value.split()) / 8, 1.0)  # Clear value description
        
        # Check for vague terms
        vague_terms = ['thing', 'stuff', 'something', 'anything', 'whatever']
        vague_penalty = sum(1 for term in vague_terms if term in user_story.lower()) * 0.2
        
        clarity_score = (story_length_score + value_clarity_score) / 2
        return max(clarity_score - vague_penalty, 0.0)
    
    def _assess_value_proposition(self, story_data: Dict[str, Any]) -> float:
        """Assess strength of value proposition"""
        user_story = story_data.get('user_story', '')
        primitive_value = story_data.get('primitive_value', '')
        expression = story_data.get('expression', '')
        
        # Check for clear benefit articulation
        benefit_indicators = ['so that', 'because', 'in order to', 'enabling', 'allowing']
        has_clear_benefit = any(indicator in user_story.lower() for indicator in benefit_indicators)
        
        # Check primitive value specificity
        value_words = ['efficiency', 'automation', 'clarity', 'control', 'confidence', 'reliability']
        has_concrete_value = any(word in primitive_value.lower() for word in value_words)
        
        # Check expression tangibility
        has_tangible_expression = len(expression.split()) > 3
        
        value_elements = sum([has_clear_benefit, has_concrete_value, has_tangible_expression])
        return value_elements / 3.0
    
    def _assess_touchpoints(self, story_data: Dict[str, Any]) -> float:
        """Assess touchpoint relevance and completeness"""
        touch_points = story_data.get('touch_points', [])
        
        if not touch_points:
            return 0.0
        
        # Check for reasonable number of touchpoints
        count_score = min(len(touch_points) / 3, 1.0)  # Optimal 1-3 touchpoints
        
        # Check for specific, actionable touchpoints
        generic_touchpoints = ['interface', 'system', 'component']
        specificity_score = 1.0 - (sum(1 for tp in touch_points 
                                     if any(generic in tp.lower() for generic in generic_touchpoints)) 
                                  / len(touch_points))
        
        return (count_score + specificity_score) / 2


class UserStorySynthesiserAgent(Agent):
    """Agent responsible for generating and maintaining user stories"""
    
    def __init__(self, db_path: Path = None):
        super().__init__("user_story_synthesiser")
        
        # Initialize core components
        self.db_path = db_path or Path.home() / "qtm3" / "core.db"
        self.registry = ComponentRegistry(self.db_path)
        self.component_analyzer = ComponentAnalyzer()
        self.story_generator = StoryGenerator()
        self.quality_assessor = StoryQualityAssessor()
        
        self.logger.info("User-Story Synthesiser Agent initialized")
    
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle USS requests"""
        action = message.get("action")
        
        try:
            if action == "synthesize_story":
                return self._synthesize_component_story(message.get("component_info"))
            elif action == "update_story":
                return self._update_existing_story(message.get("component_id"), message.get("changes"))
            elif action == "validate_story":
                return self._validate_story_quality(message.get("story_data"))
            elif action == "get_component_story":
                return self._get_component_story(message.get("component_id"))
            elif action == "batch_analyze":
                return self._batch_analyze_components(message.get("component_list"))
            elif action == "get_coverage_stats":
                return self._get_coverage_stats()
            else:
                return {"error": f"Unknown action: {action}"}
        
        except Exception as e:
            self.logger.error(f"Error handling USS message: {e}")
            return {"error": str(e)}
    
    def _synthesize_component_story(self, component_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate user story for component"""
        try:
            # Register component if not already registered
            component_id = self.registry.register_component(component_info)
            
            # Log analysis start
            log_id = self.registry.log_analysis(component_id, 'initial', 'running')
            
            # Analyze component structure and purpose
            analysis = self.component_analyzer.analyze_component(component_info)
            
            # Generate user story using AI reasoning
            story_data = self.story_generator.generate_story(analysis)
            
            # Assess quality of generated story
            quality_score = self.quality_assessor.assess_quality(story_data)
            
            # Package result
            result = {
                "component_id": component_id,
                "component": component_info['name'],
                "user_story": story_data['user_story'],
                "engagement": story_data['engagement'],
                "touch_points": story_data['touch_points'],
                "primitive_value": story_data['primitive_value'],
                "expression": story_data['expression'],
                "quality_score": quality_score.overall_score,
                "confidence": quality_score.confidence,
                "analysis_metadata": {
                    "analyzed_at": datetime.now().isoformat(),
                    "analyzer_version": "1.0",
                    "component_analysis": analysis.to_dict(),
                    "quality_breakdown": quality_score.to_dict()
                }
            }
            
            # Store user story in registry
            story_id = self.registry.store_user_story(component_id, result)
            result["story_id"] = story_id
            
            # Log analysis completion
            self.registry.log_analysis(component_id, 'initial', 'completed', result)
            
            self.logger.info(f"Successfully synthesized story for {component_info['name']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to synthesize story: {e}")
            if 'component_id' in locals():
                self.registry.log_analysis(component_id, 'initial', 'failed', error_message=str(e))
            return {"error": str(e)}
    
    def _update_existing_story(self, component_id: str, changes: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing user story with changes"""
        try:
            # Get current story
            current_story = self.registry.get_component_story(component_id)
            if not current_story:
                return {"error": f"No story found for component {component_id}"}
            
            # Re-analyze if component has changed
            component = self.registry.get_component(component_id)
            if component:
                component_info = {
                    'name': component['name'],
                    'type': component['type'],
                    'file_path': component['file_path']
                }
                
                # Re-run analysis
                return self._synthesize_component_story(component_info)
            else:
                return {"error": f"Component {component_id} not found"}
                
        except Exception as e:
            self.logger.error(f"Failed to update story: {e}")
            return {"error": str(e)}
    
    def _validate_story_quality(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quality of provided story data"""
        try:
            quality_score = self.quality_assessor.assess_quality(story_data)
            
            return {
                "valid": quality_score.overall_score > 0.6,
                "quality_score": quality_score.overall_score,
                "quality_breakdown": quality_score.to_dict(),
                "recommendations": self._generate_quality_recommendations(quality_score)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to validate story quality: {e}")
            return {"error": str(e)}
    
    def _get_component_story(self, component_id: str) -> Dict[str, Any]:
        """Retrieve current user story for component"""
        try:
            story = self.registry.get_component_story(component_id)
            if story:
                return {"success": True, "story": story}
            else:
                return {"success": False, "message": "No story found"}
                
        except Exception as e:
            self.logger.error(f"Failed to get component story: {e}")
            return {"error": str(e)}
    
    def _batch_analyze_components(self, component_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze multiple components in batch"""
        try:
            results = []
            for component_info in component_list:
                result = self._synthesize_component_story(component_info)
                results.append(result)
            
            return {
                "batch_complete": True,
                "total_processed": len(results),
                "successful": len([r for r in results if "error" not in r]),
                "failed": len([r for r in results if "error" in r]),
                "results": results
            }
            
        except Exception as e:
            self.logger.error(f"Failed batch analysis: {e}")
            return {"error": str(e)}
    
    def _get_coverage_stats(self) -> Dict[str, Any]:
        """Get USS coverage statistics"""
        try:
            stats = self.registry.get_coverage_stats()
            return {"success": True, "stats": stats}
            
        except Exception as e:
            self.logger.error(f"Failed to get coverage stats: {e}")
            return {"error": str(e)}
    
    def _generate_quality_recommendations(self, quality_score: QualityScore) -> List[str]:
        """Generate recommendations for improving story quality"""
        recommendations = []
        
        if quality_score.format_score < 0.8:
            recommendations.append("Ensure story follows 'As a [user] I want [goal] so that [benefit]' format")
        
        if quality_score.clarity_score < 0.7:
            recommendations.append("Make the story more specific and avoid vague language")
        
        if quality_score.value_score < 0.7:
            recommendations.append("Clearly articulate the user benefit and value proposition")
        
        if quality_score.touchpoint_score < 0.6:
            recommendations.append("Define specific, actionable touchpoints for user interaction")
        
        return recommendations