"""
Scenario-based testing for emotional states and therapeutic responses.

This module provides:
- Scenario definitions (scenarios.json)
- Scenario test runner (test_emotional_states.py)
- Validation framework for bot responses
"""

from .test_emotional_states import (
    ScenarioLoader,
    ScenarioTester,
    ScenarioTestResult,
)

__all__ = [
    'ScenarioLoader',
    'ScenarioTester',
    'ScenarioTestResult',
]
