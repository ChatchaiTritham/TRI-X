"""
Unit tests for Triage module.
"""

import pytest
from trix import TriageModule, RiskLevel

class TestTriageModule:
 """Test cases for TriageModule"""

 def setup_method(self):
 """Setup test fixtures"""
 self.triage = TriageModule(threshold=0.7)

 def test_initialization(self):
 """Test module initialization"""
 assert self.triage.threshold == 0.7
 assert self.triage.risk_thresholds[RiskLevel.CRITICAL] == 0.9

 def test_low_risk_assessment(self):
 """Test low risk classification"""
 input_data = {
 "features": {
 "urgency": 0.2,
 "severity": 0.15,
 "complexity": 0.1
 }
 }

 result = self.triage.assess(input_data)

 assert result.risk_level in [RiskLevel.MINIMAL, RiskLevel.LOW]
 assert result.risk_score < 0.5

 def test_high_risk_assessment(self):
 """Test high risk classification"""
 input_data = {
 "features": {
 "urgency": 0.95,
 "severity": 0.88,
 "complexity": 0.85
 }
 }

 result = self.triage.assess(input_data)

 assert result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
 assert result.risk_score > 0.7

 def test_feature_weights(self):
 """Test custom feature weights"""
 triage_weighted = TriageModule(
 threshold=0.7,
 feature_weights={'urgency': 2.0, 'severity': 1.0}
 )

 input_data = {
 "features": {
 "urgency": 0.8,
 "severity": 0.3
 }
 }

 result = triage_weighted.assess(input_data)

 assert result.risk_score > 0
 assert "urgency" in result.features
 assert "severity" in result.features

 def test_empty_features(self):
 """Test handling of empty features"""
 input_data = {"features": {}}

 result = self.triage.assess(input_data)

 assert result.risk_score == 0.0
 assert result.risk_level == RiskLevel.MINIMAL

 def test_batch_assessment(self):
 """Test batch processing"""
 inputs = [
 {"features": {"urgency": 0.2}},
 {"features": {"urgency": 0.5}},
 {"features": {"urgency": 0.9}},
 ]

 results = self.triage.batch_assess(inputs)

 assert len(results) == 3
 assert all(hasattr(r, 'risk_level') for r in results)

 def test_threshold_update(self):
 """Test threshold modification"""
 new_thresholds = {
 RiskLevel.HIGH: 0.8,
 RiskLevel.CRITICAL: 0.95
 }

 self.triage.update_thresholds(new_thresholds)

 assert self.triage.risk_thresholds[RiskLevel.HIGH] == 0.8
 assert self.triage.risk_thresholds[RiskLevel.CRITICAL] == 0.95

if __name__ == "__main__":
 pytest.main([__file__, "-v"])
