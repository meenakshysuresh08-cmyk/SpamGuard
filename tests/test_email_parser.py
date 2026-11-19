"""
Tests for email_parser module.
"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.email_parser import (
    validate_upload, parse_txt_file, parse_eml_file,
    parse_txt_file_from_content, parse_eml_file_from_content,
    extract_text_from_content
)


def test_validate_txt_file():
    """Test validation of .txt files."""
    content = b"This is a test file"
    
    is_valid, error = validate_upload("test.txt", content)
    
    assert is_valid is True
    assert error is None


def test_validate_eml_file():
    """Test validation of .eml files."""
    content = b"Subject: Test\r\n\r\nBody content"
    
    is_valid, error = validate_upload("test.eml", content)
    
    assert is_valid is True
    assert error is None


def test_validate_invalid_extension():
    """Test rejection of invalid file extensions."""
    content = b"Test content"
    
    is_valid, error = validate_upload("test.docx", content)
    
    assert is_valid is False
    assert error is not None


def test_validate_empty_file():
    """Test rejection of empty files."""
    content = b""
    
    is_valid, error = validate_upload("test.txt", content)
    
    assert is_valid is False


def test_validate_file_too_large():
    """Test rejection of files over 1MB."""
    content = b"X" * (1024 * 1024 + 1)  # Just over 1MB
    
    is_valid, error = validate_upload("test.txt", content)
    
    assert is_valid is False


def test_validate_non_utf8():
    """Test rejection of non-UTF-8 files."""
    content = b"\xff\xfe"  # Invalid UTF-8
    
    is_valid, error = validate_upload("test.txt", content)
    
    assert is_valid is False


def test_parse_txt_file_content():
    """Test parsing of .txt file content."""
    content = "Subject Line\n\nBody content here\nWith multiple lines."
    
    subject, body = parse_txt_file_from_content(content)
    
    assert subject == "Subject Line"
    assert "Body content" in body
    assert "multiple lines" in body


def test_parse_txt_file_no_body():
    """Test parsing of .txt file with only subject."""
    content = "Just a subject line"
    
    subject, body = parse_txt_file_from_content(content)
    
    assert subject == "Just a subject line"
    assert body == ""


def test_parse_eml_file_content():
    """Test parsing of .eml file content."""
    content = """From: sender@example.com
To: recipient@example.com
Subject: Test Email

This is the body of the email.
With multiple lines."""

    subject, body = parse_eml_file_from_content(content)
    
    assert subject == "Test Email"
    assert "body of the email" in body
    assert "multiple lines" in body


def test_parse_eml_file_with_continuation():
    """Test parsing of .eml file with long subject."""
    content = """From: sender@example.com
To: recipient@example.com
Subject: This is a very long subject line that
 continues on this line

Email body here."""

    subject, body = parse_eml_file_from_content(content)
    
    assert "very long subject" in subject
    assert "body here" in body


def test_parse_eml_file_empty_body():
    """Test parsing of .eml file with empty body."""
    content = """From: sender@example.com
To: recipient@example.com
Subject: Test Email
"""

    subject, body = parse_eml_file_from_content(content)
    
    assert subject == "Test Email"
    assert body == ""


def test_extract_txt_from_content():
    """Test extracting subject/body from .txt content."""
    content = "Subject\n\nBody content"
    
    subject, body = extract_text_from_content("test.txt", content)
    
    assert subject == "Subject"
    assert "Body content" in body


def test_extract_eml_from_content():
    """Test extracting subject/body from .eml content."""
    content = """Subject: Test

Body"""
    
    subject, body = extract_text_from_content("test.eml", content)
    
    assert subject == "Test"
    assert "Body" in body


def test_extract_invalid_extension():
    """Test handling of invalid file extension."""
    content = "Test"
    
    subject, body = extract_text_from_content("test.pdf", content)
    
    assert subject is None
    assert body is None


def test_parse_eml_file_full():
    """Test parsing a complete .eml file."""
    temp_dir = tempfile.mkdtemp()
    
    try:
        eml_content = """From: sender@example.com
To: recipient@example.com
Subject: Full Email Test

This is the full email body.
With multiple paragraphs.

Best regards,
Sender"""
        
        filepath = os.path.join(temp_dir, "test.eml")
        with open(filepath, 'w') as f:
            f.write(eml_content)
        
        subject, body = parse_eml_file(filepath)
        
        assert subject == "Full Email Test"
        assert "full email body" in body
        assert "Best regards" in body
        
    finally:
        import shutil
        shutil.rmtree(temp_dir)


def test_parse_txt_file_full():
    """Test parsing a complete .txt file."""
    temp_dir = tempfile.mkdtemp()
    
    try:
        txt_content = """Subject Line

This is the body of the text file.
It has multiple lines."""
        
        filepath = os.path.join(temp_dir, "test.txt")
        with open(filepath, 'w') as f:
            f.write(txt_content)
        
        subject, body = parse_txt_file(filepath)
        
        assert subject == "Subject Line"
        assert "body of the text file" in body
        
    finally:
        import shutil
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
