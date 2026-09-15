"""Trusted source registry loader."""

import json
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from app.schemas.sources import TrustedSource

DEFAULT_REGISTRY_PATH = Path(__file__).with_name("trusted_sources.json")


class SourceRegistryError(ValueError):
    """Raised when the trusted source registry cannot be loaded."""


def load_trusted_sources(path: Path | None = None) -> list[TrustedSource]:
    """Load and validate trusted sources from a JSON registry file."""

    registry_path = path or DEFAULT_REGISTRY_PATH

    try:
        registry_data = json.loads(registry_path.read_text(encoding="utf-8"))
        return TypeAdapter(list[TrustedSource]).validate_python(registry_data)
    except FileNotFoundError as exc:
        raise SourceRegistryError(f"Trusted source registry not found: {registry_path}") from exc
    except json.JSONDecodeError as exc:
        raise SourceRegistryError(f"Trusted source registry is not valid JSON: {registry_path}") from exc
    except ValidationError as exc:
        raise SourceRegistryError(f"Trusted source registry failed validation: {registry_path}") from exc


def get_enabled_sources(path: Path | None = None) -> list[TrustedSource]:
    """Return only enabled trusted sources."""

    return [source for source in load_trusted_sources(path) if source.enabled]
