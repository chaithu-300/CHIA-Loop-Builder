import sys
import json
import argparse
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, model_validator, field_validator, ValidationError


class EdgeType(str, Enum):
    PROGRAMMATIC = "programmatic"
    AGENTIC = "agentic"
    CONDITIONAL = "conditional"
    DEFAULT = "default"


class CHIANode(BaseModel):
    id: str = Field(..., description="Unique node identifier in the hardware pipeline.")
    type: str = Field(..., description="CHIA node type (e.g., agent, tool_executor, evaluator, simulator, optimizer).")
    function: Optional[str] = Field(
        default=None,
        description="Python function executing the hardware design pipeline step (e.g. run_champsim_simulation, evaluate_cache_hierarchy)."
    )
    python_function: Optional[str] = Field(
        default=None,
        description="Alias for Python function executing the hardware design pipeline step."
    )
    description: Optional[str] = Field(default=None, description="Detailed explanation of what this pipeline step performs.")
    tool: Optional[str] = Field(default=None, description="External tool or binary invoked by this function.")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Hardware parameters and step configurations.")
    inputs: Optional[List[str]] = Field(default_factory=list, description="Input state variables or artifact dependencies.")
    outputs: Optional[List[str]] = Field(default_factory=list, description="Output metrics or updated state keys.")

    @model_validator(mode="after")
    def populate_function_defaults(self):
        """Ensures that every node maps to a Python function for executing the pipeline step."""
        if not self.function and not self.python_function:
            func_name = self.tool or f"{self.type}_{self.id}"
            self.function = str(func_name).replace("-", "_").lower()
        elif self.python_function and not self.function:
            self.function = self.python_function
        return self


class CHIAEdge(BaseModel):
    source: str = Field(..., description="Source node ID.")
    target: str = Field(..., description="Target node ID.")
    edge_type: EdgeType = Field(
        default=EdgeType.PROGRAMMATIC,
        description="Type of transition between hardware steps: 'programmatic' (deterministic/rule-based) or 'agentic' (LLM-driven routing/decision)."
    )
    condition: Optional[str] = Field(default=None, description="Execution condition or LLM routing prompt.")
    description: Optional[str] = Field(default=None, description="Description of the transition or data flow.")

    @field_validator("edge_type", mode="before")
    @classmethod
    def normalize_edge_type(cls, v):
        """Normalizes edge_type strings into valid EdgeType enum."""
        if isinstance(v, str):
            v_lower = v.strip().lower()
            if v_lower in ("programmatic", "deterministic", "rule", "standard", "code"):
                return EdgeType.PROGRAMMATIC
            elif v_lower in ("agentic", "llm", "decision", "dynamic", "prompt"):
                return EdgeType.AGENTIC
            elif v_lower in ("conditional", "condition"):
                return EdgeType.CONDITIONAL
            elif v_lower in ("default",):
                return EdgeType.DEFAULT
        return v


class CHIALoop(BaseModel):
    name: str = Field(..., description="Name of the CHIA hardware optimization loop.")
    description: Optional[str] = Field(default=None, description="Summary of loop objectives.")
    nodes: List[CHIANode] = Field(..., min_length=1, description="List of nodes representing hardware pipeline step functions.")
    edges: List[CHIAEdge] = Field(default_factory=list, description="List of programmatic or agentic transitions between steps.")
    node_types: Optional[List[str]] = Field(default_factory=list, description="All unique node types used in this loop.")
    tools_used: Optional[List[str]] = Field(default_factory=list, description="All tools used in this loop.")
    state_schema: Optional[Dict[str, Any]] = Field(default_factory=dict, description="State schema defining hardware parameters and metrics.")

    @model_validator(mode="after")
    def validate_graph_integrity(self):
        """Validates node uniqueness and edge source/target references."""
        node_id_set = set()
        for node in self.nodes:
            if node.id in node_id_set:
                raise ValueError(f"Duplicate node ID detected: '{node.id}'")
            node_id_set.add(node.id)

        for idx, edge in enumerate(self.edges):
            if edge.source not in node_id_set:
                raise ValueError(f"Edge #{idx} references non-existent source node '{edge.source}'")
            if edge.target not in node_id_set:
                raise ValueError(f"Edge #{idx} references non-existent target node '{edge.target}'")

        if not self.node_types:
            self.node_types = sorted(list({n.type for n in self.nodes}))

        if not self.tools_used:
            self.tools_used = sorted(list({n.tool for n in self.nodes if n.tool}))

        return self


def validate_loop_data(raw_data: Union[dict, str, Path]) -> tuple[bool, Optional[CHIALoop], List[str]]:
    """
    Validates raw dictionary, JSON string, or file path against the CHIALoop Pydantic schema.
    Returns: (is_valid: bool, loop_instance: Optional[CHIALoop], errors: List[str])
    """
    errors: List[str] = []
    
    if isinstance(raw_data, (str, Path)):
        # Check if it is a file path
        path = Path(raw_data)
        if path.is_file():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                return False, None, [f"Error reading JSON file '{path}': {e}"]
        else:
            try:
                data = json.loads(str(raw_data))
            except Exception as e:
                return False, None, [f"Invalid JSON string: {e}"]
    elif isinstance(raw_data, dict):
        data = raw_data
    else:
        return False, None, [f"Unsupported input type: {type(raw_data)}"]

    try:
        validated_loop = CHIALoop.model_validate(data)
        return True, validated_loop, []
    except ValidationError as e:
        for err in e.errors():
            loc = " -> ".join(str(l) for l in err["loc"])
            msg = err["msg"]
            errors.append(f"[{loc}] {msg}")
        return False, None, errors
    except Exception as e:
        return False, None, [str(e)]


def main():
    parser = argparse.ArgumentParser(description="Strict Pydantic type-checker for CHIA loops.")
    parser.add_argument("input", nargs="?", help="Path to JSON file or raw JSON string. If omitted, reads from stdin.")
    parser.add_argument("--quiet", "-q", action="store_true", help="Only output exit code (0 for valid, 1 for invalid).")
    args = parser.parse_args()

    if args.input:
        input_data = args.input
    else:
        if sys.stdin.isatty():
            print("Error: No input provided via argument or stdin.", file=sys.stderr)
            sys.exit(1)
        input_data = sys.stdin.read()

    is_valid, validated_loop, errors = validate_loop_data(input_data)

    if not args.quiet:
        if is_valid and validated_loop:
            print(json.dumps({
                "status": "valid",
                "message": "CHIA loop successfully validated against Pydantic schema.",
                "loop_name": validated_loop.name,
                "node_count": len(validated_loop.nodes),
                "edge_count": len(validated_loop.edges),
                "edge_types": {e.source + "->" + e.target: e.edge_type.value for e in validated_loop.edges},
                "node_functions": {n.id: n.function for n in validated_loop.nodes}
            }, indent=2))
        else:
            print(json.dumps({
                "status": "invalid",
                "message": "CHIA loop schema validation failed.",
                "errors": errors
            }, indent=2), file=sys.stderr)

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
