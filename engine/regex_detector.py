"""
Regex-based spam detection module.
Implements pattern matching for common spam indicators.
"""

import re
from typing import List, Dict, Any


# Spam indicator patterns with named groups for easy extraction
PATTERNS = {
    "suspicious_url": {
        "regex": r"(?i)(?:https?://[^\s<>\"']+|(?:\b[\w-]+\.)+(?:com|net|org|xyz|top|click|link|ru|cc|me|info|biz|co|uk|de|fr|today|work|live|online|loan)(?:/[\S]*)?|\b(?:click\s+(?:here|the\s+link|below)|follow\s+(?:the\s+)?(?:link|steps)|access\s+url|link\s+removed|url\s+removed|unlock\s+(?:this\s+|your\s+)?profile)\b)",
        "description": "Suspicious URL patterns, action links, and link redirects",
        "weight": 15
    },
    "free_offer": {
        "regex": r"(?i)\b(?:free|free\s+gift|free\s+trial|free\s+access|free\s+download|free\s+entry|100%\s+free|no\s+cost)\b",
        "description": "Free offer promises that are common in spam",
        "weight": 20
    },
    "prize_winner": {
        "regex": r"(?i)\b(?:winner|prize|jackpot|lottery|million|billion|cash\s+prize|claim\s+your\s+prize|reward)\b",
        "description": "Prize and winner notifications, often scams",
        "weight": 25
    },
    "urgent_wording": {
        "regex": r"(?i)\b(?:urgent|immediately|asap|instantly|right\s+now|limited\s+time|act\s+now|don't\s+miss|expires\s+soon|warning|locked|suspension|suspended|failed\s+login|shut\s+down|mandatory|nearest\s+time|compromised|unauthorized\s+access|security\s+alert|effective\s+immediately|temporary\s+suspension|identity\s+theft|within\s+\d+\s*(?:hours?|days?|minutes?|mins?))\b",
        "description": "Urgent language designed to create panic or force immediate action",
        "weight": 20
    },
    "discount_offer": {
        "regex": r"(?i)\b(?:\d+%?\s*(?:off|discount|sale|deal|coupon|promo|save|bargain)|discounted|special\s+offer|limited\s+offer)\b",
        "description": "Discount and promotional language",
        "weight": 15
    },
    "credential_request": {
        "regex": r"(?i)\b(?:password|pin|otp|one-time\s+password|card\s+number|credit\s+card|debit\s+card|atm(?:\/visa)?(?:\s+check)?\s+card|ssn|social\s+security(?:\s+number)?|account\s*(?:#|num|no|number)|banking\s+details|login|log\s*in|userids?|credentials?|verify\s+(?:your\s+)?(?:identity|account|profile)|sign\s*on\s*to\s*internet\s*banking)\b",
        "description": "Requests for sensitive personal information, credentials, or accounts",
        "weight": 30
    },
    "money_transfer": {
        "regex": r"(?i)(?:wire\s+transfer|bank\s+transfer|western\s+union|money\s+gram|pay\s*pal|paypal\s+transfer|cashapp|venmo|money\s+transfer|eft\s+(?:activity|payment|debit)?|payment\s*(?:\([$€£\d.,]+\))?\s*is\s*processing|checking\s+account|one\s+time\s+(?:eft|payment))",
        "description": "References to money transfer methods, EFT payments, or banking activity",
        "weight": 20
    },
    "guarantee_words": {
        "regex": r"(?i)\b(?:guaranteed|100%\s*guaranteed|money-back|satisfaction\s+guaranteed|no\s*risk|risk-free)\b",
        "description": "Over-promising guarantee language",
        "weight": 15
    }
}


class RegexDetector:
    """Detects spam indicators using regular expressions."""
    
    def __init__(self):
        self.patterns = PATTERNS
        self.compiled_patterns = {}
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile all regex patterns for efficiency."""
        for name, config in self.patterns.items():
            self.compiled_patterns[name] = re.compile(config["regex"], re.IGNORECASE)
    
    def detect(self, text: str) -> List[Dict[str, Any]]:
        """
        Scan text for spam indicators.
        
        Args:
            text: The email text to scan
            
        Returns:
            List of matching patterns with details
        """
        if not text:
            return []
            
        matches = []
        
        for name, compiled_regex in self.compiled_patterns.items():
            found = compiled_regex.findall(text)
            if found:
                # Get pattern config
                config = self.patterns[name]
                matches.append({
                    "pattern_name": name,
                    "pattern_description": config["description"],
                    "weight": config["weight"],
                    "matches": found,
                    "match_count": len(found)
                })
        
        return matches
    
    def get_matched_text(self, text: str, pattern_name: str) -> List[str]:
        """
        Extract the actual matched text for a specific pattern.
        
        Args:
            text: The email text to scan
            pattern_name: Name of the pattern to match
            
        Returns:
            List of matched strings
        """
        if pattern_name not in self.compiled_patterns:
            return []
            
        compiled = self.compiled_patterns[pattern_name]
        return compiled.findall(text)
    
    def highlight_matches(self, text: str) -> str:
        """
        Highlight all matches in the text for display.
        
        Args:
            text: The email text to highlight
            
        Returns:
            HTML-safe string with matches wrapped in <mark> tags
        """
        if not text:
            return text
            
        # First escape HTML to prevent XSS
        import html
        safe_text = html.escape(text)
        
        # Build a combined pattern for all matches
        all_patterns = [compiled for compiled in self.compiled_patterns.values()]
        
        # Sort by pattern name length (longer first) to avoid partial matches
        # This is a simplified approach - in production, use a more sophisticated method
        result = safe_text
        
        # Apply highlighting for each pattern
        for name, compiled in self.compiled_patterns.items():
            matches = compiled.findall(text)
            for match in matches:
                # Escape the match for safe replacement
                escaped_match = html.escape(match)
                result = result.replace(escaped_match, f'<mark class="highlight">{escaped_match}</mark>')
        
        return result
