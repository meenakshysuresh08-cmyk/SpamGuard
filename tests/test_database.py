"""
Tests for database module.
"""

import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use a temporary database for testing
original_db_path = None


def setup_test_db():
    """Set up a temporary database for testing."""
    global original_db_path
    
    # Save original path
    from database import db
    original_db_path = db.DATABASE_PATH
    
    # Create temporary directory and database
    temp_dir = tempfile.mkdtemp()
    temp_db = os.path.join(temp_dir, "test_spamguard.db")
    
    # Override database path
    db.DATABASE_PATH = temp_db
    
    # Reinitialize
    db.init_db()
    
    return temp_dir


def teardown_test_db(temp_dir):
    """Clean up temporary database."""
    shutil.rmtree(temp_dir)
    
    # Restore original path
    from database import db
    db.DATABASE_PATH = original_db_path


def test_init_db():
    """Test database initialization creates tables."""
    temp_dir = setup_test_db()
    
    try:
        from database import db
        
        # Should not raise exception
        db.init_db()
        
        # Verify table exists
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scans'")
        table = cursor.fetchone()
        conn.close()
        
        assert table is not None
        
    finally:
        teardown_test_db(temp_dir)


def test_save_and_get_scan():
    """Test saving and retrieving a scan."""
    temp_dir = setup_test_db()
    
    try:
        from database import db
        
        # Save a scan
        scan_id = db.save_scan(
            subject="Test Email",
            classification="Spam",
            score=75.5,
            regex_matches=[{"pattern_name": "free_offer", "match_count": 1}],
            dfa_result={"is_accepted": True}
        )
        
        assert scan_id is not None
        
        # Retrieve the scan
        scan = db.get_scan_by_id(scan_id)
        
        assert scan is not None
        assert scan["subject"] == "Test Email"
        assert scan["classification"] == "Spam"
        assert scan["heuristic_risk_score"] == 75.5
        
    finally:
        teardown_test_db(temp_dir)


def test_get_recent_scans():
    """Test retrieving recent scans."""
    temp_dir = setup_test_db()
    
    try:
        from database import db
        
        # Clear any existing scans
        db.clear_history()
        
        # Add several scans with small delay to ensure different timestamps
        import time
        for i in range(5):
            db.save_scan(
                subject=f"Test Email {i}",
                classification="Spam",
                score=75.5,
                regex_matches=[],
                dfa_result={}
            )
            time.sleep(0.01)  # Small delay to ensure unique timestamps
        
        # Get recent scans
        recent = db.get_recent_scans(3)
        
        assert len(recent) == 3
        # Should get the last 3 scans (newest first)
        subjects = [s["subject"] for s in recent]
        # Just verify we got 3 distinct scans
        assert len(set(subjects)) == 3
        
    finally:
        teardown_test_db(temp_dir)


def test_get_statistics():
    """Test statistics calculation."""
    temp_dir = setup_test_db()
    
    try:
        from database import db
        
        # Clear any existing scans
        db.clear_history()
        
        # Add scans of different types
        db.save_scan("Legit 1", "Legitimate", 10, [], {})
        db.save_scan("Legit 2", "Legitimate", 15, [], {})
        db.save_scan("Suspicious", "Suspicious", 45, [], {})
        db.save_scan("Spam 1", "Spam", 80, [], {})
        db.save_scan("Spam 2", "Spam", 90, [], {})
        db.save_scan("Spam 3", "Spam", 95, [], {})
        
        stats = db.get_statistics()
        
        assert stats["total"] == 6
        assert stats["legitimate"] == 2
        assert stats["suspicious"] == 1
        assert stats["spam"] == 3
        
    finally:
        teardown_test_db(temp_dir)


def test_clear_history():
    """Test clearing all history."""
    temp_dir = setup_test_db()
    
    try:
        from database import db
        
        # Add some scans
        db.save_scan("Test 1", "Spam", 75, [], {})
        db.save_scan("Test 2", "Spam", 80, [], {})
        
        # Verify they exist
        scans = db.get_all_scans()
        assert len(scans) == 2
        
        # Clear history
        result = db.clear_history()
        assert result is True
        
        # Verify cleared
        scans = db.get_all_scans()
        assert len(scans) == 0
        
    finally:
        teardown_test_db(temp_dir)


def test_get_all_scans():
    """Test retrieving all scans."""
    temp_dir = setup_test_db()
    
    try:
        from database import db
        
        # Clear any existing scans
        db.clear_history()
        
        # Add scans
        db.save_scan("Test 1", "Spam", 75, [], {})
        db.save_scan("Test 2", "Legitimate", 10, [], {})
        
        # Get all scans
        all_scans = db.get_all_scans()
        
        assert len(all_scans) == 2
        
    finally:
        teardown_test_db(temp_dir)


def test_get_scan_not_found():
    """Test getting a non-existent scan."""
    temp_dir = setup_test_db()
    
    try:
        from database import db
        
        scan = db.get_scan_by_id(99999)
        
        assert scan is None
        
    finally:
        teardown_test_db(temp_dir)


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
