"""Source chunk and retrieval schemas."""

from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, Field

from app.schemas.sources import Jurisdiction, LanguageCode, TopicCategory, TrustTier


class SourceChunk(BaseModel):
    """Cleaned source text chunk prepared for embedding and indexing."""

    chunk_id: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    page_id: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    source_id: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    source_url: AnyHttpUrl
    title: str = Field(min_length=1)
    section_heading: str | None = None
    topic: TopicCategory = TopicCategory.GENERAL_HEALTHCARE_NAVIGATION
    jurisdiction: Jurisdiction = Jurisdiction.ONTARIO
    language: LanguageCode = LanguageCode.ENGLISH
    trust_tier: TrustTier
    chunk_index: int = Field(ge=0)
    text: str = Field(min_length=1)
    token_count: int = Field(gt=0)
    content_hash: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    last_crawled_at: datetime
    embedding_model: str | None = None
    chunking_version: str | None = None
    indexed_at: datetime | None = None


class ChunkCitation(BaseModel):
    """Citation data derived from a retrieved source chunk."""

    title: str = Field(min_length=1)
    url: AnyHttpUrl
    source_id: str = Field(min_length=1)
    section_heading: str | None = None


class RetrievalHit(BaseModel):
    """Single retrieved chunk with ranking metadata."""

    chunk: SourceChunk
    score: float = Field(ge=0.0, le=1.0)
    rerank_score: float | None = Field(default=None, ge=0.0, le=1.0)

    def to_citation(self) -> ChunkCitation:
        """Create a citation for answer rendering."""

        return ChunkCitation(
            title=self.chunk.title,
            url=self.chunk.source_url,
            source_id=self.chunk.source_id,
            section_heading=self.chunk.section_heading,
        )


class RetrievalResult(BaseModel):
    """Collection of retrieved chunks returned by the retrieval layer."""

    query: str = Field(min_length=1)
    hits: list[RetrievalHit] = Field(default_factory=list)
    filters: dict[str, str] = Field(default_factory=dict)
