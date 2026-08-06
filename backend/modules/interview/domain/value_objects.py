from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
from typing import Optional

@dataclass(frozen=True)
class AggregateMetadata:
    """
    Metadata for tracking the identity and lifecycle of an aggregate root.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None
    
    def increment_version(self) -> "AggregateMetadata":
        """
        Returns a new AggregateMetadata instance with the version incremented 
        and updated_at refreshed. Value objects are immutable.
        """
        return AggregateMetadata(
            id=self.id,
            version=self.version + 1,
            created_at=self.created_at,
            updated_at=datetime.now(timezone.utc),
            correlation_id=self.correlation_id
        )
