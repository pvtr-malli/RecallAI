"""Gradio UI for RecallAI - Simple frontend without CSS."""

import gradio as gr
import requests
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional

API_BASE_URL = "http://localhost:8000"

# Feedback database (stored in indexes folder with other persistent data)
FEEDBACK_DB = Path("indexes/feedback.db")


def init_feedback_db():
    """Initialize feedback database."""
    # Ensure indexes directory exists
    FEEDBACK_DB.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(FEEDBACK_DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            query TEXT NOT NULL,
            mode TEXT NOT NULL,
            chunks_retrieved INTEGER NOT NULL,
            feedback TEXT NOT NULL,
            comment TEXT
        )
    """)
    conn.commit()
    conn.close()


# Initialize on module load
init_feedback_db()


def save_feedback(metadata: dict, feedback_type: str, comment: str) -> str:
    """
    Save user feedback to database.

    param metadata: Search metadata (query, mode, chunks).
    param feedback_type: Feedback type ("positive" or "negative").
    param comment: Optional user comment.
    return: Confirmation message.
    """
    if not metadata or "query" not in metadata:
        return "⚠️ No search performed yet. Please run a search first."

    try:
        conn = sqlite3.connect(FEEDBACK_DB)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO feedback (timestamp, query, mode, chunks_retrieved, feedback, comment)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(),
                metadata["query"],
                metadata["mode"],
                metadata["chunks"],
                feedback_type,
                comment.strip() if comment.strip() else None
            )
        )
        conn.commit()
        conn.close()

        return f"✅ Thank you for your feedback! ({feedback_type})"

    except Exception as e:
        return f"❌ Error saving feedback: {str(e)}"


def update_folders(folders_input: str) -> str:
    """
    Update folders configuration.

    param folders_input: Comma-separated folder paths.
    return: Status message.
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/folders",
            json={"folders": folders_input},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()

        folders_list = "\n".join(f"  • {folder}" for folder in result["folders"])
        return f"✅ {result['message']}\n\nConfigured folders:\n{folders_list}"

    except requests.exceptions.ConnectionError:
        return "❌ Error: Cannot connect to RecallAI server. Make sure it's running on http://localhost:8000"
    except requests.exceptions.RequestException as e:
        return f"❌ Error updating folders: {str(e)}"


def index_files(rebuild: bool) -> str:
    """
    Index files from configured folders.

    param rebuild: Whether to rebuild index from scratch.
    return: Status message with indexing results.
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/index",
            params={"rebuild": rebuild},
            timeout=300  # 5 minutes timeout for indexing
        )
        response.raise_for_status()
        result = response.json()

        mode = "Rebuilt" if rebuild else "Indexed"
        classified = result["classified"]

        return f"""✅ {mode} successfully!

📊 Indexing Summary:
  • Total files processed: {result['total_files']}
  • Code files: {classified['code']}
  • Document files: {classified['document']}
  • Notebook files: {classified['notebook']}

The files have been embedded and stored in the search index."""

    except requests.exceptions.ConnectionError:
        return "❌ Error: Cannot connect to RecallAI server. Make sure it's running on http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ Error: Indexing timed out. Try indexing fewer files or increase timeout."
    except requests.exceptions.RequestException as e:
        return f"❌ Error indexing files: {str(e)}"


def search_query(query: str, mode: str, search_in: str, top_k: int) -> Tuple[str, str, dict]:
    """
    Search for documents and code.

    param query: Search query.
    param mode: Search mode ("search" or "answer").
    param search_in: Where to search ("documents", "code", "both").
    param top_k: Number of results to return.
    return: Tuple of (results_summary, chunks_detail, search_metadata).
    """
    if not query.strip():
        return "⚠️ Please enter a search query.", "", {}

    try:
        response = requests.post(
            f"{API_BASE_URL}/search",
            json={
                "query": query,
                "mode": mode,
                "search_in": search_in,
                "top_k": top_k
            },
            timeout=60
        )
        response.raise_for_status()
        result = response.json()

        # Store metadata for feedback
        metadata = {
            "query": query,
            "mode": mode,
            "chunks": len(result.get("results", [])) if mode == "search" else len(result.get("file_references", []))
        }

        if mode == "search":
            # Search mode: return file names/types + chunks separately
            summary, chunks = _format_search_results(result)
            return summary, chunks, metadata
        else:
            # Answer mode: return answer + file names/types only
            answer, _ = _format_answer_results(result)
            return answer, "", metadata

    except requests.exceptions.ConnectionError:
        return "❌ Error: Cannot connect to RecallAI server. Make sure it's running on http://localhost:8000", "", {}
    except requests.exceptions.Timeout:
        return "❌ Error: Search timed out. Try a simpler query or reduce top_k.", "", {}
    except requests.exceptions.RequestException as e:
        return f"❌ Error searching: {str(e)}", "", {}


def _format_search_results(result: dict) -> Tuple[str, str]:
    """
    Format search mode results.

    param result: API response for search mode.
    return: Tuple of (file summary, chunks detail).
    """
    results = result.get("results", [])

    if not results:
        return "No results found.", ""

    # File summary (file name and type only)
    file_summary = f"📊 Found {len(results)} results for: **{result['query']}**\n\n"
    for idx, item in enumerate(results, 1):
        file_path = item["file_path"]
        file_name = file_path.split("/")[-1]
        file_type = item["file_type"]
        score = item["score"]
        file_summary += f"{idx}. 📄 **{file_name}** ({file_type}) - Score: {score:.3f}\n"

    # Chunks detail (bottom section)
    chunks_detail = "## 📝 Matching Chunks\n\n"
    for idx, item in enumerate(results, 1):
        file_path = item["file_path"]
        file_name = file_path.split("/")[-1]
        chunk_text = item["chunk_text"]
        chunk_index = item["chunk_index"]

        chunks_detail += f"### Result {idx}: {file_name} (Chunk {chunk_index})\n"
        chunks_detail += f"```\n{chunk_text}\n```\n\n"

    return file_summary, chunks_detail


def _format_answer_results(result: dict) -> Tuple[str, str]:
    """
    Format answer mode results.

    param result: API response for answer mode.
    return: Tuple of (answer with files, empty string).
    """
    answer = result.get("answer", "No answer generated.")
    file_references = result.get("file_references", [])

    # Answer with file references
    output = f"## 💡 Answer\n\n{answer}\n\n"

    if file_references:
        output += "---\n\n## 📚 Sources\n\n"
        for idx, ref in enumerate(file_references, 1):
            file_path = ref["file_path"]
            file_name = file_path.split("/")[-1]
            file_type = ref["file_type"]
            output += f"{idx}. 📄 **{file_name}** ({file_type})\n"

    return output, ""


def create_interface() -> gr.Blocks:
    """Create and return the Gradio interface."""
    with gr.Blocks(title="RecallAI") as app:
        gr.Markdown("""
        # 🔍 RecallAI - Semantic Search for Your Files

        Search through your documents and code using natural language.
        """)

        with gr.Tab("📁 Configure Folders"):
            gr.Markdown("""
            ### Add Folders to Index
            Enter folder paths separated by commas. Examples:
            - `~/projects/notes`
            - `~/projects/notes, ~/documents, ~/code`
            """)

            folders_input = gr.Textbox(
                label="Folder Paths",
                placeholder="~/projects/notes, ~/documents",
                lines=2
            )

            update_btn = gr.Button("Update Folders", variant="primary")
            folders_output = gr.Textbox(label="Status", lines=8, interactive=False)

            update_btn.click(
                fn=update_folders,
                inputs=[folders_input],
                outputs=[folders_output]
            )

        with gr.Tab("🔄 Index Files"):
            gr.Markdown("""
            ### Index Your Files

            Index files from configured folders to make them searchable.

            **Note:** First-time indexing may take a few minutes depending on the number of files.
            """)

            rebuild_checkbox = gr.Checkbox(
                label="Rebuild index from scratch (clears existing index)",
                value=False
            )

            index_btn = gr.Button("Start Indexing", variant="primary")
            index_output = gr.Textbox(label="Indexing Status", lines=12, interactive=False)

            index_btn.click(
                fn=index_files,
                inputs=[rebuild_checkbox],
                outputs=[index_output]
            )

        with gr.Tab("🔍 Search"):
            gr.Markdown("""
            ### Search Your Files

            Use natural language to search through your indexed documents and code.
            """)

            with gr.Row():
                with gr.Column(scale=3):
                    query_input = gr.Textbox(
                        label="Search Query",
                        placeholder="e.g., How to handle authentication? or error handling patterns",
                        lines=2
                    )
                with gr.Column(scale=1):
                    mode_radio = gr.Radio(
                        choices=["search", "answer"],
                        value="search",
                        label="Mode",
                        info="search: Get matching files | answer: Get LLM answer"
                    )

            with gr.Row():
                search_in_radio = gr.Radio(
                    choices=["both", "documents", "code"],
                    value="both",
                    label="Search In",
                    info="Where to search"
                )
                top_k_slider = gr.Slider(
                    minimum=1,
                    maximum=20,
                    value=5,
                    step=1,
                    label="Number of Results",
                    info="How many results to return"
                )

            search_btn = gr.Button("Search", variant="primary", size="lg")

            gr.Markdown("### Results")
            results_output = gr.Markdown(label="Search Results")

            gr.Markdown("### Chunks Detail")
            chunks_output = gr.Markdown(label="Matching Chunks", visible=True)

            # Feedback section
            gr.Markdown("---")
            gr.Markdown("### 📝 Feedback")
            gr.Markdown("Help us improve by providing feedback on the search results.")

            with gr.Row():
                feedback_positive_btn = gr.Button("👍 Helpful", variant="secondary")
                feedback_negative_btn = gr.Button("👎 Not Helpful", variant="secondary")

            feedback_comment = gr.Textbox(
                label="Optional Comment",
                placeholder="Any additional comments about the results...",
                lines=2
            )

            feedback_status = gr.Textbox(label="Feedback Status", interactive=False, lines=1)

            # Hidden state to store search metadata
            search_metadata = gr.State({})

            # Wire up search
            search_btn.click(
                fn=search_query,
                inputs=[query_input, mode_radio, search_in_radio, top_k_slider],
                outputs=[results_output, chunks_output, search_metadata]
            )

            # Wire up feedback buttons
            feedback_positive_btn.click(
                fn=lambda metadata, comment: save_feedback(metadata, "positive", comment),
                inputs=[search_metadata, feedback_comment],
                outputs=[feedback_status]
            )

            feedback_negative_btn.click(
                fn=lambda metadata, comment: save_feedback(metadata, "negative", comment),
                inputs=[search_metadata, feedback_comment],
                outputs=[feedback_status]
            )

        gr.Markdown("""
        ---
        💡 **Quick Start:**
        1. Configure folders in the "Configure Folders" tab
        2. Index files in the "Index Files" tab
        3. Search your content in the "Search" tab
        """)

    return app


def main():
    """Entry point for standalone UI (deprecated - use recall_ai.app instead)."""
    print("Starting RecallAI UI...")
    print("Make sure RecallAI server is running on http://localhost:8000")
    app = create_interface()
    app.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    main()
