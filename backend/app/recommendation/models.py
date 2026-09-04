from dataclasses import dataclass

@dataclass
class RecommendationItem:
    type: str
    id: int
    name: str
    reason: str
    score: float
    price: str | None = None
