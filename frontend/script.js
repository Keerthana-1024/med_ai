const API_URL = 'http://localhost:5000';
let sessionId = generateSessionId();

function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function addMessage(text, isUser = false) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = `<p>${text}</p>`;
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function setLoading(isLoading) {
    const sendBtn = document.getElementById('sendBtn');
    const sendBtnText = document.getElementById('sendBtnText');
    const sendBtnLoader = document.getElementById('sendBtnLoader');
    const userInput = document.getElementById('userInput');
    
    sendBtn.disabled = isLoading;
    userInput.disabled = isLoading;
    
    if (isLoading) {
        sendBtnText.style.display = 'none';
        sendBtnLoader.style.display = 'inline-block';
    } else {
        sendBtnText.style.display = 'inline';
        sendBtnLoader.style.display = 'none';
    }
}

async function sendMessage() {
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // Add user message
    addMessage(message, true);
    userInput.value = '';
    
    // Show loading
    setLoading(true);
    
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        
        // Add bot response
        addMessage(data.reply, false);
        
        // Show latency info
        console.log(`Response time: ${data.latency}s`);
        
    } catch (error) {
        console.error('Error:', error);
        addMessage('Sorry, I encountered an error. Please try again.', false);
    } finally {
        setLoading(false);
        userInput.focus();
    }
}

async function resetChat() {
    if (!confirm('Are you sure you want to start a new consultation?')) {
        return;
    }
    
    try {
        await fetch(`${API_URL}/reset`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });
        
        // Clear chat
        const chatContainer = document.getElementById('chatContainer');
        chatContainer.innerHTML = `
            <div class="message bot-message">
                <div class="message-content">
                    <p>Hello! I'm your AI medical assistant. Please describe your symptoms separated by commas (e.g., "headache, fever, cough").</p>
                </div>
            </div>
        `;
        
        // Generate new session ID
        sessionId = generateSessionId();
        
    } catch (error) {
        console.error('Error resetting chat:', error);
    }
}

// Allow Enter key to send message
document.getElementById('userInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});