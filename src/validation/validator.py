from typing import Dict, Any, List, Set

VALID_CHIA_NODE_TYPES: Set[str] = {
    "agent",
    "tool",
    "tool_executor",
    "evaluator",
    "router",
    "aggregator",
    "condition",
    "state_updater",
    "input",
    "output",
    "simulator",
    "optimizer",
    "analyzer",
    "champsim_runner",
    "llm",
    "custom",
}


def validate_chia_loop(loop_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates a CHIA loop configuration:
    - Verifies top-level structure (nodes, edges).
    - Verifies node uniqueness, required fields, and valid CHIA node types.
    - Verifies proper edge formatting (source and target existence, format).
    - Checks for orphan nodes and connectivity issues.
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(loop_data, dict):
        return {
            "valid": False,
            "errors": ["Loop configuration must be a JSON object (dictionary)."],
            "warnings": [],
            "details": {}
        }

    # 1. Validate Nodes
    nodes = loop_data.get("nodes")
    if nodes is None:
        errors.append("Missing required field 'nodes'.")
        nodes = []
    elif not isinstance(nodes, list):
        errors.append("Field 'nodes' must be a list.")
        nodes = []
    elif len(nodes) == 0:
        errors.append("Field 'nodes' must contain at least one node definition.")

    node_ids: Set[str] = set()
    node_types_found: Set[str] = set()
    tools_used: Set[str] = set()

    for idx, node in enumerate(nodes):
        if not isinstance(node, dict):
            errors.append(f"Node at index {idx} must be a JSON object.")
            continue

        node_id = node.get("id")
        if node_id is None or str(node_id).strip() == "":
            errors.append(f"Node at index {idx} is missing a valid 'id'.")
        else:
            node_id_str = str(node_id)
            if node_id_str in node_ids:
                errors.append(f"Duplicate node id '{node_id_str}' found at index {idx}.")
            node_ids.add(node_id_str)

        node_type = node.get("type") or node.get("node_type")
        if not node_type or str(node_type).strip() == "":
            errors.append(f"Node '{node_id or idx}' is missing required 'type'.")
        else:
            node_type_str = str(node_type).strip().lower()
            node_types_found.add(node_type_str)
            if node_type_str not in VALID_CHIA_NODE_TYPES:
                warnings.append(
                    f"Node '{node_id or idx}' has non-standard node type '{node_type}'. "
                    f"Standard types are: {', '.join(sorted(VALID_CHIA_NODE_TYPES))}."
                )

        # Collect tools if present
        if "tool" in node and node["tool"]:
            tools_used.add(str(node["tool"]))
        if "tools" in node and isinstance(node["tools"], list):
            for t in node["tools"]:
                tools_used.add(str(t))

    # 2. Validate Edges
    edges = loop_data.get("edges")
    if edges is None:
        errors.append("Missing required field 'edges'.")
        edges = []
    elif not isinstance(edges, list):
        errors.append("Field 'edges' must be a list.")
        edges = []

    connected_nodes: Set[str] = set()

    for idx, edge in enumerate(edges):
        if not isinstance(edge, dict):
            errors.append(f"Edge at index {idx} must be a JSON object.")
            continue

        source = edge.get("source") or edge.get("from")
        target = edge.get("target") or edge.get("to")

        if source is None or str(source).strip() == "":
            errors.append(f"Edge at index {idx} is missing a 'source' node identifier.")
        else:
            source_str = str(source)
            if source_str not in node_ids:
                errors.append(f"Edge at index {idx} references undefined source node '{source_str}'.")
            else:
                connected_nodes.add(source_str)

        if target is None or str(target).strip() == "":
            errors.append(f"Edge at index {idx} is missing a 'target' node identifier.")
        else:
            target_str = str(target)
            if target_str not in node_ids:
                errors.append(f"Edge at index {idx} references undefined target node '{target_str}'.")
            else:
                connected_nodes.add(target_str)

    # 3. Check for disconnected / orphan nodes if there are multiple nodes
    if len(node_ids) > 1:
        orphan_nodes = node_ids - connected_nodes
        if orphan_nodes:
            warnings.append(f"Detected orphan node(s) with no connected edges: {', '.join(sorted(orphan_nodes))}.")

    is_valid = len(errors) == 0

    return {
        "valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "details": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "node_types": sorted(list(node_types_found)),
            "tools_used": sorted(list(tools_used)),
            "nodes": sorted(list(node_ids)),
        }
    }
