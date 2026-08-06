class DomainException(Exception):
    """Base exception for domain invariant violations."""
    pass


class InvalidStateTransitionException(DomainException):
    """Raised when an interview attempts an invalid state transition."""
    pass


class StaleAggregateVersionException(DomainException):
    """Raised when attempting to save a stale aggregate version (optimistic concurrency)."""
    pass


class InvariantViolationException(DomainException):
    """Raised when a specific business invariant is violated."""
    pass
