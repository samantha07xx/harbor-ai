from fastapi import APIRouter

from app.utils.markdown_loader import load_markdown_documents
from app.utils.text_chunker import split_text_into_chunks

router = APIRouter()


@router.get("/knowledge-base")
def get_knowledge_base():
    documents = load_markdown_documents()

    return {
        "count": len(documents),
        "documents": [
            {
                "title": document["title"],
                "path": document["path"],
                "chunk_count": len(split_text_into_chunks(document["content"])),
                "content_preview": document["content"][:200],
            }
            for document in documents
        ],
    }