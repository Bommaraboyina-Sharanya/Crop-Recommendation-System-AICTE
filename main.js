// Speech Recognition Setup
let recognition = null;
let currentField = null;
let currentLanguage = 'en';
let isRecognitionActive = false;

// Language codes for speech recognition
const speechLanguages = {
    'en': 'en-US',
    'hi': 'hi-IN',
    'te': 'te-IN',
    'ta': 'ta-IN',
    'ml': 'ml-IN',
    'kn': 'kn-IN',
    'mr': 'mr-IN',
    'bn': 'bn-IN',
    'gu': 'gu-IN',
    'pa': 'pa-IN'
};

// Initialize speech recognition if available
function initializeRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        console.log('Speech recognition initialized successfully');
        return true;
    } else {
        console.warn('Speech recognition not supported in this browser');
        return false;
    }
}

// Call initialization
const recognitionSupported = initializeRecognition();

// Translations for UI elements
const translations = {
    'en': {
        'form-title': 'Enter Soil & Climate Parameters',
        'results-title': 'Recommended Crop',
        'instructions-title': 'How to Use',
        'voiceBtnText': 'Voice Input',
        'predictBtn': 'Get Recommendation',
        'label-nitrogen': 'Nitrogen (N) - kg/ha',
        'label-phosphorus': 'Phosphorus (P) - kg/ha',
        'label-potassium': 'Potassium (K) - kg/ha',
        'label-temperature': 'Temperature (°C)',
        'label-humidity': 'Humidity (%)',
        'label-ph': 'Soil pH',
        'label-rainfall': 'Rainfall (mm)'
    }
};

// Change language
function changeLanguage() {
    currentLanguage = document.getElementById('language').value;
    
    // Update speech recognition language
    if (recognition) {
        recognition.lang = speechLanguages[currentLanguage] || 'en-US';
    }
    
    // Translate UI elements
    translateUI();
}

// Translate UI elements
async function translateUI() {
    if (currentLanguage === 'en') {
        // Use English defaults
        Object.keys(translations['en']).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                if (element.tagName === 'BUTTON') {
                    element.textContent = translations['en'][key];
                } else if (element.tagName === 'SPAN') {
                    element.textContent = translations['en'][key];
                } else {
                    element.textContent = translations['en'][key];
                }
            }
        });
        return;
    }
    
    // Translate each UI element
    for (const [key, text] of Object.entries(translations['en'])) {
        try {
            const response = await fetch('/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    target_lang: currentLanguage
                })
            });
            
            const data = await response.json();
            if (data.success) {
                const element = document.getElementById(key);
                if (element) {
                    if (element.tagName === 'BUTTON') {
                        element.textContent = data.translated;
                    } else if (element.tagName === 'SPAN') {
                        element.textContent = data.translated;
                    } else {
                        element.textContent = data.translated;
                    }
                }
            }
        } catch (error) {
            console.error('Translation error:', error);
        }
    }
}

// Start voice input for specific field
function startVoiceForField(fieldName, evt) {
    console.log('=== startVoiceForField called for:', fieldName, '===');
    
    if (!recognition) {
        alert('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
        return;
    }
    
    // Stop if already active
    if (isRecognitionActive) {
        console.log('Recognition already active, stopping it first');
        try {
            recognition.abort();
        } catch (e) {
            console.error('Error aborting recognition:', e);
        }
        isRecognitionActive = false;
        // Wait a moment before continuing
        setTimeout(() => startVoiceForField(fieldName, evt), 300);
        return;
    }
    
    const micBtn = evt && evt.target ? evt.target : document.querySelector(`button[onclick*="'${fieldName}'"]`);
    const input = document.getElementById(fieldName);
    
    if (!input) {
        console.error('Could not find input field:', fieldName);
        return;
    }
    
    console.log('Starting speech recognition for field:', fieldName);
    console.log('Input element:', input);
    console.log('Mic button:', micBtn);
    
    // Add visual feedback
    if (micBtn) {
        micBtn.classList.add('listening');
        micBtn.style.background = '#ff4444';
    }
    
    // Configure recognition for this session
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.lang = speechLanguages[currentLanguage] || 'en-US';
    
    console.log('Recognition language set to:', recognition.lang);
    
    // Set up event handlers
    recognition.onstart = function() {
        isRecognitionActive = true;
        console.log('✅ Recognition STARTED successfully');
    };
    
    recognition.onresult = function(event) {
        console.log('✅ Recognition RESULT received');
        console.log('Event results:', event.results);
        
        if (event.results && event.results.length > 0) {
            const transcript = event.results[0][0].transcript;
            const confidence = event.results[0][0].confidence;
            
            console.log('Transcript:', transcript);
            console.log('Confidence:', confidence);
            
            // Extract number from transcript
            const number = extractNumber(transcript);
            if (number !== null) {
                input.value = number;
                console.log('✅ Set input value to NUMBER:', number);
            } else {
                input.value = transcript;
                console.log('✅ Set input value to TEXT:', transcript);
            }
        }
    };
    
    recognition.onerror = function(event) {
        console.error('❌ Recognition ERROR:', event.error);
        console.error('Error event:', event);
        
        isRecognitionActive = false;
        if (micBtn) {
            micBtn.classList.remove('listening');
            micBtn.style.background = '';
        }
        
        // Show specific error messages
        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
            alert('❌ Microphone access denied!\n\nPlease:\n1. Click the 🔒 lock icon in the address bar\n2. Allow microphone access\n3. Refresh the page and try again');
        } else if (event.error === 'no-speech') {
            console.log('No speech detected - this is normal if you didn\'t speak');
            alert('No speech detected. Please try again and speak clearly.');
        } else if (event.error === 'audio-capture') {
            alert('❌ No microphone found!\n\nPlease check:\n1. Microphone is connected\n2. Microphone is not being used by another app\n3. Microphone is selected as default device');
        } else if (event.error === 'network') {
            alert('❌ Network error!\n\nSpeech recognition needs internet connection.\nPlease check your connection and try again.');
        } else if (event.error === 'aborted') {
            console.log('Recognition aborted');
        } else {
            alert('Speech recognition error: ' + event.error);
        }
    };
    
    recognition.onend = function() {
        console.log('Recognition ENDED');
        isRecognitionActive = false;
        if (micBtn) {
            micBtn.classList.remove('listening');
            micBtn.style.background = '';
        }
    };
    
    // Start recognition
    try {
        console.log('Calling recognition.start()...');
        recognition.start();
        console.log('recognition.start() called successfully');
    } catch (error) {
        console.error('❌ Exception when calling start():', error);
        isRecognitionActive = false;
        if (micBtn) {
            micBtn.classList.remove('listening');
            micBtn.style.background = '';
        }
        
        if (error.name === 'InvalidStateError') {
            alert('Speech recognition is already running. Please wait a moment and try again.');
        } else {
            alert('Failed to start speech recognition:\n' + error.message);
        }
    }
}

// Extract number from text
function extractNumber(text) {
    // Remove common words and extract digits
    const cleaned = text.toLowerCase()
        .replace(/point/g, '.')
        .replace(/decimal/g, '.')
        .replace(/dot/g, '.');
    
    // Try to find a number
    const match = cleaned.match(/[\d.]+/);
    return match ? parseFloat(match[0]) : null;
}

// Toggle continuous voice input
function toggleVoiceInput() {
    console.log('=== toggleVoiceInput called ===');
    
    if (!recognition) {
        alert('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
        return;
    }
    
    const btn = document.getElementById('voiceBtn');
    const status = document.getElementById('voiceStatus');
    
    if (!btn || !status) {
        console.error('Could not find voice button or status element');
        return;
    }
    
    if (btn.classList.contains('listening')) {
        // Stop listening
        console.log('Stopping continuous voice input');
        try {
            recognition.abort();
        } catch (e) {
            console.error('Error stopping recognition:', e);
        }
        btn.classList.remove('listening');
        status.textContent = '';
        isRecognitionActive = false;
        return;
    }
    
    // Start listening
    console.log('Starting continuous voice input');
    btn.classList.add('listening');
    status.textContent = '🎤 Listening... Speak field names and values';
    
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.lang = speechLanguages[currentLanguage] || 'en-US';
    
    recognition.onstart = function() {
        isRecognitionActive = true;
        console.log('✅ Continuous recognition STARTED');
    };
    
    recognition.onresult = function(event) {
        const transcript = event.results[event.results.length - 1][0].transcript.toLowerCase();
        console.log('Heard:', transcript);
        status.textContent = `Heard: "${transcript}"`;
        
        // Smart field detection
        if (transcript.includes('nitrogen')) {
            const num = extractNumber(transcript);
            if (num) {
                document.getElementById('nitrogen').value = num;
                console.log('Set nitrogen to:', num);
            }
        } else if (transcript.includes('phosphorus')) {
            const num = extractNumber(transcript);
            if (num) {
                document.getElementById('phosphorus').value = num;
                console.log('Set phosphorus to:', num);
            }
        } else if (transcript.includes('potassium')) {
            const num = extractNumber(transcript);
            if (num) {
                document.getElementById('potassium').value = num;
                console.log('Set potassium to:', num);
            }
        } else if (transcript.includes('temperature')) {
            const num = extractNumber(transcript);
            if (num) {
                document.getElementById('temperature').value = num;
                console.log('Set temperature to:', num);
            }
        } else if (transcript.includes('humidity')) {
            const num = extractNumber(transcript);
            if (num) {
                document.getElementById('humidity').value = num;
                console.log('Set humidity to:', num);
            }
        } else if (transcript.includes('ph') || transcript.includes('p h')) {
            const num = extractNumber(transcript);
            if (num) {
                document.getElementById('ph').value = num;
                console.log('Set pH to:', num);
            }
        } else if (transcript.includes('rainfall') || transcript.includes('rain')) {
            const num = extractNumber(transcript);
            if (num) {
                document.getElementById('rainfall').value = num;
                console.log('Set rainfall to:', num);
            }
        }
    };
    
    recognition.onerror = function(event) {
        console.error('❌ Continuous recognition ERROR:', event.error);
        btn.classList.remove('listening');
        isRecognitionActive = false;
        
        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
            status.textContent = '❌ Microphone access denied';
        } else if (event.error === 'no-speech') {
            status.textContent = '⚠️ No speech detected';
        } else if (event.error === 'audio-capture') {
            status.textContent = '❌ No microphone found';
        } else if (event.error === 'network') {
            status.textContent = '❌ Network error';
        } else if (event.error === 'aborted') {
            status.textContent = '';
        } else {
            status.textContent = `❌ Error: ${event.error}`;
        }
    };
    
    recognition.onend = function() {
        console.log('Continuous recognition ENDED');
        btn.classList.remove('listening');
        isRecognitionActive = false;
        if (status.textContent.includes('Listening')) {
            status.textContent = '';
        }
    };
    
    try {
        console.log('Starting continuous recognition...');
        recognition.start();
    } catch (error) {
        console.error('❌ Exception starting continuous recognition:', error);
        btn.classList.remove('listening');
        isRecognitionActive = false;
        status.textContent = `❌ Error: ${error.message}`;
    }
}

// Form submission
document.getElementById('predictionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        nitrogen: document.getElementById('nitrogen').value,
        phosphorus: document.getElementById('phosphorus').value,
        potassium: document.getElementById('potassium').value,
        temperature: document.getElementById('temperature').value,
        humidity: document.getElementById('humidity').value,
        ph: document.getElementById('ph').value,
        rainfall: document.getElementById('rainfall').value,
        language: currentLanguage
    };
    
    // Show loading
    const resultsSection = document.getElementById('resultsSection');
    const resultsDiv = document.getElementById('results');
    resultsSection.style.display = 'block';
    resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>Analyzing your data...</p></div>';
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            resultsDiv.innerHTML = `<div class="error">Error: ${data.error}</div>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<div class="error">Failed to connect to server. Please try again.</div>`;
        console.error('Error:', error);
    }
});

// Display results
function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    const info = data.info;
    
    resultsDiv.innerHTML = `
        <div class="crop-name">🌱 ${info.name}</div>
        <div class="crop-info">
            <div class="info-item">
                <strong>📖 Description</strong>
                <p>${info.description}</p>
            </div>
            <div class="info-item">
                <strong>📅 Season</strong>
                <p>${info.season}</p>
            </div>
            <div class="info-item">
                <strong>🌍 Soil Type</strong>
                <p>${info.soil_type}</p>
            </div>
            <div class="info-item">
                <strong>💡 Tips</strong>
                <p>${info.tips}</p>
            </div>
        </div>
    `;
    
    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Set initial language
    if (recognition) {
        recognition.lang = 'en-US';
    }
});
