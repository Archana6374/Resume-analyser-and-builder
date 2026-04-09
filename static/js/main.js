function validateFile() {
    alert("Button clicked");
    window.location.href = "/parsed/";
}

console.log('chatbot main.js loaded');
window.chatbotLoaded = true;

// Chatbot variables
let chatExpanded = false;
let resumeText = ""; // Will store uploaded resume text if available
let chatHistory = [];

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Toggle chatbot
function toggleChat() {
    const container = document.getElementById('chatbot-container');
    const toggle = document.getElementById('chatbot-toggle');
    if (!container || !toggle) return;
    chatExpanded = !chatExpanded;
    container.classList.toggle('chatbot-open', chatExpanded);
    toggle.innerText = chatExpanded ? '_' : '+';
}

document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('chatbot-container');
    const toggle = document.getElementById('chatbot-toggle');
    if (container) {
        container.classList.remove('chatbot-open');
    }
    if (toggle) {
        toggle.innerText = '+';
    }

    // Handle navigation links with data-target
    // document.querySelectorAll('a[data-target]').forEach(link => {
    //     link.addEventListener('click', function(e) {
    //         e.preventDefault();
    //         const target = this.getAttribute('data-target');
    //         const href = this.getAttribute('href');
    //         if (target && document.getElementById(target)) {
    //             if (typeof setVisible === 'function') setVisible(target);
    //         } else if (href) {
    //             window.location.href = href;
    //         }
    //     });
    // });
});

// Send message
async function sendChatMessage() {
    console.log('sendChatMessage called');
    const inputEl = document.getElementById('chatbot-input');
    const chatBox = document.getElementById('chatbot-messages');
    const typingIndicator = document.getElementById('chatbot-typing');
    if (!inputEl) {
        console.error('chatbot input element missing');
        return;
    }
    const userMessage = inputEl.value.trim();
    if(!userMessage) return;

    console.log('chatbot sending:', userMessage);
    const userMessageEl = document.createElement('div');
    userMessageEl.className = 'message user';
    userMessageEl.textContent = userMessage;
    chatBox.appendChild(userMessageEl);
    requestAnimationFrame(() => userMessageEl.classList.add('visible'));
    chatBox.scrollTop = chatBox.scrollHeight;
    inputEl.value = '';
    typingIndicator.style.display = 'block';

    chatHistory.push({ role: 'user', content: userMessage });

    try {
        const response = await fetch('/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                message: userMessage,
                chat_history: chatHistory,
                resume_text: resumeText
            })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Chatbot request failed');
        }

        const botMessage = document.createElement('div');
        botMessage.className = 'message bot';
        botMessage.textContent = data.reply;
        chatBox.appendChild(botMessage);
        requestAnimationFrame(() => botMessage.classList.add('visible'));
        chatHistory.push({ role: 'bot', content: data.reply });
    } catch (error) {
        chatBox.innerHTML += `<div class="message bot">Sorry, the resume assistant is unavailable right now.</div>`;
        console.error('Chatbot error:', error);
    } finally {
        chatBox.scrollTop = chatBox.scrollHeight;
        typingIndicator.style.display = 'none';
    }
}

// Call this when you parse the user resume
function setResumeContext(text) {
    resumeText = text;
}

window.toggleChat = toggleChat;
window.sendChatMessage = sendChatMessage;
window.setResumeContext = setResumeContext;
