import json
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from src.api.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "CHIA Loop Builder API"
    assert "POST /generate-loop" in data["endpoints"]


def test_validate_loop_valid():
    valid_loop = {
        "name": "L1/L2 Cache Prefetch Optimization Loop",
        "description": "Explores prefetcher aggressiveness and cache size trade-offs.",
        "node_types": ["agent", "tool_executor", "evaluator"],
        "tools_used": ["champsim_runner", "trace_analyzer"],
        "nodes": [
            {"id": "init_state", "type": "input", "description": "Loads initial config"},
            {"id": "agent_propose", "type": "agent", "description": "Proposes new prefetcher setting"},
            {"id": "simulate", "type": "tool_executor", "tool": "champsim_runner", "description": "Runs ChampSim"},
            {"id": "evaluate", "type": "evaluator", "description": "Evaluates IPC and miss rate"}
        ],
        "edges": [
            {"source": "init_state", "target": "agent_propose"},
            {"source": "agent_propose", "target": "simulate"},
            {"source": "simulate", "target": "evaluate"},
            {"source": "evaluate", "target": "agent_propose", "condition": "metrics.ipc < target_ipc"}
        ]
    }

    response = client.post("/validate-loop", json={"loop": valid_loop})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert len(data["errors"]) == 0
    assert data["details"]["node_count"] == 4
    assert data["details"]["edge_count"] == 4


def test_validate_loop_invalid():
    invalid_loop = {
        "name": "Broken Loop",
        "nodes": [
            {"id": "node1", "type": "agent"},
        ],
        "edges": [
            {"source": "node1", "target": "non_existent_node"}
        ]
    }

    response = client.post("/validate-loop", json={"loop": invalid_loop})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert any("non_existent_node" in err for err in data["errors"])


def test_run_simulation_missing_binary():
    loop_config = {
        "name": "Simulation Loop",
        "nodes": [
            {"id": "n1", "type": "simulator"}
        ],
        "edges": []
    }

    response = client.post(
        "/run-simulation",
        json={
            "loop_config": loop_config,
            "binary_path": "./non_existent_champsim_bin",
            "warmup_instructions": 1000,
            "simulation_instructions": 5000,
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "binary_not_found"
    assert "champsim" in data["stderr"].lower()


@patch("src.api.main.subprocess.run")
def test_run_simulation_success_mocked(mock_subproc):
    mock_subproc.return_value = MagicMock(
        returncode=0,
        stdout="ChampSim simulation completed.\nCumulative IPC: 1.845\ninstructions: 10000000\ncycles: 5420054\nBRANCH PREDICTOR ACCURACY: 98.4 %",
        stderr=""
    )

    loop_config = {
        "name": "Simulation Loop",
        "nodes": [
            {"id": "n1", "type": "simulator"}
        ],
        "edges": []
    }

    with patch("pathlib.Path.exists", return_value=True):
        response = client.post(
            "/run-simulation",
            json={
                "loop_config": loop_config,
                "binary_path": "./bin/champsim",
                "warmup_instructions": 1000,
                "simulation_instructions": 5000,
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["exit_code"] == 0
    assert data["metrics"]["cumulative_ipc"] == 1.845
    assert data["metrics"]["branch_accuracy_percent"] == 98.4


@patch("src.api.main.ChatGroq")
def test_generate_loop_mocked(mock_chatgroq):
    mock_loop_json = {
        "name": "Cache Hierarchy Optimization Loop",
        "description": "Optimizes L1/L2 cache sizing and replacement policy.",
        "node_types": ["agent", "tool_executor", "evaluator"],
        "tools_used": ["champsim_runner"],
        "state_schema": {"ipc": 0.0, "best_ipc": 0.0},
        "nodes": [
            {"id": "proposer", "type": "agent", "description": "Proposes cache parameters"},
            {"id": "runner", "type": "tool_executor", "tool": "champsim_runner"},
            {"id": "evaluator", "type": "evaluator", "description": "Compares IPC"}
        ],
        "edges": [
            {"source": "proposer", "target": "runner"},
            {"source": "runner", "target": "evaluator"}
        ]
    }

    mock_llm_instance = MagicMock()
    mock_llm_instance.ainvoke = AsyncMock(return_value=AIMessage(content=json.dumps(mock_loop_json)))
    mock_chatgroq.return_value = mock_llm_instance

    response = client.post(
        "/generate-loop",
        json={
            "query": "Optimize cache hierarchy",
            "api_key": "mock_groq_key"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "Optimize cache hierarchy"
    assert data["generated_loop"]["name"] == "Cache Hierarchy Optimization Loop"
    assert data["validation"]["valid"] is True
