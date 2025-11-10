"""Simple standalone test for graph_to_yaml converter.

No external dependencies needed - just the converter itself.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.quest_builder.graph_to_yaml_converter import graph_to_yaml


def test_graph_to_yaml():
    """Test converting React Flow graph to YAML."""

    graph = {
        "nodes": [
            {
                "id": "node1",
                "type": "start",
                "data": {
                    "label": "Добро пожаловать!",
                    "introText": "Начинаем наш квест!"
                }
            },
            {
                "id": "node2",
                "type": "questStep",
                "data": {
                    "prompt": "Сколько будет 2+2?",
                    "psychologicalMethod": "cognitive_challenge",
                    "validation": {"minLength": 1, "maxLength": 10},
                    "rewards": {"xp": 10, "items": []}
                }
            },
            {
                "id": "node3",
                "type": "end",
                "data": {
                    "completionMessage": "Отлично! Квест завершен!",
                    "finalRewards": {"xp": 100}
                }
            }
        ],
        "edges": [
            {"source": "node1", "target": "node2"},
            {"source": "node2", "target": "node3"}
        ],
        "metadata": {
            "quest_id": "test_quest_001",
            "title": "Математический Квест",
            "description": "Простой квест по математике",
            "difficulty": "easy",
            "age_range": "8-10",
            "psychological_module": "CBT",
            "location": "forest"
        }
    }

    print("🧪 Testing graph_to_yaml conversion...")

    try:
        yaml_str = graph_to_yaml(graph)

        print("\n✅ Conversion successful!")
        print(f"\n📄 Generated YAML ({len(yaml_str)} characters):\n")
        print(yaml_str)

        # Basic validation
        assert "quest_id: test_quest_001" in yaml_str, "quest_id not found"
        assert "title: Математический Квест" in yaml_str, "title not found"
        assert "node_id: node1" in yaml_str, "node1 not found"
        assert "node_id: node2" in yaml_str, "node2 not found"
        assert "node_id: node3" in yaml_str, "node3 not found"
        assert "psychological_module: CBT" in yaml_str, "psychological_module not found"

        print("\n✅ All assertions passed!")
        print("\n🎯 Test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_graph_to_yaml()
    sys.exit(0 if success else 1)
