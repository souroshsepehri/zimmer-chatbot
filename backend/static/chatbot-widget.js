/**
 * Chatbot Widget for External Websites
 * Universal embeddable script that works on any HTML page
 */

(function() {
    'use strict';
    
    // Read configuration from global config object
    var config = window.ZIMMER_CHATBOT_CONFIG || {};
    var apiBaseUrl = config.apiBaseUrl || "https://chatbot.zimmerai.com";
    var widgetId = 'zimmer-chatbot-widget';
    var isOpen = false;
    
    // Create widget CSS
    function createWidgetCSS() {
        const style = document.createElement('style');
        style.textContent = `
            #${widgetId} {
                position: fixed;
                right: 20px;
                bottom: 20px;
                z-index: 999999;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            #${widgetId} .chatbot-toggle {
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
            
            #${widgetId} .chatbot-toggle:hover {
                transform: scale(1.1);
            }
            
            #${widgetId} .chatbot-icon, #${widgetId} .chatbot-close {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
            
            #${widgetId} .chatbot-window {
                position: absolute;
                right: 0;
                bottom: 70px;
                width: 350px;
                height: 500px;
                background: white;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                display: none;
                overflow: hidden;
            }
            
            #${widgetId} .chatbot-window.open {
                display: block;
            }
            
            #${widgetId} .chatbot-window iframe {
                width: 100%;
                height: 100%;
                border: none;
                border-radius: 15px;
            }
            
            @media (max-width: 480px) {
                #${widgetId} .chatbot-window {
                    width: calc(100vw - 40px);
                    height: calc(100vh - 100px);
                    right: -10px;
                }
            }
        `;
        return style;
    }
    
    // Create widget HTML
    function createWidgetHTML() {
        const widget = document.createElement('div');
        widget.id = widgetId;
        
        const toggle = document.createElement('div');
        toggle.className = 'chatbot-toggle';
        toggle.setAttribute('role', 'button');
        toggle.setAttribute('aria-label', 'Toggle chatbot');
        
        const icon = document.createElement('div');
        icon.className = 'chatbot-icon';
        icon.textContent = '🤖';
        
        const close = document.createElement('div');
        close.className = 'chatbot-close';
        close.style.display = 'none';
        close.textContent = '✕';
        
        toggle.appendChild(icon);
        toggle.appendChild(close);
        
        const window = document.createElement('div');
        window.className = 'chatbot-window';
        
        const iframe = document.createElement('iframe');
        iframe.src = apiBaseUrl + "/static/chat-window.html";
        iframe.setAttribute('title', 'Chatbot Window');
        iframe.setAttribute('allow', 'microphone');
        
        window.appendChild(iframe);
        
        widget.appendChild(toggle);
        widget.appendChild(window);
        
        // Toggle functionality
        toggle.addEventListener('click', function() {
            isOpen = !isOpen;
            if (isOpen) {
                window.classList.add('open');
                icon.style.display = 'none';
                close.style.display = 'block';
            } else {
                window.classList.remove('open');
                icon.style.display = 'block';
                close.style.display = 'none';
            }
        });
        
        return widget;
    }
    
    // Initialize widget
    function initWidget() {
        // Check if widget already exists
        if (document.getElementById(widgetId)) {
            return;
        }
        
        // Wait for body to be available
        function attachWidget() {
            if (document.body) {
                // Create and append CSS
                const style = createWidgetCSS();
                document.head.appendChild(style);
                
                // Create and append widget HTML
                const widget = createWidgetHTML();
                document.body.appendChild(widget);
            } else {
                setTimeout(attachWidget, 10);
            }
        }
        
        attachWidget();
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initWidget);
    } else {
        initWidget();
    }
    
})();
