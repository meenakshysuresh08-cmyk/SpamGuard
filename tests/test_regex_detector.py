"""
Tests for regex_detector module.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.regex_detector import RegexDetector


def test_regex_detector_initialization():
    """Test that RegexDetector initializes correctly."""
    detector = RegexDetector()
    assert detector is not None
    assert len(detector.patterns) > 0


def test_detect_free_offer():
    """Test detection of free offer patterns."""
    detector = RegexDetector()
    text = "Get your free gift now!"
    matches = detector.detect(text)
    
    assert len(matches) > 0
    assert any(m['pattern_name'] == 'free_offer' for m in matches)


def test_detect_prize_winner():
    """Test detection of prize/winner patterns."""
    detector = RegexDetector()
    text = "You are a WINNER! Claim your prize now!"
    matches = detector.detect(text)
    
    assert len(matches) > 0
    assert any(m['pattern_name'] == 'prize_winner' for m in matches)


def test_detect_urgent_wording():
    """Test detection of urgent wording patterns."""
    detector = RegexDetector()
    text = "URGENT: Action required immediately!"
    matches = detector.detect(text)
    
    assert len(matches) > 0
    assert any(m['pattern_name'] == 'urgent_wording' for m in matches)


def test_detect_suspicious_url():
    """Test detection of suspicious URL patterns."""
    detector = RegexDetector()
    text = "Click here: https://example.xyz/secure"
    matches = detector.detect(text)
    
    assert len(matches) > 0
    assert any(m['pattern_name'] == 'suspicious_url' for m in matches)


def test_detect_credential_request():
    """Test detection of credential request patterns."""
    detector = RegexDetector()
    text = "Please enter your password and OTP"
    matches = detector.detect(text)
    
    assert len(matches) > 0
    assert any(m['pattern_name'] == 'credential_request' for m in matches)


def test_detect_discount_offer():
    """Test detection of discount offer patterns."""
    detector = RegexDetector()
    text = "50% discount on all items!"
    matches = detector.detect(text)
    
    assert len(matches) > 0
    assert any(m['pattern_name'] == 'discount_offer' for m in matches)


def test_detect_money_transfer():
    """Test detection of money transfer patterns."""
    detector = RegexDetector()
    text = "Send money via Western Union"
    matches = detector.detect(text)
    
    # Western Union matches money_transfer pattern (case insensitive)
    assert len(matches) > 0
    assert any(m['pattern_name'] == 'money_transfer' for m in matches)
    # Verify the match contains "Western Union"
    mt_match = next((m for m in matches if m['pattern_name'] == 'money_transfer'), None)
    assert mt_match is not None
    assert any("Western Union" in m for m in mt_match['matches'])


def test_detect_guarantee_words():
    """Test detection of guarantee word patterns."""
    detector = RegexDetector()
    text = "100% guaranteed money-back offer"
    matches = detector.detect(text)
    
    assert len(matches) > 0
    assert any(m['pattern_name'] == 'guarantee_words' for m in matches)


def test_no_matches_for_legitimate_text():
    """Test that legitimate text doesn't trigger false positives."""
    detector = RegexDetector()
    text = "Let's schedule a meeting for next week."
    matches = detector.detect(text)
    
    # Should have few or no matches for legitimate text
    match_count = sum(m['match_count'] for m in matches)
    assert match_count < 3  # Allow some minor matches


def test_multiple_matches_same_pattern():
    """Test detection of multiple matches for same pattern."""
    detector = RegexDetector()
    text = "Free offer! Another free gift! Third free item!"
    matches = detector.detect(text)
    
    free_match = next((m for m in matches if m['pattern_name'] == 'free_offer'), None)
    assert free_match is not None
    assert free_match['match_count'] >= 2


def test_pattern_weights():
    """Test that pattern weights are properly defined."""
    detector = RegexDetector()
    
    assert detector.patterns['suspicious_url']['weight'] == 15
    assert detector.patterns['credential_request']['weight'] == 30
    assert detector.patterns['prize_winner']['weight'] == 25


def test_empty_text():
    """Test handling of empty text."""
    detector = RegexDetector()
    matches = detector.detect("")
    
    assert matches == []


def test_none_text():
    """Test handling of None text."""
    detector = RegexDetector()
    matches = detector.detect(None)
    
    assert matches == []


def test_detect_real_world_phishing_elements():
    """Test detection of real-world phishing elements (capitalized PIN, Social Security, locked account)."""
    detector = RegexDetector()
    text = "Your account has been locked. Unlock your profile with: Check Card number and PIN. Social Security Number, Account #."
    matches = detector.detect(text)
    
    pattern_names = [m['pattern_name'] for m in matches]
    assert 'credential_request' in pattern_names
    assert 'urgent_wording' in pattern_names


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
