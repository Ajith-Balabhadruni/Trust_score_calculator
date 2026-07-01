from datetime import datetime, timezone
from dataclasses import asdict
import hashlib
import json

from models import (
    AuditEvent,
    EvidencePack,
    TrustResult
)
class TrustScoreCalculator:
    SCORE_COUNT = 6
    def calculate(self,scores: list[float],weights: list[float]) -> TrustResult:
        self._validate(scores, weights)
        original_weight_sum = sum(weights)
        normalized_weights, was_normalized = (self._normalize_weights(weights))
        weighted_score = self._calculate_score(scores,normalized_weights)
        risk_level = self._determine_risk(weighted_score)
        evidence_pack = self._build_evidence_pack(
            scores=scores,
            original_weights=weights,
            normalized_weights=normalized_weights,
            original_weight_sum=original_weight_sum,
            weights_normalized=was_normalized,
            weighted_score=weighted_score,
            risk_level=risk_level
        )
        evidence_dict = asdict(evidence_pack)
        sha256_hash = self._generate_hash(evidence_dict)
        return TrustResult(weighted_score=round(weighted_score,2),
            risk_level=risk_level,
            evidence_json=evidence_dict,
            sha256_hash=sha256_hash
        )
    def _validate(self,scores,weights):
        if len(scores) != self.SCORE_COUNT:
            raise ValueError(
                "Exactly 6 scores required"
            )
        if len(weights) != self.SCORE_COUNT:
            raise ValueError(
                "Exactly 6 weights required"
            )
        if sum(weights) == 0:
            raise ValueError(
                "Weight sum cannot be zero"
            )
        for score in scores:
            if not (0 <= score <= 100):
                raise ValueError(
                    "Scores must be between 0 and 100"
                )
        for weight in weights:
            if weight < 0:
                raise ValueError(
                    "Weights cannot be negative"
                )

    def _normalize_weights(self,weights):
        total = sum(weights)
        was_normalized = (
            abs(total - 1.0) > 1e-9
        )
        normalized_weights = [
            w / total
            for w in weights
        ]
        return (
            normalized_weights,
            was_normalized
        )
    def _calculate_score(self,scores,weights):
        return sum(
            score * weight
            for score, weight
            in zip(scores, weights)
        )
    def _determine_risk(self,score):
        if score >= 85:
            return "LOW"
        if score >= 70:
            return "MEDIUM"
        if score >= 50:
            return "HIGH"
        return "CRITICAL"
    def _build_evidence_pack(self,scores,original_weights,normalized_weights,original_weight_sum,weights_normalized,weighted_score,risk_level):
        timestamp = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )
        audit_events = []
        if weights_normalized:
            audit_events.append(
                AuditEvent(
                    event_type=
                    "WEIGHT_NORMALIZATION",
                    timestamp=timestamp,
                    details={
                        "original_sum":
                            round(
                                original_weight_sum,
                                6
                            ),

                        "normalized_sum":
                            1.0
                    }
                )
            )
        return EvidencePack(
            metadata={
                "timestamp":
                    timestamp,
                "calculator_version":
                    "1.0.0"
            },
            inputs={
                "scores":
                    scores,
                "weights":
                    original_weights
            },
            processing={
                "weights_normalized":
                    weights_normalized,
                "original_weight_sum":
                    round(
                        original_weight_sum,
                        6
                    ),
                "normalized_weights":
                    [
                        round(w, 6)
                        for w
                        in normalized_weights
                    ]
            },
            outputs={
                "weighted_score":
                    round(
                        weighted_score,
                        2
                    ),
                "risk_level":
                    risk_level
            },
            audit_events=
                audit_events
        )
    def _generate_hash(self,evidence):
        serialized = json.dumps(
            evidence,
            sort_keys=True
        ).encode("utf-8")
        return hashlib.sha256(
            serialized
        ).hexdigest()
    def _printing_output(self,result):
        print("Weighted Score:", result.weighted_score)
        print("Risk Level:", result.risk_level)
        print("Evidence JSON:", json.dumps(result.evidence_json, indent=2))
        print("SHA256 Hash:", result.sha256_hash)
if __name__ == "__main__":
    calculator = (
        TrustScoreCalculator()
    )
    result = calculator.calculate(
        scores=[
            90,
            85,
            80,
            88,
            95,
            92
        ],
        weights=[
            0.3,
            0.6,
            0.3,
            0.3,
            0.3,
            9.5
        ]
    )
    calculator._printing_output(result)