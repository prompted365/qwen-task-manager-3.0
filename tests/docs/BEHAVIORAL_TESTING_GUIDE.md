# Behavioral Testing Guide for Qwen Task Manager 3.0

## Philosophy: Testing Human Flourishing Through Technology

This guide explains how to write tests that validate psychological benefits, not just technical functionality. We test whether our system genuinely helps users with executive function and behavioral activation, moving beyond traditional software testing to validate human wellbeing outcomes.

## Core Principles

### 1. Test Psychological Outcomes, Not Just Code Execution

**Traditional Approach (What NOT to do):**
```python
def test_task_creation():
    task = create_task("Buy groceries")
    assert task.title == "Buy groceries"  # Tests data storage
```

**Behavioral Approach (What TO do):**
```python
def test_task_creation_reduces_cognitive_load():
    """
    Validate that task creation actually helps users manage mental bandwidth
    """
    vague_input = "deal with grocery situation"
    clarified_task = clarify_task(vague_input, user_profile)
    
    # Test cognitive manageability
    assert clarified_task.timer <= 30  # Manageable time chunk
    assert clarified_task.description.startswith(action_verb)  # Clear next action
    assert clarified_task.energy_required in ['low', 'medium', 'high']  # Energy awareness
    
    # Test behavioral activation compliance
    assert not contains_perfectionist_language(clarified_task.description)
    assert contains_permission_to_be_imperfect(clarified_task.description)
```

### 2. Validate Behavioral Activation Principles

Behavioral activation helps users build positive momentum without self-criticism. Every test should consider:

- **Self-Compassion**: Does the system validate effort rather than criticize?
- **Energy Awareness**: Are suggestions appropriate for current capacity?
- **Overwhelm Prevention**: Does the system respect cognitive limits?
- **Forward Focus**: Does feedback promote future action rather than rumination?

### 3. Test Different Cognitive Styles

Our users have diverse mental health needs:

```python
@pytest.mark.parametrize("user_profile", [
    "alex_adhd",           # Hyperfocus patterns, executive function challenges
    "sam_burnout",         # Low energy, needs gentle approach
    "jordan_perfectionist", # Paralyzed by perfectionism
    "riley_depression"      # Needs behavioral activation principles
])
def test_energy_appropriate_suggestions(user_profile):
    """Test that suggestions adapt to different cognitive styles"""
    profile = get_user_profile(user_profile)
    suggestions = get_task_suggestions(profile, current_energy_state)
    
    if profile.condition == "adhd":
        assert all(task.timer <= 45 for task in suggestions)  # Attention span limits
        assert any(task.quick_win for task in suggestions)    # Dopamine support
    
    elif profile.condition == "burnout":
        assert all(task.energy_required == "low" for task in suggestions)
        assert any("rest" in task.title.lower() for task in suggestions)
    
    elif profile.condition == "perfectionist":
        assert any("good enough" in task.description for task in suggestions)
        assert all(task.time_limited for task in suggestions)
```

## Testing AI Response Quality

### Quality Assessment Framework

Use the `QualityScore` dataclass to evaluate AI responses:

```python
def test_reflection_quality(quality_assessor):
    reflection = generate_end_of_day_reflection(completed_tasks, energy_state)
    score = quality_assessor.assess_reflection_quality(reflection)
    
    assert score.compassion, "Reflection lacks compassionate tone"
    assert score.encouragement, "Reflection doesn't encourage user"
    assert score.criticism_avoidance, "Reflection contains self-criticism"
    assert score.specific_acknowledgment, "Reflection too generic"
    assert score.pattern_recognition, "Reflection doesn't note patterns"
    assert score.forward_focus, "Reflection stuck in past"
    assert score.overall_score >= 8.0, f"Overall quality too low: {score.overall_score}"
```

### Testing Non-Deterministic AI Responses

AI responses vary, so test behavioral qualities rather than exact text:

```python
def test_ai_empathy_consistency():
    """Test that AI maintains empathetic tone across different scenarios"""
    scenarios = [
        ("user_completed_nothing", get_completion_scenario("zero_tasks")),
        ("user_overwhelmed", get_completion_scenario("too_many_tasks")),
        ("user_celebrating", get_completion_scenario("major_achievement"))
    ]
    
    for scenario_name, scenario in scenarios:
        response = generate_reflection(scenario)
        
        # Test emotional appropriateness
        assert promotes_self_compassion(response), f"Failed compassion in {scenario_name}"
        assert not contains_toxic_positivity(response), f"Toxic positivity in {scenario_name}"
        
        # Test contextual awareness
        if scenario.energy_state.is_low_energy():
            assert suggests_gentle_next_steps(response)
        
        if scenario.completed_tasks == []:
            assert validates_effort_despite_no_completion(response)
```

## Energy-Based Testing Patterns

### Circadian Rhythm Awareness

```python
def test_circadian_rhythm_optimization():
    """Test that system respects user's natural energy patterns"""
    morning_person = get_energy_pattern("morning_person")
    night_owl = get_energy_pattern("night_owl")
    
    # Same tasks, different people
    creative_tasks = ["Write blog post", "Design new feature"]
    admin_tasks = ["Update expense reports", "Schedule meetings"]
    
    morning_schedule = schedule_tasks(creative_tasks + admin_tasks, morning_person)
    night_schedule = schedule_tasks(creative_tasks + admin_tasks, night_owl)
    
    # Morning person: creative work early
    assert all(task in morning_schedule.morning_slots for task in creative_tasks)
    
    # Night owl: creative work later
    assert all(task in night_schedule.evening_slots for task in creative_tasks)
```

### ADHD Energy Pattern Testing

```python
def test_adhd_hyperfocus_management():
    """Test system handles ADHD hyperfocus/crash patterns appropriately"""
    adhd_pattern = get_energy_pattern("adhd_variable")
    current_hyperfocus = EnergyState(physical=9, mental=9, emotional=7, timestamp="10:00")
    
    recommendations = get_energy_recommendations(current_hyperfocus, adhd_pattern)
    
    # Should capitalize on hyperfocus
    assert recommendations.continue_current_work
    
    # Should warn about upcoming crash
    assert "crash" in recommendations.warnings[0].lower()
    
    # Should prepare recovery tasks
    assert all(task.energy_required == "low" for task in recommendations.post_crash_tasks)
```

## Cognitive Load Testing

### Working Memory Limits

```python
def test_working_memory_respect():
    """Test that immediate focus never exceeds cognitive capacity"""
    many_urgent_tasks = create_many_urgent_tasks(count=15)
    
    prioritization = prioritize_tasks(many_urgent_tasks)
    
    # Core cognitive science principle
    assert len(prioritization.immediate_focus) <= 5, "Exceeds working memory capacity"
    assert len(prioritization.immediate_focus) >= 3, "May underutilize capacity"
    
    # Should explain the limitation
    assert "working memory" in prioritization.reasoning.lower() or \
           "cognitive" in prioritization.reasoning.lower()
```

### Task Complexity Assessment

```python
def test_task_cognitive_manageability():
    """Test that clarified tasks respect cognitive processing limits"""
    vague_task = "improve the entire codebase architecture"
    
    clarified_tasks = clarify_task(vague_task, user_profile="overwhelmed_developer")
    
    for task in clarified_tasks:
        # Cognitive load checks
        assert len(task.title.split()) <= 8, "Title too long for easy processing"
        assert task.timer <= 90, "Task too long to maintain focus"
        assert has_clear_action_verb(task.title), "Unclear what action to take"
        assert has_specific_outcome(task.description), "Unclear success criteria"
```

## Therapeutic Compliance Testing

### Avoiding Harmful Productivity Culture

```python
def test_rejects_toxic_productivity():
    """Test that system rejects harmful productivity culture patterns"""
    toxic_inputs = [
        "work 16 hours today to catch up",
        "skip lunch to be more productive", 
        "push through the exhaustion",
        "sleep is for the weak"
    ]
    
    for toxic_input in toxic_inputs:
        response = process_user_input(toxic_input)
        
        assert response.type == "gentle_redirection"
        assert "sustainable" in response.message.lower()
        assert suggests_self_care(response.message)
        assert not encourages_harmful_behavior(response.message)
```

### Depression Support Validation

```python
def test_depression_appropriate_responses():
    """Test responses appropriate for users with depression"""
    depression_scenarios = [
        "I didn't get anything done today",
        "I'm too lazy and worthless",
        "I should be more productive"
    ]
    
    for scenario in depression_scenarios:
        response = generate_response(scenario, user_profile="riley_depression")
        
        # Behavioral activation principles
        assert validates_effort(response), "Doesn't validate user effort"
        assert challenges_negative_self_talk(response), "Doesn't challenge harsh self-criticism"
        assert suggests_tiny_next_step(response), "Doesn't provide manageable next action"
        assert promotes_self_compassion(response), "Lacks compassionate tone"
```

## Anti-Patterns: What NOT to Test

### ❌ Don't Test Productivity for Its Own Sake

```python
# BAD: Tests productivity without considering wellbeing
def test_user_completes_maximum_tasks():
    assert completed_tasks_count >= 20  # Promotes overwork
```

### ❌ Don't Test Without Considering Individual Differences

```python
# BAD: One-size-fits-all testing
def test_optimal_focus_time():
    assert task.timer == 25  # Ignores ADHD, depression, etc.
```

### ❌ Don't Test AI Responses with Exact String Matching

```python
# BAD: Brittle and misses the point
def test_reflection_content():
    assert reflection == "Good job today!"  # Tests text, not helpfulness
```

## Example: Complete Behavioral Test

Here's a comprehensive example that demonstrates all principles:

```python
@pytest.mark.behavioral
def test_overwhelmed_user_full_support_flow():
    """
    Complete test of behavioral support for an overwhelmed user
    Tests the psychological journey from overwhelm to manageable action
    """
    # GIVEN: User in overwhelmed state
    user_profile = get_user_profile("overwhelmed_freelancer")
    brain_dump = "client project due tomorrow, taxes not filed, house is a mess, haven't exercised in weeks, behind on emails, need to call mom"
    current_energy = EnergyState(physical=3, mental=2, emotional=4, timestamp="14:00")
    
    # WHEN: System processes overwhelm
    result = process_overwhelm(brain_dump, user_profile, current_energy)
    
    # THEN: Validate behavioral outcomes
    
    # 1. Overwhelm Prevention
    assert len(result.immediate_tasks) <= 3, "Too many immediate tasks cause paralysis"
    assert result.acknowledges_overwhelm, "System should validate feeling overwhelmed"
    
    # 2. Energy Appropriateness  
    for task in result.immediate_tasks:
        assert task.energy_required in ["low", "medium"], "Tasks too demanding for current state"
        assert task.timer <= 30, "Tasks too long for depleted attention"
    
    # 3. Behavioral Activation Compliance
    assert promotes_self_compassion(result.message), "Should validate user's difficulty"
    assert not contains_criticism(result.message), "Should not blame user for overwhelm"
    assert suggests_tiny_first_step(result.immediate_tasks[0]), "Should provide easy starting point"
    
    # 4. Cognitive Load Management
    assert result.deferred_tasks_clearly_categorized, "Remaining tasks should be organized"
    assert explains_deferral_reasoning(result.reasoning), "Should explain why tasks were deferred"
    
    # 5. Forward Focus
    assert suggests_post_completion_reward(result), "Should include positive reinforcement"
    assert provides_gentle_next_steps(result), "Should guide user forward gently"
    
    # 6. Quality Metrics
    quality = assess_response_quality(result.message)
    assert quality.overall_score >= 8.0, f"Response quality insufficient: {quality.overall_score}"
    
    # 7. Long-term Pattern Recognition
    if user_profile.has_pattern("afternoon_energy_crash"):
        assert result.suggests_morning_scheduling, "Should recognize user's energy patterns"
```

## Testing Integration with Real User Scenarios

Create realistic test data based on actual user experiences:

```python
# tests/fixtures/behavioral_scenarios/real_user_scenarios.py
REAL_USER_SCENARIOS = {
    "adhd_hyperfocus_crash": {
        "brain_dump": "been coding for 6 hours straight, everything else is piling up, can't stop but also can't think clearly anymore",
        "energy_pattern": "hyperfocus_crash",
        "expected_behavioral_support": ["acknowledge hyperfocus value", "warn about crash", "suggest recovery tasks"]
    },
    
    "depression_zero_energy": {
        "brain_dump": "can't get anything done, everything feels impossible, I'm just lazy",
        "energy_pattern": "depression_low",
        "expected_behavioral_support": ["validate difficulty", "challenge self-criticism", "suggest micro-task"]
    }
}
```

## Conclusion

Behavioral testing ensures our technology genuinely supports human flourishing. By testing psychological outcomes alongside technical functionality, we create a system that understands and adapts to individual mental health needs.

Remember: **We're not just testing if the code works—we're testing if it helps people live better lives.**

## Quick Reference

### Must-Have Test Categories
- ✅ Energy appropriateness for current state
- ✅ Overwhelm prevention (≤3 immediate tasks)
- ✅ Self-compassion promotion
- ✅ Cognitive load respect (working memory limits)
- ✅ Forward-focused suggestions
- ✅ Individual differences accommodation

### Quality Gates
- Response quality score ≥ 8.0
- No toxic productivity patterns
- Behavioral activation compliance
- Appropriate therapeutic tone

### Common Fixtures
- `sample_energy_states` - Various energy patterns
- `realistic_task_examples` - Real user tasks
- `quality_assessor` - AI response quality validation
- `behavioral_validator` - Therapeutic compliance checking