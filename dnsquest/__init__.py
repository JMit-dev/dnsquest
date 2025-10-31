"""DNSQuest - An iterative DNS resolver"""

from .resolver import (
    DNSQuestResolver,
    DNSResolutionError,
    NXDomainError,
    TimeoutError,
    NoRecordError,
)

__version__ = "1.0.0"
__all__ = [
    "DNSQuestResolver",
    "DNSResolutionError",
    "NXDomainError",
    "TimeoutError",
    "NoRecordError",
]
