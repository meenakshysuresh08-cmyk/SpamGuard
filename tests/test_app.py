"""
Tests for Flask application routes and API endpoints.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index_redirect(client):
    """Test index redirects to dashboard."""
    response = client.get('/')
    assert response.status_code == 302
    assert '/dashboard' in response.headers['Location']


@pytest.mark.parametrize('route', [
    '/dashboard',
    '/scanner',
    '/regex-lab',
    '/dfa-simulator',
    '/history',
    '/about-toc'
])
def test_page_routes_render(client, route):
    """Test that all frontend pages render without template or routing errors."""
    response = client.get(route)
    assert response.status_code == 200
    assert b"SpamGuard" in response.data


def test_api_analyze(client):
    """Test /api/analyze endpoint with valid input."""
    payload = {
        "subject": "Urgent: Claim your prize now!",
        "body": "Congratulations, you won a free gift. Click here http://example.com and enter your password."
    }
    response = client.post('/api/analyze', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "classification" in data
    assert "heuristic_risk_score" in data
    assert data["classification"] == "Spam"


def test_api_regex_info(client):
    """Test /api/regex/info endpoint."""
    response = client.get('/api/regex/info?pattern=free_offer')
    assert response.status_code == 200
    data = response.get_json()
    assert data["pattern"] == "free_offer"
    assert "regex" in data


def test_api_dfa_config(client):
    """Test /api/dfa/config endpoint."""
    response = client.get('/api/dfa/config')
    assert response.status_code == 200
    data = response.get_json()
    assert "states" in data
    assert "transition_table" in data


def test_api_dfa_run(client):
    """Test /api/dfa/run endpoint."""
    response = client.post('/api/dfa/run', json={"tokens": ["LURE", "URGENT", "URL", "CREDENTIAL"]})
    assert response.status_code == 200
    data = response.get_json()
    assert data["is_accepted"] is True
