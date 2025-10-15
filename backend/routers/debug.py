"""
Debug API endpoints for chatbot monitoring and troubleshooting
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.debugger import debugger, DebugSession, DebugRequest
from core.db import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/debug/status")
async def get_debug_status():
    """Get current debug system status"""
    try:
        stats = debugger.get_debug_statistics()
        return {
            "status": "active",
            "timestamp": datetime.now().isoformat(),
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debug status error: {str(e)}")

@router.post("/debug/session/start")
async def start_debug_session(session_id: Optional[str] = None):
    """Start a new debug session"""
    try:
        session_id = debugger.start_debug_session(session_id)
        return {
            "status": "success",
            "session_id": session_id,
            "message": f"Debug session started: {session_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start debug session: {str(e)}")

@router.post("/debug/session/end/{session_id}")
async def end_debug_session(session_id: str):
    """End a debug session"""
    try:
        debugger.end_debug_session(session_id)
        return {
            "status": "success",
            "session_id": session_id,
            "message": f"Debug session ended: {session_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end debug session: {str(e)}")

@router.get("/debug/sessions")
async def get_debug_sessions():
    """Get all debug sessions"""
    try:
        sessions = {}
        for session_id, session in debugger.sessions.items():
            sessions[session_id] = {
                "session_id": session.session_id,
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "total_requests": session.total_requests,
                "successful_requests": session.successful_requests,
                "failed_requests": session.failed_requests,
                "average_response_time": session.average_response_time,
                "errors": session.errors
            }
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sessions: {str(e)}")

@router.get("/debug/requests")
async def get_debug_requests(
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    limit: int = Query(100, description="Maximum number of requests to return"),
    offset: int = Query(0, description="Number of requests to skip")
):
    """Get debug requests with optional filtering"""
    try:
        requests = debugger.requests
        
        # Filter by session if specified
        if session_id:
            requests = [r for r in requests if r.session_id == session_id]
        
        # Apply pagination
        requests = requests[offset:offset + limit]
        
        # Convert to dict format
        request_data = []
        for req in requests:
            request_data.append({
                "request_id": req.request_id,
                "session_id": req.session_id,
                "timestamp": req.timestamp.isoformat(),
                "user_message": req.user_message,
                "response": req.response,
                "response_time": req.response_time,
                "intent_detected": req.intent_detected,
                "faq_matches": req.faq_matches,
                "search_scores": req.search_scores,
                "error_message": req.error_message,
                "debug_info": req.debug_info
            })
        
        return {
            "requests": request_data,
            "total": len(debugger.requests),
            "filtered": len(requests),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get requests: {str(e)}")

@router.get("/debug/diagnose/database")
async def diagnose_database():
    """Diagnose database health and content"""
    try:
        diagnosis = debugger.diagnose_database()
        return diagnosis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database diagnosis failed: {str(e)}")

@router.get("/debug/diagnose/services")
async def diagnose_services():
    """Diagnose chatbot services health"""
    try:
        diagnosis = debugger.diagnose_chatbot_services()
        return diagnosis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Services diagnosis failed: {str(e)}")

@router.post("/debug/test/response")
async def test_chatbot_response(
    message: str,
    chatbot_type: str = Query("simple", description="Chatbot type: simple or smart")
):
    """Test chatbot response with detailed debugging"""
    try:
        test_result = debugger.test_chatbot_response(message, chatbot_type)
        return test_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response test failed: {str(e)}")

@router.get("/debug/statistics")
async def get_debug_statistics(session_id: Optional[str] = Query(None)):
    """Get comprehensive debug statistics"""
    try:
        stats = debugger.get_debug_statistics(session_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@router.get("/debug/export")
async def export_debug_data(
    session_id: Optional[str] = Query(None),
    format: str = Query("json", description="Export format: json")
):
    """Export debug data for analysis"""
    try:
        filename = debugger.export_debug_data(session_id, format)
        return {
            "status": "success",
            "filename": filename,
            "message": f"Debug data exported to {filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.delete("/debug/clear")
async def clear_debug_data(session_id: Optional[str] = Query(None)):
    """Clear debug data"""
    try:
        debugger.clear_debug_data(session_id)
        return {
            "status": "success",
            "message": f"Debug data cleared for session: {session_id or 'all'}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear debug data: {str(e)}")

@router.get("/debug/interface", response_class=HTMLResponse)
async def debug_interface():
    """Debug web interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chatbot Debug Interface</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }
            .content {
                padding: 20px;
            }
            .section {
                margin-bottom: 30px;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            .section h3 {
                margin-top: 0;
                color: #333;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }
            .button {
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                margin: 5px;
                font-size: 14px;
            }
            .button:hover {
                background: #5a6fd8;
            }
            .button.danger {
                background: #e74c3c;
            }
            .button.danger:hover {
                background: #c0392b;
            }
            .status {
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
            }
            .status.success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .status.error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .status.info {
                background: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
            }
            .log-output {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 5px;
                padding: 15px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                max-height: 400px;
                overflow-y: auto;
                white-space: pre-wrap;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }
            .metric {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
            }
            .metric-value {
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
            }
            .metric-label {
                color: #666;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Chatbot Debug Interface</h1>
                <p>Monitor, diagnose, and troubleshoot your chatbot</p>
            </div>
            
            <div class="content">
                <!-- Status Section -->
                <div class="section">
                    <h3>📊 System Status</h3>
                    <div id="status-info" class="status info">Loading status...</div>
                    <button class="button" onclick="loadStatus()">Refresh Status</button>
                    <button class="button" onclick="startSession()">Start Debug Session</button>
                </div>
                
                <!-- Statistics Section -->
                <div class="section">
                    <h3>📈 Statistics</h3>
                    <div id="statistics" class="grid">
                        <div class="metric">
                            <div class="metric-value" id="total-requests">-</div>
                            <div class="metric-label">Total Requests</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value" id="success-rate">-</div>
                            <div class="metric-label">Success Rate</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value" id="avg-response-time">-</div>
                            <div class="metric-label">Avg Response Time</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value" id="active-sessions">-</div>
                            <div class="metric-label">Active Sessions</div>
                        </div>
                    </div>
                    <button class="button" onclick="loadStatistics()">Refresh Statistics</button>
                </div>
                
                <!-- Diagnostics Section -->
                <div class="section">
                    <h3>🔍 Diagnostics</h3>
                    <button class="button" onclick="diagnoseDatabase()">Check Database</button>
                    <button class="button" onclick="diagnoseServices()">Check Services</button>
                    <button class="button" onclick="testResponse()">Test Response</button>
                    <div id="diagnostic-results" class="log-output" style="display: none;"></div>
                </div>
                
                <!-- Test Section -->
                <div class="section">
                    <h3>🧪 Test Chatbot</h3>
                    <input type="text" id="test-message" placeholder="Enter test message..." style="width: 70%; padding: 10px; margin-right: 10px;">
                    <select id="chatbot-type" style="padding: 10px; margin-right: 10px;">
                        <option value="simple">Simple Chatbot</option>
                        <option value="smart">Smart Chatbot</option>
                    </select>
                    <button class="button" onclick="testChatbot()">Test</button>
                    <div id="test-results" class="log-output" style="display: none;"></div>
                </div>
                
                <!-- Recent Requests Section -->
                <div class="section">
                    <h3>📝 Recent Requests</h3>
                    <button class="button" onclick="loadRecentRequests()">Load Recent Requests</button>
                    <button class="button" onclick="exportData()">Export Data</button>
                    <div id="recent-requests" class="log-output" style="display: none;"></div>
                </div>
                
                <!-- Management Section -->
                <div class="section">
                    <h3>⚙️ Management</h3>
                    <button class="button" onclick="clearDebugData()">Clear Debug Data</button>
                    <button class="button danger" onclick="clearAllData()">Clear All Data</button>
                </div>
            </div>
        </div>
        
        <script>
            const API_BASE = '/api/debug';
            
            async function apiCall(endpoint, method = 'GET', body = null) {
                try {
                    const options = {
                        method: method,
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    };
                    
                    if (body) {
                        options.body = JSON.stringify(body);
                    }
                    
                    const response = await fetch(`${API_BASE}${endpoint}`, options);
                    const data = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(data.detail || 'API call failed');
                    }
                    
                    return data;
                } catch (error) {
                    console.error('API call error:', error);
                    showStatus(`Error: ${error.message}`, 'error');
                    return null;
                }
            }
            
            function showStatus(message, type = 'info') {
                const statusDiv = document.getElementById('status-info');
                statusDiv.textContent = message;
                statusDiv.className = `status ${type}`;
            }
            
            function showResults(elementId, data) {
                const element = document.getElementById(elementId);
                element.style.display = 'block';
                element.textContent = JSON.stringify(data, null, 2);
            }
            
            async function loadStatus() {
                showStatus('Loading status...', 'info');
                const data = await apiCall('/status');
                if (data) {
                    showStatus(`System Status: ${data.status} - ${data.statistics.total_requests} total requests`, 'success');
                }
            }
            
            async function loadStatistics() {
                const data = await apiCall('/statistics');
                if (data) {
                    document.getElementById('total-requests').textContent = data.total_requests || 0;
                    document.getElementById('success-rate').textContent = `${(data.success_rate || 0).toFixed(1)}%`;
                    document.getElementById('avg-response-time').textContent = `${(data.average_response_time || 0).toFixed(3)}s`;
                    document.getElementById('active-sessions').textContent = data.active_sessions || 0;
                }
            }
            
            async function startSession() {
                const data = await apiCall('/session/start', 'POST');
                if (data) {
                    showStatus(data.message, 'success');
                }
            }
            
            async function diagnoseDatabase() {
                showStatus('Diagnosing database...', 'info');
                const data = await apiCall('/diagnose/database');
                if (data) {
                    showResults('diagnostic-results', data);
                    showStatus('Database diagnosis completed', 'success');
                }
            }
            
            async function diagnoseServices() {
                showStatus('Diagnosing services...', 'info');
                const data = await apiCall('/diagnose/services');
                if (data) {
                    showResults('diagnostic-results', data);
                    showStatus('Services diagnosis completed', 'success');
                }
            }
            
            async function testResponse() {
                showStatus('Testing response...', 'info');
                const data = await apiCall('/test/response?message=سلام&chatbot_type=simple');
                if (data) {
                    showResults('diagnostic-results', data);
                    showStatus('Response test completed', 'success');
                }
            }
            
            async function testChatbot() {
                const message = document.getElementById('test-message').value;
                const chatbotType = document.getElementById('chatbot-type').value;
                
                if (!message.trim()) {
                    showStatus('Please enter a test message', 'error');
                    return;
                }
                
                showStatus('Testing chatbot...', 'info');
                const data = await apiCall(`/test/response?message=${encodeURIComponent(message)}&chatbot_type=${chatbotType}`);
                if (data) {
                    showResults('test-results', data);
                    showStatus('Chatbot test completed', 'success');
                }
            }
            
            async function loadRecentRequests() {
                showStatus('Loading recent requests...', 'info');
                const data = await apiCall('/requests?limit=10');
                if (data) {
                    showResults('recent-requests', data);
                    showStatus('Recent requests loaded', 'success');
                }
            }
            
            async function exportData() {
                showStatus('Exporting data...', 'info');
                const data = await apiCall('/export');
                if (data) {
                    showStatus(data.message, 'success');
                }
            }
            
            async function clearDebugData() {
                if (confirm('Are you sure you want to clear debug data?')) {
                    const data = await apiCall('/clear', 'DELETE');
                    if (data) {
                        showStatus(data.message, 'success');
                        loadStatistics();
                    }
                }
            }
            
            async function clearAllData() {
                if (confirm('Are you sure you want to clear ALL debug data? This cannot be undone!')) {
                    const data = await apiCall('/clear', 'DELETE');
                    if (data) {
                        showStatus(data.message, 'success');
                        loadStatistics();
                    }
                }
            }
            
            // Load initial data
            document.addEventListener('DOMContentLoaded', function() {
                loadStatus();
                loadStatistics();
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get("/debug/logs")
async def get_debug_logs(
    lines: int = Query(100, description="Number of log lines to return"),
    level: str = Query("INFO", description="Log level filter")
):
    """Get recent debug logs"""
    try:
        log_file = Path('logs/debug.log')
        if not log_file.exists():
            return {"logs": [], "message": "No log file found"}
        
        # Read last N lines from log file
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
        
        # Filter by level if specified
        if level != "ALL":
            all_lines = [line for line in all_lines if level in line]
        
        # Get last N lines
        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        return {
            "logs": recent_lines,
            "total_lines": len(all_lines),
            "filtered_lines": len(recent_lines),
            "level": level
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read logs: {str(e)}")
