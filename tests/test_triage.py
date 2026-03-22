"""Unit tests for the TRI-X triage module."""

import pytest

from trix import RiskLevel, TriageModule


class TestTriageModule:
    """Test cases for ``TriageModule``."""

    def setup_method(self) -> None:
        self.triage = TriageModule(threshold=0.7)

    def test_initialization(self) -> None:
        assert self.triage.threshold == 0.7
        assert self.triage.risk_thresholds[RiskLevel.CRITICAL] == 0.9

    def test_low_risk_assessment(self) -> None:
        input_data = {
            "features": {
                "urgency": 0.2,
                "severity": 0.15,
                "complexity": 0.1,
            }
        }

        result = self.triage.assess(input_data)
        assert result.risk_level in [RiskLevel.MINIMAL, RiskLevel.LOW]
        assert result.risk_score < 0.5

    def test_high_risk_assessment(self) -> None:
        input_data = {
            "features": {
                "urgency": 0.95,
                "severity": 0.88,
                "complexity": 0.85,
            }
        }

        result = self.triage.assess(input_data)
        assert result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert result.risk_score > 0.7

    def test_feature_weights(self) -> None:
        weighted_triage = TriageModule(
            threshold=0.7,
            feature_weights={"urgency": 2.0, "severity": 1.0},
        )
        input_data = {"features": {"urgency": 0.8, "severity": 0.3}}

        result = weighted_triage.assess(input_data)
        assert result.risk_score > 0
        assert "urgency" in result.features
        assert "severity" in result.features

    def test_empty_features(self) -> None:
        result = self.triage.assess({"features": {}})
        assert result.risk_score == 0.0
        assert result.risk_level == RiskLevel.MINIMAL

    def test_batch_assessment(self) -> None:
        inputs = [
            {"features": {"urgency": 0.2}},
            {"features": {"urgency": 0.5}},
            {"features": {"urgency": 0.9}},
        ]

        results = self.triage.batch_assess(inputs)
        assert len(results) == 3
        assert all(hasattr(result, "risk_level") for result in results)

    def test_threshold_update(self) -> None:
        new_thresholds = {
            RiskLevel.HIGH: 0.8,
            RiskLevel.CRITICAL: 0.95,
        }

        self.triage.update_thresholds(new_thresholds)
        assert self.triage.risk_thresholds[RiskLevel.HIGH] == 0.8
        assert self.triage.risk_thresholds[RiskLevel.CRITICAL] == 0.95


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
