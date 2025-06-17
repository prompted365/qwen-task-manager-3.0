# 🚀 Quick Start Testing Guide
*Get running with behavioral-first testing in 5 minutes*

## ⚡ 5-Minute Setup

### **Step 1: Install Dependencies** (1 minute)
```bash
# Install testing framework
pip install pytest pytest-asyncio pytest-mock pytest-cov

# Install behavioral testing dependencies
pip install psychopy scipy pandas matplotlib

# Install AI testing tools
pip install openai anthropic transformers
```

### **Step 2: Verify Installation** (1 minute)
```bash
# Run basic test to verify setup
cd tests/
pytest examples/example_behavioral_test.py -v

# Should see:
# ✅ test_task_creation_reduces_cognitive_load PASSED
# ✅ test_ai_suggestions_are_explainable PASSED
# ✅ test_energy_patterns_are_respected PASSED
```

### **Step 3: Run Your First Behavioral Test** (2 minutes)
```bash
# Run a complete behavioral test suite
pytest behavioral/test_behavioral_framework.py::test_user_stress_reduction -v

# Watch the magic happen:
# 🧠 Analyzing cognitive load... PASSED
# ⚡ Validating energy alignment... PASSED
# 🎯 Checking behavioral outcomes... PASSED
```

### **Step 4: Generate Your First Test Report** (1 minute)
```bash
# Create a beautiful behavioral test report
python reporting/test_report_generator.py --output-format html

# Open the generated report in your browser
open test_reports/behavioral_analysis_$(date +%Y%m%d).html
```

**🎉 Congratulations! You're now running the world's most advanced behavioral testing framework!**

---

## 🎯 Essential Commands for Daily Use

### **Run Complete Test Suite**
```bash
# Full behavioral validation (recommended daily)
pytest --cov=. --cov-report=html

# Quick smoke test (before commits)
pytest behavioral/test_behavioral_framework.py -v

# Performance regression check
pytest performance/ -v
```

### **Generate Behavioral Insights**
```bash
# Create behavioral metrics dashboard
python reporting/behavioral_metrics.py --analyze-week

# Generate AI reasoning report
python tools/ai_response_validator.py --validate-latest

# Create anonymized test data
python tools/test_data_anonymizer.py --generate-sample
```

### **Auto-Generate New Tests**
```bash
# Create tests for new features
python tools/behavioral_test_generator.py --feature "task_prioritization"

# Generate edge case tests
python tools/behavioral_test_generator.py --edge-cases --persona "stressed_student"
```

---

## 📖 Common Testing Scenarios

### **Scenario 1: Testing a New Task Creation Feature**

```python
# File: test_my_new_feature.py
import pytest
from fixtures.behavioral_scenarios.real_world_scenarios import *
from utils.test_helpers import behavioral_test, UserPersona

@behavioral_test
def test_new_task_feature_reduces_overwhelm():
    """Validates new task creation doesn't increase user stress."""
    
    # Given: User with high task anxiety
    user = UserPersona.overwhelmed_professional()
    initial_stress = user.current_stress_level
    
    # When: They use the new task creation feature
    task = user.create_task_with_new_feature(
        title="Prepare presentation",
        context="deadline_pressure"
    )
    
    # Then: Stress decreases and clarity increases
    assert user.current_stress_level < initial_stress
    assert task.cognitive_load_score <= 6
    assert task.has_clear_next_action == True
    assert task.estimated_duration is not None
```

### **Scenario 2: Testing AI Interactions**

```python
# File: test_ai_feature.py
from ai_reasoning.test_qwen_interactions import *

@behavioral_test
def test_ai_provides_helpful_task_suggestions():
    """Validates AI suggestions are actually helpful to users."""
    
    # Given: User stuck on a complex project
    user = UserPersona.creative_blocked()
    project = user.current_project
    
    # When: AI provides task breakdown suggestions
    suggestions = ai_agent.suggest_task_breakdown(
        project=project,
        user_context=user.get_context()
    )
    
    # Then: Suggestions reduce complexity and increase motivation
    assert len(suggestions) <= 7  # Miller's Rule: 7±2 items
    assert all(s.has_clear_outcome for s in suggestions)
    assert suggestions.confidence_score >= 0.8
    assert suggestions.reasoning_provided == True
    
    # And: User feels more capable
    user.review_suggestions(suggestions)
    assert user.project_confidence > user.baseline_confidence
```

### **Scenario 3: Testing Performance Under Stress**

```python
# File: test_stress_performance.py
from performance.test_stress_scenarios import *

@behavioral_test
async def test_system_maintains_quality_under_load():
    """Validates behavioral quality doesn't degrade under system stress."""
    
    # Given: High-load scenario with multiple users
    users = [UserPersona.generate_random() for _ in range(100)]
    
    # When: All users interact simultaneously
    async with stress_test_context(concurrent_users=100):
        responses = await asyncio.gather(*[
            user.create_complex_task_sequence() for user in users
        ])
    
    # Then: All behavioral quality gates still pass
    for response in responses:
        assert response.cognitive_load_score <= 7
        assert response.response_time <= 200  # milliseconds
        assert response.ai_reasoning_quality >= 0.9
```

---

## 🔧 Troubleshooting Common Issues

### **Issue: Tests fail with "Behavioral threshold not met"**

**Problem**: Your feature isn't meeting behavioral quality standards.

**Solution**:
```python
# Check what's failing
pytest --behavioral-debug test_your_feature.py

# Common fixes:
# 1. Reduce cognitive complexity
task.simplify_interface()

# 2. Improve AI explanations
ai_response.add_reasoning_chain()

# 3. Align with user energy levels
task.adjust_for_user_energy(user.current_energy)
```

### **Issue: AI tests timeout or fail**

**Problem**: AI interactions aren't responding properly.

**Solution**:
```bash
# Check AI service connectivity
python tools/ai_response_validator.py --health-check

# Reset AI test fixtures
python -m pytest --setup-only ai_reasoning/

# Use mock AI for development
export TESTING_MODE=mock_ai
pytest ai_reasoning/ -v
```

### **Issue: Performance tests are inconsistent**

**Problem**: System performance varies between test runs.

**Solution**:
```python
# Use performance baselines
@pytest.mark.performance_baseline
def test_with_consistent_baseline():
    with performance_baseline_context():
        # Your test here
        pass

# Or exclude performance tests during development
pytest -m "not performance"
```

### **Issue: Behavioral scenarios feel artificial**

**Problem**: Tests don't reflect real user behavior.

**Solution**:
```python
# Use real-world scenarios from research
from fixtures.behavioral_scenarios.real_world_scenarios import *

# Base tests on actual user interviews
scenario = UserInterviewScenario.stressed_parent_morning_routine()

# Include emotional context
user = UserPersona.from_real_interview(interview_id="parent_001")
```

---

## 📚 Learning Resources

### **🎓 Next Steps for Deeper Learning**

1. **Understand the Philosophy** 
   → [`docs/BEHAVIORAL_TESTING_GUIDE.md`](./docs/BEHAVIORAL_TESTING_GUIDE.md)

2. **Master AI Testing Patterns**
   → [`docs/AI_TESTING_PATTERNS.md`](./docs/AI_TESTING_PATTERNS.md)

3. **Learn Implementation Details**
   → [`docs/IMPLEMENTATION_GUIDE.md`](./docs/IMPLEMENTATION_GUIDE.md)

4. **Study Working Examples**
   → [`examples/example_behavioral_test.py`](./examples/example_behavioral_test.py)

5. **Understand Testing Workflows**
   → [`docs/TESTING_WORKFLOWS.md`](./docs/TESTING_WORKFLOWS.md)

### **🛠️ Essential Tools to Master**

```bash
# Behavioral test generator - creates tests from user stories
python tools/behavioral_test_generator.py --help

# AI response validator - ensures AI quality
python tools/ai_response_validator.py --help

# Test data anonymizer - protects user privacy
python tools/test_data_anonymizer.py --help
```

### **📊 Monitoring Your Progress**

```bash
# Daily behavioral health check
python reporting/behavioral_metrics.py --daily-summary

# Weekly quality dashboard
python reporting/quality_dashboard.py --week-view

# Monthly testing ecosystem health
python reporting/test_report_generator.py --ecosystem-health
```

---

## 🎯 Pro Tips for Maximum Effectiveness

### **1. Start with User Stories**
```python
# Always begin with the human need
@behavioral_test
def test_helps_busy_parent_plan_week():
    """Story: As a busy parent, I want to quickly plan my week 
    so that I can feel more in control and less overwhelmed."""
    
    # Implementation follows the story
```

### **2. Use Real User Personas**
```python
# Don't test with generic users
user = UserPersona.busy_single_parent(
    children_ages=[5, 8],
    work_schedule="variable_retail",
    stress_level="high",
    tech_comfort="medium"
)
```

### **3. Test Emotional Outcomes**
```python
# Measure what matters to humans
assert user.feels_more_capable_after_interaction()
assert task.reduces_decision_fatigue()
assert ai_suggestion.increases_confidence()
```

### **4. Include Recovery Scenarios**
```python
# Test how gracefully you handle problems
def test_graceful_failure_reduces_frustration():
    # When something goes wrong...
    with simulated_failure():
        response = user.attempt_complex_task()
    
    # User should still feel supported
    assert response.provides_helpful_alternatives()
    assert user.frustration_level < baseline_frustration
```

### **5. Validate AI Transparency**
```python
# Always test that AI decisions are explainable
def test_ai_reasoning_is_understandable():
    suggestion = ai_agent.suggest_task_order(user_tasks)
    
    assert suggestion.reasoning_chain is not None
    assert suggestion.confidence_level is not None
    assert suggestion.alternative_approaches is not None
```

---

## 🚀 Ready to Build Better Software?

You now have everything you need to start testing like a behavioral scientist! Remember:

- **Start small** - Begin with one behavioral test
- **Think human-first** - Every test should validate human benefit
- **Iterate quickly** - Use our tools to generate tests faster
- **Measure what matters** - Focus on real user outcomes

**Your next step**: Pick a feature you're working on and write your first behavioral test using the examples above.

---

## 🆘 Need Help?

- **Quick Questions**: Check the troubleshooting section above
- **Implementation Help**: Read [`docs/IMPLEMENTATION_GUIDE.md`](./docs/IMPLEMENTATION_GUIDE.md)
- **Conceptual Questions**: Start with [`docs/BEHAVIORAL_TESTING_GUIDE.md`](./docs/BEHAVIORAL_TESTING_GUIDE.md)
- **AI Testing Issues**: See [`docs/AI_TESTING_PATTERNS.md`](./docs/AI_TESTING_PATTERNS.md)

**Happy testing! 🧪✨**

*Remember: We're not just testing code—we're validating that technology truly serves human flourishing.*