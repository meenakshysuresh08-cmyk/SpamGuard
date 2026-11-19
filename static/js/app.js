// SpamGuard — Enterprise Frontend Application for Theory of Computation Engine
// Zero-ML, Deterministic Automata & Regex UI Controller

document.addEventListener('DOMContentLoaded', function() {
    initializeScanner();
    initializeRegexLab();
    initializeDfaSimulator();
    initializeHistory();
});

// ==================== TOAST UTILITY ====================
function showToast(message, duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
        <span>${escapeHtml(message)}</span>
    `;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// ==================== 1. EMAIL SCANNER ====================
function initializeScanner() {
    const analyzeBtn = document.getElementById('analyze-btn');
    const clearBtn = document.getElementById('clear-btn');
    const fileUpload = document.getElementById('file-upload');
    const dropzone = document.getElementById('dropzone');
    const scanForm = document.getElementById('scan-form');
    const bodyInput = document.getElementById('body');
    const charCount = document.getElementById('char-count');
    const btnRemoveFile = document.getElementById('btn-remove-file');

    // Quick sample loaders
    const sampleSpamBtn = document.getElementById('load-sample-spam');
    const sampleSusBtn = document.getElementById('load-sample-suspicious');
    const sampleCleanBtn = document.getElementById('load-sample-clean');

    if (bodyInput && charCount) {
        bodyInput.addEventListener('input', () => {
            const count = bodyInput.value.length;
            charCount.textContent = `${count} character${count === 1 ? '' : 's'}`;
        });
    }

    // Sample data
    if (sampleSpamBtn) {
        sampleSpamBtn.addEventListener('click', () => {
            document.getElementById('subject').value = "People's Bank Security Alert: Account Locked";
            bodyInput.value = `Dear People's Bank Client,\n\nFor your security, the profile that you are using to access People's Bank Online Banking has been locked because of too many failed login attempts. You can unlock this profile online by selecting an option below:\n\nUnlock your profile with:\n- My ATM/Visa Check Card number and PIN\n- Other personal information (Social Security Number, Account #, etc)\n- E-mail address\n\nWe regret any inconvenience this may cause you.\n\nSincerely,\nPeople's Bank Account Review Department.\n\nWe are requesting this information to verify and protect your identity. This is in order to prevent the use of the U.S. banking system in terrorist and other illegal activity.\n\nNeed help? Use "Site Helper" or call customer service at 1.800.788.7000.\nPlease do not "Reply" to this Alert.`;
            bodyInput.dispatchEvent(new Event('input'));
            showToast('Loaded Real Bank Phishing Sample');
        });
    }

    if (sampleSusBtn) {
        sampleSusBtn.addEventListener('click', () => {
            document.getElementById('subject').value = 'Urgent: Your Account Has Been Compromised!';
            bodyInput.value = `Dear Customer,\n\nURGENT: Your bank account has been locked due to suspicious activity. We detected an unauthorized login attempt from an unknown device.\n\nIMMEDIATELY verify your identity by clicking our security link: https://account-verify-secure.xyz/login\n\nYour OTP confirmation code is: 492019. Do NOT share this code with anyone. Failure to verify within 24 hours will cause permanent account closure.`;
            bodyInput.dispatchEvent(new Event('input'));
            showToast('Loaded Suspicious Alert sample');
        });
    }

    if (sampleCleanBtn) {
        sampleCleanBtn.addEventListener('click', () => {
            document.getElementById('subject').value = 'Project Sync: Theory of Computation Capstone Review';
            bodyInput.value = `Hi Team,\n\nThis is a quick reminder about our weekly project progress meeting scheduled for tomorrow at 2:00 PM in Conference Room B.\n\nAgenda:\n1. DFA state transition validation and testing\n2. Regular expression heuristic weights verification\n3. UI telemetry audit\n\nPlease review your assigned pull requests and bring any questions.\n\nBest regards,\nSarah Johnson\nEngineering Project Lead`;
            bodyInput.dispatchEvent(new Event('input'));
            showToast('Loaded Clean Email sample');
        });
    }

    // Dropzone drag & drop
    if (dropzone && fileUpload) {
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                fileUpload.files = e.dataTransfer.files;
                handleSelectedFile(fileUpload.files[0]);
            }
        });

        fileUpload.addEventListener('change', () => {
            if (fileUpload.files && fileUpload.files[0]) {
                handleSelectedFile(fileUpload.files[0]);
            }
        });
    }

    if (btnRemoveFile) {
        btnRemoveFile.addEventListener('click', () => {
            if (fileUpload) fileUpload.value = '';
            document.getElementById('file-name-display').classList.add('hidden');
        });
    }

    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', () => {
            if (fileUpload && fileUpload.files && fileUpload.files.length > 0) {
                analyzeUploadedFile();
            } else {
                analyzeEmailText();
            }
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', resetScanner);
    }

    if (scanForm) {
        scanForm.addEventListener('submit', (e) => e.preventDefault());
    }
}

function handleSelectedFile(file) {
    const display = document.getElementById('file-name-display');
    const textSpan = display.querySelector('.file-name-text');
    textSpan.textContent = `Attached: ${file.name} (${Math.round(file.size / 1024)} KB)`;
    display.classList.remove('hidden');
    showToast(`File "${file.name}" ready to analyze`);
}

async function analyzeEmailText() {
    const subject = document.getElementById('subject').value.trim();
    const body = document.getElementById('body').value.trim();

    if (!subject && !body) {
        showScannerError('Please enter an email subject or body content to scan.');
        return;
    }

    toggleScannerLoading(true);
    hideScannerError();

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ subject, body })
        });

        const data = await response.json();
        if (!response.ok) {
            showScannerError(data.error || 'Automata analysis encountered an error.');
            return;
        }

        renderScanResults(data);
        showToast('TOC Evaluation Complete');
    } catch (err) {
        showScannerError('Communication error: ' + err.message);
    } finally {
        toggleScannerLoading(false);
    }
}

async function analyzeUploadedFile() {
    const fileUpload = document.getElementById('file-upload');
    const file = fileUpload.files[0];
    if (!file) return;

    toggleScannerLoading(true);
    hideScannerError();

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/analyze-file', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (!response.ok) {
            showScannerError(data.error || 'Failed to parse and analyze file.');
            return;
        }

        renderScanResults(data);
        showToast(`Analyzed ${file.name}`);
    } catch (err) {
        showScannerError('File upload error: ' + err.message);
    } finally {
        toggleScannerLoading(false);
    }
}

function renderScanResults(data) {
    const placeholder = document.getElementById('scanner-placeholder');
    const resultContainer = document.getElementById('result-container');
    const statusPill = document.getElementById('result-status-pill');
    const verdictBanner = document.getElementById('verdict-banner');
    const classificationEl = document.getElementById('classification');
    const scoreEl = document.getElementById('score');
    const explanationEl = document.getElementById('explanation');
    const tokensContainer = document.getElementById('tokens-container');
    const dfaPill = document.getElementById('dfa-acceptance-pill');
    const dfaSummary = document.getElementById('dfa-summary-row');
    const matchesContainer = document.getElementById('matches-container');

    if (placeholder) placeholder.classList.add('hidden');
    if (resultContainer) resultContainer.classList.remove('hidden');

    const classification = data.classification || 'Unknown';
    const score = Number(data.heuristic_risk_score || 0).toFixed(1);

    // Update Status Pill
    if (statusPill) {
        statusPill.className = `badge-status status-${classification.toLowerCase()}`;
        statusPill.innerHTML = `<span class="status-indicator-dot dot-${classification === 'Spam' ? 'rose' : classification === 'Suspicious' ? 'amber' : 'green'}"></span> ${classification}`;
    }

    // Verdict Banner Styling
    if (verdictBanner) {
        verdictBanner.className = `verdict-banner verdict-${classification.toLowerCase()}`;
    }

    if (classificationEl) classificationEl.textContent = classification;
    if (scoreEl) {
        scoreEl.textContent = score;
        scoreEl.className = `score-dial-val ${classification === 'Spam' ? 'text-rose' : classification === 'Suspicious' ? 'text-amber' : 'text-emerald'}`;
    }

    // Explanation
    if (explanationEl) {
        const header = data.explanation?.header || '';
        const reasons = data.explanation?.reasons || [];
        explanationEl.innerHTML = `
            <strong>${escapeHtml(header)}</strong>
            <ul style="margin-top: 0.5rem; padding-left: 1.25rem;">
                ${reasons.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
            </ul>
        `;
    }

    // DFA Tokens Stream
    const dfaResult = data.dfa_result || {};
    const tokens = dfaResult.tokens || data.tokens || [];
    if (tokensContainer) {
        if (tokens.length > 0) {
            tokensContainer.innerHTML = tokens.map(t => `<span class="token ${t.toLowerCase()}">${escapeHtml(t)}</span>`).join('');
        } else {
            tokensContainer.innerHTML = '<span class="text-muted" style="font-size: 0.85rem;">No suspicious tokens detected in alphabet Σ.</span>';
        }
    }

    // DFA Acceptance Pill
    if (dfaPill) {
        const isAccepted = dfaResult.is_accepted;
        dfaPill.className = `pill-dfa-status ${isAccepted ? 'accepted' : 'rejected'}`;
        dfaPill.textContent = isAccepted ? 'DFA Accepted (Threat Sequence)' : 'DFA Rejected (Non-threat)';
    }

    if (dfaSummary) {
        dfaSummary.innerHTML = `
            <strong>Final State:</strong> <code class="font-mono">${escapeHtml(dfaResult.final_state || 'q0')}</code>
            &nbsp;•&nbsp; <strong>Transition Steps:</strong> ${dfaResult.trace ? dfaResult.trace.length : 0} transitions processed
        `;
    }

    // Detected Regex Matches
    if (matchesContainer) {
        const matches = data.regex_matches || [];
        if (matches.length > 0) {
            matchesContainer.innerHTML = matches.map(m => `
                <div class="match-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>${escapeHtml(m.pattern_name)}</strong>
                        <span class="match-count">${m.match_count} match${m.match_count === 1 ? '' : 'es'}</span>
                    </div>
                    <p style="margin: 0.25rem 0 0; font-size: 0.8rem; color: var(--slate-600);">${escapeHtml(m.description)}</p>
                </div>
            `).join('');
        } else {
            matchesContainer.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">No known spam pattern signatures matched.</p>';
        }
    }
}

function resetScanner() {
    document.getElementById('subject').value = '';
    const bodyInput = document.getElementById('body');
    if (bodyInput) {
        bodyInput.value = '';
        bodyInput.dispatchEvent(new Event('input'));
    }
    const fileUpload = document.getElementById('file-upload');
    if (fileUpload) fileUpload.value = '';
    document.getElementById('file-name-display')?.classList.add('hidden');
    document.getElementById('result-container')?.classList.add('hidden');
    document.getElementById('scanner-placeholder')?.classList.remove('hidden');
    const statusPill = document.getElementById('result-status-pill');
    if (statusPill) {
        statusPill.className = 'badge-status-waiting';
        statusPill.textContent = 'Awaiting Input';
    }
    hideScannerError();
}

function toggleScannerLoading(show) {
    const loading = document.getElementById('loading');
    const placeholder = document.getElementById('scanner-placeholder');
    const resultContainer = document.getElementById('result-container');
    if (loading) {
        if (show) {
            loading.classList.remove('hidden');
            if (placeholder) placeholder.classList.add('hidden');
            if (resultContainer) resultContainer.classList.add('hidden');
        } else {
            loading.classList.add('hidden');
        }
    }
}

function showScannerError(msg) {
    const errBox = document.getElementById('error-message');
    const errText = document.getElementById('error-text');
    if (errBox && errText) {
        errText.textContent = msg;
        errBox.classList.remove('hidden');
    }
}

function hideScannerError() {
    const errBox = document.getElementById('error-message');
    if (errBox) errBox.classList.add('hidden');
}

// ==================== 2. REGEX LAB ====================
const REGEX_SAMPLE_TEXTS = {
    'suspicious_url': 'Please log in to claim your account at http://security-update-center.xyz/auth or http://free-gift.top',
    'free_offer': 'Congratulations, you received a 100% free gift and a free trial for one year!',
    'prize_winner': 'Official Notice: You are the jackpot winner of a million cash prize in this week sweepstakes!',
    'urgent_wording': 'URGENT: Your account requires immediate verification. Please act now asap or access terminates.',
    'discount_offer': 'Special seasonal promotion: get 50% discount and exclusive clearance deal on all orders today.',
    'credential_request': 'Security prompt: please enter your password, backup pin, card number, or ssn to proceed.',
    'money_transfer': 'Kindly dispatch the requested amount via wire transfer or western union money gram.',
    'guarantee_words': 'Our software provides 100% guaranteed security with an unconditional money-back, no risk pledge.'
};

const REGEX_WEIGHTS = {
    'credential_request': 30,
    'prize_winner': 25,
    'free_offer': 20,
    'urgent_wording': 20,
    'money_transfer': 20,
    'suspicious_url': 15,
    'discount_offer': 15,
    'guarantee_words': 15
};

function initializeRegexLab() {
    const patternSelect = document.getElementById('pattern-select');
    const testBtn = document.getElementById('test-btn');
    const copyBtn = document.getElementById('btn-copy-regex');
    const loadExampleBtn = document.getElementById('btn-load-regex-example');
    const catalogCards = document.querySelectorAll('.catalog-card');

    if (patternSelect) {
        patternSelect.addEventListener('change', updateRegexInfo);
        updateRegexInfo();
    }

    if (testBtn) {
        testBtn.addEventListener('click', evaluateActiveRegex);
    }

    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const regexText = document.getElementById('pattern-regex')?.textContent || '';
            if (regexText) {
                navigator.clipboard.writeText(regexText).then(() => {
                    showToast('Pattern copied to clipboard');
                }).catch(() => {
                    showToast('Failed to copy');
                });
            }
        });
    }

    if (loadExampleBtn && patternSelect) {
        loadExampleBtn.addEventListener('click', () => {
            const key = patternSelect.value;
            const sampleArea = document.getElementById('sample-text');
            if (sampleArea && REGEX_SAMPLE_TEXTS[key]) {
                sampleArea.value = REGEX_SAMPLE_TEXTS[key];
                showToast(`Loaded example for ${key}`);
            }
        });
    }

    catalogCards.forEach(card => {
        card.addEventListener('click', () => {
            const pat = card.dataset.pattern;
            if (patternSelect && pat) {
                patternSelect.value = pat;
                patternSelect.dispatchEvent(new Event('change'));
                document.getElementById('sample-text')?.scrollIntoView({ behavior: 'smooth' });
                showToast(`Selected "${pat}"`);
            }
        });
    });
}

async function updateRegexInfo() {
    const patternSelect = document.getElementById('pattern-select');
    const patternDesc = document.getElementById('pattern-description');
    const patternRegex = document.getElementById('pattern-regex');
    const weightBadge = document.getElementById('pattern-weight-badge');
    if (!patternSelect) return;

    const patternName = patternSelect.value;

    if (weightBadge && REGEX_WEIGHTS[patternName]) {
        weightBadge.textContent = `Weight: ${REGEX_WEIGHTS[patternName]} pts`;
    }

    try {
        const response = await fetch(`/api/regex/info?pattern=${patternName}`);
        if (response.ok) {
            const data = await response.json();
            if (patternDesc) patternDesc.textContent = data.description || '';
            if (patternRegex) patternRegex.textContent = data.regex || '';
            return;
        }
    } catch (e) {
        // Fallback
    }
}

async function evaluateActiveRegex() {
    const patternSelect = document.getElementById('pattern-select');
    const sampleInput = document.getElementById('sample-text');
    const testResult = document.getElementById('test-result');
    const testStatus = document.getElementById('test-status');
    const matchCount = document.getElementById('match-count');
    const matchesUl = document.getElementById('matches-ul');
    const highlightedOutput = document.getElementById('highlighted-output');

    if (!sampleInput || !patternSelect) return;
    const sampleText = sampleInput.value.trim();
    const pattern = patternSelect.value;

    if (!sampleText) {
        showToast('Please enter sample text to evaluate.');
        return;
    }

    try {
        const response = await fetch('/api/regex/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pattern, text: sampleText })
        });

        const data = await response.json();
        if (!response.ok) {
            showToast(data.error || 'Evaluation error');
            return;
        }

        testResult.classList.remove('hidden');

        if (data.found) {
            testStatus.className = 'test-status-pill match';
            testStatus.innerHTML = '✓ Language Matched (Accepts Substring)';
        } else {
            testStatus.className = 'test-status-pill no-match';
            testStatus.innerHTML = '✕ No Match Found (Rejects)';
        }

        matchCount.textContent = data.match_count || 0;

        // Render matched items
        matchesUl.innerHTML = '';
        if (data.matches && data.matches.length > 0) {
            data.matches.forEach(m => {
                const li = document.createElement('li');
                li.textContent = typeof m === 'string' ? m : JSON.stringify(m);
                matchesUl.appendChild(li);
            });
        } else {
            matchesUl.innerHTML = '<li style="background:none; color:var(--slate-400);">No substring tokens</li>';
        }

        // Render highlighted text
        let renderedHtml = escapeHtml(sampleText);
        if (data.matches && data.matches.length > 0) {
            // Sort matches by length descending to replace accurately
            const sortedMatches = [...new Set(data.matches)].sort((a, b) => b.length - a.length);
            sortedMatches.forEach(m => {
                const escaped = escapeHtml(m);
                const reg = new RegExp(`(${escaped})`, 'gi');
                renderedHtml = renderedHtml.replace(reg, '<mark style="background-color: #fef08a; padding: 2px 4px; border-radius: 3px; font-weight: 700; color: #854d0e;">$1</mark>');
            });
        }
        highlightedOutput.innerHTML = renderedHtml;
        showToast(`Found ${data.match_count} match(es)`);

    } catch (err) {
        showToast('Regex evaluation failed: ' + err.message);
    }
}

// ==================== 3. DFA SIMULATOR ====================
let dfaConfig = null;
let currentDfaTrace = [];
let currentDfaStepIndex = 0;

function initializeDfaSimulator() {
    loadDfaConfiguration();

    const runBtn = document.getElementById('run-btn');
    const stepBtn = document.getElementById('step-btn');
    const clearBtn = document.getElementById('clear-btn');
    const exampleBtns = document.querySelectorAll('.example-btn');
    const tokenAddBtns = document.querySelectorAll('.btn-token-add');

    if (runBtn) runBtn.addEventListener('click', runFullDFA);
    if (stepBtn) stepBtn.addEventListener('click', stepDfaForward);
    if (clearBtn) clearBtn.addEventListener('click', resetDfaSimulation);

    exampleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const seq = btn.dataset.seq;
            const input = document.getElementById('token-sequence');
            if (input && seq) {
                input.value = seq;
                showToast(`Loaded preset: ${seq}`);
                runFullDFA();
            }
        });
    });

    tokenAddBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const token = btn.dataset.token;
            const input = document.getElementById('token-sequence');
            if (input && token) {
                const current = input.value.trim();
                input.value = current ? `${current}, ${token}` : token;
            }
        });
    });
}

async function loadDfaConfiguration() {
    try {
        const response = await fetch('/api/dfa/config');
        if (!response.ok) return;
        dfaConfig = await response.json();
        renderDfaTopologyGraph(dfaConfig);
        renderTransitionMatrix(dfaConfig);
    } catch (e) {
        console.error('Failed to load DFA config:', e);
    }
}

function renderDfaTopologyGraph(config) {
    const svg = document.getElementById('state-diagram');
    if (!svg || !config) return;

    // Fixed coordinate layout for clear presentation
    // q0 (start), q1 (lure), q2 (pressure), q3 (link), q4 (cred), q_dead (sink)
    const nodeCoords = {
        'q0': { x: 90, y: 130, label: 'q0: Start', type: 'start' },
        'q1': { x: 230, y: 70, label: 'q1: Lure', type: 'intermediate' },
        'q2': { x: 380, y: 70, label: 'q2: Pressure', type: 'intermediate' },
        'q3': { x: 530, y: 70, label: 'q3: Link', type: 'accept' },
        'q4': { x: 680, y: 70, label: 'q4: Credential', type: 'accept' },
        'q_dead': { x: 410, y: 210, label: 'q_dead: Sink', type: 'dead' }
    };

    let svgHtml = `
        <defs>
            <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
                <polygon points="0 0, 8 3, 0 6" fill="#94a3b8" />
            </marker>
            <marker id="arrow-active" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
                <polygon points="0 0, 8 3, 0 6" fill="#6366f1" />
            </marker>
        </defs>
        
        <!-- Start Arrow into q0 -->
        <path d="M 25 130 L 62 130" stroke="#818cf8" stroke-width="2.5" marker-end="url(#arrow)" />
        <text x="42" y="122" font-family="Plus Jakarta Sans" font-size="11" font-weight="700" fill="#a5b4fc" text-anchor="middle">START</text>

        <!-- Forward Transition Edges -->
        <!-- q0 -> q1 (LURE) -->
        <path d="M 112 110 L 205 80" stroke="#64748b" stroke-width="1.8" marker-end="url(#arrow)" />
        <text x="150" y="85" font-family="JetBrains Mono" font-size="10" font-weight="600" fill="#cbd5e1">LURE</text>

        <!-- q0 -> q2 (URGENT) -->
        <path d="M 115 130 C 180 160, 290 140, 355 88" stroke="#64748b" stroke-width="1.8" marker-end="url(#arrow)" fill="none" />
        <text x="210" y="152" font-family="JetBrains Mono" font-size="10" font-weight="600" fill="#cbd5e1">URGENT</text>

        <!-- q1 -> q2 (URGENT) -->
        <path d="M 255 70 L 352 70" stroke="#64748b" stroke-width="1.8" marker-end="url(#arrow)" />
        <text x="303" y="62" font-family="JetBrains Mono" font-size="10" font-weight="600" fill="#cbd5e1">URGENT</text>

        <!-- q2 -> q3 (URL) -->
        <path d="M 405 70 L 502 70" stroke="#64748b" stroke-width="1.8" marker-end="url(#arrow)" />
        <text x="453" y="62" font-family="JetBrains Mono" font-size="10" font-weight="600" fill="#cbd5e1">URL</text>

        <!-- q3 -> q4 (CREDENTIAL) -->
        <path d="M 555 70 L 652 70" stroke="#64748b" stroke-width="1.8" marker-end="url(#arrow)" />
        <text x="603" y="62" font-family="JetBrains Mono" font-size="10" font-weight="600" fill="#cbd5e1">CREDENTIAL</text>

        <!-- q0/q1/q2 -> q_dead edges (Sink) -->
        <path d="M 230 95 L 385 200" stroke="#475569" stroke-width="1.2" stroke-dasharray="3 3" marker-end="url(#arrow)" />
        <path d="M 380 95 L 405 185" stroke="#475569" stroke-width="1.2" stroke-dasharray="3 3" marker-end="url(#arrow)" />
        <text x="300" y="215" font-family="JetBrains Mono" font-size="10" fill="#94a3b8">OTHER (Invalid) →</text>
    `;

    // Render State Circles
    Object.keys(nodeCoords).forEach(stateId => {
        const node = nodeCoords[stateId];
        const isAccept = config.accepting_states?.includes(stateId);
        const isDead = stateId === config.dead_state;
        const isStart = stateId === config.initial_state;

        let circleFill = '#1e293b';
        let strokeColor = '#64748b';
        let strokeWidth = 2;

        if (isStart) {
            strokeColor = '#6366f1';
            strokeWidth = 2.5;
        } else if (isAccept) {
            strokeColor = '#f43f5e';
            strokeWidth = 2.5;
        } else if (isDead) {
            circleFill = '#0f172a';
            strokeColor = '#475569';
        }

        svgHtml += `
            <g class="dfa-node" id="node-${stateId}" data-state="${stateId}">
                ${isAccept ? `<circle cx="${node.x}" cy="${node.y}" r="32" fill="none" stroke="${strokeColor}" stroke-width="1.5" />` : ''}
                <circle cx="${node.x}" cy="${node.y}" r="26" fill="${circleFill}" stroke="${strokeColor}" stroke-width="${strokeWidth}" class="node-circle" id="circle-${stateId}" />
                <text x="${node.x}" y="${node.y + 4}" text-anchor="middle" font-family="JetBrains Mono" font-size="12" font-weight="700" fill="#ffffff">${stateId}</text>
                <text x="${node.x}" y="${node.y + (stateId === 'q_dead' ? 38 : -32)}" text-anchor="middle" font-family="Plus Jakarta Sans" font-size="10" font-weight="600" fill="#94a3b8">${node.label.split(':')[1]}</text>
            </g>
        `;
    });

    svg.innerHTML = svgHtml;
    highlightActiveStateNode('q0');
}

function renderTransitionMatrix(config) {
    const table = document.getElementById('transition-table');
    if (!table || !config || !config.transition_table) return;

    const alphabet = config.alphabet || [];
    let thead = '<thead><tr><th>State Q</th>';
    alphabet.forEach(sym => {
        thead += `<th>${sym}</th>`;
    });
    thead += '<th>Accepting?</th></tr></thead>';

    let tbody = '<tbody>';
    config.transition_table.forEach(row => {
        const isAccept = config.accepting_states?.includes(row.state);
        tbody += `<tr id="matrix-row-${row.state}">`;
        tbody += `<td class="state-col">${row.state}</td>`;
        alphabet.forEach(sym => {
            const next = row[sym] || '—';
            tbody += `<td class="font-mono text-sm" id="cell-${row.state}-${sym}">${next}</td>`;
        });
        tbody += `<td>${isAccept ? '<span class="status-indicator-dot dot-rose"></span> <strong class="text-rose">Accept (Spam)</strong>' : '<span class="status-indicator-dot dot-gray"></span> Reject'}</td>`;
        tbody += '</tr>';
    });
    tbody += '</tbody>';

    table.innerHTML = thead + tbody;
}

function highlightActiveStateNode(stateId) {
    document.querySelectorAll('.node-circle').forEach(c => {
        c.style.filter = 'none';
        c.setAttribute('stroke', c.parentElement.dataset.state.startsWith('q3') || c.parentElement.dataset.state.startsWith('q4') ? '#f43f5e' : '#64748b');
    });

    const activeCircle = document.getElementById(`circle-${stateId}`);
    if (activeCircle) {
        activeCircle.setAttribute('stroke', '#6366f1');
        activeCircle.style.filter = 'drop-shadow(0 0 8px rgba(99, 102, 241, 0.9))';
    }

    const badge = document.getElementById('current-state-badge');
    const desc = document.getElementById('current-state-desc');
    if (badge) badge.textContent = `${stateId}`;
    if (desc && dfaConfig && dfaConfig.state_descriptions) {
        desc.textContent = dfaConfig.state_descriptions[stateId] || 'State active';
    }
}

async function runFullDFA() {
    const input = document.getElementById('token-sequence');
    if (!input) return;

    const raw = input.value.trim();
    if (!raw) {
        showToast('Please enter tokens (e.g. LURE, URGENT, URL)');
        return;
    }

    const tokens = raw.split(',').map(t => t.trim().toUpperCase()).filter(Boolean);
    if (tokens.length === 0) {
        showToast('No valid tokens provided.');
        return;
    }

    try {
        const response = await fetch('/api/dfa/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tokens })
        });

        const data = await response.json();
        if (!response.ok) {
            showToast(data.error || 'DFA execution error');
            return;
        }

        currentDfaTrace = data.trace || [];
        currentDfaStepIndex = currentDfaTrace.length;

        // Render final result
        const resultsBox = document.getElementById('run-results');
        const statusBadge = document.getElementById('acceptance-status');
        const finalDisplay = document.getElementById('final-state-display');
        const verdictBanner = document.getElementById('sim-verdict-banner');

        if (resultsBox) resultsBox.classList.remove('hidden');

        const isAccepted = data.is_accepted;
        if (statusBadge) {
            statusBadge.textContent = isAccepted ? 'SEQUENCE ACCEPTED (SPAM PATTERN)' : 'SEQUENCE REJECTED (SAFE OR INCOMPLETE)';
            statusBadge.className = `verdict-title ${isAccepted ? 'text-rose' : 'text-emerald'}`;
        }

        if (verdictBanner) {
            verdictBanner.className = `verdict-banner sim-verdict ${isAccepted ? 'verdict-spam' : 'verdict-legitimate'}`;
        }

        if (finalDisplay) {
            finalDisplay.innerHTML = `
                <span>Final State: <strong>${data.final_state}</strong></span>
                <span class="badge-status ${isAccepted ? 'status-spam' : 'status-legitimate'}" style="margin-top: 0.35rem; display: inline-block;">
                    ${isAccepted ? 'Accepting (q ∈ F)' : 'Non-Accepting (q ∉ F)'}
                </span>
            `;
        }

        // Render Trace Table
        renderDfaTraceTable(currentDfaTrace, currentDfaTrace.length - 1);
        highlightActiveStateNode(data.final_state);
        showToast(`DFA terminated at state ${data.final_state}`);

    } catch (err) {
        showToast('Simulation failed: ' + err.message);
    }
}

function renderDfaTraceTable(trace, activeIndex) {
    const tbody = document.querySelector('#trace-table tbody');
    if (!tbody) return;

    tbody.innerHTML = '';
    trace.forEach((step, idx) => {
        const tr = document.createElement('tr');
        if (idx === activeIndex) tr.className = 'active-step';
        tr.innerHTML = `
            <td class="font-mono text-muted">#${idx + 1}</td>
            <td class="font-mono font-bold text-main">${step.current_state}</td>
            <td><span class="token ${step.input_token.toLowerCase()}">${step.input_token}</span></td>
            <td class="font-mono font-bold text-primary">${step.next_state}</td>
            <td class="text-sm text-slate-600">${escapeHtml(step.state_description || '')}</td>
        `;
        tbody.appendChild(tr);
    });
}

function stepDfaForward() {
    if (!currentDfaTrace || currentDfaTrace.length === 0) {
        runFullDFA();
        currentDfaStepIndex = 0;
    }

    if (currentDfaStepIndex >= currentDfaTrace.length) {
        currentDfaStepIndex = 0;
    }

    const step = currentDfaTrace[currentDfaStepIndex];
    if (step) {
        highlightActiveStateNode(step.next_state);
        renderDfaTraceTable(currentDfaTrace, currentDfaStepIndex);
        showToast(`Step ${currentDfaStepIndex + 1}: ${step.current_state} + ${step.input_token} → ${step.next_state}`);
        currentDfaStepIndex++;
    }
}

function resetDfaSimulation() {
    currentDfaTrace = [];
    currentDfaStepIndex = 0;
    document.getElementById('run-results')?.classList.add('hidden');
    document.querySelector('#trace-table tbody').innerHTML = '';
    highlightActiveStateNode('q0');
    showToast('DFA Reset to q0');
}

// ==================== 4. SCAN HISTORY ====================
function initializeHistory() {
    const clearBtn = document.getElementById('clear-history-btn');
    const filterTabs = document.querySelectorAll('.filter-tab');
    const searchInput = document.getElementById('history-search');

    if (clearBtn) {
        clearBtn.addEventListener('click', confirmClearAllHistory);
    }

    // Filter tabs
    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            filterHistoryRows();
        });
    });

    if (searchInput) {
        searchInput.addEventListener('input', filterHistoryRows);
    }

    // Modal inspect handler
    document.addEventListener('click', (e) => {
        const target = e.target.closest('.view-btn');
        if (target) {
            const scanId = target.dataset.scanId;
            if (scanId) inspectScanDetails(scanId);
        } else if (e.target.closest('.close-btn')) {
            document.getElementById('view-modal')?.classList.add('hidden');
        }
    });

    // Close on backdrop click
    const modalBackdrop = document.getElementById('view-modal');
    if (modalBackdrop) {
        modalBackdrop.addEventListener('click', (e) => {
            if (e.target === modalBackdrop) {
                modalBackdrop.classList.add('hidden');
            }
        });
    }
}

function filterHistoryRows() {
    const activeTab = document.querySelector('.filter-tab.active');
    const filterValue = activeTab ? activeTab.dataset.filter : 'all';
    const searchQuery = (document.getElementById('history-search')?.value || '').toLowerCase().trim();

    const rows = document.querySelectorAll('#scan-table tbody tr.scan-row');
    rows.forEach(row => {
        const classification = row.dataset.classification || '';
        const text = row.textContent.toLowerCase();

        const matchesFilter = filterValue === 'all' || classification === filterValue;
        const matchesSearch = !searchQuery || text.includes(searchQuery);

        if (matchesFilter && matchesSearch) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

async function confirmClearAllHistory() {
    if (!confirm('Are you sure you want to delete all historical email scan records from SQLite?')) {
        return;
    }

    try {
        const response = await fetch('/api/history/clear', { method: 'POST' });
        if (response.ok) {
            showToast('Scan history cleared');
            window.location.reload();
        } else {
            const err = await response.json();
            alert('Error clearing history: ' + (err.error || 'Unknown'));
        }
    } catch (e) {
        alert('Network error: ' + e.message);
    }
}

async function inspectScanDetails(scanId) {
    const modal = document.getElementById('view-modal');
    const modalBody = document.getElementById('modal-body');
    if (!modal || !modalBody) return;

    modalBody.innerHTML = '<div style="padding: 2rem; text-align: center;"><div class="scanner-radar"></div><p>Fetching forensic record from SQLite...</p></div>';
    modal.classList.remove('hidden');

    try {
        const response = await fetch(`/api/history/${scanId}`);
        const data = await response.json();
        if (!response.ok) {
            modalBody.innerHTML = `<p class="text-rose">Error: ${escapeHtml(data.error || 'Record not found')}</p>`;
            return;
        }

        // Reconstruct regex matches
        let matchesHtml = '<p class="text-muted" style="font-size:0.85rem;">No regex patterns detected.</p>';
        if (data.regex_matches) {
            try {
                const matches = typeof data.regex_matches === 'string' ? JSON.parse(data.regex_matches) : data.regex_matches;
                if (Array.isArray(matches) && matches.length > 0) {
                    matchesHtml = matches.map(m => `
                        <div class="match-item" style="margin-bottom:0.4rem;">
                            <strong>${escapeHtml(m.pattern_name)}</strong> (${m.match_count} match${m.match_count === 1 ? '' : 'es'})
                            <p style="margin:0; font-size:0.78rem; color:var(--slate-500);">${escapeHtml(m.description)}</p>
                        </div>
                    `).join('');
                }
            } catch (e) {}
        }

        // Reconstruct DFA result
        let dfaHtml = '<p class="text-muted" style="font-size:0.85rem;">No DFA trace available.</p>';
        let dfaTokens = [];
        if (data.dfa_result) {
            try {
                const dfa = typeof data.dfa_result === 'string' ? JSON.parse(data.dfa_result) : data.dfa_result;
                dfaTokens = dfa.tokens || [];
                dfaHtml = `
                    <div style="font-size:0.85rem; line-height: 1.6;">
                        <p><strong>Tokens Recognized (Σ*):</strong> ${dfaTokens.length ? dfaTokens.join(' → ') : 'None'}</p>
                        <p><strong>Final State:</strong> <code class="font-mono">${escapeHtml(dfa.final_state || 'q0')}</code></p>
                        <p><strong>Verdict:</strong> ${dfa.is_accepted ? '<span class="text-rose font-bold">Accepted Threat Pattern (Spam)</span>' : '<span class="text-emerald font-bold">Rejected (Benign / Incomplete)</span>'}</p>
                    </div>
                `;
            } catch (e) {}
        }

        modalBody.innerHTML = `
            <div class="result-card">
                <div class="result-header">
                    <span class="badge-code font-mono">Scan Record #${data.id}</span>
                    <span class="badge-status status-${data.classification.toLowerCase()}">${data.classification}</span>
                </div>
                
                <div class="result-grid">
                    <div class="result-item">
                        <span class="result-label">Email Subject</span>
                        <span class="result-value" style="font-size:0.88rem;">${escapeHtml(data.subject || 'Untitled Content')}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Calculated Risk Score</span>
                        <span class="result-value font-mono ${data.heuristic_risk_score >= 60 ? 'text-rose' : data.heuristic_risk_score >= 30 ? 'text-amber' : 'text-emerald'}">
                            ${Number(data.heuristic_risk_score).toFixed(1)} / 100
                        </span>
                    </div>
                </div>

                <div class="dfa-box">
                    <h4>Automata DFA Analysis:</h4>
                    ${dfaHtml}
                </div>

                <div class="token-box">
                    <h4>Token Sequence:</h4>
                    <div class="token-badges-stream">
                        ${dfaTokens.length > 0 ? dfaTokens.map(t => `<span class="token ${t.toLowerCase()}">${escapeHtml(t)}</span>`).join('') : '<span class="text-muted">None</span>'}
                    </div>
                </div>

                <div class="matches-box">
                    <h4>Matched Regex Heuristics:</h4>
                    ${matchesHtml}
                </div>

                <div class="explanation-box">
                    <h4>Logged Timestamp</h4>
                    <p class="font-mono text-sm text-muted">${escapeHtml(data.timestamp || '')}</p>
                </div>
            </div>
        `;
    } catch (err) {
        modalBody.innerHTML = `<p class="text-rose">Inspection failed: ${escapeHtml(err.message)}</p>`;
    }
}
