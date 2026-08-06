from dataclasses import dataclass
from .role import ProjectionRole
from .capabilities import ProjectionCapabilities

@dataclass(frozen=True)
class ProjectionContext:
    """
    The context passed into a projection implementation, containing
    the resolved capabilities and the requesting role.
    """
    role: ProjectionRole
    capabilities: ProjectionCapabilities
    # Future additions: tenant_id, correlation_id, etc.
