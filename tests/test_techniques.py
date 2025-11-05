"""Tests for therapeutic techniques."""

import pytest
from src.techniques import CBTReframing, GroundingTechnique, ValidationTechnique


@pytest.mark.asyncio
async def test_cbt_reframing():
    """Test CBT cognitive reframing."""
    cbt = CBTReframing()

    context = {
        "primary_emotion": "anger",
        "distress_level": "moderate"
    }

    result = await cbt.apply("Она ВСЕГДА настраивает ребёнка против меня", context)

    assert result.success
    assert "catastrophizing" in result.metadata.get("distortion_detected", "")
    assert len(result.response) > 0


@pytest.mark.asyncio
async def test_grounding_technique():
    """Test grounding exercises."""
    grounding = GroundingTechnique()

    context = {
        "distress_level": "high",
        "primary_emotion": "fear"
    }

    result = await grounding.apply("Я не могу справиться", context)

    assert result.success
    assert "5-4-3-2-1" in result.response or "дыхание" in result.response.lower()


@pytest.mark.asyncio
async def test_validation():
    """Test emotional validation."""
    validation = ValidationTechnique()

    context = {
        "primary_emotion": "grief",
        "distress_level": "high"
    }

    result = await validation.apply("Мне так тяжело", context)

    assert result.success
    assert len(result.response) > 50
