/**
 * Enhanced chat functionality for the medical expert system
 */

// Make setInput globally accessible
window.setInput = function(text) {
    const input = document.getElementById('message-input');
    const form = document.getElementById('input-form');

    if (!input || !form) return;

    input.value = text;
    input.focus();
    // Trigger form submission
    form.dispatchEvent(new Event('submit'));
};

// Make setInputOnly globally accessible
window.setInputOnly = function(text) {
    const input = document.getElementById('message-input');

    if (!input) return;

    input.value = text;
    input.focus();
};

document.addEventListener('DOMContentLoaded', function() {
    // Initialize chat components
    const form = document.getElementById('input-form');
    const input = document.getElementById('message-input');
    const messages = document.getElementById('messages');
    const typingIndicator = document.getElementById('typing-indicator');
    const suggestionsContainer = document.getElementById('suggestions');

    // Set smooth scrolling behavior
    if (messages) {
        messages.style.scrollBehavior = 'smooth';
    }

    // Add welcome message if no messages exist
    if (messages.children.length === 0) {
        appendMessage('bot', "Hello! I'm your medical expert assistant. How can I help you today?");
    }

    // Handle form submission
    if (form) {
        form.onsubmit = async function(e) {
            e.preventDefault();

            const userMsg = input.value.trim();
            if (!userMsg) return;

            // Add user message to chat
            appendMessage('user', userMsg);
            input.value = '';

            // Show typing indicator
            showTypingIndicator();

            try {
                // Send message to server using Django's CSRF protection
                const formData = new FormData();
                formData.append('message', userMsg);

                const response = await fetch('', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                });

                // Hide typing indicator
                hideTypingIndicator();

                // Get response data
                const data = await response.json();

                // Add bot response to chat
                appendMessage('bot', data.response);

                // Handle suggestions if provided
                if (data.suggestions && data.suggestions.length > 0) {
                    showSuggestions(data.suggestions);
                } else {
                    clearSuggestions();
                }

                // If it's a structured form question, ensure suggestions are cleared
                if (data.is_structured_form) {
                    clearSuggestions();
                }

            } catch (error) {
                hideTypingIndicator();
                appendMessage('bot', 'Sorry, there was an error. Please try again.');
                console.error('Error:', error);
            }
        };
    }

    // Function to format time
    function formatTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    // Function to create message HTML
    function createMessageHTML(sender, text) {
        const isUser = sender === 'user';
        const avatarIcon = isUser ? 'bi-person-fill' : 'bi-robot';
        const avatarBg = isUser ? 'var(--primary-color)' : 'var(--success-color)';

        return `
            <div class="message ${sender}">
                <div class="message-avatar" style="background-color: ${avatarBg};">
                    <i class="bi ${avatarIcon}"></i>
                </div>
                <div class="message-content">
                    <div>${text}</div>
                    <div class="message-time">${formatTime()}</div>
                </div>
            </div>
        `;
    }

    // Function to append message to chat
    function appendMessage(sender, text) {
        if (!messages) return;

        const messageHTML = createMessageHTML(sender, text);
        messages.insertAdjacentHTML('beforeend', messageHTML);
        messages.scrollTop = messages.scrollHeight;
    }

    // Function to show typing indicator
    function showTypingIndicator() {
        if (typingIndicator) {
            typingIndicator.style.display = 'block';
            if (messages) {
                messages.scrollTop = messages.scrollHeight;
            }
        }
    }

    // Function to hide typing indicator
    function hideTypingIndicator() {
        if (typingIndicator) {
            typingIndicator.style.display = 'none';
        }
    }

    // Function to clear suggestions
    function clearSuggestions() {
        if (suggestionsContainer) {
            suggestionsContainer.innerHTML = '';
        }
    }

    // Function to show suggestions
    function showSuggestions(suggestions) {
        if (!suggestionsContainer || !suggestions || suggestions.length === 0) {
            clearSuggestions();
            return;
        }

        clearSuggestions();
        suggestionsContainer.innerHTML = '';

        const suggestionsHTML = suggestions.map(suggestion => 
            `<button class="suggestion-chip" onclick="setInput('${suggestion}')">${suggestion}</button>`
        ).join('');

        suggestionsContainer.innerHTML = `<div class="suggestions-container">${suggestionsHTML}</div>`;
    }

    // Function to set input value
    function setInput(text) {
        if (!input || !form) return;
        input.value = text;
        input.focus();
        // Trigger form submission
        form.dispatchEvent(new Event('submit'));
    }

    // Function to set input value without submitting
    function setInputOnly(text) {
        if (!input) return;
        input.value = text;
        input.focus();
    }

    // Function to get cookie value
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

    // Add enter key support for sending messages
    if (input && form) {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                form.dispatchEvent(new Event('submit'));
            }
        });
    }

    // Add click handlers for suggestion chips
    const suggestionChips = document.querySelectorAll('.suggestion-chip');
    if (suggestionChips.length > 0) {
        suggestionChips.forEach(chip => {
            chip.addEventListener('click', function() {
                setInput(this.textContent);
            });
        });
    }

    // Add click handler for send button
    const sendButton = document.querySelector('.send-button');
    if (sendButton && form) {
        sendButton.addEventListener('click', function(e) {
            e.preventDefault();
            if (input && input.value.trim()) {
                form.dispatchEvent(new Event('submit'));
            }
        });
    }

    // Initialize with a welcome message and suggestions
    if (messages && messages.children.length === 0) {
        appendMessage('bot', "Hello! I'm your medical expert assistant. How can I help you today?");
        // Add initial suggestions
        showSuggestions([
            "What is a stomach ulcer?",
            "What causes stomach ulcers?",
            "What are the symptoms?",
            "How are ulcers treated?"
        ]);
    }
});
