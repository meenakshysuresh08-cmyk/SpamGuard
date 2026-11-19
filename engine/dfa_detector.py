"""
DFA-based spam detection module.
Implements a deterministic finite automaton to detect suspicious pattern sequences.
"""

from typing import List, Dict, Any, Set, Optional


class DFA:
    """
    Deterministic Finite Automaton for spam pattern detection.
    
    Token alphabet:
    - LURE: Free/prize/discount/money offer
    - URGENT: Urgent pressure language
    - URL: URL or link reference
    - CREDENTIAL: Request for password/OTP/card/SSN
    - OTHER: Anything else
    """
    
    # Token types
    TOKEN_LURE = "LURE"
    TOKEN_URGENT = "URGENT"
    TOKEN_URL = "URL"
    TOKEN_CREDENTIAL = "CREDENTIAL"
    TOKEN_OTHER = "OTHER"
    
    def __init__(self):
        self.states: Set[str] = {"q0", "q1", "q2", "q3", "q4", "q_dead"}
        self.alphabet: Set[str] = {
            self.TOKEN_LURE, 
            self.TOKEN_URGENT, 
            self.TOKEN_URL, 
            self.TOKEN_CREDENTIAL, 
            self.TOKEN_OTHER
        }
        self.initial_state: str = "q0"
        self.accepting_states: Set[str] = {"q3", "q4"}
        self.dead_state: str = "q_dead"
        
        # Transition function: (current_state, input_token) -> next_state
        self.transitions: Dict[tuple, str] = {
            ("q0", self.TOKEN_LURE): "q1",
            ("q0", self.TOKEN_URGENT): "q2",
            ("q0", self.TOKEN_URL): "q0",
            ("q0", self.TOKEN_CREDENTIAL): "q0",
            ("q0", self.TOKEN_OTHER): "q0",
            
            ("q1", self.TOKEN_LURE): "q1",
            ("q1", self.TOKEN_URGENT): "q2",
            ("q1", self.TOKEN_URL): "q3",
            ("q1", self.TOKEN_CREDENTIAL): "q4",
            ("q1", self.TOKEN_OTHER): "q1",
            
            ("q2", self.TOKEN_LURE): "q2",
            ("q2", self.TOKEN_URGENT): "q2",
            ("q2", self.TOKEN_URL): "q3",
            ("q2", self.TOKEN_CREDENTIAL): "q4",
            ("q2", self.TOKEN_OTHER): "q2",
            
            ("q3", self.TOKEN_LURE): "q3",
            ("q3", self.TOKEN_URGENT): "q3",
            ("q3", self.TOKEN_URL): "q3",
            ("q3", self.TOKEN_CREDENTIAL): "q4",
            ("q3", self.TOKEN_OTHER): "q3",
            
            ("q4", self.TOKEN_LURE): "q4",
            ("q4", self.TOKEN_URGENT): "q4",
            ("q4", self.TOKEN_URL): "q4",
            ("q4", self.TOKEN_CREDENTIAL): "q4",
            ("q4", self.TOKEN_OTHER): "q4",
            
            ("q_dead", self.TOKEN_LURE): "q_dead",
            ("q_dead", self.TOKEN_URGENT): "q_dead",
            ("q_dead", self.TOKEN_URL): "q_dead",
            ("q_dead", self.TOKEN_CREDENTIAL): "q_dead",
            ("q_dead", self.TOKEN_OTHER): "q_dead",
        }
        
        # State descriptions for UI
        self.state_descriptions = {
            "q0": "Start state - waiting for initial lure",
            "q1": "Lure detected - waiting for pressure",
            "q2": "Pressure applied - waiting for link",
            "q3": "Link presented - waiting for credential request",
            "q4": "Credential request detected - SUSPICIOUS SEQUENCE",
            "q_dead": "Dead state - no valid path to acceptance"
        }
    
    def get_transition(self, state: str, token: str) -> str:
        """
        Get the next state for a given state and input token.
        
        Args:
            state: Current state
            token: Input token
            
        Returns:
            Next state
        """
        return self.transitions.get((state, token), self.dead_state)
    
    def step(self, state: str, token: str) -> Dict[str, Any]:
        """
        Perform a single step in the automaton.
        
        Args:
            state: Current state
            token: Input token
            
        Returns:
            Step result with current state, input, next state, and whether it's a valid transition
        """
        next_state = self.get_transition(state, token)
        is_valid = (state, token) in self.transitions
        is_accepting = next_state in self.accepting_states
        is_dead = next_state == self.dead_state
        
        return {
            "current_state": state,
            "input_token": token,
            "next_state": next_state,
            "transition_valid": is_valid,
            "is_accepting": is_accepting,
            "is_dead": is_dead,
            "state_description": self.state_descriptions.get(next_state, "")
        }
    
    def run(self, tokens: List[str]) -> Dict[str, Any]:
        """
        Run the DFA on a sequence of tokens.
        
        Args:
            tokens: List of tokens to process
            
        Returns:
            Full trace of the run including final state and acceptance result
        """
        trace = []
        current_state = self.initial_state
        
        for i, token in enumerate(tokens):
            step_result = self.step(current_state, token)
            step_result["step_number"] = i + 1
            
            trace.append(step_result)
            
            # Update current state
            current_state = step_result["next_state"]
            
            if step_result["is_dead"]:
                # Once in dead state, stay there
                # We continue to add steps for remaining tokens but they all go to dead
                # Actually, we break here since we're already in dead state
                # But we need to add the dead state to the trace
                break
        
        # Check final state
        is_accepted = current_state in self.accepting_states
        
        return {
            "tokens": tokens,
            "trace": trace,
            "final_state": current_state,
            "is_accepted": is_accepted,
            "is_rejected": not is_accepted
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert DFA to a dictionary representation for UI.
        
        Returns:
            DFA definition for visualization
        """
        # Build transition table
        transition_table = []
        for state in sorted(self.states):
            row = {"state": state}
            for token in sorted(self.alphabet):
                next_state = self.get_transition(state, token)
                row[token] = next_state
            transition_table.append(row)
        
        return {
            "states": sorted(list(self.states)),
            "alphabet": sorted(list(self.alphabet)),
            "initial_state": self.initial_state,
            "accepting_states": sorted(list(self.accepting_states)),
            "dead_state": self.dead_state,
            "state_descriptions": self.state_descriptions,
            "transition_table": transition_table
        }


def tokenize(text: str, regex_matches: List[Dict]) -> List[str]:
    """
    Tokenize text into a sequence of formal tokens based on regex matches.
    Extracts tokens in order of occurrence within the text.
    
    Args:
        text: The text to tokenize
        regex_matches: List of matches from regex detector
        
    Returns:
        List of formal alphabet tokens
    """
    import re
    
    pattern_to_token = {
        "free_offer": DFA.TOKEN_LURE,
        "prize_winner": DFA.TOKEN_LURE,
        "discount_offer": DFA.TOKEN_LURE,
        "money_transfer": DFA.TOKEN_LURE,
        "urgent_wording": DFA.TOKEN_URGENT,
        "suspicious_url": DFA.TOKEN_URL,
        "credential_request": DFA.TOKEN_CREDENTIAL,
    }
    
    # Collect all match spans with their assigned token
    occurrences = []
    for match in regex_matches:
        p_name = match.get("pattern_name")
        token_type = pattern_to_token.get(p_name)
        if not token_type:
            continue
        for m_str in match.get("matches", []):
            if not isinstance(m_str, str) or not m_str.strip():
                continue
            for m in re.finditer(re.escape(m_str), text, re.IGNORECASE):
                occurrences.append((m.start(), m.end(), token_type))
    
    if not occurrences:
        return [DFA.TOKEN_OTHER]
    
    # Sort by start position (longest match first on collision)
    occurrences.sort(key=lambda x: (x[0], -(x[1] - x[0])))
    
    # Filter overlapping matches to build pure token stream
    tokens = []
    last_end = 0
    for start, end, token in occurrences:
        if start >= last_end:
            tokens.append(token)
            last_end = end
    
    return tokens if tokens else [DFA.TOKEN_OTHER]


# Global DFA instance
_dfa_instance: Optional[DFA] = None


def get_dfa() -> DFA:
    """Get or create the global DFA instance."""
    global _dfa_instance
    if _dfa_instance is None:
        _dfa_instance = DFA()
    return _dfa_instance


def analyze_with_dfa(text: str, regex_matches: List[Dict]) -> Dict[str, Any]:
    """
    Analyze text using DFA on tokenized regex matches.
    
    Args:
        text: The email text to analyze
        regex_matches: List of matches from regex detector
        
    Returns:
        DFA analysis results
    """
    dfa = get_dfa()
    tokens = tokenize(text, regex_matches)
    result = dfa.run(tokens)
    
    return {
        "tokens": tokens,
        "trace": result["trace"],
        "final_state": result["final_state"],
        "is_accepted": result["is_accepted"],
        "is_rejected": result["is_rejected"],
        "dfa_config": dfa.to_dict()
    }
