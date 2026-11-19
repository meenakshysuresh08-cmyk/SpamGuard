"""
Main analyzer module.
Orchestrates regex detection, DFA analysis, and scoring.
"""

from typing import Dict, Any, List, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.regex_detector import RegexDetector
from engine.dfa_detector import analyze_with_dfa, tokenize, DFA
from engine.spam_scorer import calculate_risk_score, explain_classification


class EmailAnalyzer:
    """Main email analyzer class."""
    
    def __init__(self):
        self.regex_detector = RegexDetector()
        self.dfa = DFA()
    
    def analyze(self, subject: str, body: str) -> Dict[str, Any]:
        """
        Analyze an email for spam.
        
        Args:
            subject: Email subject
            body: Email body content
            
        Returns:
            Complete analysis results
        """
        # Combine subject and body for analysis
        full_text = f"{subject}\n\n{body}"
        
        if not full_text.strip():
            return {
                "error": "No content to analyze",
                "classification": "Unknown",
                "score": 0
            }
        
        # Step 1: Regex detection
        regex_matches = self.regex_detector.detect(full_text)
        
        # Step 2: DFA analysis
        dfa_result = analyze_with_dfa(full_text, regex_matches)
        
        # Step 3: Calculate score
        score_result = calculate_risk_score(regex_matches, dfa_result)
        
        # Build explanation
        explanation = explain_classification(
            score_result["heuristic_risk_score"],
            score_result["contributions"],
            score_result["dfa_status"]
        )
        
        return {
            "subject": subject,
            "body_snippet": body[:200] + "..." if len(body) > 200 else body,
            "classification": score_result["classification"],
            "heuristic_risk_score": score_result["heuristic_risk_score"],
            "explanation": explanation,
            "regex_matches": regex_matches,
            "dfa_result": dfa_result,
            "score_breakdown": score_result,
            "tokens": dfa_result.get("tokens", []),
            "total_characters": len(full_text),
            "total_words": len(full_text.split())
        }
    
    def analyze_token_sequence(self, tokens: List[str]) -> Dict[str, Any]:
        """
        Analyze a token sequence using DFA.
        
        Args:
            tokens: List of tokens
            
        Returns:
            DFA trace and result
        """
        result = self.dfa.run(tokens)
        return {
            "tokens": tokens,
            "trace": result["trace"],
            "final_state": result["final_state"],
            "is_accepted": result["is_accepted"],
            "is_rejected": result["is_rejected"]
        }
    
    def get_dfa_config(self) -> Dict[str, Any]:
        """Get DFA configuration for visualization."""
        return self.dfa.to_dict()
