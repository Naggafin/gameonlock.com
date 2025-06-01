import sqlite3
from pathlib import Path

from chunker import scan_project
from embedder import embed
from sentence_transformers import CrossEncoder
from token_counter import count_tokens
from tqdm import tqdm
from vector_store import add_chunks, query

DB_PATH = Path(".embed_cache/file_timestamps.db")


def init_timestamp_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS file_timestamps (
                path TEXT PRIMARY KEY,
                mtime REAL,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def get_file_mtime(file_path):
    return Path(file_path).stat().st_mtime


def get_cached_mtime(file_path):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT mtime FROM file_timestamps WHERE path = ?", (str(file_path),)
        )
        row = cur.fetchone()
        return row[0] if row else None


def update_cached_mtime(file_path, mtime):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO file_timestamps (path, mtime) VALUES (?, ?)",
            (str(file_path), mtime),
        )


def index_project(project_path, progress_callback=None):
    init_timestamp_db()
    all_chunks = []

    # Scan files with progress
    file_iterator = scan_project(project_path)
    file_iterator = tqdm(file_iterator, desc="Scanning files", leave=False)

    for file, chunks in file_iterator:
        for chunk in chunks:
            chunk["metadata"]["path"] = str(file)
            all_chunks.append((file, chunk))
        update_cached_mtime(file, get_file_mtime(file))
        if progress_callback:
            progress_callback()

    # Embed chunks with progress
    if all_chunks:
        chunk_iterator = tqdm(all_chunks, desc="Embedding chunks", leave=False)
        embeddings = embed(chunk_iterator)
        add_chunks(all_chunks, embeddings)
        print(f"Indexed {len(all_chunks)} code chunks.")
    else:
        print("No chunks to index.")


def index_project_incremental(project_path, progress_callback=None):
    init_timestamp_db()
    all_chunks = []

    # Scan files with progress
    file_iterator = scan_project(project_path)
    file_iterator = tqdm(file_iterator, desc="Scanning files", leave=False)

    for file, chunks in file_iterator:
        current_mtime = get_file_mtime(file)
        cached_mtime = get_cached_mtime(file)
        if cached_mtime is None or current_mtime > cached_mtime:
            for chunk in chunks:
                chunk["metadata"]["path"] = str(file)
                all_chunks.append((file, chunk))
            update_cached_mtime(file, current_mtime)
        if progress_callback:
            progress_callback()

    # Embed chunks with progress
    if all_chunks:
        chunk_iterator = tqdm(all_chunks, desc="Embedding chunks", leave=False)
        embeddings = embed(chunk_iterator)
        add_chunks(all_chunks, embeddings)
        print(f"Incrementally indexed {len(all_chunks)} code chunks.")
    else:
        print("No changes detected.")


def context_aggregator(chunks, metadatas, max_tokens=8000):
    summary = []
    total_tokens = 0

    for chunk, meta in zip(chunks, metadatas, strict=False):
        chunk_tokens = count_tokens(chunk)
        if total_tokens + chunk_tokens > max_tokens:
            break
        path = meta.get("path", "unknown")
        code_type = meta.get("type", "unknown")
        start_line = meta.get("start_line", 1)
        end_line = meta.get("end_line", 1)
        name = meta.get("name", "")
        content = f"File: {path}, Type: {code_type}, Name: {name}, Lines: {start_line}-{end_line}\n{chunk}\n"
        summary.append(content)
        total_tokens += chunk_tokens

    return "\n".join(summary), total_tokens


def search_code_hybrid(query_text, k=5, max_tokens=8000, metadata_filter=None):
    query_text = " ".join(query_text.lower().split())
    # Apply metadata filter (e.g., {"type": "class"})
    where_clause = metadata_filter if metadata_filter else None
    docs, metas = query(query_text, embed, k=k * 2, where=where_clause)

    if not docs:
        return {"content": "", "metadata": [], "tokens": 0}

    cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    pairs = [[query_text, doc] for doc in docs]
    scores = cross_encoder.predict(pairs)

    ranked = sorted(
        zip(scores, docs, metas, strict=False), key=lambda x: x[0], reverse=True
    )[:k]
    ranked_docs = [doc for _, doc, _ in ranked]
    ranked_metas = [meta for _, _, meta in ranked]

    context, tokens = context_aggregator(ranked_docs, ranked_metas, max_tokens)

    return {
        "content": context,
        "metadata": [
            {
                "path": m["path"],
                "type": m["type"],
                "name": m.get("name", ""),
                "start_line": m["start_line"],
                "end_line": m.get("end_line", 1),
            }
            for m in ranked_metas
        ],
        "tokens": tokens,
    }
