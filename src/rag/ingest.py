import os
import json
import time
import logging
from html.parser import HTMLParser
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("chia_ingestion")

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DOCS_DIR = PROJECT_ROOT / "data" / "docs"
DEFAULT_LOOPS_DIR = PROJECT_ROOT / "data" / "loops"
DEFAULT_CHROMA_DIR = PROJECT_ROOT / "chroma_db"
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_COLLECTION_NAME = "chia_rag"

# Supported file extensions
SUPPORTED_DOC_EXTENSIONS = {".pdf", ".html", ".htm", ".md", ".markdown", ".txt"}
SUPPORTED_LOOP_EXTENSIONS = {".json"}
ALL_SUPPORTED_EXTENSIONS = SUPPORTED_DOC_EXTENSIONS | SUPPORTED_LOOP_EXTENSIONS


# ---------------------------------------------------------------------------
# HTML Parsing Utility
# ---------------------------------------------------------------------------

class HTMLTextExtractor(HTMLParser):
    """Simple HTML parser to strip markup, styles, and scripts."""
    def __init__(self):
        super().__init__()
        self.fed: List[str] = []
        self.ignore_tags = {"script", "style", "head", "title", "meta", "noscript"}
        self.in_ignore = False

    def handle_starttag(self, tag: str, attrs: list):
        if tag.lower() in self.ignore_tags:
            self.in_ignore = True

    def handle_endtag(self, tag: str):
        if tag.lower() in self.ignore_tags:
            self.in_ignore = False

    def handle_data(self, data: str):
        if not self.in_ignore:
            text = data.strip()
            if text:
                self.fed.append(text)

    def get_text(self) -> str:
        return "\n".join(self.fed)


# ---------------------------------------------------------------------------
# Text Extractors for Dynamic Routing
# ---------------------------------------------------------------------------

def extract_text_from_pdf(file_path: Path) -> str:
    """Extracts raw text from a PDF file using pypdf."""
    try:
        import pypdf
        reader = pypdf.PdfReader(str(file_path))
        pages_text = []
        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages_text.append(f"--- Page {idx + 1} ---\n{page_text}")
        return "\n\n".join(pages_text)
    except Exception as e:
        raise RuntimeError(f"PDF extraction failed for '{file_path}': {e}") from e


def extract_text_from_html(file_path: Path) -> str:
    """Extracts clean text from an HTML document."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            html_content = f.read()
        parser = HTMLTextExtractor()
        parser.feed(html_content)
        return parser.get_text()
    except Exception as e:
        raise RuntimeError(f"HTML extraction failed for '{file_path}': {e}") from e


def extract_text_from_markdown(file_path: Path) -> str:
    """Extracts raw text from a Markdown file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        raise RuntimeError(f"Markdown extraction failed for '{file_path}': {e}") from e


def extract_text_from_txt(file_path: Path) -> str:
    """Extracts raw text from a plain text file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        raise RuntimeError(f"Text file extraction failed for '{file_path}': {e}") from e


def extract_metadata_and_summary_from_json(file_path: Path) -> Tuple[Dict[str, Any], str, Dict[str, Any]]:
    """
    Parses a loop JSON file, extracts tools_used, node_types, and metadata,
    and returns (metadata, natural_language_summary, raw_dict).
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_json_str = f.read()

    if not raw_json_str.strip():
        raise ValueError("JSON file is empty.")

    try:
        data = json.loads(raw_json_str)
    except json.JSONDecodeError as err:
        raise ValueError(f"Invalid JSON syntax in '{file_path}': {err}") from err

    if not isinstance(data, dict):
        data = {"raw_content": data}

    name = data.get("name") or data.get("title") or file_path.stem
    description = data.get("description") or data.get("summary") or "No description provided."

    # Extract tools_used
    tools_used = data.get("tools_used") or data.get("tools") or []
    if not tools_used and "nodes" in data and isinstance(data["nodes"], (list, dict)):
        nodes = data["nodes"] if isinstance(data["nodes"], list) else data["nodes"].values()
        extracted_tools = set()
        for node in nodes:
            if isinstance(node, dict):
                if "tool" in node and node["tool"]:
                    extracted_tools.add(str(node["tool"]))
                if "tools" in node and isinstance(node["tools"], list):
                    for t in node["tools"]:
                        extracted_tools.add(str(t))
        tools_used = list(extracted_tools)

    if isinstance(tools_used, list):
        tools_used_str = ", ".join(str(t) for t in tools_used) if tools_used else "None"
    else:
        tools_used_str = str(tools_used)

    # Extract node_types
    node_types = data.get("node_types") or []
    if not node_types and "nodes" in data and isinstance(data["nodes"], (list, dict)):
        nodes = data["nodes"] if isinstance(data["nodes"], list) else data["nodes"].values()
        extracted_types = set()
        for node in nodes:
            if isinstance(node, dict):
                n_type = node.get("type") or node.get("node_type") or node.get("kind")
                if n_type:
                    extracted_types.add(str(n_type))
        node_types = list(extracted_types)

    if isinstance(node_types, list):
        node_types_str = ", ".join(str(nt) for nt in node_types) if node_types else "None"
    else:
        node_types_str = str(node_types)

    summary_parts = [
        f"Loop Name: {name}",
        f"Description: {description}",
        f"Tools Used: {tools_used_str}",
        f"Node Types: {node_types_str}",
    ]
    if "category" in data:
        summary_parts.append(f"Category: {data['category']}")
    if "tags" in data and isinstance(data["tags"], list):
        summary_parts.append(f"Tags: {', '.join(str(tag) for tag in data['tags'])}")

    nl_summary = "\n".join(summary_parts)

    metadata = {
        "source": str(file_path),
        "file_name": file_path.name,
        "doc_type": "loop",
        "name": str(name),
        "tools_used": tools_used_str,
        "node_types": node_types_str,
    }

    return metadata, nl_summary, data


# ---------------------------------------------------------------------------
# Vector Store & Embeddings Initialization
# ---------------------------------------------------------------------------

def get_embedding_function(model_name: str = DEFAULT_EMBEDDING_MODEL) -> HuggingFaceEmbeddings:
    """Initializes and returns the HuggingFace embedding function."""
    return HuggingFaceEmbeddings(model_name=model_name)


def get_vector_store(
    chroma_dir: Union[Path, str] = DEFAULT_CHROMA_DIR,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
) -> Chroma:
    """Returns an existing Chroma vector store instance or initializes a new one."""
    chroma_path = Path(chroma_dir)
    chroma_path.mkdir(parents=True, exist_ok=True)
    embeddings = get_embedding_function(model_name=embedding_model)
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(chroma_path),
    )


# ---------------------------------------------------------------------------
# Single File Processing & Incremental Insertion
# ---------------------------------------------------------------------------

def process_single_file(
    file_path: Union[Path, str],
    chroma_dir: Union[Path, str] = DEFAULT_CHROMA_DIR,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    vector_store: Optional[Chroma] = None,
) -> bool:
    """
    Processes a single file according to Dynamic Routing rules and appends it
    incrementally to the ChromaDB collection.

    Enforces Strict Error Handling:
    Catches errors for corrupt/unparseable files and logs warnings without crashing.
    """
    path = Path(file_path)
    if not path.is_file():
        return False

    ext = path.suffix.lower()

    # Rule 1: Dynamic Routing
    if ext not in ALL_SUPPORTED_EXTENSIONS:
        logger.debug(f"Ignoring unsupported file extension '{ext}' for file: {path.name}")
        return False

    # Retry helper to handle brief Windows OS file locks when files are created/modified
    retries = 3
    for attempt in range(retries):
        try:
            # Rule 2: Strict Error Handling wrap
            if ext in SUPPORTED_DOC_EXTENSIONS:
                # Text extraction based on file type
                if ext == ".pdf":
                    raw_text = extract_text_from_pdf(path)
                elif ext in {".html", ".htm"}:
                    raw_text = extract_text_from_html(path)
                elif ext in {".md", ".markdown"}:
                    raw_text = extract_text_from_markdown(path)
                elif ext == ".txt":
                    raw_text = extract_text_from_txt(path)
                else:
                    return False

                if not raw_text.strip():
                    logger.warning(f"File '{path.name}' contains no readable text. Skipping.")
                    return False

                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
                )
                raw_chunks = text_splitter.split_text(raw_text)
                if not raw_chunks:
                    return False

                documents: List[Document] = []
                doc_ids: List[str] = []
                for idx, chunk in enumerate(raw_chunks):
                    meta = {
                        "source": str(path),
                        "file_name": path.name,
                        "file_type": ext.lstrip("."),
                        "doc_type": "documentation",
                        "chunk_index": idx,
                    }
                    documents.append(Document(page_content=chunk, metadata=meta))
                    doc_ids.append(f"{path.name}_chunk_{idx}")

            elif ext in SUPPORTED_LOOP_EXTENSIONS:
                # Loop JSON atomic processing
                metadata, nl_summary, raw_json_data = extract_metadata_and_summary_from_json(path)
                full_content = (
                    f"### Natural Language Summary\n"
                    f"{nl_summary}\n\n"
                    f"### Raw Loop JSON\n"
                    f"{json.dumps(raw_json_data, indent=2)}"
                )
                documents = [Document(page_content=full_content, metadata=metadata)]
                doc_ids = [f"loop_{path.name}"]
            else:
                return False

            # Rule 3: Incremental Updates to ChromaDB
            target_store = vector_store or get_vector_store(
                chroma_dir=chroma_dir,
                collection_name=collection_name,
                embedding_model=embedding_model,
            )

            target_store.add_documents(documents=documents, ids=doc_ids)
            logger.info(
                f"Successfully ingested and indexed {len(documents)} document(s) from '{path.name}' into collection '{collection_name}'."
            )
            return True

        except (PermissionError, IOError) as lock_err:
            if attempt < retries - 1:
                time.sleep(0.3)
                continue
            logger.warning(f"File lock error while reading '{path.name}': {lock_err}")
            return False
        except Exception as err:
            # Strict Error Handling: Log warning, do NOT crash the watcher
            logger.warning(f"Error warning: Failed to process file '{path.name}': {err}")
            return False

    return False


# ---------------------------------------------------------------------------
# Initial Full Scan Functionality
# ---------------------------------------------------------------------------

def run_initial_scan(
    docs_dir: Union[Path, str] = DEFAULT_DOCS_DIR,
    loops_dir: Union[Path, str] = DEFAULT_LOOPS_DIR,
    chroma_dir: Union[Path, str] = DEFAULT_CHROMA_DIR,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> int:
    """
    Performs a full initial scan of all existing files inside docs_dir and loops_dir,
    parses and embeds them into chroma_db, and prints the total number of indexed documents.
    """
    docs_path = Path(docs_dir)
    loops_path = Path(loops_dir)
    chroma_path = Path(chroma_dir)

    docs_path.mkdir(parents=True, exist_ok=True)
    loops_path.mkdir(parents=True, exist_ok=True)
    chroma_path.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("Starting Full Initial Scan of existing files...")
    logger.info(f"Scanning Docs Directory : {docs_path}")
    logger.info(f"Scanning Loops Directory: {loops_path}")
    logger.info("=" * 60)

    # Initialize vector store
    vector_store = get_vector_store(
        chroma_dir=chroma_path,
        collection_name=collection_name,
        embedding_model=embedding_model,
    )

    # Find all supported doc files
    doc_files = [
        f for f in docs_path.rglob("*")
        if f.is_file() and f.suffix.lower() in SUPPORTED_DOC_EXTENSIONS
    ]

    # Find all supported loop files
    loop_files = [
        f for f in loops_path.rglob("*")
        if f.is_file() and f.suffix.lower() in SUPPORTED_LOOP_EXTENSIONS
    ]

    total_files_found = len(doc_files) + len(loop_files)
    logger.info(f"Discovered {len(doc_files)} doc file(s) and {len(loop_files)} loop file(s) ({total_files_found} total).")

    successful_ingestions = 0

    # Ingest doc files
    for doc_file in doc_files:
        success = process_single_file(
            file_path=doc_file,
            chroma_dir=chroma_path,
            collection_name=collection_name,
            embedding_model=embedding_model,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            vector_store=vector_store,
        )
        if success:
            successful_ingestions += 1

    # Ingest loop files
    for loop_file in loop_files:
        success = process_single_file(
            file_path=loop_file,
            chroma_dir=chroma_path,
            collection_name=collection_name,
            embedding_model=embedding_model,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            vector_store=vector_store,
        )
        if success:
            successful_ingestions += 1

    # Retrieve total document count from collection
    total_indexed_documents = 0
    try:
        total_indexed_documents = vector_store._collection.count()
    except Exception as e:
        logger.warning(f"Unable to query collection item count directly: {e}")

    logger.info("=" * 60)
    logger.info("Initial Scan Completed Successfully:")
    logger.info(f" - Files processed successfully : {successful_ingestions}/{total_files_found}")
    logger.info(f" - Total indexed items in Chroma: {total_indexed_documents}")
    logger.info("=" * 60)

    return total_indexed_documents


# ---------------------------------------------------------------------------
# Watchdog FileSystemEventHandler
# ---------------------------------------------------------------------------

class IngestionEventHandler(FileSystemEventHandler):
    """
    Watchdog FileSystemEventHandler that continuously monitors directories
    for on_created and on_modified events and dynamically routes files to ingest.
    """
    def __init__(
        self,
        chroma_dir: Union[Path, str] = DEFAULT_CHROMA_DIR,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    ):
        super().__init__()
        self.chroma_dir = chroma_dir
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self._last_processed: Dict[str, float] = {}

    def _should_process(self, src_path: str) -> bool:
        """Debounce events for the same file occurring in quick succession."""
        now = time.time()
        last_time = self._last_processed.get(src_path, 0)
        if now - last_time < 0.5:
            return False
        self._last_processed[src_path] = now
        return True

    def on_created(self, event: FileCreatedEvent):
        if event.is_directory:
            return
        file_path = Path(event.src_path)
        if file_path.suffix.lower() in ALL_SUPPORTED_EXTENSIONS and self._should_process(str(file_path)):
            logger.info(f"[Watchdog Event] New file created: {file_path.name}")
            process_single_file(
                file_path=file_path,
                chroma_dir=self.chroma_dir,
                collection_name=self.collection_name,
                embedding_model=self.embedding_model,
            )

    def on_modified(self, event: FileModifiedEvent):
        if event.is_directory:
            return
        file_path = Path(event.src_path)
        if file_path.suffix.lower() in ALL_SUPPORTED_EXTENSIONS and self._should_process(str(file_path)):
            logger.info(f"[Watchdog Event] File modified: {file_path.name}")
            process_single_file(
                file_path=file_path,
                chroma_dir=self.chroma_dir,
                collection_name=self.collection_name,
                embedding_model=self.embedding_model,
            )


# ---------------------------------------------------------------------------
# Batch Ingestion Utilities (Backward Compatibility)
# ---------------------------------------------------------------------------

def load_and_chunk_markdown_docs(
    docs_dir: Path = DEFAULT_DOCS_DIR,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Document]:
    """Reads all documentation files (.md, .txt, .html, .pdf) from docs_dir and chunks them."""
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        logger.warning(f"Docs directory does not exist: {docs_path}")
        return []

    doc_files = [f for f in docs_path.rglob("*") if f.is_file() and f.suffix.lower() in SUPPORTED_DOC_EXTENSIONS]
    if not doc_files:
        logger.info(f"No supported doc files found in {docs_path}")
        return []

    logger.info(f"Found {len(doc_files)} doc file(s) in {docs_path}")
    raw_documents: List[Document] = []

    for file_path in doc_files:
        ext = file_path.suffix.lower()
        try:
            if ext == ".pdf":
                content = extract_text_from_pdf(file_path)
            elif ext in {".html", ".htm"}:
                content = extract_text_from_html(file_path)
            elif ext in {".md", ".markdown"}:
                content = extract_text_from_markdown(file_path)
            elif ext == ".txt":
                content = extract_text_from_txt(file_path)
            else:
                continue

            if not content.strip():
                continue

            metadata = {
                "source": str(file_path),
                "file_name": file_path.name,
                "file_type": ext.lstrip("."),
                "doc_type": "documentation",
            }
            raw_documents.append(Document(page_content=content, metadata=metadata))
        except Exception as e:
            logger.warning(f"Error reading doc file {file_path}: {e}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
    )

    chunked_docs = text_splitter.split_documents(raw_documents)
    for idx, doc in enumerate(chunked_docs):
        doc.metadata["chunk_index"] = idx

    logger.info(f"Split {len(raw_documents)} doc(s) into {len(chunked_docs)} chunk(s).")
    return chunked_docs


def load_loop_documents(loops_dir: Path = DEFAULT_LOOPS_DIR) -> List[Document]:
    """Reads all JSON files from loops_dir as single atomic documents (no chunking)."""
    loops_path = Path(loops_dir)
    if not loops_path.exists():
        logger.warning(f"Loops directory does not exist: {loops_path}")
        return []

    json_files = list(loops_path.rglob("*.json"))
    if not json_files:
        logger.info(f"No JSON files found in {loops_path}")
        return []

    logger.info(f"Found {len(json_files)} loop JSON file(s) in {loops_path}")
    loop_documents: List[Document] = []

    for file_path in json_files:
        try:
            metadata, nl_summary, parsed_data = extract_metadata_and_summary_from_json(file_path)
            full_content = (
                f"### Natural Language Summary\n"
                f"{nl_summary}\n\n"
                f"### Raw Loop JSON\n"
                f"{json.dumps(parsed_data, indent=2)}"
            )
            loop_documents.append(
                Document(
                    page_content=full_content,
                    metadata=metadata,
                )
            )
        except Exception as e:
            logger.warning(f"Error processing loop JSON file {file_path}: {e}")

    logger.info(f"Loaded {len(loop_documents)} atomic loop document(s).")
    return loop_documents


def build_vector_store(
    docs_dir: Path = DEFAULT_DOCS_DIR,
    loops_dir: Path = DEFAULT_LOOPS_DIR,
    chroma_dir: Path = DEFAULT_CHROMA_DIR,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
) -> Optional[Chroma]:
    """Main batch ingestion pipeline."""
    chroma_path = Path(chroma_dir)
    chroma_path.mkdir(parents=True, exist_ok=True)

    chunked_docs = load_and_chunk_markdown_docs(docs_dir=docs_dir)
    loop_docs = load_loop_documents(loops_dir=loops_dir)
    all_documents = chunked_docs + loop_docs

    if not all_documents:
        logger.warning(f"No documents found to ingest from {docs_dir} or {loops_dir}.")
        return None

    logger.info(f"Total documents to index: {len(all_documents)}")
    embeddings = get_embedding_function(model_name=embedding_model)
    vector_store = Chroma.from_documents(
        documents=all_documents,
        embedding=embeddings,
        persist_directory=str(chroma_path),
        collection_name=collection_name,
    )
    logger.info(f"Vector store successfully saved to '{chroma_path}' in collection '{collection_name}'.")
    return vector_store


def retrieve_context(
    query: str,
    k_docs: int = 3,
    k_loops: int = 2,
    chroma_dir: Union[Path, str] = DEFAULT_CHROMA_DIR,
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> Dict[str, Any]:
    """Retrieves both documentation chunks and similar loop examples for a given query."""
    try:
        vector_store = get_vector_store(
            chroma_dir=chroma_dir,
            collection_name=collection_name
        )
        
        docs_results = []
        try:
            docs_results = vector_store.similarity_search(
                query=query,
                k=k_docs,
                filter={"doc_type": "documentation"}
            )
        except Exception as e:
            logger.debug(f"Filtered docs search fallback: {e}")

        loops_results = []
        try:
            loops_results = vector_store.similarity_search(
                query=query,
                k=k_loops,
                filter={"doc_type": "loop"}
            )
        except Exception as e:
            logger.debug(f"Filtered loops search fallback: {e}")

        if not docs_results and not loops_results:
            general_results = vector_store.similarity_search(query=query, k=k_docs + k_loops)
            for res in general_results:
                if res.metadata.get("doc_type") == "loop":
                    loops_results.append(res)
                else:
                    docs_results.append(res)

        return {
            "query": query,
            "docs": [{"content": d.page_content, "metadata": d.metadata} for d in docs_results],
            "loops": [{"content": d.page_content, "metadata": d.metadata} for d in loops_results]
        }
    except Exception as e:
        logger.error(f"Error retrieving context from ChromaDB: {e}")
        return {"query": query, "docs": [], "loops": [], "error": str(e)}


# ---------------------------------------------------------------------------
# Watcher Service Main Loop
# ---------------------------------------------------------------------------

def start_watcher(
    docs_dir: Union[Path, str] = DEFAULT_DOCS_DIR,
    loops_dir: Union[Path, str] = DEFAULT_LOOPS_DIR,
    chroma_dir: Union[Path, str] = DEFAULT_CHROMA_DIR,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    sleep_interval: float = 1.0,
    block: bool = True,
    run_initial: bool = True,
) -> Observer:
    """
    1. Runs a full initial scan of all existing files inside docs_dir and loops_dir.
    2. Parses and embeds them into chroma_db and prints the total number of indexed documents.
    3. Only after the initial scan completes, starts the watchdog observer loop to monitor for newly added files.
    """
    docs_path = Path(docs_dir)
    loops_path = Path(loops_dir)
    chroma_path = Path(chroma_dir)

    # 1. Run full initial scan first
    if run_initial:
        total_indexed = run_initial_scan(
            docs_dir=docs_path,
            loops_dir=loops_path,
            chroma_dir=chroma_path,
            collection_name=collection_name,
            embedding_model=embedding_model,
        )
        logger.info(f"Initial scan complete. Total indexed documents in '{collection_name}': {total_indexed}")

    # 2. Only after initial scan completes, initialize and start Watchdog Observer
    event_handler = IngestionEventHandler(
        chroma_dir=chroma_path,
        collection_name=collection_name,
        embedding_model=embedding_model,
    )

    observer = Observer()
    observer.schedule(event_handler, path=str(docs_path), recursive=True)
    observer.schedule(event_handler, path=str(loops_path), recursive=True)

    logger.info("=" * 60)
    logger.info("Starting Watchdog Observer Loop for Real-time Monitoring")
    logger.info(f"Monitoring Docs Directory : {docs_path}")
    logger.info(f"Monitoring Loops Directory: {loops_path}")
    logger.info(f"ChromaDB Persist Dir      : {chroma_path}")
    logger.info("=" * 60)

    observer.start()

    if block:
        try:
            while True:
                time.sleep(sleep_interval)
        except KeyboardInterrupt:
            logger.info("Shutting down CHIA Ingestion Service observer...")
            observer.stop()
        observer.join()
        logger.info("Ingestion Service stopped cleanly.")

    return observer


if __name__ == "__main__":
    start_watcher()
