from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"


def load_markdown_documents():
    documents = []

    for file_path in KNOWLEDGE_BASE_DIR.rglob("*.md"):
        content = file_path.read_text(encoding="utf-8").strip()

        documents.append(
            {
                "title": file_path.stem.replace("_", " ").title(),
                "path": str(file_path.relative_to(PROJECT_ROOT)),
                "content": content,
            }
        )

    return documents