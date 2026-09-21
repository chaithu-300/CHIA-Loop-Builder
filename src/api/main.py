import os
from dotenv import load_dotenv

# Load environment variables from the .env file (if present)
load_dotenv()

# The rest of your FastAPI setup goes here...
import json
import re
import time
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic import SecretStr

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

from src.rag.ingest import retrieve_context, get_vector_store
from src.validation.validator import validate_chia_loop

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("chia_api")

app = FastAPI(
    title="CHIA Loop Builder API",
    description="API for generating, validating, and simulating CHIA agentic loops using RAG and ChampSim.",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic Request/Response Models
# ---------------------------------------------------------------------------

class GenerateLoopRequest(BaseModel):
    query: str = Field(..., description="Plain English description of the desired CHIA loop (e.g., 'Optimize cache hierarchy').")
    model_name: Optional[str] = Field(default="llama-3.3-70b-versatile", description="Groq model name.")
    temperature: Optional[float] = Field(default=0.1, ge=0.0, le=1.0, description="Sampling temperature.")
    api_key: Optional[SecretStr] = Field(default=None, description="Optional Groq API key override.")


class GenerateLoopResponse(BaseModel):
    query: str
    generated_loop: Dict[str, Any]
    validation: Dict[str, Any]
    retrieved_context: Dict[str, Any]


class ValidateLoopRequest(BaseModel):
    loop: Dict[str, Any] = Field(..., description="JSON configuration of the CHIA loop.")


class ValidateLoopResponse(BaseModel):
    valid: bool
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]


class RunSimulationRequest(BaseModel):
    loop_config: Dict[str, Any] = Field(..., description="CHIA loop configuration to simulate.")
    binary_path: Optional[str] = Field(default=None, description="Path to ChampSim binary executable. Defaults to CHAMPSIM_BIN env var or ./bin/champsim.")
    trace_path: Optional[str] = Field(default=None, description="Path to benchmark/trace file (e.g., .champsimtrace.xz).")
    warmup_instructions: Optional[int] = Field(default=1000000, description="Warmup instruction count.")
    simulation_instructions: Optional[int] = Field(default=10000000, description="Simulation instruction count.")
    extra_args: Optional[List[str]] = Field(default=None, description="Additional command-line arguments for ChampSim.")
    timeout_seconds: Optional[int] = Field(default=60, description="Execution timeout in seconds.")


class RunSimulationResponse(BaseModel):
    status: str
    command: List[str]
    exit_code: Optional[int]
    stdout: str
    stderr: str
    execution_time_seconds: float
    message: str
    metrics: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def _clean_json_response(raw_text: str) -> Dict[str, Any]:
    """Cleans markdown formatting and parses JSON object from LLM response."""
    cleaned = raw_text.strip()
    
    # Strip markdown code blocks if wrapped in ```json ... ```
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned)
    
    # Locate first { and last }
    start_idx = cleaned.find("{")
    end_idx = cleaned.rfind("}")
    if start_idx != -1 and end_idx != -1:
        cleaned = cleaned[start_idx:end_idx + 1]

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as err:
        raise ValueError(f"Failed to parse model output as JSON: {err}\nRaw output:\n{raw_text}")


def _build_system_prompt() -> str:
    return """You are the expert CHIA Loop Architect (Compiler, Hardware, and Instruction Architecture agentic workflow designer).
Your task is to generate a comprehensive, syntactically valid CHIA loop definition strictly as a JSON object.

A valid CHIA loop adheres to the following specification:
1. Top-Level Keys:
   - "name": String descriptive title of the loop.
   - "description": String detailed summary of what the loop accomplishes and its optimization goal.
   - "node_types": List of strings representing all unique node types used in this loop.
   - "tools_used": List of strings representing all external tools/scripts used (e.g. "champsim_runner", "cache_config_writer", "trace_analyzer", "perf_evaluator").
   - "state_schema": Object defining the loop state fields (e.g., current_config, iteration, best_ipc, metrics, history).
   - "nodes": Array of node objects, each containing:
       - "id": Unique string identifier (e.g. "init_config", "simulate", "evaluate", "optimize_step").
       - "type": Valid CHIA node type (e.g. "agent", "tool_executor", "evaluator", "router", "optimizer", "simulator", "condition", "state_updater", "input", "output").
       - "description": Brief purpose of this node.
       - "tool": Optional string name of tool invoked by this node.
       - "config": Object with node-specific settings/hyperparameters.
   - "edges": Array of directed edge objects connecting nodes, each containing:
       - "source": ID of the source node.
       - "target": ID of the target node.
       - "condition": Optional string condition or routing rule (e.g. "metrics.ipc > threshold", "iteration < max_iterations", "default").

STRICT OUTPUT RULES:
- Output ONLY valid, parsable JSON.
- Do NOT output explanations, introductory text, or markdown prose outside the JSON object.
"""


def _parse_champsim_metrics(stdout: str) -> Dict[str, Any]:
    """Extracts common ChampSim statistics (IPC, Branch accuracy, Cache Miss Rate) if present in output."""
    metrics: Dict[str, Any] = {}
    
    # Extract cumulative IPC
    ipc_match = re.search(r"(?:cumulative\s+)?IPC:\s*([\d\.]+)", stdout, re.IGNORECASE)
    if ipc_match:
        try:
            metrics["cumulative_ipc"] = float(ipc_match.group(1))
        except ValueError:
            pass

    # Extract instructions and cycles
    instr_match = re.search(r"instructions:\s*(\d+)", stdout, re.IGNORECASE)
    if instr_match:
        metrics["instructions"] = int(instr_match.group(1))

    cycles_match = re.search(r"cycles:\s*(\d+)", stdout, re.IGNORECASE)
    if cycles_match:
        metrics["cycles"] = int(cycles_match.group(1))

    # Extract branch prediction accuracy
    branch_match = re.search(r"BRANCH PREDICTOR ACCURACY:\s*([\d\.]+)\s*%", stdout, re.IGNORECASE)
    if branch_match:
        metrics["branch_accuracy_percent"] = float(branch_match.group(1))

    # Extract LLC miss rate / hit rate if present
    llc_miss_match = re.search(r"LLC\s+TOTAL\s+ACCESS:\s*\d+\s+HIT:\s*\d+\s+MISS:\s*(\d+)", stdout, re.IGNORECASE)
    if llc_miss_match:
        metrics["llc_misses"] = int(llc_miss_match.group(1))

    return metrics


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "service": "CHIA Loop Builder API",
        "status": "online",
        "endpoints": [
            "POST /generate-loop",
            "POST /validate-loop",
            "POST /run-simulation"
        ]
    }


@app.post("/generate-loop", response_model=GenerateLoopResponse)
async def generate_loop(request: GenerateLoopRequest):
    """
    Accepts a plain English query, queries the local ChromaDB vector store
    for relevant CHIA documentation and loop examples, constructs a strict prompt,
    and returns a newly generated CHIA loop using ChatGroq.
    """
    logger.info(f"Received loop generation request for query: '{request.query}'")

    # 1. Retrieve relevant context from ChromaDB
    retrieved_data = retrieve_context(query=request.query, k_docs=3, k_loops=2)

    docs_context_str = "\n\n".join([
        f"[Documentation Snippet from {d.get('metadata', {}).get('file_name', 'Doc')}]:\n{d.get('content', '')}"
        for d in retrieved_data.get("docs", [])
    ]) or "No direct documentation matches found."

    loops_context_str = "\n\n".join([
        f"[Similar Loop Reference '{l.get('metadata', {}).get('name', 'Loop')}']:\n{l.get('content', '')}"
        for l in retrieved_data.get("loops", [])
    ]) or "No similar loop examples found."

    # 2. Check for Groq API key
    groq_api_key = request.api_key.get_secret_value() if request.api_key else os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GROQ_API_KEY is not set. Please set the GROQ_API_KEY environment variable or pass 'api_key' in the request."
        )

# 3. Construct LangChain ChatGroq LLM and Prompt
    try:
        llm = ChatGroq(
            api_key=SecretStr(groq_api_key),
            model=request.model_name or "llama-3.3-70b-versatile",
            temperature=request.temperature if request.temperature is not None else 0.2,
            model_kwargs={"response_format": {"type": "json_object"}},
        )

        system_prompt = _build_system_prompt()

        user_message_content = f"""Please generate a complete CHIA Loop configuration based on the user's objective.

User Objective:
"{request.query}"

Relevant CHIA Architectural Documentation:
{docs_context_str}

Reference CHIA Loop Examples:
{loops_context_str}

Generate the JSON object for this loop now:"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message_content)
        ]

        logger.info(f"Invoking ChatGroq with model '{request.model_name}'...")
        response = await llm.ainvoke(messages)
        generated_json = _clean_json_response(str(response.content))

    except Exception as e:
        logger.error(f"Error during loop generation with ChatGroq: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating loop with ChatGroq: {str(e)}"
        )

    # 4. Validate the generated loop
    validation_result = validate_chia_loop(generated_json)

    return GenerateLoopResponse(
        query=request.query,
        generated_loop=generated_json,
        validation=validation_result,
        retrieved_context={
            "docs_count": len(retrieved_data.get("docs", [])),
            "loops_count": len(retrieved_data.get("loops", [])),
            "retrieved_docs": retrieved_data.get("docs", []),
            "retrieved_loops": retrieved_data.get("loops", []),
        }
    )


@app.post("/validate-loop", response_model=ValidateLoopResponse)
def validate_loop(request: ValidateLoopRequest):
    """
    Accepts a JSON loop definition and verifies that it contains valid CHIA node types
    and proper edge formatting.
    """
    logger.info(f"Validating loop configuration: {request.loop.get('name', 'Unnamed Loop')}")
    result = validate_chia_loop(request.loop)
    return ValidateLoopResponse(
        valid=result["valid"],
        errors=result["errors"],
        warnings=result["warnings"],
        details=result["details"],
    )


@app.post("/run-simulation", response_model=RunSimulationResponse)
def run_simulation(request: RunSimulationRequest):
    """
    Accepts a valid loop config and executes a local shell command to run it via the ChampSim binary.
    """
    logger.info(f"Received simulation request for loop: {request.loop_config.get('name', 'Unnamed')}")

    # 1. Validate loop config first
    validation = validate_chia_loop(request.loop_config)
    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Invalid loop configuration provided.",
                "errors": validation["errors"]
            }
        )

    # 2. Determine ChampSim binary location
    binary_path = (
        request.binary_path
        or os.environ.get("CHAMPSIM_BIN")
        or shutil.which("champsim")
        or str(Path(__file__).resolve().parent.parent.parent / "bin" / "champsim")
        or str(Path(__file__).resolve().parent.parent.parent / "bin" / "champsim.exe")
    )

    # 3. Construct ChampSim CLI command
    cmd: List[str] = [str(binary_path)]

    if request.warmup_instructions is not None:
        cmd.extend(["--warmup-instructions", str(request.warmup_instructions)])

    if request.simulation_instructions is not None:
        cmd.extend(["--simulation-instructions", str(request.simulation_instructions)])

    if request.trace_path:
        cmd.extend(["--traces", str(request.trace_path)])

    if request.extra_args:
        cmd.extend(request.extra_args)

    # 4. Check if binary executable exists
    bin_file = Path(binary_path)
    if not bin_file.exists() and not shutil.which(binary_path):
        logger.warning(f"ChampSim binary not found at '{binary_path}'")
        return RunSimulationResponse(
            status="binary_not_found",
            command=cmd,
            exit_code=None,
            stdout="",
            stderr=f"ChampSim binary was not found at '{binary_path}'. Please provide a valid path via 'binary_path' or the CHAMPSIM_BIN environment variable.",
            execution_time_seconds=0.0,
            message="ChampSim binary not located on host system.",
            metrics=None
        )

    # 5. Execute binary subprocess
    start_time = time.time()
    try:
        logger.info(f"Executing ChampSim command: {' '.join(cmd)}")
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=request.timeout_seconds,
            check=False,
        )
        elapsed_time = round(time.time() - start_time, 4)
        stdout = process.stdout
        stderr = process.stderr
        exit_code = process.returncode

        metrics = _parse_champsim_metrics(stdout)

        return RunSimulationResponse(
            status="success" if exit_code == 0 else "failed",
            command=cmd,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            execution_time_seconds=elapsed_time,
            message="ChampSim simulation completed." if exit_code == 0 else f"ChampSim exited with non-zero code {exit_code}.",
            metrics=metrics if metrics else None
        )

    except subprocess.TimeoutExpired:
        elapsed_time = round(time.time() - start_time, 4)
        logger.error(f"ChampSim simulation timed out after {request.timeout_seconds}s.")
        return RunSimulationResponse(
            status="timeout",
            command=cmd,
            exit_code=None,
            stdout="",
            stderr=f"Simulation timed out after {request.timeout_seconds} seconds.",
            execution_time_seconds=elapsed_time,
            message=f"Simulation process timed out after {request.timeout_seconds} seconds.",
            metrics=None
        )
    except Exception as e:
        elapsed_time = round(time.time() - start_time, 4)
        logger.error(f"Error running ChampSim simulation: {e}")
        return RunSimulationResponse(
            status="error",
            command=cmd,
            exit_code=-1,
            stdout="",
            stderr=str(e),
            execution_time_seconds=elapsed_time,
            message=f"Execution error: {str(e)}",
            metrics=None
        )
