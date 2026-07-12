from fastapi import APIRouter

from app.utils.markdown_loader import load_markdown_documents

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
                "content_preview": document["content"][:200],
            }
            for document in documents
        ],
    }