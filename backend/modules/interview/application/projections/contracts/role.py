from enum import Enum

class ProjectionRole(Enum):
    """
    Defines the persona or system requesting the projection.
    """
    CANDIDATE = "Candidate"
    RECRUITER = "Recruiter"
    DEVELOPER = "Developer"
    ANALYTICS = "Analytics"
    TELEMETRY = "Telemetry"
