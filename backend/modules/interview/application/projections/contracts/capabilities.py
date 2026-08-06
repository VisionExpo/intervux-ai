from dataclasses import dataclass

@dataclass(frozen=True)
class ProjectionCapabilities:
    """
    Flat boolean flags indicating what the projection is allowed to include.
    Resolved by the PolicyResolver based on the requester's role.
    """
    show_internal_reasoning: bool = False
    show_scores: bool = False
    show_risk_flags: bool = False
    show_raw_transcripts: bool = False
    show_system_prompts: bool = False
