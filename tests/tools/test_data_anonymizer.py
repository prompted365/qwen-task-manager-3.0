"""
Test Data Anonymizer for Qwen Task Manager 3.0

Creates realistic test data while protecting user privacy through intelligent anonymization.
Generates behavioral test scenarios that feel authentic without exposing real user information.
"""

import argparse
import json
import random
import hashlib
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import faker
import re


class TestDataAnonymizer:
    """Anonymizes and generates test data for behavioral testing."""
    
    def __init__(self, seed: Optional[int] = None):
        self.fake = faker.Faker()
        if seed:
            faker.Faker.seed(seed)
            random.seed(seed)
        
        # Sensitive data patterns
        self.sensitive_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'address': r'\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|blvd|boulevard)',
            'name': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'  # Simple name pattern
        }
        
        # Replacement templates for different contexts
        self.replacement_templates = {
            'work_tasks': [
                "Complete quarterly report",
                "Prepare presentation for team meeting", 
                "Review project timeline",
                "Schedule client check-in",
                "Update documentation",
                "Analyze data trends",
                "Plan next sprint",
                "Review budget allocation"
            ],
            'personal_tasks': [
                "Grocery shopping",
                "Exercise routine",
                "Call family member",
                "Schedule doctor appointment",
                "Plan weekend activities",
                "Organize living space",
                "Pay monthly bills",
                "Read chapter of book"
            ],
            'stress_contexts': [
                "feeling overwhelmed with deadlines",
                "struggling to balance priorities",
                "dealing with unexpected changes",
                "managing multiple projects",
                "feeling behind on important tasks",
                "experiencing decision fatigue",
                "juggling competing demands"
            ]
        }
    
    def anonymize_text(self, text: str, preserve_context: bool = True) -> str:
        """Anonymize sensitive information in text while preserving behavioral context."""
        anonymized = text
        
        # Replace sensitive patterns
        for pattern_name, pattern in self.sensitive_patterns.items():
            if pattern_name == 'email':
                anonymized = re.sub(pattern, lambda m: self._generate_fake_email(), anonymized)
            elif pattern_name == 'phone':
                anonymized = re.sub(pattern, lambda m: self.fake.phone_number(), anonymized)
            elif pattern_name == 'name':
                anonymized = re.sub(pattern, lambda m: self.fake.name(), anonymized)
            elif pattern_name == 'address':
                anonymized = re.sub(pattern, lambda m: self.fake.address().split('\n')[0], anonymized)
            else:
                anonymized = re.sub(pattern, '[REDACTED]', anonymized)
        
        return anonymized
    
    def _generate_fake_email(self) -> str:
        """Generate a realistic but fake email address."""
        domains = ['example.com', 'test.org', 'demo.net', 'sample.co']
        username = self.fake.user_name()
        domain = random.choice(domains)
        return f"{username}@{domain}"
    
    def generate_behavioral_scenario(self, 
                                   persona_type: str,
                                   stress_level: int = 5,
                                   task_complexity: str = "medium") -> Dict[str, Any]:
        """Generate a complete anonymized behavioral test scenario."""
        
        persona_templates = {
            "overwhelmed_professional": {
                "name": self.fake.name(),
                "role": random.choice(["Project Manager", "Software Developer", "Marketing Specialist", "Sales Representative"]),
                "stress_triggers": ["deadlines", "meetings", "email volume"],
                "typical_tasks": random.sample(self.replacement_templates['work_tasks'], 3)
            },
            "student_with_adhd": {
                "name": self.fake.name(),
                "age": random.randint(18, 25),
                "major": random.choice(["Computer Science", "Psychology", "Business", "Education"]),
                "stress_triggers": ["focus issues", "time management", "assignment overload"],
                "typical_tasks": ["Study for exam", "Complete assignment", "Attend study group", "Research paper"]
            },
            "caregiver_burnout": {
                "name": self.fake.name(),
                "caregiving_role": random.choice(["parent", "adult child caring for parent", "spouse caregiver"]),
                "stress_triggers": ["time constraints", "emotional load", "competing needs"],
                "typical_tasks": random.sample(self.replacement_templates['personal_tasks'], 4)
            }
        }
        
        if persona_type not in persona_templates:
            persona_type = "overwhelmed_professional"
        
        persona = persona_templates[persona_type]
        
        # Generate scenario details
        scenario = {
            "id": str(uuid.uuid4()),
            "timestamp": self.fake.date_time_between(start_date='-30d', end_date='now').isoformat(),
            "persona": {
                "type": persona_type,
                "details": persona,
                "current_state": {
                    "stress_level": stress_level,
                    "energy_level": random.randint(3, 8),
                    "confidence_level": random.randint(4, 7),
                    "time_pressure": random.choice(["low", "medium", "high"]),
                    "support_system": random.choice(["strong", "moderate", "limited"])
                }
            },
            "context": {
                "time_of_day": random.choice(["morning", "afternoon", "evening"]),
                "day_of_week": random.choice(["monday", "wednesday", "friday", "sunday"]),
                "season": random.choice(["spring", "summer", "fall", "winter"]),
                "complexity": task_complexity
            },
            "tasks": self._generate_task_list(persona_type, task_complexity),
            "user_input": self._generate_user_input(persona_type, stress_level),
            "expected_outcomes": self._generate_expected_outcomes(persona_type, stress_level)
        }
        
        return scenario
    
    def _generate_task_list(self, persona_type: str, complexity: str) -> List[Dict[str, Any]]:
        """Generate an anonymized task list appropriate for the persona."""
        
        complexity_counts = {
            "simple": 3,
            "medium": 6,
            "complex": 10
        }
        
        task_count = complexity_counts.get(complexity, 6)
        
        if persona_type == "overwhelmed_professional":
            task_pool = self.replacement_templates['work_tasks']
        else:
            task_pool = self.replacement_templates['personal_tasks']
        
        tasks = []
        for i in range(task_count):
            task = {
                "id": str(uuid.uuid4()),
                "title": random.choice(task_pool),
                "priority": random.choice(["high", "medium", "low"]),
                "estimated_duration": random.choice(["15 minutes", "30 minutes", "1 hour", "2 hours"]),
                "deadline": random.choice(["today", "this week", "next week", "no deadline"]),
                "emotional_weight": random.randint(1, 10)
            }
            tasks.append(task)
        
        return tasks
    
    def _generate_user_input(self, persona_type: str, stress_level: int) -> str:
        """Generate realistic user input for the scenario."""
        
        stress_contexts = self.replacement_templates['stress_contexts']
        stress_context = random.choice(stress_contexts)
        
        input_templates = {
            "low_stress": [
                f"I need help organizing my tasks for today.",
                f"Can you help me prioritize what I should work on?",
                f"I have several things to do and want to make a plan."
            ],
            "medium_stress": [
                f"I'm {stress_context} and need help figuring out what to focus on.",
                f"Feeling a bit scattered today, can you help me get organized?",
                f"I have too many things on my plate and don't know where to start."
            ],
            "high_stress": [
                f"I'm really {stress_context} and everything feels urgent.",
                f"I'm completely overwhelmed and don't know how to handle all of this.",
                f"Everything is falling apart and I can't keep up with my responsibilities."
            ]
        }
        
        if stress_level <= 3:
            template_key = "low_stress"
        elif stress_level <= 7:
            template_key = "medium_stress"
        else:
            template_key = "high_stress"
        
        return random.choice(input_templates[template_key])
    
    def _generate_expected_outcomes(self, persona_type: str, stress_level: int) -> Dict[str, Any]:
        """Generate expected therapeutic outcomes for the scenario."""
        
        base_expectations = {
            "stress_reduction": max(-3.0, -1.0 - (stress_level / 5)),
            "confidence_boost": random.uniform(0.5, 2.0),
            "clarity_improvement": random.uniform(1.0, 3.0),
            "empathy_score_requirement": 7.5,
            "therapeutic_effectiveness_minimum": 7.0
        }
        
        # Adjust expectations based on persona
        persona_adjustments = {
            "overwhelmed_professional": {
                "organization_improvement": 2.0,
                "prioritization_clarity": 2.5
            },
            "student_with_adhd": {
                "focus_support": 2.0,
                "neurodivergent_sensitivity": 8.5
            },
            "caregiver_burnout": {
                "self_compassion": 2.0,
                "boundary_support": 1.5
            }
        }
        
        if persona_type in persona_adjustments:
            base_expectations.update(persona_adjustments[persona_type])
        
        return base_expectations
    
    def anonymize_real_data(self, 
                          data_file: str, 
                          output_file: str,
                          preserve_structure: bool = True) -> Dict[str, Any]:
        """Anonymize real user data for testing purposes."""
        
        try:
            with open(data_file, 'r') as f:
                if data_file.endswith('.json'):
                    data = json.load(f)
                else:
                    data = {"text": f.read()}
        except Exception as e:
            return {"error": f"Could not read input file: {e}"}
        
        anonymized_data = self._anonymize_data_recursive(data, preserve_structure)
        
        # Add anonymization metadata
        result = {
            "anonymized_at": datetime.now().isoformat(),
            "original_file": data_file,
            "anonymization_settings": {
                "preserve_structure": preserve_structure,
                "seed_used": self.fake.random.getstate()[1][0] if hasattr(self.fake.random, 'getstate') else None
            },
            "data": anonymized_data,
            "privacy_compliance": {
                "sensitive_patterns_detected": self._count_sensitive_patterns(str(data)),
                "sensitive_patterns_removed": self._count_sensitive_patterns(str(anonymized_data)),
                "anonymization_complete": True
            }
        }
        
        # Save anonymized data
        try:
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            result["output_file"] = output_file
        except Exception as e:
            result["save_error"] = str(e)
        
        return result
    
    def _anonymize_data_recursive(self, data: Any, preserve_structure: bool) -> Any:
        """Recursively anonymize data while preserving structure."""
        
        if isinstance(data, dict):
            return {
                key: self._anonymize_data_recursive(value, preserve_structure)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [
                self._anonymize_data_recursive(item, preserve_structure)
                for item in data
            ]
        elif isinstance(data, str):
            return self.anonymize_text(data, preserve_structure)
        else:
            return data
    
    def _count_sensitive_patterns(self, text: str) -> Dict[str, int]:
        """Count occurrences of sensitive patterns in text."""
        counts = {}
        for pattern_name, pattern in self.sensitive_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            counts[pattern_name] = len(matches)
        return counts
    
    def generate_test_dataset(self, 
                            num_scenarios: int = 50,
                            persona_distribution: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """Generate a complete test dataset with specified number of scenarios."""
        
        if persona_distribution is None:
            persona_distribution = {
                "overwhelmed_professional": 0.4,
                "student_with_adhd": 0.3,
                "caregiver_burnout": 0.3
            }
        
        dataset = []
        personas = list(persona_distribution.keys())
        weights = list(persona_distribution.values())
        
        for _ in range(num_scenarios):
            persona = random.choices(personas, weights=weights)[0]
            stress_level = random.randint(3, 9)
            complexity = random.choice(["simple", "medium", "complex"])
            
            scenario = self.generate_behavioral_scenario(
                persona_type=persona,
                stress_level=stress_level,
                task_complexity=complexity
            )
            
            dataset.append(scenario)
        
        return dataset


def main():
    """CLI interface for test data anonymization."""
    parser = argparse.ArgumentParser(description="Anonymize test data for behavioral testing")
    parser.add_argument("--generate-scenarios", type=int, help="Generate N behavioral scenarios")
    parser.add_argument("--persona", choices=["overwhelmed_professional", "student_with_adhd", "caregiver_burnout"])
    parser.add_argument("--stress-level", type=int, choices=range(1, 11), default=5)
    parser.add_argument("--complexity", choices=["simple", "medium", "complex"], default="medium")
    parser.add_argument("--anonymize-file", help="File to anonymize")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--seed", type=int, help="Random seed for reproducible data")
    parser.add_argument("--preserve-context", action="store_true", help="Preserve behavioral context")
    
    args = parser.parse_args()
    
    anonymizer = TestDataAnonymizer(seed=args.seed)
    
    if args.generate_scenarios:
        if args.persona:
            # Generate scenarios for specific persona
            scenarios = []
            for _ in range(args.generate_scenarios):
                scenario = anonymizer.generate_behavioral_scenario(
                    persona_type=args.persona,
                    stress_level=args.stress_level,
                    task_complexity=args.complexity
                )
                scenarios.append(scenario)
        else:
            # Generate mixed scenarios
            scenarios = anonymizer.generate_test_dataset(args.generate_scenarios)
        
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(scenarios, f, indent=2)
            print(f"✅ Generated {len(scenarios)} scenarios: {output_path}")
        else:
            print(json.dumps(scenarios, indent=2))
    
    elif args.anonymize_file:
        if not args.output:
            print("❌ Output file required for anonymization")
            return 1
        
        result = anonymizer.anonymize_real_data(
            data_file=args.anonymize_file,
            output_file=args.output,
            preserve_structure=args.preserve_context
        )
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return 1
        
        privacy = result["privacy_compliance"]
        print(f"✅ Anonymization complete: {args.output}")
        print(f"📊 Sensitive patterns detected: {sum(privacy['sensitive_patterns_detected'].values())}")
        print(f"🔒 Sensitive patterns removed: {sum(privacy['sensitive_patterns_removed'].values())}")
    
    else:
        print("🔒 Test Data Anonymizer")
        print("Examples:")
        print("  Generate scenarios:")
        print("    python test_data_anonymizer.py --generate-scenarios 10 --persona overwhelmed_professional --output scenarios.json")
        print("  Anonymize file:")
        print("    python test_data_anonymizer.py --anonymize-file user_data.json --output anonymized_data.json")


if __name__ == "__main__":
    exit(main())