"""
Seasonal and Temporal Pattern Scenarios for Qwen Task Manager 3.0

This module contains scenarios that test the system's understanding of seasonal
and temporal influences on mental health, energy patterns, and task management.
Validates appropriate adaptation to natural rhythms and seasonal challenges.

Focus: Seasonal Affective Disorder, circadian rhythms, holiday stress,
anniversary reactions, and temporal mental health patterns.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, date
from tests.conftest import EnergyState


class Season(Enum):
    """Four seasons with mental health implications"""
    SPRING = "spring"
    SUMMER = "summer" 
    FALL = "fall"
    WINTER = "winter"


class TimeOfDay(Enum):
    """Time of day categories affecting energy and mood"""
    EARLY_MORNING = "early_morning"  # 5-8 AM
    MORNING = "morning"  # 8-12 PM
    AFTERNOON = "afternoon"  # 12-5 PM  
    EVENING = "evening"  # 5-8 PM
    NIGHT = "night"  # 8 PM-12 AM
    LATE_NIGHT = "late_night"  # 12-5 AM


@dataclass
class SeasonalScenario:
    """Represents a seasonal/temporal scenario for testing"""
    id: str
    title: str
    description: str
    season: Season
    time_of_day: TimeOfDay
    daylight_hours: str
    weather_pattern: str
    user_presentation: str
    seasonal_factors: List[str]
    energy_pattern: EnergyState
    mood_influences: List[str]
    behavioral_patterns: List[str]
    required_adaptations: List[str]
    therapeutic_considerations: List[str]


class WinterSeasonalScenarios:
    """Winter-specific seasonal challenges"""
    
    SCENARIOS = [
        SeasonalScenario(
            id="winter_sad_onset",
            title="Seasonal Affective Disorder Onset in Deep Winter",
            description="User experiencing classic SAD symptoms during darkest winter months",
            season=Season.WINTER,
            time_of_day=TimeOfDay.AFTERNOON,
            daylight_hours="7_hours_weak_sunlight",
            weather_pattern="overcast_cold_dreary",
            user_presentation="I don't understand what's wrong with me. I was fine in October, but now I can barely get out of bed. I'm sleeping 10+ hours and still exhausted. Everything feels impossible and I just want to hibernate until spring. I've gained 15 pounds from carb cravings and I hate how I look.",
            seasonal_factors=["reduced_daylight", "vitamin_d_deficiency", "circadian_rhythm_disruption"],
            energy_pattern=EnergyState(2, 2, 1, "14:00"),
            mood_influences=["light_deprivation", "seasonal_isolation", "winter_weight_gain"],
            behavioral_patterns=["oversleeping", "carbohydrate_craving", "social_withdrawal", "afternoon_energy_crash"],
            required_adaptations=["light_therapy_discussion", "seasonal_pattern_normalization", "winter_coping_strategies"],
            therapeutic_considerations=["SAD_psychoeducation", "light_therapy", "seasonal_depression_treatment"]
        ),
        
        SeasonalScenario(
            id="holiday_grief_anniversary",
            title="Holiday Season Grief and Anniversary Reactions",
            description="User struggling with grief intensified by holiday season and anniversaries",
            season=Season.WINTER,
            time_of_day=TimeOfDay.EVENING,
            daylight_hours="limited_winter_daylight",
            weather_pattern="cold_clear_festive_atmosphere",
            user_presentation="The holidays are everywhere and I feel like I'm drowning. This is my first Christmas without Mom and everyone expects me to be festive, but I just want to hide. All the family traditions feel wrong without her. I'm angry at people for being happy when my world is broken.",
            seasonal_factors=["holiday_expectations", "family_tradition_disruption", "anniversary_proximity"],
            energy_pattern=EnergyState(3, 4, 1, "19:00"),
            mood_influences=["grief_intensification", "social_expectation_pressure", "memory_triggers"],
            behavioral_patterns=["holiday_avoidance", "family_gathering_anxiety", "tradition_painful_associations"],
            required_adaptations=["grief_and_holidays_support", "tradition_modification_guidance", "social_expectation_management"],
            therapeutic_considerations=["complicated_grief", "holiday_grief_counseling", "anniversary_reaction_support"]
        ),
        
        SeasonalScenario(
            id="winter_isolation_compound",
            title="Winter Weather Compounding Social Isolation",
            description="User with existing social anxiety finding winter weather worsening isolation",
            season=Season.WINTER,
            time_of_day=TimeOfDay.LATE_NIGHT,
            daylight_hours="minimal_winter_daylight",
            weather_pattern="blizzard_conditions_housebound",
            user_presentation="I've been snowed in for three days and I realize I haven't talked to another human being in over a week. I was already struggling with social anxiety, but now the weather gives me an excuse to stay inside. I order everything online, work from home, and I'm becoming a hermit. I know this isn't healthy but leaving feels impossible.",
            seasonal_factors=["weather_isolation", "reduced_social_opportunities", "seasonal_depression_overlay"],
            energy_pattern=EnergyState(3, 3, 2, "23:00"),
            mood_influences=["isolation_compounding", "social_skill_atrophy", "cabin_fever"],
            behavioral_patterns=["complete_social_avoidance", "online_life_preference", "weather_excuse_making"],
            required_adaptations=["isolation_breaking_strategies", "gradual_exposure_planning", "social_connection_creativity"],
            therapeutic_considerations=["social_anxiety_treatment", "isolation_intervention", "seasonal_behavioral_activation"]
        )
    ]


class SpringSeasonalScenarios:
    """Spring-specific seasonal patterns and challenges"""
    
    SCENARIOS = [
        SeasonalScenario(
            id="spring_anxiety_energy_surge",
            title="Spring Anxiety from Sudden Energy Increase",
            description="User with anxiety experiencing destabilization from spring energy surge",
            season=Season.SPRING,
            time_of_day=TimeOfDay.MORNING,
            daylight_hours="rapidly_increasing_daylight",
            weather_pattern="bright_warming_energizing",
            user_presentation="Everyone talks about spring being great, but I feel overwhelmed by all this energy. I was in a low-energy winter routine and now I feel like I should be doing everything at once. My anxiety is through the roof because there's so much light and activity. I preferred the quiet hibernation of winter.",
            seasonal_factors=["daylight_increase", "energy_level_fluctuation", "seasonal_expectation_pressure"],
            energy_pattern=EnergyState(8, 7, 4, "09:00"),
            mood_influences=["overstimulation", "seasonal_pressure", "routine_disruption"],
            behavioral_patterns=["overcommitment", "anxiety_from_energy_surge", "spring_cleaning_compulsion"],
            required_adaptations=["energy_management_strategies", "seasonal_transition_support", "overstimulation_reduction"],
            therapeutic_considerations=["anxiety_management", "energy_regulation", "seasonal_transition_therapy"]
        ),
        
        SeasonalScenario(
            id="spring_depression_contrast",
            title="Depression Feeling Worse in Contrast to Spring Renewal",
            description="User with depression feeling more hopeless as world renews around them",
            season=Season.SPRING,
            time_of_day=TimeOfDay.AFTERNOON,
            daylight_hours="long_bright_spring_days",
            weather_pattern="beautiful_renewal_growth",
            user_presentation="Everything is blooming and beautiful and I feel like garbage. Everyone else seems to come alive in spring but I still feel dead inside. The contrast makes me feel worse - like I'm broken because I can't feel the joy that everyone else feels. The world is renewing but I'm still stuck in winter.",
            seasonal_factors=["renewal_contrast", "social_energy_expectation", "seasonal_recovery_pressure"],
            energy_pattern=EnergyState(2, 3, 2, "15:00"),
            mood_influences=["hopelessness_contrast", "social_comparison", "seasonal_guilt"],
            behavioral_patterns=["spring_activity_avoidance", "social_withdrawal_from_happy_people", "nature_avoidance"],
            required_adaptations=["depression_validation_regardless_of_season", "contrast_normalization", "gradual_seasonal_engagement"],
            therapeutic_considerations=["depression_treatment", "seasonal_comparison_work", "hope_rebuilding"]
        )
    ]


class SummerSeasonalScenarios:
    """Summer-specific challenges and patterns"""
    
    SCENARIOS = [
        SeasonalScenario(
            id="summer_body_image_anxiety",
            title="Summer Body Image Anxiety and Social Pressure",
            description="User experiencing intense body image anxiety due to summer clothing and activities",
            season=Season.SUMMER,
            time_of_day=TimeOfDay.AFTERNOON,
            daylight_hours="long_bright_summer_days",
            weather_pattern="hot_sunny_beach_weather",
            user_presentation="Summer is torture for me. Everyone's posting beach photos and wearing shorts and I hate my body. I'm sweating through long sleeves because I can't bear to show my arms. Pool parties and beach trips fill me with dread. I feel like I'm wasting the beautiful weather hiding inside.",
            seasonal_factors=["clothing_exposure_pressure", "summer_activity_expectations", "body_comparison_increase"],
            energy_pattern=EnergyState(5, 4, 2, "14:00"),
            mood_influences=["body_shame", "social_comparison", "activity_avoidance"],
            behavioral_patterns=["summer_activity_avoidance", "inappropriate_clothing_for_weather", "social_isolation"],
            required_adaptations=["body_image_support", "seasonal_activity_modification", "self_acceptance_work"],
            therapeutic_considerations=["body_image_therapy", "eating_disorder_screening", "self_compassion_work"]
        ),
        
        SeasonalScenario(
            id="summer_schedule_disruption_adhd",
            title="Summer Schedule Disruption Affecting ADHD Management",
            description="User with ADHD struggling with summer schedule changes affecting coping strategies",
            season=Season.SUMMER,
            time_of_day=TimeOfDay.MORNING,
            daylight_hours="very_long_summer_days",
            weather_pattern="hot_bright_energetic",
            user_presentation="My ADHD was finally manageable with my school year routine, but summer has thrown everything off. No structure, irregular sleep because it's light so late, and I can't focus on anything. My medication feels different too. I feel scattered and I'm dreading fall because I'll have to rebuild all my systems.",
            seasonal_factors=["routine_disruption", "daylight_pattern_change", "seasonal_medication_effects"],
            energy_pattern=EnergyState(7, 8, 5, "10:00"),
            mood_influences=["structure_loss_anxiety", "ADHD_symptom_increase", "seasonal_transition_stress"],
            behavioral_patterns=["sleep_schedule_disruption", "hyperfocus_in_wrong_areas", "planning_difficulty"],
            required_adaptations=["summer_structure_creation", "ADHD_seasonal_adjustments", "routine_flexibility_training"],
            therapeutic_considerations=["ADHD_management", "seasonal_adjustment_strategies", "routine_building"]
        )
    ]


class FallSeasonalScenarios:
    """Fall-specific patterns and transitions"""
    
    SCENARIOS = [
        SeasonalScenario(
            id="fall_transition_anxiety",
            title="Fall Transition Anxiety and Change Sensitivity",
            description="User with change sensitivity struggling with fall transitions and endings",
            season=Season.FALL,
            time_of_day=TimeOfDay.EVENING,
            daylight_hours="rapidly_decreasing_daylight",
            weather_pattern="crisp_changing_leaves_dying",
            user_presentation="Fall makes me so anxious. Everything is ending - the leaves are dying, it's getting dark earlier, summer is over. I know it's natural but it feels like everything good is going away. Back to school energy is everywhere and I feel this pressure to start new things, but I'm already grieving what's ending.",
            seasonal_factors=["transition_sensitivity", "ending_symbolism", "back_to_school_pressure"],
            energy_pattern=EnergyState(4, 5, 3, "18:00"),
            mood_influences=["change_anxiety", "loss_anticipation", "seasonal_pressure"],
            behavioral_patterns=["change_resistance", "ending_grief", "new_beginning_avoidance"],
            required_adaptations=["transition_support", "change_anxiety_management", "cycle_normalization"],
            therapeutic_considerations=["change_anxiety_treatment", "transition_therapy", "loss_processing"]
        ),
        
        SeasonalScenario(
            id="fall_productivity_pressure",
            title="Fall Productivity Pressure and New Year Syndrome",
            description="User feeling pressure to be productive and start fresh in fall academic calendar",
            season=Season.FALL,
            time_of_day=TimeOfDay.MORNING,
            daylight_hours="shorter_but_crisp_productive_light",
            weather_pattern="clear_cool_energizing",
            user_presentation="Everyone's talking about fresh starts and new goals because it's fall, but I feel overwhelmed by all the pressure to be productive. It's like a second New Year and I already failed at my January resolutions. I want to start new projects but I'm paralyzed by the expectation to reinvent myself.",
            seasonal_factors=["productivity_culture_pressure", "fresh_start_expectations", "academic_year_influence"],
            energy_pattern=EnergyState(6, 6, 4, "08:00"),
            mood_influences=["productivity_anxiety", "fresh_start_pressure", "failure_anticipation"],
            behavioral_patterns=["goal_setting_overwhelm", "perfectionist_paralysis", "comparison_to_others_productivity"],
            required_adaptations=["productivity_pressure_relief", "realistic_goal_setting", "perfectionism_management"],
            therapeutic_considerations=["perfectionism_treatment", "goal_setting_therapy", "productivity_culture_critique"]
        )
    ]


class CircadianAndTemporalScenarios:
    """Scenarios related to circadian rhythms and time-of-day patterns"""
    
    SCENARIOS = [
        SeasonalScenario(
            id="night_owl_morning_world_conflict",
            title="Night Owl Struggling in Morning-Oriented World",
            description="Natural night owl forced into early morning schedule causing chronic issues",
            season=Season.WINTER,  # Worse in winter with limited light
            time_of_day=TimeOfDay.EARLY_MORNING,
            daylight_hours="limited_winter_dawn",
            weather_pattern="dark_cold_early_morning",
            user_presentation="I'm naturally a night person but the world demands I be a morning person. I've tried everything - going to bed earlier, morning light, caffeine - but I'm chronically exhausted and my work performance is suffering. I feel most creative and alive at 11 PM but that's when I'm supposed to be winding down.",
            seasonal_factors=["circadian_rhythm_mismatch", "social_schedule_conflict", "seasonal_light_timing"],
            energy_pattern=EnergyState(2, 2, 2, "07:00"),
            mood_influences=["chronic_sleep_deprivation", "circadian_misalignment", "social_jet_lag"],
            behavioral_patterns=["forced_early_rising", "evening_energy_surge", "chronic_fatigue"],
            required_adaptations=["circadian_rhythm_respect", "schedule_flexibility_advocacy", "chronotype_education"],
            therapeutic_considerations=["sleep_medicine", "circadian_rhythm_therapy", "workplace_accommodation"]
        ),
        
        SeasonalScenario(
            id="shift_work_disorder_family_impact",
            title="Shift Work Sleep Disorder Affecting Family Relationships",
            description="Healthcare worker with rotating shifts struggling with family life and mood",
            season=Season.FALL,
            time_of_day=TimeOfDay.AFTERNOON,
            daylight_hours="moderate_fall_daylight",
            weather_pattern="variable_unpredictable",
            user_presentation="I'm a nurse working rotating shifts and my sleep is destroyed. I'm exhausted when my family is awake and wide awake when they're sleeping. My mood swings are affecting my marriage and I snapped at my kids yesterday. I love my job but I feel like I'm sacrificing my family and my mental health.",
            seasonal_factors=["shift_work_sleep_disorder", "family_schedule_mismatch", "seasonal_time_change_impact"],
            energy_pattern=EnergyState(3, 2, 2, "15:00"),
            mood_influences=["sleep_deprivation_mood_impact", "family_relationship_strain", "guilt_about_work_impact"],
            behavioral_patterns=["irregular_sleep_schedule", "mood_instability", "family_conflict"],
            required_adaptations=["shift_work_coping_strategies", "family_schedule_coordination", "sleep_hygiene_for_shift_work"],
            therapeutic_considerations=["shift_work_sleep_disorder_treatment", "family_therapy", "work_life_balance"]
        ),
        
        SeasonalScenario(
            id="daylight_saving_disruption",
            title="Daylight Saving Time Transition Disruption",
            description="User with mood disorder experiencing severe disruption from time change",
            season=Season.SPRING,  # Spring forward is often harder
            time_of_day=TimeOfDay.MORNING,
            daylight_hours="disrupted_by_time_change",
            weather_pattern="spring_but_chronically_misaligned",
            user_presentation="The time change has completely thrown me off and it's been two weeks. I have bipolar disorder and my sleep schedule is crucial for my stability, but this hour shift has messed everything up. I'm getting hypomanic symptoms and I'm scared I'm heading for an episode. Why do we still do this to ourselves?",
            seasonal_factors=["daylight_saving_disruption", "circadian_rhythm_sensitivity", "mood_disorder_vulnerability"],
            energy_pattern=EnergyState(8, 7, 3, "08:00"),  # Elevated but unstable
            mood_influences=["mood_destabilization", "sleep_rhythm_disruption", "hypomania_risk"],
            behavioral_patterns=["sleep_schedule_chaos", "mood_elevation_warning_signs", "routine_disruption"],
            required_adaptations=["mood_stabilization_focus", "gradual_schedule_adjustment", "episode_prevention_strategies"],
            therapeutic_considerations=["bipolar_disorder_management", "sleep_schedule_stabilization", "mood_episode_prevention"]
        )
    ]


def get_all_seasonal_scenarios() -> List[SeasonalScenario]:
    """Return all seasonal scenarios for comprehensive testing"""
    all_scenarios = []
    all_scenarios.extend(WinterSeasonalScenarios.SCENARIOS)
    all_scenarios.extend(SpringSeasonalScenarios.SCENARIOS)
    all_scenarios.extend(SummerSeasonalScenarios.SCENARIOS)
    all_scenarios.extend(FallSeasonalScenarios.SCENARIOS)
    all_scenarios.extend(CircadianAndTemporalScenarios.SCENARIOS)
    return all_scenarios


def get_scenarios_by_season(season: Season) -> List[SeasonalScenario]:
    """Return scenarios filtered by season"""
    all_scenarios = get_all_seasonal_scenarios()
    return [scenario for scenario in all_scenarios if scenario.season == season]


def get_scenarios_by_time_of_day(time_of_day: TimeOfDay) -> List[SeasonalScenario]:
    """Return scenarios filtered by time of day"""
    all_scenarios = get_all_seasonal_scenarios()
    return [scenario for scenario in all_scenarios if scenario.time_of_day == time_of_day]


def get_scenarios_by_therapeutic_consideration(consideration: str) -> List[SeasonalScenario]:
    """Return scenarios that include a specific therapeutic consideration"""
    all_scenarios = get_all_seasonal_scenarios()
    return [scenario for scenario in all_scenarios if consideration in scenario.therapeutic_considerations]


def get_current_season_scenarios() -> List[SeasonalScenario]:
    """Return scenarios appropriate for the current season"""
    today = date.today()
    current_month = today.month
    
    # Determine current season based on month
    if current_month in [12, 1, 2]:
        current_season = Season.WINTER
    elif current_month in [3, 4, 5]:
        current_season = Season.SPRING
    elif current_month in [6, 7, 8]:
        current_season = Season.SUMMER
    else:  # 9, 10, 11
        current_season = Season.FALL
    
    return get_scenarios_by_season(current_season)