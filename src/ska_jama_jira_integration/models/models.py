"""
Data Classes
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Requirement:
    requirement_id: str
    jama_url: str
    name: str
    description: Optional[str] = None
    status: Optional[str] = None
    verification_method: Optional[str] = None
    verification_milestones: Optional[str] = None
    rationale: Optional[str] = None
    category: Optional[str] = None
    allocation: Optional[str] = None
    compliance: Optional[str] = None
    tags: Optional[str] = None
    component: Optional[str] = None
