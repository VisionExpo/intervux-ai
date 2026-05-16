class IntervuxSystemError(Exception):
    severity = "ERROR"
    retryable = False
    
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)

class GeminiQuotaExceeded(IntervuxSystemError):
    severity = "DEGRADED"
    retryable = False

class ResumeParseFailure(IntervuxSystemError):
    severity = "RECOVERABLE"
    retryable = True

class RedisHydrationMismatch(IntervuxSystemError):
    severity = "FATAL"
    retryable = False

class SequenceDesync(IntervuxSystemError):
    severity = "FATAL"
    retryable = False

class StaleSocketSend(IntervuxSystemError):
    severity = "INFO"
    retryable = False

class TaskCancellationFailure(IntervuxSystemError):
    severity = "WARNING"
    retryable = False
