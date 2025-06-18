import pytest
import importlib.util
from pathlib import Path

# The repository contains both an `agents` package directory and an
# `agents.py` module which would shadow the package when importing
# normally. We load the `component_registry` module directly from its
# file path to avoid that conflict.
spec = importlib.util.spec_from_file_location(
    "component_registry",
    Path(__file__).resolve().parents[2] / "agents" / "component_registry.py",
)
component_registry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(component_registry)
ComponentRegistry = component_registry.ComponentRegistry

@pytest.fixture
def registry(tmp_path):
    db = tmp_path / "registry.db"
    return ComponentRegistry(db)

def test_register_and_get_component(registry):
    comp_id = registry.register_component({
        'name': 'TestModule',
        'type': 'module',
        'file_path': '/tmp/test_module.py'
    })

    stored = registry.get_component(comp_id)
    assert stored is not None
    assert stored['name'] == 'TestModule'
    assert stored['type'] == 'module'
    assert stored['file_path'] == '/tmp/test_module.py'

def test_get_components_by_path(registry):
    path = '/tmp/shared.py'
    registry.register_component({'name': 'A', 'type': 'module', 'file_path': path})
    registry.register_component({'name': 'B', 'type': 'module', 'file_path': path})

    comps = registry.get_components_by_path(path)
    assert len(comps) == 2
    names = {c['name'] for c in comps}
    assert names == {'A', 'B'}

def test_store_and_retrieve_user_story(registry):
    comp_id = registry.register_component({'name': 'StoryComp', 'type': 'module', 'file_path': '/tmp/story.py'})
    uss = {
        'user_story': 'As a user, I test components',
        'engagement': 'direct',
        'primitive_value': 'testing',
        'expression': 'works',
        'confidence': 0.9,
        'quality_score': 0.8,
        'touch_points': ['cli', 'api']
    }
    registry.store_user_story(comp_id, uss)

    story = registry.get_component_story(comp_id)
    assert story is not None
    assert story['user_story'] == uss['user_story']
    assert set(story['touch_points']) == {'cli', 'api'}

def test_flag_and_resolve_component(registry):
    comp_id = registry.register_component({'name': 'FlagMe', 'type': 'module', 'file_path': '/tmp/flag.py'})
    registry.flag_component(comp_id, 'minor', 'needs review')

    flagged = registry.get_flagged_components()
    assert any(f['id'] == comp_id for f in flagged)

    resolved = registry.resolve_flag(comp_id, resolved_by='tester')
    assert resolved
    assert registry.get_flagged_components() == []
