"""
Email parsing utilities.
Handles parsing of .eml files and extraction of subject/body.
"""

from typing import Tuple, Optional
import os


def parse_eml_file(filepath: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse an .eml file and extract subject and body.
    
    Args:
        filepath: Path to the .eml file
        
    Returns:
        Tuple of (subject, body) or (None, None) on error
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        subject = None
        body_lines = []
        in_body = False
        
        for line in lines:
            if not in_body:
                if line.lower().startswith('subject:'):
                    subject = line[8:].strip()
                    # Handle continuation lines
                    while True:
                        next_line = lines[lines.index(line) + 1] if lines.index(line) + 1 < len(lines) else ''
                        if next_line.startswith(' ') or next_line.startswith('\t'):
                            subject += next_line.strip()
                            lines[lines.index(line) + 1] = ''
                        else:
                            break
                
                elif line.strip() == '':
                    # Empty line marks end of headers
                    in_body = True
            else:
                body_lines.append(line)
        
        body = '\n'.join(body_lines).strip() if body_lines else ""
        
        return subject, body
    
    except Exception as e:
        return None, None


def parse_txt_file(filepath: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse a .txt file and extract subject and body.
    Assumes subject is first line, body is rest.
    
    Args:
        filepath: Path to the .txt file
        
    Returns:
        Tuple of (subject, body) or (None, None) on error
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        if lines:
            subject = lines[0].strip()
            body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ""
            return subject, body
        
        return None, None
    
    except Exception as e:
        return None, None


def validate_upload(filename: str, content: bytes, max_size: int = 1024 * 1024) -> Tuple[bool, Optional[str]]:
    """
    Validate an uploaded file.
    
    Args:
        filename: Original filename
        content: File content as bytes
        max_size: Maximum file size in bytes (default 1MB)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file extension
    valid_extensions = {'.txt', '.eml'}
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in valid_extensions:
        return False, f"Invalid file type. Only .txt and .eml files are allowed."
    
    # Check file size
    if len(content) > max_size:
        return False, f"File too large. Maximum size is {max_size // 1024}KB."
    
    # Check for empty file
    if len(content) == 0:
        return False, "File is empty."
    
    # Try to decode as UTF-8
    try:
        content.decode('utf-8')
    except UnicodeDecodeError:
        return False, "File must be UTF-8 encoded."
    
    return True, None


def extract_text_from_content(filename: str, content: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract subject and body from file content based on extension.
    
    Args:
        filename: The filename (for extension detection)
        content: File content as string
        
    Returns:
        Tuple of (subject, body) or (None, None) on error
    """
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == '.eml':
        return parse_eml_file_from_content(content)
    elif ext == '.txt':
        return parse_txt_file_from_content(content)
    else:
        return None, None


def parse_eml_file_from_content(content: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse .eml content directly (without file path).
    
    Args:
        content: .eml file content
        
    Returns:
        Tuple of (subject, body) or (None, None) on error
    """
    try:
        lines = content.split('\n')
        
        subject = None
        body_lines = []
        in_body = False
        
        for line in lines:
            if not in_body:
                if line.lower().startswith('subject:'):
                    subject = line[8:].strip()
                
                elif line.strip() == '':
                    in_body = True
            else:
                body_lines.append(line)
        
        body = '\n'.join(body_lines).strip() if body_lines else ""
        
        return subject, body
    
    except Exception as e:
        return None, None


def parse_txt_file_from_content(content: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse .txt content directly (without file path).
    
    Args:
        content: .txt file content
        
    Returns:
        Tuple of (subject, body) or (None, None) on error
    """
    try:
        lines = content.split('\n')
        
        if lines:
            subject = lines[0].strip()
            body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ""
            return subject, body
        
        return None, None
    
    except Exception as e:
        return None, None
