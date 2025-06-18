# Test Suite Overview

This directory contains the automated tests for Qwen Task Manager 3.0.
The suite covers behavioral scenarios, integration flows and unit logic.

## Component Registry Tests

New unit tests in `tests/unit/test_component_registry.py` verify the
`ComponentRegistry` database layer:

- registering components and retrieving them by id
- querying components by file path
- persisting user story data
- flagging components and resolving those flags

Each test uses a temporary SQLite database so execution is isolated and does
not interfere with real data.
