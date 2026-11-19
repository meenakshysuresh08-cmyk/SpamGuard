"""
Spam scoring module.
Combines regex and DFA detection results into a heuristic risk score.
"""

from typing import List, Dict, Any


# Weight constants for scoring
WEIGHTS = {
    "suspicious_url": 15,
    "free_offer": 20,
    "prize_winner": 25,
    "urgent_wording": 20,
    "discount_offer": 15,
    "credential_request": 30,
    "money_transfer": 20,
    "guarantee_words": 15,
}

# DFA contribution weights
DFA_WEIGHTS = {
    "accepted": 30,  # Full suspicious sequence detected
    "partial": 15,   # Partial sequence detected
    "rejected": 0,   # No suspicious sequence
}

# Thresholds for classification
THRESHOLDS = {
    "legitimate": 30,  # Score < 30
    "suspicious": 60,  # 30 <= score < 60
    "spam": 60,        # Score >= 60
}


def calculate_risk_score(regex_matches: List[Dict], dfa_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate a heuristic risk score based on regex matches and DFA analysis.
    
    Args:
        regex_matches: List of matches from regex detector
        dfa_result: Result from DFA analysis
        
    Returns:
        Dictionary with score breakdown and classification
    """
    # Calculate regex-based score
    regex_score = 0
    contributions = []
    
    for match in regex_matches:
        pattern_name = match["pattern_name"]
        weight = WEIGHTS.get(pattern_name, 0)
        match_count = match["match_count"]
        
        # Apply diminishing returns for multiple matches of same type
        # First match receives full weight; additional occurrences add fractional weight
        effective_weight = weight + min(weight * 0.5, (match_count - 1) * (weight * 0.2)) if match_count > 1 else weight
        
        contributions.append({
            "pattern": pattern_name,
            "description": match["pattern_description"],
            "count": match_count,
            "score": round(effective_weight, 1),
            "sample_matches": match["matches"][:3]  # Show up to 3 samples
        })
        
        regex_score += effective_weight
    
    # Calculate DFA score
    dfa_score = 0
    dfa_status = "not_analyzed"
    
    if dfa_result:
        if dfa_result.get("is_accepted"):
            dfa_score = DFA_WEIGHTS["accepted"]
            dfa_status = "accepted"
        elif dfa_result.get("trace"):
            # Check if any state in trace is an accepting state
            for step in dfa_result["trace"]:
                if step.get("is_accepting"):
                    dfa_score = DFA_WEIGHTS["partial"]
                    dfa_status = "partial"
                    break
            if dfa_status == "not_analyzed":
                dfa_score = DFA_WEIGHTS["rejected"]
                dfa_status = "rejected"
        else:
            dfa_score = DFA_WEIGHTS["rejected"]
            dfa_status = "rejected"
    
    # Combine scores (capped at 100)
    total_score = min(100, round(regex_score + dfa_score, 1))
    
    # Classify
    if total_score < THRESHOLDS["legitimate"]:
        classification = "Legitimate"
        explanation = "This email appears to be legitimate. No significant spam indicators detected."
    elif total_score < THRESHOLDS["suspicious"]:
        classification = "Suspicious"
        explanation = "This email has some suspicious characteristics but isn't definitively spam. Exercise caution."
    else:
        classification = "Spam"
        explanation = "This email shows multiple strong indicators of being spam. Do not interact with links or provide personal information."
    
    return {
        "heuristic_risk_score": total_score,
        "classification": classification,
        "explanation": explanation,
        "regex_score": round(regex_score, 1),
        "dfa_score": dfa_score,
        "contributions": contributions,
        "dfa_status": dfa_status,
        "thresholds": THRESHOLDS
    }


def get_classification(score: float) -> str:
    """
    Get classification based on score.
    
    Args:
        score: Heuristic risk score (0-100)
        
    Returns:
        Classification string: "Legitimate", "Suspicious", or "Spam"
    """
    if score < THRESHOLDS["legitimate"]:
        return "Legitimate"
    elif score < THRESHOLDS["suspicious"]:
        return "Suspicious"
    else:
        return "Spam"


def explain_classification(score: float, contributions: List[Dict], dfa_status: str) -> str:
    """
    Generate plain-language explanation for classification.
    
    Args:
        score: Heuristic risk score
        contributions: List of regex match contributions
        dfa_status: DFA analysis result
        
    Returns:
        Human-readable explanation
    """
    classification = get_classification(score)
    
    explanations = {
        "Legitimate": {
            "header": "This email appears to be legitimate.",
            "reasons": [
                "No significant spam indicators found",
                "Content appears normal and professional"
            ]
        },
        "Suspicious": {
            "header": "This email has some suspicious characteristics.",
            "reasons": [
                "Contains some spam-like indicators",
                "May be legitimate but warrants caution"
            ]
        },
        "Spam": {
            "header": "This email shows strong spam indicators.",
            "reasons": [
                "Contains multiple spam indicators",
                "May contain phishing or scam attempts"
            ]
        }
    }
    
    result = explanations.get(classification, explanations["Legitimate"])
    
    # Add specific reasons based on contributions
    if contributions:
        patterns_found = [c["pattern"] for c in contributions]
        result["reasons"].append(f"Detected patterns: {', '.join(patterns_found)}")
    
    if dfa_status == "accepted":
        result["reasons"].append("Suspicious sequence pattern detected (LURE -> URGENT -> URL -> CREDENTIAL)")
    elif dfa_status == "partial":
        result["reasons"].append("Partial suspicious sequence detected")
    
    return result
