from typing import Optional, List
from backend.modules.interview.domain.aggregate import InterviewAggregate
from .contracts.role import ProjectionRole
from .contracts.context import ProjectionContext
from .contracts.envelope import ProjectionEnvelope
from .contracts.delivery import ProjectionDelivery
from .registry import ProjectionRegistry
from .policy_resolver import ProjectionPolicyResolver

class ProjectionExecutor:
    """
    The main orchestrator for the Projection Pipeline.
    Given an aggregate and a list of roles, it resolves the policy, executes the projections,
    and returns (or optionally delivers) the Envelopes.
    """
    
    def __init__(
        self, 
        registry: ProjectionRegistry, 
        policy_resolver: ProjectionPolicyResolver,
        delivery: Optional[ProjectionDelivery] = None
    ):
        self.registry = registry
        self.policy_resolver = policy_resolver
        self.delivery = delivery

    def execute(self, aggregate: InterviewAggregate, roles: List[ProjectionRole]) -> List[ProjectionEnvelope]:
        """
        Executes projections for the requested roles on the provided aggregate.
        """
        envelopes = []
        
        for role in roles:
            capabilities = self.policy_resolver.resolve_capabilities(role)
            context = ProjectionContext(role=role, capabilities=capabilities)
            
            projection = self.registry.resolve(role)
            if not projection:
                continue
                
            envelope = projection.project(aggregate, context)
            envelopes.append(envelope)
            
            if self.delivery:
                self.delivery.deliver(envelope)
                
        return envelopes
