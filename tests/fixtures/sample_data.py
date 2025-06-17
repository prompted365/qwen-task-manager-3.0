"""
Test data and fixtures representing realistic user scenarios

This module provides authentic test data based on behavioral research and real user patterns.
The data represents diverse user types with different cognitive styles, energy patterns,
and behavioral challenges that our system needs to support effectively.

Key Principles:
- Realistic Brain Dumps: Actual messy inputs users provide
- Diverse User Profiles: ADHD, burnout, high-achiever, etc.
- Energy Pattern Variations: Morning person, night owl, irregular
- Behavioral Triggers: Avoidance, overwhelm, perfectionism
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

@dataclass
class UserProfile:
    """Represents a user with specific behavioral patterns and needs"""
    name: str
    cognitive_style: str  # "adhd", "burnout", "high_achiever", "perfectionist", "procrastinator"
    energy_pattern: str   # "morning_person", "night_owl", "irregular", "steady"
    common_triggers: List[str]  # What causes overwhelm/avoidance
    preferred_task_size: str    # "micro", "small", "medium", "large"
    behavioral_notes: str

# Realistic User Profiles
USER_PROFILES = {
    "alex_adhd": UserProfile(
        name="Alex",
        cognitive_style="adhd",
        energy_pattern="irregular",
        common_triggers=["perfectionism", "multi_step_tasks", "unclear_priorities"],
        preferred_task_size="micro",
        behavioral_notes="Hyperfocus periods followed by crashes. Needs dopamine wins. Executive function challenges with planning."
    ),
    
    "sarah_burnout": UserProfile(
        name="Sarah",
        cognitive_style="burnout",
        energy_pattern="steady_low",
        common_triggers=["overwhelm", "deadline_pressure", "self_criticism"],
        preferred_task_size="small",
        behavioral_notes="Recovering from workplace burnout. Low energy but steady. Needs self-compassion and gentle progress."
    ),
    
    "marcus_high_achiever": UserProfile(
        name="Marcus",
        cognitive_style="high_achiever",
        energy_pattern="morning_person",
        common_triggers=["perfectionism", "inefficiency", "unclear_impact"],
        preferred_task_size="large",
        behavioral_notes="Driven but prone to taking on too much. Needs prioritization help and boundary setting."
    ),
    
    "jamie_perfectionist": UserProfile(
        name="Jamie",
        cognitive_style="perfectionist",
        energy_pattern="night_owl",
        common_triggers=["ambiguity", "criticism", "time_pressure"],
        preferred_task_size="medium",
        behavioral_notes="Paralyzed by perfectionism. Needs permission to do 'good enough' work and start before ready."
    ),
    
    "taylor_procrastinator": UserProfile(
        name="Taylor",
        cognitive_style="procrastinator", 
        energy_pattern="deadline_driven",
        common_triggers=["boring_tasks", "no_deadline", "unclear_value"],
        preferred_task_size="small",
        behavioral_notes="Motivation follows interest and urgency. Needs deadline creation and interest injection."
    )
}

# Realistic Brain Dumps - Messy user inputs that need clarification
REALISTIC_BRAIN_DUMPS = {
    "adhd_overwhelm": {
        "raw_input": "fix website update docs call insurance about claim organize photos prepare presentation research pricing update linkedin profile clean desk write blog post about ai schedule dentist appointment backup computer review quarterly numbers",
        "context": "ADHD brain dump during overwhelm period",
        "expected_count": 12,  # Should be broken into many small tasks
        "energy_required": "mixed"
    },
    
    "burnout_minimal": {
        "raw_input": "maybe call sarah back about project if energy answer important emails organize desk a bit",
        "context": "Burnout recovery - very low energy, tentative language",
        "expected_count": 3,
        "energy_required": "low"
    },
    
    "high_achiever_packed": {
        "raw_input": "finish q4 analysis prepare board presentation review team performance data schedule 1:1s with direct reports update project roadmap research new market opportunities",
        "context": "High achiever trying to pack too much in",
        "expected_count": 6,
        "energy_required": "high"
    },
    
    "perfectionist_paralysis": {
        "raw_input": "write the perfect blog post about productivity that will really help people and showcase my expertise",
        "context": "Perfectionist stuck on one overwhelming task",
        "expected_count": 4,  # Should break into smaller steps
        "energy_required": "high"
    },
    
    "procrastinator_avoidance": {
        "raw_input": "taxes... ugh. also should probably update resume at some point. maybe clean out garage?",
        "context": "Procrastinator avoiding important but boring tasks",
        "expected_count": 3,
        "energy_required": "mixed"
    },
    
    "normal_day_planning": {
        "raw_input": "grocery shopping weekly review prep for tomorrow's meeting write thank you notes call mom review budget",
        "context": "Normal daily planning session",
        "expected_count": 6,
        "energy_required": "mixed"
    }
}

# Energy Pattern Data - Based on circadian research and user tracking
ENERGY_PATTERNS = {
    "morning_person_week": [
        # Monday through Sunday, hourly energy levels (physical, mental, emotional)
        {
            "day": "monday",
            "pattern": [
                {"hour": 6, "physical": 6, "mental": 7, "emotional": 6},
                {"hour": 8, "physical": 8, "mental": 9, "emotional": 7},
                {"hour": 10, "physical": 8, "mental": 9, "emotional": 8},
                {"hour": 12, "physical": 7, "mental": 7, "emotional": 7},
                {"hour": 14, "physical": 6, "mental": 6, "emotional": 6},
                {"hour": 16, "physical": 5, "mental": 5, "emotional": 6},
                {"hour": 18, "physical": 4, "mental": 4, "emotional": 5},
                {"hour": 20, "physical": 3, "mental": 3, "emotional": 4}
            ]
        }
        # Additional days would follow similar pattern
    ],
    
    "night_owl_week": [
        {
            "day": "monday", 
            "pattern": [
                {"hour": 6, "physical": 2, "mental": 2, "emotional": 3},
                {"hour": 8, "physical": 3, "mental": 3, "emotional": 4},
                {"hour": 10, "physical": 4, "mental": 5, "emotional": 5},
                {"hour": 12, "physical": 6, "mental": 6, "emotional": 6},
                {"hour": 14, "physical": 7, "mental": 7, "emotional": 7},
                {"hour": 16, "physical": 8, "mental": 8, "emotional": 7},
                {"hour": 18, "physical": 8, "mental": 8, "emotional": 8},
                {"hour": 20, "physical": 9, "mental": 9, "emotional": 8}
            ]
        }
    ],
    
    "adhd_irregular": [
        {
            "day": "monday",
            "pattern": [
                {"hour": 6, "physical": 2, "mental": 2, "emotional": 3},
                {"hour": 8, "physical": 3, "mental": 4, "emotional": 4},
                {"hour": 10, "physical": 9, "mental": 9, "emotional": 8},  # Hyperfocus
                {"hour": 12, "physical": 3, "mental": 2, "emotional": 4},  # Crash
                {"hour": 14, "physical": 4, "mental": 3, "emotional": 3},
                {"hour": 16, "physical": 7, "mental": 8, "emotional": 6},  # Second wind
                {"hour": 18, "physical": 4, "mental": 3, "emotional": 5},
                {"hour": 20, "physical": 2, "mental": 2, "emotional": 4}
            ]
        }
    ],
    
    "burnout_recovery": [
        {
            "day": "monday",
            "pattern": [
                {"hour": 6, "physical": 3, "mental": 2, "emotional": 2},
                {"hour": 8, "physical": 4, "mental": 3, "emotional": 3},
                {"hour": 10, "physical": 4, "mental": 4, "emotional": 4},
                {"hour": 12, "physical": 3, "mental": 3, "emotional": 3},
                {"hour": 14, "physical": 3, "mental": 3, "emotional": 4},
                {"hour": 16, "physical": 2, "mental": 2, "emotional": 3},
                {"hour": 18, "physical": 2, "mental": 2, "emotional": 2},
                {"hour": 20, "physical": 2, "mental": 2, "emotional": 3}
            ]
        }
    ]
}

# Task Completion Scenarios - Realistic daily completions
DAILY_COMPLETION_SCENARIOS = {
    "productive_day": {
        "completed_tasks": [
            {"title": "Review morning emails", "energy_used": "low", "satisfaction": 7},
            {"title": "Finish project proposal", "energy_used": "high", "satisfaction": 9},
            {"title": "Quick desk organization", "energy_used": "low", "satisfaction": 8},
            {"title": "Team check-in call", "energy_used": "medium", "satisfaction": 6},
            {"title": "Update project timeline", "energy_used": "medium", "satisfaction": 7}
        ],
        "energy_end_state": {"physical": 6, "mental": 5, "emotional": 8},
        "notes": "High satisfaction day with good energy management"
    },
    
    "struggle_day": {
        "completed_tasks": [
            {"title": "Check emails", "energy_used": "low", "satisfaction": 4},
            {"title": "Organize one folder", "energy_used": "low", "satisfaction": 6}
        ],
        "energy_end_state": {"physical": 3, "mental": 2, "emotional": 3},
        "notes": "Low energy day, minimal completion but some progress"
    },
    
    "hyperfocus_day": {
        "completed_tasks": [
            {"title": "Deep work on architecture design", "energy_used": "high", "satisfaction": 10},
            {"title": "Code implementation sprint", "energy_used": "high", "satisfaction": 9},
            {"title": "Documentation updates", "energy_used": "medium", "satisfaction": 7}
        ],
        "energy_end_state": {"physical": 2, "mental": 1, "emotional": 6},
        "notes": "ADHD hyperfocus session - high achievement but exhausting crash"
    },
    
    "balanced_day": {
        "completed_tasks": [
            {"title": "Morning planning session", "energy_used": "low", "satisfaction": 7},
            {"title": "Client presentation", "energy_used": "high", "satisfaction": 8},
            {"title": "Lunch walk", "energy_used": "low", "satisfaction": 9},
            {"title": "Admin tasks batch", "energy_used": "medium", "satisfaction": 6},
            {"title": "Evening reflection", "energy_used": "low", "satisfaction": 8}
        ],
        "energy_end_state": {"physical": 6, "mental": 6, "emotional": 7},
        "notes": "Well-balanced day with energy restoration activities"
    }
}

# Context Tagging Test Data - Files and expected tags
CONTEXT_TAGGING_TEST_DATA = {
    "project_files": {
        "README.md": ["documentation", "project_overview", "onboarding"],
        "package.json": ["dependencies", "configuration", "nodejs"],
        "src/components/TaskList.tsx": ["frontend", "react", "ui_component"],
        "tests/unit/test_agents.py": ["testing", "python", "unit_tests"],
        "docs/api/endpoints.md": ["api", "documentation", "backend"],
        "config/database.yml": ["configuration", "database", "backend"],
        "scripts/deploy.sh": ["deployment", "automation", "devops"],
        ".env.example": ["configuration", "environment", "secrets"],
        "Dockerfile": ["containerization", "deployment", "docker"],
        "meeting_notes_2024_01_15.md": ["meeting", "notes", "project_discussion"]
    },
    
    "accuracy_test_set": [
        # Each entry: (file_path, content_snippet, expected_tags)
        ("src/auth/login.py", "def authenticate_user(username, password):", ["authentication", "backend", "security"]),
        ("docs/user_guide.md", "# How to create your first task", ["documentation", "user_guide", "onboarding"]),
        ("tests/integration/test_api.py", "def test_task_creation_endpoint():", ["testing", "api", "integration"]),
        ("config/nginx.conf", "server { listen 80;", ["configuration", "web_server", "infrastructure"]),
        ("src/ui/Dashboard.vue", "<template><div class='dashboard'>", ["frontend", "vue", "ui_component"])
    ]
}

# AI Response Quality Examples
AI_RESPONSE_EXAMPLES = {
    "high_quality_reflection": """
    You tackled three meaningful tasks today, which is solid progress given your energy levels were lower than usual.

    The client call you completed this morning was particularly important - I noticed you'd been putting it off for a few days. Getting that done probably lifted a weight off your shoulders.

    Your pattern shows you're most focused between 10-11 AM. Consider scheduling your most challenging tasks during that window tomorrow.

    For tonight: You mentioned feeling scattered. Maybe try that 5-minute desk clear you find satisfying? Small wins like that can help reset your mental space.
    """,
    
    "medium_quality_reflection": """
    Good work today! You completed several tasks and made progress on your goals.
    
    I noticed you finished the project update and handled some emails. The client call was also important to get done.
    
    Tomorrow you might want to focus on the presentation since it's due soon. Try to start early when your energy is better.
    """,
    
    "low_quality_reflection": """
    You did some tasks today. Keep it up tomorrow.
    """,
    
    "high_quality_clarification": [
        {
            "title": "Identify website performance issues",
            "description": "Run site speed test, check error logs, document specific problems affecting user experience",
            "timer": 30,
            "energy_required": "medium",
            "priority": 8
        },
        {
            "title": "Fix critical website bugs",
            "description": "Address security vulnerabilities and broken functionality identified in audit",
            "timer": 60,
            "energy_required": "high",
            "priority": 9
        },
        {
            "title": "Update website documentation",
            "description": "Document recent changes and update deployment instructions",
            "timer": 20,
            "energy_required": "low",
            "priority": 5
        }
    ],
    
    "poor_quality_clarification": [
        {
            "title": "Fix website",
            "description": "Make the website work better",
            "timer": 0,
            "energy_required": "unknown",
            "priority": 5
        }
    ]
}

# Behavioral Intervention Test Scenarios
BEHAVIORAL_SCENARIOS = {
    "perfectionism_intervention": {
        "user_input": "I need to write the perfect blog post that will establish me as a thought leader",
        "user_profile": "jamie_perfectionist",
        "expected_interventions": [
            "break_into_smaller_steps",
            "permission_to_be_imperfect", 
            "focus_on_progress_over_perfection",
            "set_time_limits"
        ],
        "quality_indicators": [
            "suggests starting with outline",
            "mentions 'good enough' or similar",
            "includes time boxing suggestion",
            "acknowledges perfectionism struggle"
        ]
    },
    
    "overwhelm_intervention": {
        "user_input": "I have like 20 things to do and I don't know where to start everything is urgent",
        "user_profile": "alex_adhd",
        "expected_interventions": [
            "acknowledge_overwhelm",
            "suggest_priority_filtering",
            "limit_immediate_focus",
            "provide_starting_point"
        ],
        "quality_indicators": [
            "validates feeling overwhelmed",
            "suggests focusing on 2-3 items max",
            "provides specific starting suggestion",
            "explains prioritization rationale"
        ]
    },
    
    "low_energy_intervention": {
        "user_input": "I'm exhausted but I have deadlines approaching",
        "user_profile": "sarah_burnout",
        "expected_interventions": [
            "acknowledge_energy_state",
            "suggest_energy_appropriate_tasks",
            "encourage_self_compassion",
            "realistic_planning"
        ],
        "quality_indicators": [
            "validates exhaustion",
            "suggests low-energy tasks",
            "mentions rest/recovery",
            "adjusts expectations realistically"
        ]
    }
}

# Performance Test Data
PERFORMANCE_TEST_SCENARIOS = {
    "latency_test_inputs": [
        "complex project planning with multiple dependencies and stakeholders",
        "organize all my digital files and photos from the last year",
        "prepare comprehensive presentation for board meeting next week",
        "research and write detailed market analysis report",
        "plan and organize team retreat including venue booking and activities"
    ],
    
    "accuracy_baseline": {
        "context_tagging": {
            "expected_accuracy": 0.85,
            "test_files": 50,
            "tag_categories": ["project", "language", "function", "documentation"]
        },
        "task_prioritization": {
            "expected_consistency": 0.75,  # 75% consistency across sessions
            "test_scenarios": 10,
            "session_count": 5
        },
        "energy_matching": {
            "expected_accuracy": 0.80,
            "test_combinations": 20
        }
    }
}

# Utility functions for test data access
def get_user_profile(profile_name: str) -> UserProfile:
    """Get user profile by name"""
    return USER_PROFILES.get(profile_name)

def get_brain_dump(scenario: str) -> Dict[str, Any]:
    """Get brain dump scenario by name"""
    return REALISTIC_BRAIN_DUMPS.get(scenario)

def get_energy_pattern(pattern_name: str) -> List[Dict]:
    """Get energy pattern by name"""
    return ENERGY_PATTERNS.get(pattern_name, [])

def get_completion_scenario(scenario_name: str) -> Dict[str, Any]:
    """Get completion scenario by name"""
    return DAILY_COMPLETION_SCENARIOS.get(scenario_name)

def get_ai_response_example(quality_level: str, response_type: str) -> Any:
    """Get AI response example by quality and type"""
    key = f"{quality_level}_quality_{response_type}"
    return AI_RESPONSE_EXAMPLES.get(key)

def get_behavioral_scenario(scenario_name: str) -> Dict[str, Any]:
    """Get behavioral intervention scenario"""
    return BEHAVIORAL_SCENARIOS.get(scenario_name)

# Export commonly used test data
__all__ = [
    'USER_PROFILES',
    'REALISTIC_BRAIN_DUMPS', 
    'ENERGY_PATTERNS',
    'DAILY_COMPLETION_SCENARIOS',
    'CONTEXT_TAGGING_TEST_DATA',
    'AI_RESPONSE_EXAMPLES',
    'BEHAVIORAL_SCENARIOS',
    'PERFORMANCE_TEST_SCENARIOS',
    'get_user_profile',
    'get_brain_dump',
    'get_energy_pattern',
    'get_completion_scenario',
    'get_ai_response_example',
    'get_behavioral_scenario'
]