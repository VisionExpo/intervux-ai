from .contracts.role import ProjectionRole
from .contracts.capabilities import ProjectionCapabilities

class ProjectionPolicyResolver:
    """
    Resolves the capabilities/permissions for a given role.
    This separates authorization logic from the Projection logic itself.
    """
    
    def resolve_capabilities(self, role: ProjectionRole) -> ProjectionCapabilities:
        """
        Determines what data the given role is allowed to see.
        Future: Could also take tenant_id, subscription tier, etc.
        """
        if role == ProjectionRole.CANDIDATE:
            return ProjectionCapabilities(
                show_internal_reasoning=False,
                show_scores=False,
                show_risk_flags=False,
                show_raw_transcripts=False,
                show_system_prompts=False
            )
            
        elif role == ProjectionRole.RECRUITER:
            return ProjectionCapabilities(
                show_internal_reasoning=True,
                show_scores=True,
                show_risk_flags=True,
                show_raw_transcripts=True,
                show_system_prompts=False
            )
            
        elif role == ProjectionRole.DEVELOPER:
            return ProjectionCapabilities(
                show_internal_reasoning=True,
                show_scores=True,
                show_risk_flags=True,
                show_raw_transcripts=True,
                show_system_prompts=True
            )
            
        elif role == ProjectionRole.ANALYTICS:
            # Analytics might only care about scores and timelines, not personal PII
            return ProjectionCapabilities(
                show_internal_reasoning=False,
                show_scores=True,
                show_risk_flags=True,
                show_raw_transcripts=False,
                show_system_prompts=False
            )
            
        elif role == ProjectionRole.TELEMETRY:
            # Telemetry only cares about timings and latency, never data
            return ProjectionCapabilities(
                show_internal_reasoning=False,
                show_scores=False,
                show_risk_flags=False,
                show_raw_transcripts=False,
                show_system_prompts=False
            )
            
        # Default restrictive policy
        return ProjectionCapabilities()
