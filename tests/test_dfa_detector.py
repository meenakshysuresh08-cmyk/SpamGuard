"""
Tests for dfa_detector module.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.dfa_detector import DFA, tokenize, analyze_with_dfa


def test_dfa_initialization():
    """Test DFA initialization."""
    dfa = DFA()
    
    assert dfa.states == {"q0", "q1", "q2", "q3", "q4", "q_dead"}
    assert dfa.alphabet == {"LURE", "URGENT", "URL", "CREDENTIAL", "OTHER"}
    assert dfa.initial_state == "q0"
    assert dfa.accepting_states == {"q3", "q4"}


def test_dfa_transition_from_q0():
    """Test transitions from initial state."""
    dfa = DFA()
    
    # From q0, LURE should go to q1
    assert dfa.get_transition("q0", "LURE") == "q1"
    
    # From q0, OTHER should stay at q0
    assert dfa.get_transition("q0", "OTHER") == "q0"
    
    # From q0, invalid token should go to dead state
    assert dfa.get_transition("q0", "INVALID") == "q_dead"


def test_dfa_lure_urgent_url_credential_sequence():
    """Test the suspicious sequence: LURE -> URGENT -> URL -> CREDENTIAL."""
    dfa = DFA()
    tokens = ["LURE", "URGENT", "URL", "CREDENTIAL"]
    result = dfa.run(tokens)
    
    # Should be accepted (q4 is accepting)
    assert result["is_accepted"] is True
    assert result["final_state"] == "q4"
    
    # Should have 4 steps
    assert len(result["trace"]) == 4


def test_dfa_partial_sequence():
    """Test partial suspicious sequence."""
    dfa = DFA()
    tokens = ["LURE", "URGENT", "URL"]
    result = dfa.run(tokens)
    
    # Should be accepted (q3 is accepting)
    assert result["is_accepted"] is True
    assert result["final_state"] == "q3"


def test_dfa_rejected_sequence():
    """Test sequence that should be rejected."""
    dfa = DFA()
    tokens = ["OTHER", "OTHER", "URL"]
    result = dfa.run(tokens)
    
    # Should be rejected (ends at q0, not accepting)
    assert result["is_accepted"] is False


def test_dfa_invalid_token():
    """Test handling of invalid tokens - they should go to dead state."""
    dfa = DFA()
    # Test that invalid tokens from any state go to dead state
    result = dfa.run(["LURE", "INVALID"])
    
    # After invalid token from q1, goes to dead state
    assert result["final_state"] == "q_dead"


def test_dfa_to_dict():
    """Test DFA to_dict() method."""
    dfa = DFA()
    config = dfa.to_dict()
    
    assert "states" in config
    assert "alphabet" in config
    assert "initial_state" in config
    assert "accepting_states" in config
    assert "transition_table" in config


def test_dfa_state_descriptions():
    """Test state descriptions are available."""
    dfa = DFA()
    config = dfa.to_dict()
    
    assert "state_descriptions" in config
    assert "q0" in config["state_descriptions"]
    assert "q_dead" in config["state_descriptions"]


def test_dfa_step_method():
    """Test step() method returns correct structure."""
    dfa = DFA()
    
    result = dfa.step("q0", "LURE")
    
    assert "current_state" in result
    assert "input_token" in result
    assert "next_state" in result
    assert "transition_valid" in result
    assert result["current_state"] == "q0"
    assert result["next_state"] == "q1"


def test_dfa_run_trace():
    """Test that run() returns complete trace."""
    dfa = DFA()
    tokens = ["LURE", "URGENT"]
    result = dfa.run(tokens)
    
    assert "trace" in result
    assert len(result["trace"]) == 2
    
    first_step = result["trace"][0]
    assert "step_number" in first_step
    assert first_step["step_number"] == 1


def test_tokenize_with_matches():
    """Test tokenization with regex matches."""
    dfa = DFA()
    text = "Free offer! Click here: https://test.com"
    regex_matches = [
        {"pattern_name": "free_offer", "matches": ["Free"], "match_count": 1},
        {"pattern_name": "suspicious_url", "matches": ["https://test.com"], "match_count": 1}
    ]
    tokens = tokenize(text, regex_matches)
    
    # Should have at least 2 tokens
    assert len(tokens) >= 2


def test_analyze_with_dfa():
    """Test complete DFA analysis function."""
    text = "Free prize! Click now for urgent offer. https://test.com"
    regex_matches = [
        {"pattern_name": "prize_winner", "matches": ["prize"], "match_count": 1},
        {"pattern_name": "urgent_wording", "matches": ["urgent"], "match_count": 1},
        {"pattern_name": "suspicious_url", "matches": ["https://test.com"], "match_count": 1}
    ]
    
    result = analyze_with_dfa(text, regex_matches)
    
    assert "tokens" in result
    assert "trace" in result
    assert "is_accepted" in result
    assert "is_rejected" in result


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
