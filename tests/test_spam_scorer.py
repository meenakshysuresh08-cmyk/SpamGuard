"""
Tests for spam_scorer module.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.spam_scorer import calculate_risk_score, get_classification, explain_classification


def test_legitimate_score():
    """Test classification for low scores."""
    regex_matches = []
    dfa_result = {"is_accepted": False}
    
    result = calculate_risk_score(regex_matches, dfa_result)
    
    assert result["heuristic_risk_score"] < 30
    assert result["classification"] == "Legitimate"


def test_suspicious_score():
    """Test classification for medium scores."""
    # Multiple patterns needed to reach suspicious threshold
    regex_matches = [
        {
            "pattern_name": "suspicious_url",
            "pattern_description": "Suspicious URLs",
            "weight": 15,
            "matches": ["https://suspicious.com"],
            "match_count": 1
        },
        {
            "pattern_name": "urgent_wording",
            "pattern_description": "Urgent wording",
            "weight": 20,
            "matches": ["urgent"],
            "match_count": 1
        }
    ]
    dfa_result = {"is_accepted": False}
    
    result = calculate_risk_score(regex_matches, dfa_result)
    
    assert 30 <= result["heuristic_risk_score"] < 60
    assert result["classification"] == "Suspicious"


def test_spam_score():
    """Test classification for high scores."""
    regex_matches = [
        {
            "pattern_name": "credential_request",
            "pattern_description": "Credential requests",
            "weight": 30,
            "matches": ["password", "OTP"],
            "match_count": 2
        },
        {
            "pattern_name": "prize_winner",
            "pattern_description": "Prize notifications",
            "weight": 25,
            "matches": ["winner"],
            "match_count": 1
        }
    ]
    dfa_result = {"is_accepted": True}
    
    result = calculate_risk_score(regex_matches, dfa_result)
    
    assert result["heuristic_risk_score"] >= 60
    assert result["classification"] == "Spam"


def test_score_capped_at_100():
    """Test that score is capped at 100."""
    regex_matches = [
        {
            "pattern_name": "credential_request",
            "pattern_description": "Credential requests",
            "weight": 30,
            "matches": ["password"],
            "match_count": 5
        }
    ] * 5  # Many matches
    dfa_result = {"is_accepted": True}
    
    result = calculate_risk_score(regex_matches, dfa_result)
    
    assert result["heuristic_risk_score"] <= 100


def test_dfa_accepted_contribution():
    """Test DFA accepted result adds points."""
    regex_matches = []
    dfa_result = {"is_accepted": True}
    
    result = calculate_risk_score(regex_matches, dfa_result)
    
    assert result["dfa_score"] == 30  # DFA_WEIGHTS["accepted"]
    assert result["dfa_status"] == "accepted"


def test_dfa_rejected_contribution():
    """Test DFA rejected result adds no points."""
    regex_matches = []
    dfa_result = {"is_accepted": False}
    
    result = calculate_risk_score(regex_matches, dfa_result)
    
    assert result["dfa_score"] == 0
    assert result["dfa_status"] == "rejected"


def test_contributions_structure():
    """Test contributions have expected structure."""
    regex_matches = [
        {
            "pattern_name": "suspicious_url",
            "pattern_description": "Suspicious URLs",
            "weight": 15,
            "matches": ["https://test.com"],
            "match_count": 1
        }
    ]
    dfa_result = {"is_accepted": False}
    
    result = calculate_risk_score(regex_matches, dfa_result)
    
    assert "contributions" in result
    assert len(result["contributions"]) > 0
    
    contribution = result["contributions"][0]
    assert "pattern" in contribution
    assert "description" in contribution
    assert "count" in contribution
    assert "score" in contribution


def test_explanation_structure():
    """Test explanation has expected structure."""
    regex_matches = []
    dfa_result = {"is_accepted": False}
    
    result = calculate_risk_score(regex_matches, dfa_result)
    
    explanation = explain_classification(
        result["heuristic_risk_score"],
        result["contributions"],
        result["dfa_status"]
    )
    
    assert "header" in explanation
    assert "reasons" in explanation


def test_thresholds():
    """Test threshold values."""
    from engine.spam_scorer import THRESHOLDS
    
    assert THRESHOLDS["legitimate"] == 30
    assert THRESHOLDS["suspicious"] == 60


def test_empty_regex_matches():
    """Test handling of empty regex matches."""
    regex_matches = []
    dfa_result = {"is_accepted": False}
    
    result = calculate_risk_score(regex_matches, dfa_result)
    
    assert result["heuristic_risk_score"] == 0
    assert result["regex_score"] == 0


def test_get_classification():
    """Test get_classification function."""
    from engine.spam_scorer import get_classification
    
    assert get_classification(0) == "Legitimate"
    assert get_classification(29) == "Legitimate"
    assert get_classification(30) == "Suspicious"
    assert get_classification(59) == "Suspicious"
    assert get_classification(60) == "Spam"
    assert get_classification(100) == "Spam"


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
