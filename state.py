import enum

class AgentState(enum.Enum):
    OFFLINE = 1
    IDLE = 2
    ENGAGED = 3

class LeadState(enum.Enum):
    AVAILABLE = 1
    QUEUED = 2
    STARTED = 3
    FAILED = 4
    ENDED = 5
    ABANDONED = 6
