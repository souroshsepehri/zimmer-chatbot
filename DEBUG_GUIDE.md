# 🔍 Chatbot Debugger & Diagnostic Guide

A comprehensive debugging and monitoring system for your Persian chatbot to help identify and resolve issues quickly.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Debug Interface](#debug-interface)
3. [Command Line Tools](#command-line-tools)
4. [API Endpoints](#api-endpoints)
5. [Diagnostic Features](#diagnostic-features)
6. [Troubleshooting](#troubleshooting)
7. [Monitoring](#monitoring)

## 🚀 Quick Start

### 1. Run Comprehensive Diagnostic
```bash
# Windows
debug_manager.bat

# Linux/Mac
./debug_manager.sh

# Or directly
python debug_chatbot.py
```

### 2. Access Debug Web Interface
```bash
# Start your chatbot server first
npm start
# or
pm2 start ecosystem.config.js

# Then open debug interface
http://localhost:8000/api/debug/interface
```

## 🖥️ Debug Interface

The debug web interface provides a comprehensive dashboard for monitoring your chatbot:

### Features:
- **📊 System Status**: Real-time system health monitoring
- **📈 Statistics**: Performance metrics and success rates
- **🔍 Diagnostics**: Database and services health checks
- **🧪 Testing**: Interactive chatbot testing
- **📝 Request Logs**: Recent request history
- **⚙️ Management**: Data export and cleanup

### Access URLs:
- **Main Interface**: `http://localhost:8000/api/debug/interface`
- **API Status**: `http://localhost:8000/api/debug/status`
- **Statistics**: `http://localhost:8000/api/debug/statistics`

## 🛠️ Command Line Tools

### Debug Manager Scripts

#### Windows (`debug_manager.bat`)
```batch
debug_manager.bat
```

#### Linux/Mac (`debug_manager.sh`)
```bash
./debug_manager.sh
```

### Comprehensive Diagnostic (`debug_chatbot.py`)
```bash
python debug_chatbot.py
```

**What it checks:**
- ✅ Database connectivity and content
- ✅ Chatbot services health
- ✅ Configuration settings
- ✅ Log files status
- ✅ Response testing
- ✅ Performance metrics

## 🔌 API Endpoints

### Debug Status
```http
GET /api/debug/status
```

### Start Debug Session
```http
POST /api/debug/session/start
```

### End Debug Session
```http
POST /api/debug/session/end/{session_id}
```

### Get Debug Statistics
```http
GET /api/debug/statistics?session_id=optional
```

### Test Chatbot Response
```http
POST /api/debug/test/response?message=سلام&chatbot_type=simple
```

### Diagnose Database
```http
GET /api/debug/diagnose/database
```

### Diagnose Services
```http
GET /api/debug/diagnose/services
```

### Get Recent Requests
```http
GET /api/debug/requests?limit=100&offset=0
```

### Export Debug Data
```http
GET /api/debug/export?session_id=optional&format=json
```

### Clear Debug Data
```http
DELETE /api/debug/clear?session_id=optional
```

### Get Debug Logs
```http
GET /api/debug/logs?lines=100&level=INFO
```

## 🔍 Diagnostic Features

### 1. Database Health Check
- **Connection Status**: Verifies database connectivity
- **Content Analysis**: Counts FAQs, categories, and active records
- **Sample Data**: Shows sample FAQs for verification
- **Greeting Detection**: Checks for greeting-related FAQs

### 2. Services Health Check
- **Simple Chatbot**: Tests FAQ loading and response generation
- **Smart Chatbot**: Verifies advanced features
- **Intent Detector**: Tests intent recognition system
- **Error Detection**: Identifies service failures

### 3. Response Testing
- **Message Testing**: Tests various input messages
- **Performance Metrics**: Measures response times
- **Error Tracking**: Captures and logs errors
- **Intent Analysis**: Shows detected intents and confidence

### 4. Configuration Check
- **Environment Variables**: Verifies required settings
- **API Keys**: Checks for OpenAI API key
- **Database URLs**: Validates database configuration
- **File Paths**: Ensures required directories exist

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Errors
```bash
# Check database file
ls -la app.db

# Test database connection
python -c "
import sys
sys.path.append('backend')
from core.db import get_db
db = next(get_db())
print('Database connected successfully')
db.close()
"
```

#### 2. FAQ Loading Issues
```bash
# Check FAQ count
python -c "
import sys
sys.path.append('backend')
from core.db import get_db
from models.faq import FAQ
db = next(get_db())
count = db.query(FAQ).count()
print(f'Total FAQs: {count}')
db.close()
"

# Add sample data if needed
python add_sample_data.py
```

#### 3. API Key Issues
```bash
# Check environment variables
echo $OPENAI_API_KEY

# Set API key
export OPENAI_API_KEY="your-api-key-here"
```

#### 4. Service Startup Issues
```bash
# Check PM2 status
pm2 status

# Check logs
pm2 logs

# Restart services
pm2 restart all
```

### Debug Logs Location
- **Main Debug Log**: `logs/debug.log`
- **Chatbot Debug Log**: `logs/chatbot_debug.log`
- **Chat Log**: `logs/chat.log`

## 📊 Monitoring

### Real-time Monitoring
The debugger provides real-time monitoring of:
- **Request Count**: Total number of requests
- **Success Rate**: Percentage of successful responses
- **Response Time**: Average response time
- **Error Rate**: Frequency of errors
- **Active Sessions**: Number of active debug sessions

### Performance Metrics
- **Response Time Distribution**: Shows response time patterns
- **Intent Detection Accuracy**: Measures intent recognition success
- **FAQ Match Quality**: Evaluates search result relevance
- **Error Patterns**: Identifies common failure points

### Alert System
The debugger can detect:
- **High Error Rates**: When error rate exceeds threshold
- **Slow Responses**: When response time is too high
- **Database Issues**: When database queries fail
- **Service Failures**: When chatbot services are down

## 🔧 Advanced Usage

### Custom Debug Sessions
```python
from backend.services.debugger import debugger

# Start custom session
session_id = debugger.start_debug_session("my_test_session")

# Test specific functionality
result = debugger.test_chatbot_response("سلام", "simple")

# End session
debugger.end_debug_session(session_id)
```

### Export Debug Data
```python
# Export all data
filename = debugger.export_debug_data()

# Export specific session
filename = debugger.export_debug_data("session_id")
```

### Custom Diagnostics
```python
# Database diagnosis
db_diagnosis = debugger.diagnose_database()

# Services diagnosis
services_diagnosis = debugger.diagnose_chatbot_services()

# Get statistics
stats = debugger.get_debug_statistics()
```

## 📈 Best Practices

### 1. Regular Monitoring
- Run diagnostics daily
- Check debug logs weekly
- Monitor performance metrics
- Review error patterns

### 2. Proactive Maintenance
- Clear old debug data regularly
- Export important debug sessions
- Update FAQ content based on patterns
- Optimize based on performance data

### 3. Error Handling
- Always check debug logs for errors
- Use debug sessions for testing
- Monitor success rates
- Investigate performance issues

## 🎯 Success Metrics

### Healthy Chatbot Indicators
- **Success Rate**: > 90%
- **Response Time**: < 2 seconds
- **Database Connectivity**: 100%
- **Service Health**: All services running
- **FAQ Coverage**: > 10 active FAQs

### Warning Signs
- **Success Rate**: < 80%
- **Response Time**: > 5 seconds
- **Error Rate**: > 10%
- **Database Issues**: Connection failures
- **Service Failures**: Any service down

---

## 🆘 Getting Help

If you encounter issues with the debugger:

1. **Check Logs**: Review `logs/debug.log` for error details
2. **Run Diagnostics**: Use `python debug_chatbot.py`
3. **Web Interface**: Access `http://localhost:8000/api/debug/interface`
4. **Export Data**: Save debug data for analysis
5. **Clear Data**: Reset debug data if corrupted

The debugger is designed to help you maintain a healthy, high-performing chatbot system! 🚀
