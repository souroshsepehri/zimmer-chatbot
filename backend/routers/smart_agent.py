"""
Smart Agent API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse
from typing import Optional, Dict, Any
from pydantic import BaseModel
import asyncio

from services.smart_agent import smart_agent
from core.db import get_db
from sqlalchemy.orm import Session

router = APIRouter()

class SmartAgentRequest(BaseModel):
    message: str
    style: Optional[str] = "auto"
    context: Optional[Dict[str, Any]] = None

class SmartAgentResponse(BaseModel):
    response: str
    style: str
    response_time: float
    web_content_used: bool
    urls_processed: list
    context_used: bool
    timestamp: str
    debug_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class URLReadRequest(BaseModel):
    url: str
    max_length: Optional[int] = 5000

class URLReadResponse(BaseModel):
    url: str
    title: str
    description: str
    main_content: str
    links: list
    images: list
    metadata: dict
    timestamp: str
    error: Optional[str] = None

@router.post("/smart-agent/chat", response_model=SmartAgentResponse)
async def smart_agent_chat(
    request: SmartAgentRequest,
    db: Session = Depends(get_db)
):
    """Get smart AI response with multi-style capabilities and web content reading"""
    try:
        result = await smart_agent.get_smart_response(
            message=request.message,
            style=request.style,
            context=request.context
        )
        
        return SmartAgentResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart agent error: {str(e)}")

@router.post("/smart-agent/read-url", response_model=URLReadResponse)
async def read_url_content(
    request: URLReadRequest,
    db: Session = Depends(get_db)
):
    """Read and extract content from a URL"""
    try:
        content = await smart_agent.read_url_content(request.url)
        
        if "error" in content:
            return URLReadResponse(
                url=request.url,
                title="",
                description="",
                main_content="",
                links=[],
                images=[],
                metadata={},
                timestamp=content.get("timestamp", ""),
                error=content["error"]
            )
        
        return URLReadResponse(**content)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL reading error: {str(e)}")

@router.get("/smart-agent/styles")
async def get_available_styles():
    """Get available response styles"""
    try:
        styles = smart_agent.get_available_styles()
        return {
            "styles": styles,
            "default": "auto",
            "total": len(styles)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting styles: {str(e)}")

@router.get("/smart-agent/interface", response_class=HTMLResponse)
async def smart_agent_interface():
    """Smart Agent web interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Smart AI Agent</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .container {
                width: 100%;
                max-width: 1000px;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
                display: flex;
                flex-direction: column;
                height: 80vh;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2rem;
                margin-bottom: 10px;
            }
            
            .header p {
                opacity: 0.9;
                font-size: 1.1rem;
            }
            
            .content {
                flex: 1;
                display: flex;
                flex-direction: column;
                padding: 20px;
            }
            
            .chat-container {
                flex: 1;
                display: flex;
                flex-direction: column;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                overflow: hidden;
            }
            
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #f8f9fa;
                max-height: 400px;
            }
            
            .message {
                margin-bottom: 15px;
                display: flex;
                align-items: flex-start;
            }
            
            .message.user {
                justify-content: flex-end;
            }
            
            .message-content {
                max-width: 70%;
                padding: 12px 16px;
                border-radius: 18px;
                word-wrap: break-word;
                position: relative;
            }
            
            .message.bot .message-content {
                background: #e3f2fd;
                color: #1565c0;
                border-bottom-left-radius: 5px;
            }
            
            .message.user .message-content {
                background: #667eea;
                color: white;
                border-bottom-right-radius: 5px;
            }
            
            .message-meta {
                font-size: 0.8em;
                opacity: 0.7;
                margin-top: 5px;
            }
            
            .input-container {
                padding: 20px;
                background: white;
                border-top: 1px solid #e0e0e0;
                display: flex;
                gap: 10px;
                align-items: flex-end;
            }
            
            .input-group {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            
            .input-field {
                padding: 12px 16px;
                border: 2px solid #e0e0e0;
                border-radius: 25px;
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s;
            }
            
            .input-field:focus {
                border-color: #667eea;
            }
            
            .style-selector {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 20px;
                font-size: 14px;
                outline: none;
                background: white;
            }
            
            .send-button {
                background: #667eea;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                transition: background 0.3s;
                white-space: nowrap;
            }
            
            .send-button:hover {
                background: #5a6fd8;
            }
            
            .send-button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            
            .loading {
                display: none;
                text-align: center;
                padding: 10px;
                color: #666;
            }
            
            .error {
                background: #ffebee;
                color: #c62828;
                padding: 10px;
                margin: 10px 20px;
                border-radius: 8px;
                text-align: center;
            }
            
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }
            
            .feature {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                border: 1px solid #e0e0e0;
            }
            
            .feature-icon {
                font-size: 2em;
                margin-bottom: 10px;
            }
            
            .feature h3 {
                margin-bottom: 5px;
                color: #333;
            }
            
            .feature p {
                color: #666;
                font-size: 0.9em;
            }
            
            .url-input {
                display: flex;
                gap: 10px;
                margin-bottom: 10px;
            }
            
            .url-input input {
                flex: 1;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            
            .url-button {
                background: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
            }
            
            .url-button:hover {
                background: #218838;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Smart AI Agent</h1>
                <p>Advanced AI with multi-style responses and web content reading</p>
            </div>
            
            <div class="content">
                <div class="features">
                    <div class="feature">
                        <div class="feature-icon">🎨</div>
                        <h3>Multi-Style</h3>
                        <p>Responds in different styles: formal, casual, technical, creative, and more</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🌐</div>
                        <h3>Web Reading</h3>
                        <p>Reads and analyzes content from any website URL</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🧠</div>
                        <h3>Smart AI</h3>
                        <p>Advanced AI with context understanding and perfect responses</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🔗</div>
                        <h3>API Integration</h3>
                        <p>Integrates with external APIs and services</p>
                    </div>
                </div>
                
                <div class="chat-container">
                    <div class="chat-messages" id="chatMessages">
                        <div class="message bot">
                            <div class="message-content">
                                Hello! I'm your Smart AI Agent. I can:
                                <br>• Respond in different styles (formal, casual, technical, creative, etc.)
                                <br>• Read and analyze content from websites
                                <br>• Provide perfect, contextual responses
                                <br>• Integrate with external APIs
                                <br><br>Try asking me anything or share a URL to analyze!
                                <div class="message-meta">Smart AI Agent • Ready</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="loading" id="loading">AI is thinking...</div>
                    
                    <div class="input-container">
                        <div class="input-group">
                            <div class="url-input">
                                <input type="url" id="urlInput" placeholder="Enter URL to analyze (optional)">
                                <button class="url-button" onclick="analyzeUrl()">Analyze URL</button>
                            </div>
                            <input type="text" id="messageInput" class="input-field" placeholder="Ask me anything...">
                        </div>
                        <select id="styleSelect" class="style-selector">
                            <option value="auto">Auto Style</option>
                            <option value="formal">Formal</option>
                            <option value="casual">Casual</option>
                            <option value="technical">Technical</option>
                            <option value="simple">Simple</option>
                            <option value="creative">Creative</option>
                            <option value="persian">Persian</option>
                            <option value="analytical">Analytical</option>
                            <option value="empathetic">Empathetic</option>
                        </select>
                        <button id="sendButton" class="send-button" onclick="sendMessage()">Send</button>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            const API_BASE = '/api/smart-agent';
            const chatMessages = document.getElementById('chatMessages');
            const messageInput = document.getElementById('messageInput');
            const urlInput = document.getElementById('urlInput');
            const styleSelect = document.getElementById('styleSelect');
            const sendButton = document.getElementById('sendButton');
            const loading = document.getElementById('loading');
            
            function addMessage(text, isUser, meta = '') {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
                
                const contentDiv = document.createElement('div');
                contentDiv.className = 'message-content';
                contentDiv.innerHTML = text;
                
                if (meta) {
                    const metaDiv = document.createElement('div');
                    metaDiv.className = 'message-meta';
                    metaDiv.textContent = meta;
                    contentDiv.appendChild(metaDiv);
                }
                
                messageDiv.appendChild(contentDiv);
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            function showLoading() {
                loading.style.display = 'block';
                sendButton.disabled = true;
            }
            
            function hideLoading() {
                loading.style.display = 'none';
                sendButton.disabled = false;
            }
            
            function showError(message) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error';
                errorDiv.textContent = message;
                chatMessages.appendChild(errorDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            async function sendMessage() {
                const message = messageInput.value.trim();
                const url = urlInput.value.trim();
                const style = styleSelect.value;
                
                if (!message && !url) return;
                
                let fullMessage = message;
                if (url) {
                    fullMessage = (message ? message + ' ' : '') + url;
                }
                
                addMessage(fullMessage, true);
                messageInput.value = '';
                urlInput.value = '';
                showLoading();
                
                try {
                    const response = await fetch(`${API_BASE}/chat`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            message: fullMessage,
                            style: style
                        })
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    
                    let meta = `Style: ${data.style} • ${data.response_time.toFixed(2)}s`;
                    if (data.web_content_used) {
                        meta += ` • Web content used`;
                    }
                    if (data.urls_processed.length > 0) {
                        meta += ` • URLs: ${data.urls_processed.length}`;
                    }
                    
                    addMessage(data.response, false, meta);
                    
                } catch (error) {
                    console.error('Error:', error);
                    showError('Error communicating with Smart AI Agent. Please try again.');
                } finally {
                    hideLoading();
                }
            }
            
            async function analyzeUrl() {
                const url = urlInput.value.trim();
                if (!url) return;
                
                showLoading();
                
                try {
                    const response = await fetch(`${API_BASE}/read-url`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ url: url })
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    
                    if (data.error) {
                        showError(`Error reading URL: ${data.error}`);
                    } else {
                        let content = `<strong>URL Analysis:</strong><br>`;
                        content += `<strong>Title:</strong> ${data.title}<br>`;
                        content += `<strong>Description:</strong> ${data.description}<br>`;
                        content += `<strong>Content:</strong> ${data.main_content.substring(0, 500)}...<br>`;
                        content += `<strong>Links:</strong> ${data.links.length} found<br>`;
                        content += `<strong>Images:</strong> ${data.images.length} found`;
                        
                        addMessage(content, false, `URL: ${data.url}`);
                    }
                    
                } catch (error) {
                    console.error('Error:', error);
                    showError('Error analyzing URL. Please try again.');
                } finally {
                    hideLoading();
                }
            }
            
            // Event listeners
            sendButton.addEventListener('click', sendMessage);
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });
            urlInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') analyzeUrl();
            });
            
            // Focus input
            messageInput.focus();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get("/smart-agent/status")
async def get_smart_agent_status():
    """Get smart agent status and capabilities"""
    try:
        capabilities = [
            "Web content reading",
            "URL analysis",
            "API integration",
            "Real-time processing"
        ]
        
        if smart_agent.openai_available:
            capabilities.extend([
                "Multi-style responses",
                "Context understanding",
                "Advanced AI responses"
            ])
            status = "active"
            mode = "full"
        else:
            capabilities.extend([
                "Basic responses (limited mode)",
                "Fallback responses"
            ])
            status = "limited"
            mode = "fallback"
        
        return {
            "status": status,
            "mode": mode,
            "openai_available": smart_agent.openai_available,
            "capabilities": capabilities,
            "available_styles": smart_agent.get_available_styles(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status error: {str(e)}")
