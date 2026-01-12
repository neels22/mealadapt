from enum import Enum

class GateDecision(str, Enum):
    ALLOW = "ALLOW"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
