import pytest
from src.validation.schema_check import (
    CHIALoop,
    CHIANode,
    CHIAEdge,
    EdgeType,
    validate_loop_data,
)


def test_schema_check_valid_loop():
    valid_loop_data = {
        "name": "Branch Predictor Tuning Loop",
        "description": "Explores branch predictor tables and history lengths.",
        "nodes": [
            {
                "id": "fetch_trace",
                "type": "input",
                "function": "load_benchmark_trace",
                "description": "Loads the Champsim trace file"
            },
            {
                "id": "generate_bp_config",
                "type": "agent",
                "function": "propose_branch_predictor_parameters",
                "description": "Generates new branch predictor configuration"
            },
            {
                "id": "simulate_bp",
                "type": "tool_executor",
                "tool": "champsim_runner",
                "function": "run_champsim_simulation",
                "description": "Executes ChampSim with the given branch predictor configuration"
            },
            {
                "id": "evaluate_accuracy",
                "type": "evaluator",
                "function": "evaluate_branch_prediction_accuracy",
                "description": "Extracts and evaluates branch accuracy percentage"
            }
        ],
        "edges": [
            {
                "source": "fetch_trace",
                "target": "generate_bp_config",
                "edge_type": "programmatic"
            },
            {
                "source": "generate_bp_config",
                "target": "simulate_bp",
                "edge_type": "programmatic"
            },
            {
                "source": "simulate_bp",
                "target": "evaluate_accuracy",
                "edge_type": "programmatic"
            },
            {
                "source": "evaluate_accuracy",
                "target": "generate_bp_config",
                "edge_type": "agentic",
                "condition": "accuracy < 0.95"
            }
        ]
    }

    is_valid, loop_obj, errors = validate_loop_data(valid_loop_data)
    assert is_valid is True
    assert len(errors) == 0
    assert loop_obj is not None
    assert len(loop_obj.nodes) == 4
    assert len(loop_obj.edges) == 4
    assert loop_obj.edges[3].edge_type == EdgeType.AGENTIC
    assert loop_obj.nodes[2].function == "run_champsim_simulation"


def test_schema_check_invalid_node_id_reference():
    invalid_data = {
        "name": "Invalid Edge Reference Loop",
        "nodes": [
            {"id": "step1", "type": "agent"}
        ],
        "edges": [
            {"source": "step1", "target": "missing_node", "edge_type": "programmatic"}
        ]
    }

    is_valid, loop_obj, errors = validate_loop_data(invalid_data)
    assert is_valid is False
    assert loop_obj is None
    assert any("missing_node" in err for err in errors)


def test_schema_check_empty_nodes():
    invalid_data = {
        "name": "Empty Nodes Loop",
        "nodes": [],
        "edges": []
    }

    is_valid, loop_obj, errors = validate_loop_data(invalid_data)
    assert is_valid is False
    assert any("nodes" in err for err in errors)
