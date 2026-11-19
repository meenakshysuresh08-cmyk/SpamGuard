"""
SpamGuard - Email Spam Detection Using Regular Expressions and Finite Automata
A Flask web application for educational demonstration of Theory of Computation concepts.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from typing import Dict, Any, List
import sys
import os

# Add project directories to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.analyzer import EmailAnalyzer
from engine.regex_detector import RegexDetector
from engine.dfa_detector import DFA
from database.db import (
    save_scan, get_recent_scans, get_all_scans, get_scan_by_id,
    get_statistics, clear_history
)
from utils.email_parser import (
    validate_upload, extract_text_from_content,
    parse_txt_file, parse_eml_file
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB max


# Initialize components
analyzer = EmailAnalyzer()
regex_detector = RegexDetector()
dfa = DFA()


@app.route('/')
def index():
    """Redirect to dashboard."""
    return redirect(url_for('dashboard'))


# ==================== PAGE ROUTES ====================

@app.route('/dashboard')
def dashboard():
    """Render the dashboard page."""
    stats = get_statistics()
    recent = get_recent_scans(5)
    return render_template('dashboard.html', stats=stats, recent_scans=recent)


@app.route('/scanner')
def scanner():
    """Render the email scanner page."""
    return render_template('scanner.html')


@app.route('/regex-lab')
def regex_lab():
    """Render the regex lab page."""
    return render_template('regex_lab.html')


@app.route('/dfa-simulator')
def dfa_simulator():
    """Render the DFA simulator page."""
    return render_template('dfa_simulator.html')


@app.route('/history')
def history():
    """Render the scan history page."""
    scans = get_all_scans()
    return render_template('history.html', scans=scans)


@app.route('/about-toc')
def about_toc():
    """Render the About TOC page."""
    return render_template('about_toc.html')


# ==================== API ENDPOINTS ====================

@app.route('/api/analyze', methods=['POST'])
def analyze_email():
    """Analyze an email for spam."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        subject = data.get('subject', '') or ""
        body = data.get('body', '') or ""
        
        if not subject.strip() and not body.strip():
            return jsonify({"error": "Subject or body is required"}), 400
        
        # Analyze the email
        result = analyzer.analyze(subject, body)
        
        # Save to database
        scan_id = save_scan(
            subject=result.get("subject", ""),
            classification=result["classification"],
            score=result["heuristic_risk_score"],
            regex_matches=result.get("regex_matches", []),
            dfa_result=result.get("dfa_result", {})
        )
        
        result["scan_id"] = scan_id
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/analyze-file', methods=['POST'])
def analyze_file():
    """Analyze an uploaded email file."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Validate file
        content = file.read()
        is_valid, error = validate_upload(file.filename, content)
        
        if not is_valid:
            return jsonify({"error": error}), 400
        
        # Parse file
        content_str = content.decode('utf-8')
        subject, body = extract_text_from_content(file.filename, content_str)
        
        if subject is None and body is None:
            return jsonify({"error": "Failed to parse file content"}), 400
        
        # Default subject if none found
        if not subject:
            subject = f"Analysis of {file.filename}"
        
        # Analyze
        result = analyzer.analyze(subject, body)
        
        # Save to database
        scan_id = save_scan(
            subject=result.get("subject", subject),
            classification=result["classification"],
            score=result["heuristic_risk_score"],
            regex_matches=result.get("regex_matches", []),
            dfa_result=result.get("dfa_result", {})
        )
        
        result["scan_id"] = scan_id
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/dfa/run', methods=['POST'])
def run_dfa():
    """Run DFA on a token sequence."""
    try:
        data = request.get_json()
        tokens = data.get('tokens', [])
        
        if not isinstance(tokens, list):
            return jsonify({"error": "Tokens must be a list"}), 400
        
        result = analyzer.analyze_token_sequence(tokens)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/dfa/config', methods=['GET'])
def get_dfa_config():
    """Get DFA configuration for visualization."""
    config = analyzer.get_dfa_config()
    return jsonify(config)


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get all scan history."""
    scans = get_all_scans()
    return jsonify(scans)


@app.route('/api/history/clear', methods=['POST'])
def clear_scan_history():
    """Clear all scan history."""
    try:
        clear_history()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/history/<int:scan_id>', methods=['GET'])
def get_scan(scan_id):
    """Get a specific scan result."""
    scan = get_scan_by_id(scan_id)
    if scan:
        return jsonify(scan)
    return jsonify({"error": "Scan not found"}), 404


@app.route('/api/regex/info', methods=['GET'])
def get_regex_info():
    """Get information about a specific regex pattern."""
    pattern_name = request.args.get('pattern')
    if not pattern_name:
        return jsonify({"error": "Pattern parameter is required"}), 400
    
    if pattern_name not in regex_detector.patterns:
        return jsonify({"error": "Invalid pattern name"}), 400
    
    config = regex_detector.patterns[pattern_name]
    return jsonify({
        "pattern": pattern_name,
        "description": config.get("description", ""),
        "regex": config.get("regex", "")
    })


@app.route('/api/regex/test', methods=['POST'])
def test_regex():
    """Test a regex pattern against sample text."""
    try:
        data = request.get_json()
        pattern_name = data.get('pattern')
        sample_text = data.get('text', '')
        
        if not pattern_name:
            return jsonify({"error": "Pattern name is required"}), 400
        
        if pattern_name not in regex_detector.patterns:
            return jsonify({"error": "Invalid pattern name"}), 400
        
        # Get the pattern
        config = regex_detector.patterns[pattern_name]
        regex = config["regex"]
        
        # Find matches
        import re
        compiled = re.compile(regex)
        matches = compiled.findall(sample_text)
        
        return jsonify({
            "pattern": pattern_name,
            "description": config["description"],
            "regex": regex,
            "matches": matches,
            "match_count": len(matches),
            "found": len(matches) > 0
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== STATIC FILES ====================

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files from css and js directories."""
    # Handle both css/ and js/ paths
    if filename.startswith('css/') or filename.startswith('js/'):
        directory = 'static'
        return send_from_directory(directory, filename)
    # Fallback for other static files
    return send_from_directory('static', filename)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
