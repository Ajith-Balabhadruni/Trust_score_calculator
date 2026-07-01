from dataclasses import dataclass, field
from typing import List, Dict
@dataclass
class AuditEvent:
    event_type: str
    timestamp: str
    details: Dict
@dataclass
class EvidencePack:
    metadata: Dict
    inputs: Dict
    processing: Dict
    outputs: Dict
    audit_events: List[AuditEvent] = field(
        default_factory=list
    )
@dataclass
class TrustResult:
    weighted_score: float
    risk_level: str
    evidence_json: Dict
    sha256_hash: str