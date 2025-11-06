"""
Scenario-based testing for emotional states.

Tests bot responses to 7 core emotional states experienced by alienated parents:
1. Shock & Denial
2. Rage & Aggression
3. Despair & Helplessness
4. Guilt & Self-Blame
5. Bargaining
6. Obsessive Fighting
7. Reality Acceptance

Each scenario validates:
- Emotion detection
- Technique selection
- Response quality
- Safety protocols
- Content appropriateness
"""

import json
import pytest
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

# We'll need to import the actual bot components
# For now, creating structure that will work when bot is integrated


@dataclass
class ScenarioTestResult:
    """Result of running a scenario test."""
    scenario_id: str
    passed: bool
    detected_emotion: str
    techniques_used: List[str]
    response_text: str
    quality_scores: Dict[str, float]
    crisis_detected: bool
    errors: List[str]
    warnings: List[str]


class ScenarioLoader:
    """Loads and manages test scenarios."""

    def __init__(self, scenarios_file: Path = None):
        if scenarios_file is None:
            scenarios_file = Path(__file__).parent / "scenarios.json"

        with open(scenarios_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.scenarios = data['emotional_states']
        self.metadata = data['metadata']

    def get_scenarios(self, emotional_state: str = None) -> List[Dict]:
        """Get scenarios for a specific emotional state or all scenarios."""
        if emotional_state:
            return self.scenarios.get(emotional_state, [])

        # Return all scenarios
        all_scenarios = []
        for state, scenarios in self.scenarios.items():
            for scenario in scenarios:
                scenario['emotional_state'] = state
                all_scenarios.append(scenario)
        return all_scenarios

    def get_scenario_by_id(self, scenario_id: str) -> Dict:
        """Get a specific scenario by ID."""
        for state, scenarios in self.scenarios.items():
            for scenario in scenarios:
                if scenario['id'] == scenario_id:
                    scenario['emotional_state'] = state
                    return scenario
        raise ValueError(f"Scenario {scenario_id} not found")


class ScenarioTester:
    """Runs scenarios through the bot and validates responses."""

    def __init__(self):
        # TODO: Initialize bot components when available
        # self.bot = PASBot()
        # self.emotion_detector = EmotionDetector()
        # self.crisis_detector = CrisisDetector()
        pass

    async def run_scenario(self, scenario: Dict) -> ScenarioTestResult:
        """
        Run a single scenario through the bot.

        Args:
            scenario: Scenario configuration from scenarios.json

        Returns:
            ScenarioTestResult with validation results
        """
        errors = []
        warnings = []

        # TODO: Replace with actual bot call
        # For now, return mock result for structure validation

        # This is where we would call:
        # response = await self.bot.process_message(
        #     user_id=999,  # Test user
        #     message=scenario['input'],
        #     context=scenario.get('context', {})
        # )

        # Mock response for now
        detected_emotion = "unknown"
        techniques_used = []
        response_text = "Mock response"
        quality_scores = {
            'empathy': 0.0,
            'safety': 0.0,
            'therapeutic_value': 0.0
        }
        crisis_detected = False

        # Validate results against expectations
        errors.extend(self._validate_emotion(
            detected_emotion,
            scenario.get('expected_emotion', [])
        ))

        errors.extend(self._validate_techniques(
            techniques_used,
            scenario.get('expected_techniques', [])
        ))

        errors.extend(self._validate_content(
            response_text,
            scenario.get('should_contain', []),
            scenario.get('should_not_contain', [])
        ))

        errors.extend(self._validate_quality(
            quality_scores,
            scenario.get('quality_thresholds', {})
        ))

        if scenario.get('crisis_check'):
            if not crisis_detected:
                warnings.append("Crisis check expected but not triggered")

        passed = len(errors) == 0

        return ScenarioTestResult(
            scenario_id=scenario['id'],
            passed=passed,
            detected_emotion=detected_emotion,
            techniques_used=techniques_used,
            response_text=response_text,
            quality_scores=quality_scores,
            crisis_detected=crisis_detected,
            errors=errors,
            warnings=warnings
        )

    def _validate_emotion(
        self,
        detected: str,
        expected: List[str]
    ) -> List[str]:
        """Validate that detected emotion matches expectations."""
        if not expected:
            return []

        if detected not in expected:
            return [f"Expected emotion in {expected}, got '{detected}'"]
        return []

    def _validate_techniques(
        self,
        used: List[str],
        expected: List[str]
    ) -> List[str]:
        """Validate that expected techniques were used."""
        errors = []
        for technique in expected:
            if technique not in used:
                errors.append(f"Expected technique '{technique}' not used")
        return errors

    def _validate_content(
        self,
        response: str,
        should_contain: List[str],
        should_not_contain: List[str]
    ) -> List[str]:
        """Validate response content."""
        errors = []
        response_lower = response.lower()

        for phrase in should_contain:
            if phrase.lower() not in response_lower:
                errors.append(f"Response should contain '{phrase}'")

        for phrase in should_not_contain:
            if phrase.lower() in response_lower:
                errors.append(f"Response should NOT contain '{phrase}'")

        return errors

    def _validate_quality(
        self,
        scores: Dict[str, float],
        thresholds: Dict[str, float]
    ) -> List[str]:
        """Validate quality scores meet thresholds."""
        errors = []
        for metric, threshold in thresholds.items():
            if metric not in scores:
                errors.append(f"Quality metric '{metric}' not measured")
            elif scores[metric] < threshold:
                errors.append(
                    f"Quality metric '{metric}' below threshold: "
                    f"{scores[metric]:.2f} < {threshold:.2f}"
                )
        return errors


# ============================================================================
# PYTEST TESTS
# ============================================================================

@pytest.fixture
def scenario_loader():
    """Fixture providing scenario loader."""
    return ScenarioLoader()


@pytest.fixture
def scenario_tester():
    """Fixture providing scenario tester."""
    return ScenarioTester()


class TestEmotionalStates:
    """Test suite for all emotional states."""

    @pytest.mark.asyncio
    async def test_shock_and_denial_scenarios(
        self,
        scenario_loader,
        scenario_tester
    ):
        """Test all Shock & Denial scenarios."""
        scenarios = scenario_loader.get_scenarios('shock_and_denial')
        assert len(scenarios) > 0, "No shock_and_denial scenarios found"

        results = []
        for scenario in scenarios:
            result = await scenario_tester.run_scenario(scenario)
            results.append(result)

            # Log result
            print(f"\n{'='*60}")
            print(f"Scenario: {scenario['name']} ({scenario['id']})")
            print(f"Input: {scenario['input']}")
            print(f"Passed: {result.passed}")
            if result.errors:
                print(f"Errors: {result.errors}")
            if result.warnings:
                print(f"Warnings: {result.warnings}")

        # At least one scenario should pass (when bot is integrated)
        # For now, we're validating structure
        assert len(results) == len(scenarios)

    @pytest.mark.asyncio
    async def test_rage_and_aggression_scenarios(
        self,
        scenario_loader,
        scenario_tester
    ):
        """Test all Rage & Aggression scenarios."""
        scenarios = scenario_loader.get_scenarios('rage_and_aggression')
        assert len(scenarios) > 0

        for scenario in scenarios:
            result = await scenario_tester.run_scenario(scenario)

            # Scenarios with violence_assessment should trigger safety checks
            if scenario.get('violence_assessment'):
                # When integrated: assert result.crisis_detected
                pass

    @pytest.mark.asyncio
    async def test_despair_and_helplessness_scenarios(
        self,
        scenario_loader,
        scenario_tester
    ):
        """Test all Despair & Helplessness scenarios."""
        scenarios = scenario_loader.get_scenarios('despair_and_helplessness')
        assert len(scenarios) > 0

        for scenario in scenarios:
            result = await scenario_tester.run_scenario(scenario)

            # Suicide assessment scenarios are CRITICAL
            if scenario.get('columbia_ssrs_required'):
                # When integrated:
                # assert result.crisis_detected
                # assert 'columbia_ssrs' in result.techniques_used
                # assert result.quality_scores['safety'] == 1.0
                pass

            if scenario.get('hotline_referral_required'):
                # When integrated:
                # assert 'горячая линия' in result.response_text.lower()
                pass

    @pytest.mark.asyncio
    async def test_guilt_and_self_blame_scenarios(
        self,
        scenario_loader,
        scenario_tester
    ):
        """Test all Guilt & Self-Blame scenarios."""
        scenarios = scenario_loader.get_scenarios('guilt_and_self_blame')
        assert len(scenarios) > 0

        for scenario in scenarios:
            result = await scenario_tester.run_scenario(scenario)

            # CBT reframing should be common in guilt scenarios
            # When integrated:
            # assert 'cbt_reframing' in result.techniques_used

    @pytest.mark.asyncio
    async def test_bargaining_scenarios(
        self,
        scenario_loader,
        scenario_tester
    ):
        """Test all Bargaining scenarios."""
        scenarios = scenario_loader.get_scenarios('bargaining')
        assert len(scenarios) > 0

        for scenario in scenarios:
            result = await scenario_tester.run_scenario(scenario)

            # MI should be common in bargaining scenarios
            # When integrated:
            # assert 'motivational_interviewing' in result.techniques_used

    @pytest.mark.asyncio
    async def test_obsessive_fighting_scenarios(
        self,
        scenario_loader,
        scenario_tester
    ):
        """Test all Obsessive Fighting scenarios."""
        scenarios = scenario_loader.get_scenarios('obsessive_fighting')
        assert len(scenarios) > 0

        for scenario in scenarios:
            result = await scenario_tester.run_scenario(scenario)

            # IFS parts work should be common for obsessive patterns
            # When integrated:
            # assert 'ifs_parts_work' in result.techniques_used

    @pytest.mark.asyncio
    async def test_reality_acceptance_scenarios(
        self,
        scenario_loader,
        scenario_tester
    ):
        """Test all Reality Acceptance scenarios."""
        scenarios = scenario_loader.get_scenarios('reality_acceptance')
        assert len(scenarios) > 0

        for scenario in scenarios:
            result = await scenario_tester.run_scenario(scenario)

            # These should have high therapeutic value
            # When integrated:
            # assert result.quality_scores['therapeutic_value'] >= 0.75

    @pytest.mark.asyncio
    async def test_all_scenarios_coverage(self, scenario_loader):
        """Test that all 7 emotional states have scenarios."""
        expected_states = [
            'shock_and_denial',
            'rage_and_aggression',
            'despair_and_helplessness',
            'guilt_and_self_blame',
            'bargaining',
            'obsessive_fighting',
            'reality_acceptance'
        ]

        for state in expected_states:
            scenarios = scenario_loader.get_scenarios(state)
            assert len(scenarios) > 0, f"No scenarios for {state}"
            assert len(scenarios) >= 3, f"Need at least 3 scenarios for {state}"

    @pytest.mark.asyncio
    async def test_crisis_scenarios_have_safety_checks(
        self,
        scenario_loader
    ):
        """Validate that crisis scenarios have proper safety requirements."""
        all_scenarios = scenario_loader.get_scenarios()

        crisis_scenarios = [
            s for s in all_scenarios
            if s.get('crisis_check') or s.get('suicide_assessment')
        ]

        assert len(crisis_scenarios) > 0, "No crisis scenarios found"

        for scenario in crisis_scenarios:
            # Crisis scenarios should have high safety thresholds
            thresholds = scenario.get('quality_thresholds', {})
            assert thresholds.get('safety', 0) >= 0.9, \
                f"Crisis scenario {scenario['id']} has low safety threshold"

    def test_scenario_structure_validation(self, scenario_loader):
        """Validate that all scenarios have required fields."""
        all_scenarios = scenario_loader.get_scenarios()

        required_fields = ['id', 'name', 'input', 'expected_emotion']

        for scenario in all_scenarios:
            for field in required_fields:
                assert field in scenario, \
                    f"Scenario {scenario.get('id', 'unknown')} missing field '{field}'"

            # Validate ID format
            assert scenario['id'].count('_') == 1, \
                f"Invalid scenario ID format: {scenario['id']}"

            # Validate expected_emotion is a list
            assert isinstance(scenario['expected_emotion'], list), \
                f"expected_emotion should be list in {scenario['id']}"


# ============================================================================
# MANUAL TEST RUNNER (for development)
# ============================================================================

async def run_scenario_manually(scenario_id: str):
    """
    Manually run a specific scenario for testing.
    Usage: python -m pytest tests/scenarios/test_emotional_states.py::run_scenario_manually
    """
    loader = ScenarioLoader()
    tester = ScenarioTester()

    scenario = loader.get_scenario_by_id(scenario_id)
    result = await tester.run_scenario(scenario)

    print(f"\n{'='*60}")
    print(f"Scenario: {scenario['name']}")
    print(f"ID: {scenario_id}")
    print(f"{'='*60}")
    print(f"\nInput:\n{scenario['input']}")
    print(f"\nContext: {scenario.get('context', 'N/A')}")
    print(f"\nExpected Emotion: {scenario['expected_emotion']}")
    print(f"Expected Techniques: {scenario['expected_techniques']}")
    print(f"\n{'='*60}")
    print(f"RESULTS:")
    print(f"{'='*60}")
    print(f"Passed: {result.passed}")
    print(f"Detected Emotion: {result.detected_emotion}")
    print(f"Techniques Used: {result.techniques_used}")
    print(f"Crisis Detected: {result.crisis_detected}")
    print(f"\nResponse:\n{result.response_text}")
    print(f"\nQuality Scores:")
    for metric, score in result.quality_scores.items():
        print(f"  {metric}: {score:.2f}")

    if result.errors:
        print(f"\nErrors:")
        for error in result.errors:
            print(f"  ❌ {error}")

    if result.warnings:
        print(f"\nWarnings:")
        for warning in result.warnings:
            print(f"  ⚠️  {warning}")


if __name__ == "__main__":
    import asyncio

    # Example: Run a specific scenario
    asyncio.run(run_scenario_manually("despair_003"))
