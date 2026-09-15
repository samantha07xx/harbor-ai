"""Trusted source and crawled page schemas."""

from datetime import datetime
from enum import StrEnum

from pydantic import AnyHttpUrl, BaseModel, Field


class TrustTier(StrEnum):
    """Supported source trust tiers."""

    OFFICIAL_GOVERNMENT = "official_government"
    PUBLIC_HEALTH = "public_health"
    APPROVED_NONPROFIT = "approved_nonprofit"


class Jurisdiction(StrEnum):
    """Supported healthcare jurisdiction values."""

    ONTARIO = "Ontario"


class LanguageCode(StrEnum):
    """Supported source language codes for the MVP."""

    ENGLISH = "en"


class TopicCategory(StrEnum):
    """Known Ontario healthcare navigation topics."""

    OHIP_ELIGIBILITY = "ohip_eligibility"
    HEALTH_CARD_APPLICATION = "health_card_application"
    REQUIRED_DOCUMENTS = "required_documents"
    FINDING_FAMILY_DOCTOR = "finding_family_doctor"
    WALK_IN_CLINICS = "walk_in_clinics"
    EMERGENCY_CARE = "emergency_care"
    NON_EMERGENCY_ADVICE = "non_emergency_advice"
    PUBLIC_HEALTH = "public_health"
    MENTAL_HEALTH_NAVIGATION = "mental_health_navigation"
    NEWCOMER_HEALTH_SERVICES = "newcomer_health_services"
    GENERAL_HEALTHCARE_NAVIGATION = "general_healthcare_navigation"


class TrustedSource(BaseModel):
    """Approved source registry record."""

    source_id: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    name: str = Field(min_length=1)
    base_url: AnyHttpUrl
    seed_urls: list[AnyHttpUrl] = Field(min_length=1)
    allowed_url_patterns: list[str] = Field(default_factory=list)
    trust_tier: TrustTier
    jurisdiction: Jurisdiction = Jurisdiction.ONTARIO
    language: LanguageCode = LanguageCode.ENGLISH
    enabled: bool = True


class SourcePage(BaseModel):
    """Metadata captured for a crawled trusted source page."""

    page_id: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    source_id: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    url: AnyHttpUrl
    canonical_url: AnyHttpUrl | None = None
    title: str = Field(min_length=1)
    raw_html_hash: str | None = Field(default=None, pattern=r"^sha256:[a-f0-9]{64}$")
    clean_text_hash: str | None = Field(default=None, pattern=r"^sha256:[a-f0-9]{64}$")
    last_crawled_at: datetime
    source_last_updated_at: datetime | None = None
    http_status: int = Field(ge=100, le=599)
    language: LanguageCode = LanguageCode.ENGLISH
    trust_tier: TrustTier


class FetchedPage(BaseModel):
    """Raw page fetched from an approved source."""

    source_id: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    url: AnyHttpUrl
    raw_html: str = Field(min_length=1)
    http_status: int = Field(ge=100, le=599)
    fetched_at: datetime
    trust_tier: TrustTier
    language: LanguageCode = LanguageCode.ENGLISH


class ExtractedLink(BaseModel):
    """Link preserved from extracted page content."""

    text: str = Field(min_length=1)
    url: AnyHttpUrl


class ExtractedPage(BaseModel):
    """Clean text and metadata extracted from a fetched page."""

    source_id: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    url: AnyHttpUrl
    canonical_url: AnyHttpUrl | None = None
    title: str = Field(min_length=1)
    clean_text: str = Field(min_length=1)
    clean_text_hash: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    headings: list[str] = Field(default_factory=list)
    links: list[ExtractedLink] = Field(default_factory=list)
    extracted_at: datetime
    language: LanguageCode = LanguageCode.ENGLISH
    trust_tier: TrustTier
