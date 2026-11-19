"""
Database module for SpamGuard.
Handles SQLite operations for storing scan history.
"""

import sqlite3
from typing import List, Dict, Any, Optional
import os
import sys

# Get database path
DATABASE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "spamguard.db"
)


def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with required tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            classification TEXT NOT NULL,
            heuristic_risk_score REAL NOT NULL,
            regex_matches TEXT,
            dfa_result TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            analyzed_at TEXT
        )
    """)
    
    conn.commit()
    conn.close()


def save_scan(subject: str, classification: str, score: float, 
              regex_matches: List[Dict], dfa_result: Dict) -> int:
    """
    Save a scan result to the database.
    
    Args:
        subject: Email subject
        classification: Classification result
        score: Heuristic risk score
        regex_matches: List of regex matches
        dfa_result: DFA analysis result
        
    Returns:
        ID of the inserted record
    """
    import json
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO scans (subject, classification, heuristic_risk_score, 
                          regex_matches, dfa_result, analyzed_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (
        subject,
        classification,
        score,
        json.dumps(regex_matches),
        json.dumps(dfa_result)
    ))
    
    scan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return scan_id


def get_recent_scans(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent scan results.
    
    Args:
        limit: Maximum number of results
        
    Returns:
        List of scan records
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, subject, classification, heuristic_risk_score, timestamp
        FROM scans
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_all_scans() -> List[Dict[str, Any]]:
    """
    Get all scan results.
    
    Returns:
        List of all scan records
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, subject, classification, heuristic_risk_score, timestamp
        FROM scans
        ORDER BY timestamp DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_scan_by_id(scan_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific scan result by ID.
    
    Args:
        scan_id: The scan ID
        
    Returns:
        Scan record or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, subject, classification, heuristic_risk_score, 
               regex_matches, dfa_result, timestamp
        FROM scans
        WHERE id = ?
    """, (scan_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_statistics() -> Dict[str, Any]:
    """
    Get scan statistics.
    
    Returns:
        Dictionary with statistics
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total scans
    cursor.execute("SELECT COUNT(*) as total FROM scans")
    total = cursor.fetchone()["total"] or 0
    
    # Classification counts
    cursor.execute("""
        SELECT classification, COUNT(*) as count
        FROM scans
        GROUP BY classification
        ORDER BY count DESC
    """)
    class_counts = {row["classification"]: row["count"] for row in cursor.fetchall()}
    
    # Score distribution
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN heuristic_risk_score < 30 THEN 1 ELSE 0 END) as legitimate,
            SUM(CASE WHEN heuristic_risk_score >= 30 AND heuristic_risk_score < 60 THEN 1 ELSE 0 END) as suspicious,
            SUM(CASE WHEN heuristic_risk_score >= 60 THEN 1 ELSE 0 END) as spam
        FROM scans
    """)
    dist = cursor.fetchone()
    
    conn.close()
    
    return {
        "total": total,
        "legitimate": class_counts.get("Legitimate", 0),
        "suspicious": class_counts.get("Suspicious", 0),
        "spam": class_counts.get("Spam", 0),
        "score_distribution": {
            "legitimate": dist["legitimate"] or 0,
            "suspicious": dist["suspicious"] or 0,
            "spam": dist["spam"] or 0
        }
    }


def clear_history() -> bool:
    """
    Clear all scan history.
    
    Returns:
        True if successful
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM scans")
    conn.commit()
    conn.close()
    
    return True


# Initialize database on module load
init_db()
