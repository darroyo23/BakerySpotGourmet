from dataclasses import dataclass
from uuid import UUID


@dataclass
class LimitRule:
    """
    LimitRule domain entity.
    Defines constraints on orders or products (e.g., max items per order).
    """
    id: UUID
    rule_type: str
    value: float
    scope: str
    is_active: bool = True
