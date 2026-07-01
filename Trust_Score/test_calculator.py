import pytest
import json
from calculator import (
    TrustScoreCalculator
)

def create_calculator():
    return TrustScoreCalculator()
def test_weighted_score():
    calc = create_calculator()
    result = calc.calculate([100] * 6,[1/6] * 6)
    assert (result.weighted_score== 100)
def test_auto_normalization():
    calc = create_calculator()
    result = calc.calculate([100] * 6,[2] * 6)
    assert (result.weighted_score== 100)
def test_invalid_score_count():
    calc = create_calculator()
    with pytest.raises(ValueError):
        calc.calculate([10, 20],[0.5, 0.5]) 
        print(ValueError) 
def test_invalid_weight_count():
    calc = create_calculator()
    with pytest.raises(ValueError):
        calc.calculate([10] * 6,[1])
        print(ValueError)
def test_risk_level():
    calc = create_calculator()
    result = calc.calculate([90] * 6,[1/6] * 6)
    assert (result.risk_level== "LOW")
def test_hash_consistency():
    calc = create_calculator()
    result = calc.calculate([80] * 6,[1/6] * 6)
    hash1 = result.sha256_hash
    hash2 = calc._generate_hash(result.evidence_json)
    assert hash1 == hash2
def test_weightexceeds1():
    calc=create_calculator()
    result=calc.calculate([59,73,85,97,10,20],[1.5,6.5,8.8,9.5,10.3,12.5])
    assert (result.weighted_score==52.66)

