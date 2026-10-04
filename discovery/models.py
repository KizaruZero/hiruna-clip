from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class TranscriptSegment:
    id: str
    start: str
    end: str
    text: str
    def to_dict(self): return asdict(self)

@dataclass
class AudioEvent:
    timestamp: str
    type: str
    strength: float
    def to_dict(self) -> dict[str, Any]: return asdict(self)
