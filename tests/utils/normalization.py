"""
Shared utilities for normalizing test payloads to ensure deterministic assertions.
"""

from typing import Any, Dict

def normalize_metrics_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize volatile fields in a metrics payload for equality assertions.
    
    Args:
        payload: The metrics dictionary to normalize
        
    Returns:
        The normalized dictionary
    """
    normalized = payload.copy()
    
    # Normalize timestamp
    if "timestamp" in normalized:
        normalized["timestamp"] = "normalized-timestamp"
        
    # Recursive normalization for nested dicts if needed
    if "derived" in normalized and isinstance(normalized["derived"], dict):
        # We could normalize derived values too if they contain random data
        pass
        
    return normalized
