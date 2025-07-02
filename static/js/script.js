// Auth Page Interactions
document.addEventListener('DOMContentLoaded', function() {
    // Auto-resize textarea in chat input
    const textarea = document.querySelector('.chat-input textarea');
    if (textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }
    
    // Form submission handling
    const authForms = document.querySelectorAll('.auth-form');
    authForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = this.querySelectorAll('input');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.style.borderColor = '#F44336';
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                // Add shake animation to form
                this.classList.add('shake');
                setTimeout(() => {
                    this.classList.remove('shake');
                }, 500);
            }
        });
    });
    
    // Input focus effects
    const formInputs = document.querySelectorAll('.form-group input');
    formInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentNode.querySelector('i').style.color = '#3b0e68';
        });
        
        input.addEventListener('blur', function() {
            this.parentNode.querySelector('i').style.color = '#777';
        });
    });
    
    // Demo chat functionality
    if (document.querySelector('.chat-container')) {
        const suggestionBtns = document.querySelectorAll('.suggestion-btn');
        const chatInput = document.querySelector('.chat-input textarea');
        const sendBtn = document.querySelector('.btn-send');
        
        suggestionBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                chatInput.value = this.textContent;
                chatInput.focus();
                chatInput.dispatchEvent(new Event('input'));
            });
        });
        
        sendBtn.addEventListener('click', function() {
            const message = chatInput.value.trim();
            if (message) {
                addMessage(message, 'user');
                // Simulate AI response after delay
                setTimeout(() => {
                    addMessage(getAIResponse(message), 'ai');
                }, 1000);
                chatInput.value = '';
                chatInput.style.height = 'auto';
            }
        });
        
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendBtn.click();
            }
        });
    }
});

function addMessage(text, sender) {
    const messagesContainer = document.querySelector('.chat-messages');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    
    const avatar = sender === 'user' ? 
        '<i class="fas fa-user-circle"></i>' : 
        '<i class="fas fa-robot"></i>';
    
    messageElement.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">${text}</div>
    `;
    
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Add animation
    messageElement.style.animation = 'fadeInUp 0.3s ease-out';
}

function getAIResponse(userMessage) {
    const responses = [
        "I can help you with that! What specific aspect would you like to know more about?",
        "That's an interesting question. Here's what I found...",
        "I understand you're asking about " + userMessage.toLowerCase() + ". Here's some information that might help.",
        "Thanks for your question! Based on my knowledge, here's what I can tell you...",
        "I'd be happy to assist with that. Could you provide more details about what you're looking for?"
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
}