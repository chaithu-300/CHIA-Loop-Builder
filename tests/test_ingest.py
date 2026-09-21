import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from src.rag.ingest import (
    load_and_chunk_markdown_docs,
    load_loop_documents,
    build_vector_store,
    get_embedding_function,
    get_vector_store,
    process_single_file,
    extract_text_from_html,
    extract_text_from_txt,
    extract_text_from_markdown,
    extract_metadata_and_summary_from_json,
    IngestionEventHandler,
    ALL_SUPPORTED_EXTENSIONS,
    run_initial_scan,
)
from watchdog.events import FileCreatedEvent, FileModifiedEvent


def test_markdown_chunking(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    sample_md = docs_dir / "sample.md"
    sample_md.write_text(
        "# CHIA Architecture\n\n"
        "CHIA is a system for building agentic loops.\n\n"
        "## Components\n\n"
        "Nodes, Edges, State, and Tools are the primary components of any CHIA loop.\n",
        encoding="utf-8"
    )

    chunks = load_and_chunk_markdown_docs(docs_dir=docs_dir, chunk_size=50, chunk_overlap=10)
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.metadata["doc_type"] == "documentation"
        assert chunk.metadata["file_name"] == "sample.md"
        assert "chunk_index" in chunk.metadata


def test_loop_json_atomic_loading(tmp_path):
    loops_dir = tmp_path / "loops"
    loops_dir.mkdir()

    sample_loop = {
        "name": "Market Analysis Loop",
        "description": "Performs web search and synthesizes financial sentiment.",
        "tools_used": ["web_search", "sentiment_analyzer"],
        "node_types": ["agent", "tool_executor", "aggregator"],
        "nodes": [
            {"id": "search_node", "type": "tool_executor", "tool": "web_search"},
            {"id": "sentiment_node", "type": "agent", "tool": "sentiment_analyzer"}
        ]
    }

    sample_json = loops_dir / "market_analysis.json"
    sample_json.write_text(json.dumps(sample_loop), encoding="utf-8")

    loop_docs = load_loop_documents(loops_dir=loops_dir)
    assert len(loop_docs) == 1
    doc = loop_docs[0]

    # Assert atomic loading (single document)
    assert doc.metadata["doc_type"] == "loop"
    assert doc.metadata["name"] == "Market Analysis Loop"
    assert "web_search" in doc.metadata["tools_used"]
    assert "agent" in doc.metadata["node_types"]

    # Assert natural language summary prefix
    assert "### Natural Language Summary" in doc.page_content
    assert "Loop Name: Market Analysis Loop" in doc.page_content
    assert "### Raw Loop JSON" in doc.page_content
    assert '"name": "Market Analysis Loop"' in doc.page_content


def test_vector_store_build_and_query(tmp_path):
    docs_dir = tmp_path / "docs"
    loops_dir = tmp_path / "loops"
    chroma_dir = tmp_path / "chroma_db"
    docs_dir.mkdir()
    loops_dir.mkdir()

    # Markdown doc
    (docs_dir / "guide.md").write_text("# Tool Execution Guide\n\nExplains how tools execute within loops.", encoding="utf-8")

    # Loop doc
    sample_loop = {
        "name": "SQL Query Loop",
        "description": "Executes SQL queries against Postgres DB",
        "tools_used": ["sql_runner"],
        "node_types": ["database_node"]
    }
    (loops_dir / "sql_loop.json").write_text(json.dumps(sample_loop), encoding="utf-8")

    # Build store
    store = build_vector_store(
        docs_dir=docs_dir,
        loops_dir=loops_dir,
        chroma_dir=chroma_dir,
        collection_name="test_chia_rag"
    )
    assert store is not None

    # Query the store
    results = store.similarity_search("Postgres database queries", k=1)
    assert len(results) == 1
    assert "SQL Query Loop" in results[0].page_content
    assert results[0].metadata["doc_type"] == "loop"


def test_dynamic_routing_extractors(tmp_path):
    # Test HTML extractor
    html_file = tmp_path / "test.html"
    html_file.write_text("<html><head><title>Test</title></head><body><h1>ChampSim Manual</h1><p>Cache replacement policies.</p></body></html>", encoding="utf-8")
    html_text = extract_text_from_html(html_file)
    assert "ChampSim Manual" in html_text
    assert "Cache replacement policies." in html_text
    assert "<html>" not in html_text

    # Test TXT extractor
    txt_file = tmp_path / "notes.txt"
    txt_file.write_text("Plain text documentation notes.", encoding="utf-8")
    txt_text = extract_text_from_txt(txt_file)
    assert "Plain text documentation notes." in txt_text

    # Test JSON extractor
    json_file = tmp_path / "loop.json"
    json_file.write_text(json.dumps({
        "name": "Branch Predictor Loop",
        "description": "Tunes branch accuracy",
        "tools_used": ["branch_eval"],
        "node_types": ["agent", "evaluator"]
    }), encoding="utf-8")
    meta, summary, raw = extract_metadata_and_summary_from_json(json_file)
    assert meta["name"] == "Branch Predictor Loop"
    assert "branch_eval" in meta["tools_used"]
    assert "Branch Predictor Loop" in summary


def test_incremental_single_file_processing(tmp_path):
    chroma_dir = tmp_path / "chroma_db"
    
    # 1. Ingest markdown doc
    md_file = tmp_path / "spec.md"
    md_file.write_text("# Hardware Pipeline Spec\n\nDefines stages: Fetch, Decode, Execute, Writeback.", encoding="utf-8")

    success_md = process_single_file(
        file_path=md_file,
        chroma_dir=chroma_dir,
        collection_name="test_incremental"
    )
    assert success_md is True

    # 2. Ingest JSON loop
    json_file = tmp_path / "pipeline_loop.json"
    json_file.write_text(json.dumps({
        "name": "Pipeline Stage Optimizer",
        "description": "Optimizes execution latency",
        "tools_used": ["pipeline_sim"],
        "node_types": ["optimizer"]
    }), encoding="utf-8")

    success_json = process_single_file(
        file_path=json_file,
        chroma_dir=chroma_dir,
        collection_name="test_incremental"
    )
    assert success_json is True

    # 3. Ingest unsupported file
    img_file = tmp_path / "diagram.png"
    img_file.write_bytes(b"\x89PNG\r\n\x1a\n")
    success_img = process_single_file(
        file_path=img_file,
        chroma_dir=chroma_dir,
        collection_name="test_incremental"
    )
    assert success_img is False

    # Verify querying incremental store
    store = get_vector_store(chroma_dir=chroma_dir, collection_name="test_incremental")
    res = store.similarity_search("Pipeline Stage Optimizer", k=2)
    assert len(res) >= 2
    loop_results = [r for r in res if r.metadata.get("doc_type") == "loop"]
    assert len(loop_results) == 1
    assert "Pipeline Stage Optimizer" in loop_results[0].page_content
    assert loop_results[0].metadata["name"] == "Pipeline Stage Optimizer"


def test_strict_error_handling_corrupt_files(tmp_path):
    chroma_dir = tmp_path / "chroma_db"

    # Corrupt JSON file
    corrupt_json = tmp_path / "corrupt.json"
    corrupt_json.write_text("{ broken_json: [", encoding="utf-8")

    # Should log warning and return False without raising an exception or crashing
    result = process_single_file(
        file_path=corrupt_json,
        chroma_dir=chroma_dir,
        collection_name="test_error_handling"
    )
    assert result is False

    # Empty text file
    empty_txt = tmp_path / "empty.txt"
    empty_txt.write_text("", encoding="utf-8")
    result_empty = process_single_file(
        file_path=empty_txt,
        chroma_dir=chroma_dir,
        collection_name="test_error_handling"
    )
    assert result_empty is False


def test_watchdog_event_handler(tmp_path):
    chroma_dir = tmp_path / "chroma_db"
    handler = IngestionEventHandler(
        chroma_dir=chroma_dir,
        collection_name="test_watchdog"
    )

    doc_file = tmp_path / "watched_doc.md"
    doc_file.write_text("# Monitored Doc\nReal-time ingestion test.", encoding="utf-8")

    # Trigger on_created event
    created_event = FileCreatedEvent(src_path=str(doc_file))
    handler.on_created(created_event)

    # Trigger on_modified event
    doc_file.write_text("# Monitored Doc\nUpdated real-time ingestion content.", encoding="utf-8")
    # Reset debounce map for testing
    handler._last_processed.clear()
    modified_event = FileModifiedEvent(src_path=str(doc_file))
    handler.on_modified(modified_event)

    # Query Chroma
    store = get_vector_store(chroma_dir=chroma_dir, collection_name="test_watchdog")
    results = store.similarity_search("Monitored Doc", k=1)
    assert len(results) >= 1


def test_full_initial_scan(tmp_path):
    docs_dir = tmp_path / "docs"
    loops_dir = tmp_path / "loops"
    chroma_dir = tmp_path / "chroma_db"
    docs_dir.mkdir()
    loops_dir.mkdir()

    # Add 2 doc files
    (docs_dir / "guide1.md").write_text("# Guide 1\nOverview of hardware simulation.", encoding="utf-8")
    (docs_dir / "guide2.txt").write_text("Guide 2: Trace file details and format.", encoding="utf-8")

    # Add 1 loop JSON
    (loops_dir / "loop1.json").write_text(json.dumps({
        "name": "Initial Scan Loop",
        "description": "Scanned during startup",
        "tools_used": ["sim_tool"],
        "node_types": ["evaluator"]
    }), encoding="utf-8")

    total_indexed = run_initial_scan(
        docs_dir=docs_dir,
        loops_dir=loops_dir,
        chroma_dir=chroma_dir,
        collection_name="test_initial_scan"
    )

    assert total_indexed >= 3

    # Verify queryability
    store = get_vector_store(chroma_dir=chroma_dir, collection_name="test_initial_scan")
    res = store.similarity_search("Initial Scan Loop", k=1)
    assert len(res) == 1
    assert "Initial Scan Loop" in res[0].page_content

