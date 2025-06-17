"""
Real-World Behavioral Scenarios for Qwen Task Manager 3.0

This module contains realistic scenarios based on common user experiences,
providing comprehensive test data for validating behavioral and therapeutic responses.
Scenarios are designed to represent authentic user situations while protecting privacy.

Focus: Authentic user experiences, diverse life circumstances, various mental health
presentations, and realistic complexity of human situations.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from tests.conftest import EnergyState


@dataclass
class RealWorldScenario:
    """Represents a real-world user scenario for testing"""
    id: str
    title: str
    description: str
    user_context: Dict[str, Any]
    initial_user_message: str
    energy_state: EnergyState
    psychological_factors: List[str]
    environmental_factors: List[str]
    expected_response_qualities: List[str]
    therapeutic_considerations: List[str]
    difficulty_level: str  # "simple", "moderate", "complex", "crisis"


class WorkRelatedScenarios:
    """Real-world work-related scenarios"""
    
    SCENARIOS = [
        RealWorldScenario(
            id="work_burnout_approaching_deadline",
            title="Approaching Deadline with Burnout Symptoms",
            description="User showing signs of burnout while facing important work deadline",
            user_context={
                "employment_status": "full_time_knowledge_worker",
                "recent_work_pattern": "60_hour_weeks_for_month",
                "sleep_pattern": "4_to_5_hours_nightly",
                "support_system": "minimal_due_to_work_demands"
            },
            initial_user_message="I have this huge presentation due Friday and I just can't focus. I've been working non-stop but getting nowhere. My brain feels like mush and I keep making stupid mistakes. I can't afford to fail this but I'm running out of time.",
            energy_state=EnergyState(2, 3, 1, "14:00"),
            psychological_factors=["cognitive_exhaustion", "performance_anxiety", "perfectionism", "burnout_symptoms"],
            environmental_factors=["work_pressure", "time_constraints", "high_stakes"],
            expected_response_qualities=["validates_exhaustion", "addresses_perfectionism", "suggests_sustainable_approach"],
            therapeutic_considerations=["burnout_prevention", "cognitive_load_management", "self_compassion"],
            difficulty_level="complex"
        ),
        
        RealWorldScenario(
            id="job_loss_identity_crisis",
            title="Recent Job Loss and Identity Crisis",
            description="User processing unexpected job loss and questioning self-worth",
            user_context={
                "employment_status": "recently_unemployed",
                "job_loss_reason": "company_layoffs",
                "career_identity": "strongly_tied_to_work_role",
                "financial_situation": "concerning_with_savings_running_out"
            },
            initial_user_message="I got laid off three weeks ago and I don't know who I am anymore. I used to be the person everyone came to for solutions, and now I'm just... nothing. I should be job hunting but I can't even update my resume. What's the point if I'm just going to get rejected anyway?",
            energy_state=EnergyState(3, 4, 2, "10:00"),
            psychological_factors=["identity_disruption", "learned_helplessness", "shame", "grief_for_lost_role"],
            environmental_factors=["financial_stress", "job_market_uncertainty", "social_status_change"],
            expected_response_qualities=["validates_identity_loss", "reframes_worth_beyond_work", "encourages_small_steps"],
            therapeutic_considerations=["identity_work", "behavioral_activation", "values_clarification"],
            difficulty_level="complex"
        ),
        
        RealWorldScenario(
            id="workplace_neurodiversity_accommodation",
            title="ADHD Professional Seeking Workplace Accommodations",
            description="User with ADHD struggling in traditional workplace environment",
            user_context={
                "neurodiversity": "adhd_combined_type",
                "workplace_environment": "open_office_high_distractions",
                "accommodation_status": "none_currently",
                "masking_behavior": "high_effort_to_appear_neurotypical"
            },
            initial_user_message="I'm drowning at work. The open office is a nightmare - every conversation pulls my attention away. I've been staying late every day trying to catch up on what I should have done during the day, but then I'm exhausted and it's even worse the next day. I want to ask for accommodations but I'm scared they'll think I'm making excuses.",
            energy_state=EnergyState(4, 2, 3, "19:00"),
            psychological_factors=["sensory_overwhelm", "masking_exhaustion", "self_advocacy_anxiety", "imposter_syndrome"],
            environmental_factors=["sensory_hostile_environment", "neurotypical_workplace_norms", "accommodation_stigma"],
            expected_response_qualities=["validates_adhd_challenges", "supports_self_advocacy", "celebrates_neurodiversity"],
            therapeutic_considerations=["neurodiversity_affirmation", "accommodation_strategizing", "anti_ableism"],
            difficulty_level="moderate"
        )
    ]


class RelationshipScenarios:
    """Real-world relationship and family scenarios"""
    
    SCENARIOS = [
        RealWorldScenario(
            id="caring_for_aging_parent",
            title="Overwhelmed Caring for Aging Parent",
            description="Adult child struggling with increasing caregiving responsibilities",
            user_context={
                "caregiving_role": "primary_caregiver_for_parent",
                "parent_condition": "early_dementia_increasing_needs",
                "own_family": "spouse_and_teenage_children",
                "support_system": "limited_sibling_lives_far_away"
            },
            initial_user_message="Mom is getting worse and I don't know how to handle it anymore. She called me six times yesterday asking the same question. My family is getting frustrated because I'm always dealing with Mom stuff, but I can't just abandon her. I feel like I'm failing everyone and I'm so tired I can barely function.",
            energy_state=EnergyState(2, 3, 2, "21:00"),
            psychological_factors=["caregiver_stress", "guilt", "anticipatory_grief", "role_conflict"],
            environmental_factors=["increasing_care_demands", "family_tension", "time_constraints"],
            expected_response_qualities=["validates_caregiver_burden", "acknowledges_grief", "suggests_support_resources"],
            therapeutic_considerations=["caregiver_support", "boundary_setting", "grief_processing"],
            difficulty_level="complex"
        ),
        
        RealWorldScenario(
            id="relationship_anxiety_attachment",
            title="Relationship Anxiety with Insecure Attachment",
            description="User experiencing anxiety about relationship stability due to attachment patterns",
            user_context={
                "relationship_status": "committed_relationship_18_months",
                "attachment_style": "anxious_preoccupied",
                "past_relationship_trauma": "abandonment_experiences",
                "current_trigger": "partner_working_more_hours"
            },
            initial_user_message="My boyfriend has been working late a lot lately and I keep thinking he's going to leave me. I know logically that he loves me, but I can't shake this feeling that he's pulling away. I've been texting him constantly and I can see it's annoying him, which makes me panic more. I hate being this needy person but I can't stop.",
            energy_state=EnergyState(6, 5, 2, "18:00"),
            psychological_factors=["attachment_anxiety", "catastrophic_thinking", "self_awareness_with_compulsion", "shame_about_needs"],
            environmental_factors=["partner_schedule_change", "relationship_security_threat_perception"],
            expected_response_qualities=["validates_attachment_fears", "normalizes_anxiety", "suggests_grounding_techniques"],
            therapeutic_considerations=["attachment_healing", "emotional_regulation", "communication_skills"],
            difficulty_level="moderate"
        ),
        
        RealWorldScenario(
            id="parenting_overwhelm_neurodivergent_child",
            title="Parenting Neurodivergent Child While Managing Own Mental Health",
            description="Parent struggling to support neurodivergent child while managing depression",
            user_context={
                "parenting_role": "single_parent_primary_custody",
                "child_profile": "8_year_old_autistic_child",
                "own_mental_health": "depression_treatment_stable_but_challenging",
                "support_system": "limited_family_support_some_friends"
            },
            initial_user_message="My son had three meltdowns today and I just sat on the bathroom floor and cried. I know he can't help it and I love him so much, but I'm so depleted. My depression makes everything harder and I feel like I'm failing him. He needs so much and I barely have enough energy for basic things. I worry I'm damaging him by not being the parent he needs.",
            energy_state=EnergyState(2, 2, 1, "20:30"),
            psychological_factors=["parental_guilt", "caregiver_exhaustion", "depression_symptoms", "self_criticism"],
            environmental_factors=["single_parenting_stress", "neurodivergent_child_needs", "social_isolation"],
            expected_response_qualities=["validates_parenting_challenges", "affirms_love_and_effort", "suggests_respite_options"],
            therapeutic_considerations=["parental_self_compassion", "respite_planning", "depression_management"],
            difficulty_level="complex"
        )
    ]


class HealthAndWellnessScenarios:
    """Real-world health and wellness related scenarios"""
    
    SCENARIOS = [
        RealWorldScenario(
            id="chronic_illness_diagnosis_adjustment",
            title="Adjusting to New Chronic Illness Diagnosis",
            description="User processing recent diagnosis of chronic condition and lifestyle changes",
            user_context={
                "health_status": "recently_diagnosed_autoimmune_condition",
                "symptom_impact": "fatigue_pain_affecting_daily_function",
                "lifestyle_changes_required": "diet_modifications_activity_restrictions",
                "medical_support": "good_doctor_but_learning_curve_steep"
            },
            initial_user_message="I got diagnosed with rheumatoid arthritis last month and I'm struggling to accept this is my life now. Some days I can barely get out of bed, and I used to be the person who ran marathons. My doctor says I need to pace myself but I don't know how to be someone who 'paces herself'. I feel like I'm letting everyone down.",
            energy_state=EnergyState(3, 2, 2, "11:00"),
            psychological_factors=["grief_for_lost_health", "identity_adjustment", "chronic_illness_adjustment", "activity_restriction_grief"],
            environmental_factors=["medical_appointments", "symptom_unpredictability", "social_role_changes"],
            expected_response_qualities=["validates_grief_process", "supports_identity_expansion", "introduces_spoon_theory"],
            therapeutic_considerations=["chronic_illness_psychology", "pacing_education", "identity_work"],
            difficulty_level="moderate"
        ),
        
        RealWorldScenario(
            id="mental_health_medication_concerns",
            title="Anxiety About Starting Mental Health Medication",
            description="User conflicted about beginning antidepressant treatment",
            user_context={
                "mental_health_status": "depression_and_anxiety_moderate_severity",
                "treatment_history": "therapy_helpful_but_not_sufficient",
                "medication_status": "prescribed_but_not_started",
                "concerns": "side_effects_dependency_stigma"
            },
            initial_user_message="My therapist and doctor both think I should try medication for my depression, but I'm terrified. What if it changes who I am? What if I become dependent? My mom always said mental health meds are just a crutch. But I'm also tired of feeling this way. I've been staring at the bottle for a week.",
            energy_state=EnergyState(4, 5, 3, "16:00"),
            psychological_factors=["medication_ambivalence", "internalized_stigma", "fear_of_personality_change", "treatment_approach_conflict"],
            environmental_factors=["family_medication_attitudes", "mental_health_stigma", "healthcare_navigation"],
            expected_response_qualities=["validates_medication_concerns", "provides_balanced_information", "supports_informed_choice"],
            therapeutic_considerations=["medication_education", "stigma_processing", "autonomy_support"],
            difficulty_level="moderate"
        ),
        
        RealWorldScenario(
            id="body_image_recovery_eating_disorder",
            title="Body Image Struggles in Eating Disorder Recovery",
            description="User in eating disorder recovery dealing with body image distress",
            user_context={
                "recovery_status": "eating_disorder_recovery_6_months",
                "recovery_progress": "eating_patterns_stabilizing_body_image_difficult",
                "support_system": "treatment_team_family_support",
                "current_trigger": "clothing_not_fitting_weight_restoration"
            },
            initial_user_message="I'm supposed to be grateful that I'm recovering, but I hate how my body looks now. None of my clothes fit and I feel so uncomfortable in my skin. I know my treatment team says this is normal, but I just want to restrict again. I know that's not the answer but I feel so out of control.",
            energy_state=EnergyState(5, 4, 2, "14:00"),
            psychological_factors=["body_image_distress", "recovery_ambivalence", "control_issues", "eating_disorder_thoughts"],
            environmental_factors=["clothing_changes", "body_changes", "recovery_expectations"],
            expected_response_qualities=["validates_recovery_difficulty", "affirms_recovery_courage", "normalizes_body_image_struggles"],
            therapeutic_considerations=["eating_disorder_recovery_support", "body_neutrality", "recovery_motivation"],
            difficulty_level="complex"
        )
    ]


class LifeTransitionScenarios:
    """Real-world life transition scenarios"""
    
    SCENARIOS = [
        RealWorldScenario(
            id="empty_nest_identity_transition",
            title="Empty Nest Syndrome and Identity Rediscovery",
            description="Parent adjusting to children leaving home and rediscovering individual identity",
            user_context={
                "family_status": "last_child_left_for_college_month_ago",
                "previous_primary_identity": "devoted_parent_child_centered_life",
                "current_situation": "quiet_house_uncertain_purpose",
                "relationship_status": "married_but_relationship_needs_attention"
            },
            initial_user_message="The house is so quiet now that Sarah left for college. I spent 20 years being 'Mom' first and everything else second, and now I don't know who I am. My husband wants to plan trips and reconnect, but I feel like a stranger to myself. I should be happy - we raised a great kid - but I just feel empty.",
            energy_state=EnergyState(4, 5, 3, "15:00"),
            psychological_factors=["identity_transition", "purpose_redefinition", "grief_for_past_role", "relationship_adjustment"],
            environmental_factors=["physical_environment_change", "schedule_disruption", "social_role_shift"],
            expected_response_qualities=["validates_transition_difficulty", "affirms_parenting_success", "explores_identity_beyond_parenting"],
            therapeutic_considerations=["life_transition_support", "identity_exploration", "relationship_reconnection"],
            difficulty_level="moderate"
        ),
        
        RealWorldScenario(
            id="quarter_life_crisis_career_uncertainty",
            title="Quarter-Life Crisis and Career Path Uncertainty",
            description="Young adult questioning career choices and life direction",
            user_context={
                "age_demographic": "25_years_old",
                "education_status": "college_graduate_2_years_ago",
                "career_status": "job_in_field_but_unfulfilling",
                "social_comparison": "peers_appearing_more_successful_on_social_media"
            },
            initial_user_message="I'm 25 and I feel like I'm already behind in life. My friends are getting promoted, buying houses, getting engaged, and I'm still living paycheck to paycheck wondering if I chose the wrong major. I thought I'd have it figured out by now. Everyone else seems so confident and I feel like I'm just pretending to be an adult.",
            energy_state=EnergyState(5, 6, 4, "12:00"),
            psychological_factors=["quarter_life_uncertainty", "social_comparison", "imposter_syndrome", "career_anxiety"],
            environmental_factors=["social_media_comparison", "economic_pressures", "peer_life_milestones"],
            expected_response_qualities=["normalizes_quarter_life_questioning", "challenges_comparison_culture", "explores_personal_values"],
            therapeutic_considerations=["life_direction_exploration", "social_comparison_work", "values_clarification"],
            difficulty_level="moderate"
        ),
        
        RealWorldScenario(
            id="retirement_transition_purpose_crisis",
            title="Retirement Transition and Purpose Crisis",
            description="Recent retiree struggling with loss of structure and purpose",
            user_context={
                "retirement_status": "retired_6_months_ago_after_35_year_career",
                "previous_work_identity": "high_achieving_work_defined_self_worth",
                "current_situation": "financially_secure_but_purposeless",
                "health_status": "good_health_many_active_years_ahead"
            },
            initial_user_message="I worked for 35 years looking forward to retirement, and now that I'm here, I don't know what to do with myself. I used to be important, people needed me, and now I feel invisible. My wife says I should be enjoying this, but I feel useless. I never thought I'd miss the stress, but at least it gave me purpose.",
            energy_state=EnergyState(6, 7, 3, "13:00"),
            psychological_factors=["purpose_loss", "identity_crisis", "useful_contribution_need", "retirement_adjustment"],
            environmental_factors=["structure_loss", "social_role_change", "time_abundance"],
            expected_response_qualities=["validates_retirement_adjustment_difficulty", "explores_new_purpose_opportunities", "affirms_continued_value"],
            therapeutic_considerations=["retirement_transition_support", "purpose_redefinition", "meaning_making"],
            difficulty_level="moderate"
        )
    ]


def get_all_real_world_scenarios() -> List[RealWorldScenario]:
    """Return all real-world scenarios for comprehensive testing"""
    all_scenarios = []
    all_scenarios.extend(WorkRelatedScenarios.SCENARIOS)
    all_scenarios.extend(RelationshipScenarios.SCENARIOS)
    all_scenarios.extend(HealthAndWellnessScenarios.SCENARIOS)
    all_scenarios.extend(LifeTransitionScenarios.SCENARIOS)
    return all_scenarios


def get_scenarios_by_difficulty(difficulty: str) -> List[RealWorldScenario]:
    """Return scenarios filtered by difficulty level"""
    all_scenarios = get_all_real_world_scenarios()
    return [scenario for scenario in all_scenarios if scenario.difficulty_level == difficulty]


def get_scenarios_by_psychological_factor(factor: str) -> List[RealWorldScenario]:
    """Return scenarios that include a specific psychological factor"""
    all_scenarios = get_all_real_world_scenarios()
    return [scenario for scenario in all_scenarios if factor in scenario.psychological_factors]