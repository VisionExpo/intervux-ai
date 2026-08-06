import asyncio
import json
from typing import Any, Callable, Dict, Awaitable
from backend.modules.interview.application.projections.contracts.delivery import ProjectionDelivery
from backend.modules.interview.application.projections.contracts.envelope import ProjectionEnvelope

class WebSocketDelivery(ProjectionDelivery):
    """
    Delivers projection envelopes to an active WebSocket connection.
    Wraps the envelope in a transport-level format.
    """
    
    def __init__(self, async_send_fn: Callable[[str, Dict[str, Any]], Awaitable[None]]):
        """
        async_send_fn is expected to be a function that takes (session_id, payload)
        and sends it over the active WebSocket connection.
        """
        self.async_send_fn = async_send_fn

    def deliver(self, envelope: ProjectionEnvelope) -> None:
        """
        Formats the envelope into a transport message and schedules it for delivery.
        """
        transport_message = {
            "type": "projection",
            "projection": {
                "schema": envelope.schema,
                "schemaVersion": envelope.schema_version,
                "aggregateVersion": envelope.aggregate_version,
                "projectionVersion": envelope.projection_version,
                "payload": envelope.payload
            }
        }
        
        # Extract interview_id to route the message correctly
        session_id = envelope.payload.get("interviewId")
        if not session_id:
            return
            
        # Since deliver() is synchronous (called from DomainEventDispatcher),
        # we schedule the async send on the running event loop.
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.async_send_fn(session_id, transport_message))
        except RuntimeError:
            # If no running loop, we can't send asynchronously.
            # This handles edge cases in pure sync test environments.
            pass
