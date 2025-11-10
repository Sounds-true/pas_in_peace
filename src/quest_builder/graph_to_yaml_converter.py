"""Graph to YAML converter for quest export.

Converts React Flow graph structure to YAML format for backward compatibility
and export to external systems.
"""

from typing import Dict, List, Any, Optional
import yaml

from src.core.logger import get_logger

logger = get_logger(__name__)


class GraphToYamlConverter:
    """Converts React Flow graph structure to YAML quest format."""

    def convert(self, graph_structure: Dict[str, Any]) -> str:
        """Convert graph structure to YAML.

        Args:
            graph_structure: React Flow graph with nodes and edges
                {
                    "nodes": [...],
                    "edges": [...],
                    "metadata": {...}
                }

        Returns:
            YAML string representation of quest

        Raises:
            ValueError: If graph structure is invalid
        """
        if not graph_structure:
            raise ValueError("Graph structure cannot be empty")

        nodes = graph_structure.get("nodes", [])
        edges = graph_structure.get("edges", [])
        metadata = graph_structure.get("metadata", {})

        if not nodes:
            raise ValueError("Graph must contain at least one node")

        # Build YAML structure
        yaml_dict = {
            "quest_id": metadata.get("quest_id", "quest_unknown"),
            "title": metadata.get("title", "Untitled Quest"),
            "description": metadata.get("description", ""),
            "difficulty": metadata.get("difficulty", "medium"),
            "age_range": metadata.get("age_range", "8-12"),
            "psychological_module": metadata.get("psychological_module", "general"),
            "location": metadata.get("location", "forest"),
            "nodes": []
        }

        # Build node adjacency map from edges
        adjacency = self._build_adjacency_map(edges)

        # Convert nodes to YAML format
        for node in nodes:
            yaml_node = self._convert_node(node, adjacency)
            if yaml_node:
                yaml_dict["nodes"].append(yaml_node)

        # Generate YAML string
        yaml_str = yaml.dump(
            yaml_dict,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120
        )

        logger.info(
            "graph_to_yaml_conversion_complete",
            nodes_count=len(yaml_dict["nodes"]),
            quest_id=yaml_dict["quest_id"]
        )

        return yaml_str

    def _build_adjacency_map(self, edges: List[Dict]) -> Dict[str, List[str]]:
        """Build adjacency map from edges.

        Args:
            edges: List of edge objects [{"source": "node1", "target": "node2"}]

        Returns:
            Dict mapping node_id to list of target node_ids
        """
        adjacency = {}
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            if source and target:
                if source not in adjacency:
                    adjacency[source] = []
                adjacency[source].append(target)
        return adjacency

    def _convert_node(
        self,
        node: Dict[str, Any],
        adjacency: Dict[str, List[str]]
    ) -> Optional[Dict[str, Any]]:
        """Convert single React Flow node to YAML node format.

        Args:
            node: React Flow node object
            adjacency: Adjacency map for next_nodes

        Returns:
            YAML node dict or None if conversion fails
        """
        node_id = node.get("id")
        node_type = node.get("type", "questStep")
        data = node.get("data", {})

        if not node_id:
            logger.warning("node_missing_id", node=node)
            return None

        # Base YAML node
        yaml_node = {
            "node_id": node_id,
            "type": self._convert_node_type(node_type)
        }

        # Add type-specific fields
        if node_type == "start":
            yaml_node["title"] = data.get("label", "Quest Start")
            yaml_node["intro_text"] = data.get("introText", "Welcome to the quest!")

        elif node_type == "questStep":
            yaml_node["prompt"] = data.get("prompt", "What do you think?")
            yaml_node["psychological_method"] = data.get("psychologicalMethod", "reflection")

            # Validation rules
            if data.get("validation"):
                yaml_node["validation"] = {
                    "min_length": data["validation"].get("minLength", 2),
                    "max_length": data["validation"].get("maxLength", 500)
                }

            # Rewards
            if data.get("rewards"):
                yaml_node["rewards"] = {
                    "xp": data["rewards"].get("xp", 10),
                    "items": data["rewards"].get("items", [])
                }

        elif node_type == "choice":
            yaml_node["question"] = data.get("question", "What will you do?")
            yaml_node["options"] = data.get("options", [])
            # Options format: [{"text": "...", "score": 1.0, "feedback": "..."}]

        elif node_type == "realityBridge":
            yaml_node["bridge_text"] = data.get("bridgeText", "Think about this in real life...")
            yaml_node["reflection_prompt"] = data.get("reflectionPrompt", "How does this apply to you?")

        elif node_type == "end":
            yaml_node["completion_message"] = data.get("completionMessage", "Quest complete!")
            yaml_node["final_rewards"] = data.get("finalRewards", {"xp": 100})

        # Add next nodes from adjacency map
        next_nodes = adjacency.get(node_id, [])
        if next_nodes:
            if len(next_nodes) == 1:
                yaml_node["next_node"] = next_nodes[0]
            else:
                yaml_node["next_nodes"] = next_nodes

        return yaml_node

    def _convert_node_type(self, react_flow_type: str) -> str:
        """Convert React Flow node type to YAML type.

        Args:
            react_flow_type: React Flow node type

        Returns:
            YAML node type
        """
        type_map = {
            "start": "intro",
            "questStep": "question",
            "choice": "choice",
            "realityBridge": "reflection",
            "end": "completion"
        }
        return type_map.get(react_flow_type, "question")

    def convert_batch(self, graphs: List[Dict[str, Any]]) -> List[str]:
        """Convert multiple graphs to YAML.

        Args:
            graphs: List of graph structures

        Returns:
            List of YAML strings
        """
        results = []
        for i, graph in enumerate(graphs):
            try:
                yaml_str = self.convert(graph)
                results.append(yaml_str)
            except Exception as e:
                logger.error(
                    "batch_conversion_failed",
                    index=i,
                    error=str(e)
                )
                results.append(None)

        success_count = sum(1 for r in results if r is not None)
        logger.info(
            "batch_conversion_complete",
            total=len(graphs),
            success=success_count,
            failed=len(graphs) - success_count
        )

        return results


# Convenience function
def graph_to_yaml(graph_structure: Dict[str, Any]) -> str:
    """Convert graph to YAML (convenience function).

    Args:
        graph_structure: React Flow graph structure

    Returns:
        YAML string
    """
    converter = GraphToYamlConverter()
    return converter.convert(graph_structure)
