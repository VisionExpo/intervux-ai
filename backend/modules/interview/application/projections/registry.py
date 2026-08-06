from typing import Dict, Optional, Type
from .contracts.role import ProjectionRole
from .contracts.projection import Projection

class ProjectionRegistry:
    """
    Registry that maps a ProjectionRole to the specific Projection implementation.
    """
    def __init__(self):
        self._registry: Dict[ProjectionRole, Projection] = {}

    def register(self, role: ProjectionRole, projection: Projection) -> None:
        """Registers a projection for a specific role."""
        self._registry[role] = projection

    def resolve(self, role: ProjectionRole) -> Optional[Projection]:
        """Returns the projection implementation for the role, or None."""
        return self._registry.get(role)
