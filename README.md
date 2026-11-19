# SpamGuard - Email Spam Detection Using Regular Expressions and Finite Automata

An educational web application demonstrating Theory of Computation concepts (regular expressions and deterministic finite automata) applied to email spam detection.

## Overview

SpamGuard is a lightweight web application that shows students and instructors how two core Theory of Computation concepts can solve a real-world problem: judging whether an email looks like spam.

**Key Features:**
- **Email Scanner**: Analyze emails using regex pattern matching and DFA sequence validation
- **Regex Lab**: Experiment with spam detection patterns
- **DFA Simulator**: Step through the automaton state by state
- **Scan History**: Review past analyses with SQLite persistence
- **About TOC**: Learn about Theory of Computation concepts

**How It Works:**
1. **Regex Detection**: Scans text for spam indicators (suspicious URLs, free offers, urgent wording, credential requests, etc.)
2. **DFA Analysis**: Validates if detected elements form a suspicious sequence pattern
3. **Scoring**: Combines evidence into a heuristic risk score (0-100)
4. **Classification**: Labels emails as Legitimate, Suspicious, or Spam

## Installation (Windows)

1. **Clone or navigate to the project directory:**
   ```powershell
   cd "E:\TOC Capestone"
   ```

2. **Create a virtual environment (if not already created):**
   ```powershell
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Run the application:**
   ```powershell
   python app.py
   ```

6. **Open your browser:**
   Navigate to `http://127.0.0.1:5000`

## Usage

### Email Scanner
1. Navigate to the Email Scanner page
2. Enter a subject and/or paste email body content
3. Click "Analyze Email" to detect spam indicators
4. View the heuristic risk score, classification, and detailed analysis

### Regex Lab
1. Navigate to the Regex Lab page
2. Select a pattern from the dropdown (free offers, suspicious URLs, urgent wording, etc.)
3. Enter sample text in the textarea
4. Click "Test Pattern" to see matches
5. View highlighted matches and pattern explanation

### DFA Simulator
1. Navigate to the DFA Simulator page
2. Review the DFA configuration (states, transitions, accepting states)
3. Try one of the example sequences or enter your own
4. Click "Run DFA" to see the complete trace
5. Click "Step Through" to see the state transitions one by one

## Project Structure

```
e:\TOC Capestone
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── database/
│   └── db.py              # SQLite database operations
├── engine/
│   ├── analyzer.py        # Main email analyzer
│   ├── regex_detector.py  # Regex pattern matching
│   ├── dfa_detector.py    # DFA implementation
│   ├── spam_scorer.py     # Scoring algorithm
│   └── email_parser.py    # File parsing utilities
├── templates/             # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── scanner.html
│   ├── regex_lab.html
│   ├── dfa_simulator.html
│   ├── history.html
│   └── about_toc.html
├── static/
│   ├── css/
│   │   └── style.css      # CSS styles
│   └── js/
│       └── app.js         # JavaScript code
├── sample_emails/         # Example email files
│   ├── legitimate_001.txt
│   ├── legitimate_002.eml
│   ├── suspicious_001.txt
│   ├── suspicious_002.eml
│   ├── spam_001.txt
│   └── spam_002.eml
└── tests/
    ├── test_database.py
    ├── test_regex_detector.py
    ├── test_dfa_detector.py
    ├── test_spam_scorer.py
    └── test_email_parser.py
```

## Token Language

The DFA uses the following token types:

- **LURE**: Free/prize/discount/money offer
- **URGENT**: Urgent pressure language
- **URL**: URL or link reference
- **CREDENTIAL**: Request for password/OTP/card/SSN
- **OTHER**: Anything else

## DFA States

1. **q0 (Start)**: Initial state, waiting for the first suspicious element
2. **q1 (Lure)**: Detected a free offer or prize
3. **q2 (Pressure)**: Detected urgent language after a lure
4. **q3 (Link)**: Detected a suspicious URL after pressure
5. **q4 (Credential)**: Detected a credential request (accepting state)
6. **q_dead (Dead)**: Invalid sequence, cannot reach acceptance

**Accepting States**: q3 and q4 (suspicious sequence detected)

## Scoring Weights

| Pattern | Weight |
|---------|--------|
| credential_request | 30 |
| prize_winner | 25 |
| free_offer | 20 |
| urgent_wording | 20 |
| suspicious_url | 15 |
| money_transfer | 20 |
| discount_offer | 15 |
| guarantee_words | 15 |

## Classification Thresholds

| Score | Classification |
|-------|---------------|
| 0-29 | Legitimate |
| 30-59 | Suspicious |
| 60+ | Spam |

## Testing

Run the test suite:

```powershell
.\venv\Scripts\Activate.ps1
pytest tests/ -v
```

## About Theory of Computation

### Regular Expressions

Regular expressions are sequences of characters that define a search pattern. They are compiled into Finite Automata for efficient matching.

### Finite Automata

A Finite Automaton is a mathematical model of computation that recognizes patterns in strings. It consists of:
- A finite set of states
- An input alphabet
- A transition function
- An initial state
- A set of accepting states

### DFA vs NFA

| Feature | DFA | NFA |
|---------|-----|-----|
| Next State | Exactly one | Zero, one, or many |
| Empty Transitions | Not allowed | Allowed |
| Speed | Faster | Slower |
| Space | More states | Fewer states |

### Equivalence

Regex and Finite Automata are equivalent in power - both define the class of regular languages.

## Security Notes

- All analysis is performed locally on your machine
- No email content is sent to external services
- File uploads are validated (only .txt and .eml files, max 1MB)
- Output is properly escaped to prevent XSS attacks

## License

Educational use only.
