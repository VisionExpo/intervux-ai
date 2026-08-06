from typing import Optional
from backend.modules.interview.domain.aggregate import InterviewAggregate
from .contracts.role import ProjectionRole
from .contracts.context import ProjectionContext
from .contracts.envelope import ProjectionEnvelope
from .contracts.publisher import ProjectionPublisher
from .registry import ProjectionRegistry
from .policy_resolver import ProjectionPolicyResolver

class ProjectionExecutor:
    """
    The main orchestrator for the Projection Pipeline.
    Given an aggregate and a role, it resolves the policy, executes the projection,
    and returns (or optionally publishes) the Envelope.
    """
    
    def __init__(
        self, 
        registry: ProjectionRegistry, 
        policy_resolver: ProjectionPolicyResolver,
        publisher: Optional[ProjectionPublisher] = None
    ):
        self.registry = registry
        self.policy_resolver = policy_resolver
        self.publisher = publisher

    def execute(self, aggregate: InterviewAggregate, role: ProjectionRole) -> Optional[ProjectionEnvelope]:
        """
        Executes a projection for the requested role on the provided aggregate.
        """
        # 1. Resolve Policy -> Capabilities
        capabilities = self.policy_resolver.resolve_capabilities(role)
        
        # 2. Build Context
        context = ProjectionContext(role=role, capabilities=capabilities)
        
        # 3. Lookup Projection Implementation
        projection = self.registry.resolve(role)
        if not projection:
            # If no projection is registered for this role, do nothing.
            return None
            
        # 4. Execute Projection (Transforms Aggregate -> Payload)
        envelope = projection.project(aggregate, context)
        
        # 5. Optionally Publish (e.g. to WebSockets/Cache)
        if self.publisher:
            self.publisher.publish(envelope)
            
        return envelope
