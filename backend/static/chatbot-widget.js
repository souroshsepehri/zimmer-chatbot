/**
 * Chatbot Widget for External Websites
 * This script creates a floating chatbot widget that can be embedded on any website
 */

(function() {
    'use strict';
    
    // Configuration
    const CONFIG = {
        apiBase: 'http://localhost:8002/api',
        widgetId: 'chatbot-widget-container',
        position: 'bottom-right', // bottom-right, bottom-left, top-right, top-left
        theme: 'light', // light, dark
        language: 'fa'
    };
    
    // Create widget HTML
    function createWidgetHTML() {
        return `
            <div id="${CONFIG.widgetId}" class="chatbot-widget">
                <div class="chatbot-toggle" onclick="toggleChatbot()">
                    <div class="chatbot-icon">🤖</div>
                    <div class="chatbot-close" style="display: none;">✕</div>
                </div>
                <div class="chatbot-window" style="display: none;">
                    <div class="chatbot-header">
                        <div class="chatbot-title">بات هوشمند</div>
                        <div class="chatbot-subtitle">چطور می‌تونم کمکتون کنم؟</div>
                    </div>
                    <div class="chatbot-messages" id="chatbot-messages">
                        <div class="chatbot-message bot">
                            <div class="message-content">
                                سلام! من بات هوشمند هستم. چطور می‌تونم کمکتون کنم؟
                            </div>
                        </div>
                    </div>
                    <div class="chatbot-input-container">
                        <input type="text" id="chatbot-input" placeholder="پیام خود را بنویسید..." />
                        <button onclick="sendMessage()" id="chatbot-send">ارسال</button>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Create widget CSS
    function createWidgetCSS() {
        const style = document.createElement('style');
        style.textContent = `
            .chatbot-widget {
                position: fixed;
                ${CONFIG.position.includes('right') ? 'right: 20px;' : 'left: 20px;'}
                ${CONFIG.position.includes('bottom') ? 'bottom: 20px;' : 'top: 20px;'}
                z-index: 9999;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                direction: rtl;
            }
            
            .chatbot-toggle {
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                transition: transform 0.3s ease;
            }
            
            .chatbot-toggle:hover {
                transform: scale(1.1);
            }
            
            .chatbot-icon, .chatbot-close {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
            
            .chatbot-window {
                position: absolute;
                ${CONFIG.position.includes('right') ? 'right: 0;' : 'left: 0;'}
                ${CONFIG.position.includes('bottom') ? 'bottom: 70px;' : 'top: 70px;'}
                width: 350px;
                height: 500px;
                background: white;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            
            .chatbot-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 20px;
                text-align: center;
            }
            
            .chatbot-title {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            
            .chatbot-subtitle {
                font-size: 14px;
                opacity: 0.9;
            }
            
            .chatbot-messages {
                flex: 1;
                padding: 15px;
                overflow-y: auto;
                background: #f8f9fa;
            }
            
            .chatbot-message {
                margin-bottom: 15px;
                display: flex;
                align-items: flex-start;
            }
            
            .chatbot-message.user {
                justify-content: flex-end;
            }
            
            .message-content {
                max-width: 80%;
                padding: 10px 15px;
                border-radius: 18px;
                word-wrap: break-word;
                font-size: 14px;
            }
            
            .chatbot-message.bot .message-content {
                background: #e3f2fd;
                color: #1565c0;
            }
            
            .chatbot-message.user .message-content {
                background: #667eea;
                color: white;
            }
            
            .chatbot-input-container {
                padding: 15px;
                background: white;
                border-top: 1px solid #e0e0e0;
                display: flex;
                gap: 10px;
            }
            
            .chatbot-input-container input {
                flex: 1;
                padding: 10px 15px;
                border: 1px solid #ddd;
                border-radius: 20px;
                outline: none;
                font-size: 14px;
            }
            
            .chatbot-input-container input:focus {
                border-color: #667eea;
            }
            
            .chatbot-input-container button {
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 14px;
                transition: background 0.3s;
            }
            
            .chatbot-input-container button:hover {
                background: #5a6fd8;
            }
            
            .chatbot-input-container button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            
            .loading {
                text-align: center;
                padding: 10px;
                color: #666;
                font-size: 12px;
            }
            
            @media (max-width: 480px) {
                .chatbot-window {
                    width: 300px;
                    height: 400px;
                }
            }
        `;
        return style;
    }
    
    // Initialize widget
    function initWidget() {
        // Check if widget already exists
        if (document.getElementById(CONFIG.widgetId)) {
            return;
        }
        
        // Create and append CSS
        const style = createWidgetCSS();
        document.head.appendChild(style);
        
        // Create and append widget HTML
        const widgetHTML = createWidgetHTML();
        document.body.insertAdjacentHTML('beforeend', widgetHTML);
        
        // Add event listeners
        setupEventListeners();
    }
    
    // Setup event listeners
    function setupEventListeners() {
        const input = document.getElementById('chatbot-input');
        const sendButton = document.getElementById('chatbot-send');
        
        if (input) {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        }
        
        if (sendButton) {
            sendButton.addEventListener('click', sendMessage);
        }
    }
    
    // Toggle chatbot window
    window.toggleChatbot = function() {
        const widget = document.getElementById(CONFIG.widgetId);
        const window = widget.querySelector('.chatbot-window');
        const icon = widget.querySelector('.chatbot-icon');
        const close = widget.querySelector('.chatbot-close');
        
        if (window.style.display === 'none') {
            window.style.display = 'flex';
            icon.style.display = 'none';
            close.style.display = 'block';
        } else {
            window.style.display = 'none';
            icon.style.display = 'block';
            close.style.display = 'none';
        }
    };
    
    // Send message
    window.sendMessage = function() {
        const input = document.getElementById('chatbot-input');
        const messagesContainer = document.getElementById('chatbot-messages');
        const sendButton = document.getElementById('chatbot-send');
        
        const message = input.value.trim();
        if (!message) return;
        
        // Add user message
        addMessage(message, 'user');
        input.value = '';
        
        // Disable input and show loading
        input.disabled = true;
        sendButton.disabled = true;
        addLoadingMessage();
        
        // Send to API
        fetch(`${CONFIG.apiBase}/dual-answer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: message,
                use_primary_only: false,
                use_secondary_only: false
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading message
            removeLoadingMessage();
            
            // Add bot response
            addMessage(data.answer || 'متأسفانه پاسخ مناسبی پیدا نکردم.', 'bot');
        })
        .catch(error => {
            console.error('Error:', error);
            removeLoadingMessage();
            addMessage('خطا در ارتباط با سرور. لطفاً دوباره تلاش کنید.', 'bot');
        })
        .finally(() => {
            // Re-enable input
            input.disabled = false;
            sendButton.disabled = false;
            input.focus();
        });
    };
    
    // Add message to chat
    function addMessage(text, sender) {
        const messagesContainer = document.getElementById('chatbot-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message ${sender}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = text;
        
        messageDiv.appendChild(contentDiv);
        messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Add loading message
    function addLoadingMessage() {
        const messagesContainer = document.getElementById('chatbot-messages');
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading';
        loadingDiv.id = 'chatbot-loading';
        loadingDiv.textContent = 'در حال پردازش...';
        
        messagesContainer.appendChild(loadingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Remove loading message
    function removeLoadingMessage() {
        const loadingDiv = document.getElementById('chatbot-loading');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initWidget);
    } else {
        initWidget();
    }
    
})();
