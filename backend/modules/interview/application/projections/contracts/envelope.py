from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict

@dataclass(frozen=True)
class ProjectionEnvelope:
    """
    The standardized wrapper for all generated projections.
    Features independent versioning for schema, aggregate, and projection.
    """
    schema: str
    schema_version: int
    aggregate_version: int
    projection_version: int
    payload: Dict[str, Any]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
