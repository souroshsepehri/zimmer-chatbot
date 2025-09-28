# Persian Chatbot with FAQ Management

A modern Persian chatbot built with FastAPI backend and Next.js frontend, featuring FAQ management, semantic search, and comprehensive logging.

## 🚀 Features

- 🤖 **Persian Chatbot** - Natural language processing in Persian
- 📚 **FAQ Management** - Add, edit, and manage frequently asked questions
- 🔍 **Semantic Search** - AI-powered search through FAQ database
- 📊 **Comprehensive Logging** - Track all chat interactions and analytics
- 🎨 **Modern UI** - Beautiful, responsive interface with Tailwind CSS
- 🔐 **Admin Panel** - Secure admin interface for managing content
- 🐳 **Docker Support** - Easy deployment with Docker and Docker Compose
- 📈 **Analytics Dashboard** - View chat statistics and performance metrics

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Lightweight database
- **LangChain** - AI/ML framework
- **OpenAI GPT** - Language model
- **FAISS** - Vector similarity search

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS
- **Lucide React** - Beautiful icons

## ⚡ Quick Start

### Prerequisites
- Python 3.8+ and Node.js 18+
- OpenAI API key

### 1. Clone the Repository
```bash
git clone https://github.com/souroshsepehri/chatbot2.git
cd chatbot2
```

### 2. Set Environment Variables
```bash
# Set your OpenAI API key
$env:OPENAI_API_KEY="your_openai_api_key_here"
```

### 3. Start the Chatbot
```bash
# Option 1: Use the dashboard launcher (Windows)
.\open_dashboard.bat

# Option 2: Manual start
# Terminal 1 - Backend
python start_backend_robust.py

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

### 4. Access the Application
- **Main Chatbot:** http://localhost:3000
- **Admin Panel:** http://localhost:3000/admin
- **API Documentation:** http://localhost:8002/docs
- **Health Check:** http://localhost:8002/health

## 🐳 Docker Deployment (Alternative)

### 1. Set Environment Variables
Create a `.env` file in the root directory:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Run with Docker Compose
```bash
docker-compose up --build
```

## 📊 Admin Tools

### Interactive Admin Panel
```bash
python admin_panel.py
```
Features:
- View chat statistics
- Browse recent logs
- Search through conversations
- Export data to JSON
- Manage FAQs

### Log Analysis
```bash
python analyze_logs.py
```
Provides comprehensive analysis:
- Overall statistics
- Success rates by source
- Intent analysis
- Recent activity tracking

### Quick Database Test
```bash
python test_admin.py
```
Quick test of database connectivity and recent logs.

## 🔧 API Endpoints

### Chat
- `POST /api/chat` - Send a message to the chatbot
- `GET /health` - Health check

### FAQs
- `GET /api/faqs` - Get all FAQs
- `POST /api/faqs` - Create new FAQ
- `PUT /api/faqs/{id}` - Update FAQ
- `DELETE /api/faqs/{id}` - Delete FAQ
- `POST /api/faqs/reindex` - Reindex vector store

### Logs
- `GET /api/logs` - Get chat logs with filters
- `GET /api/logs/stats` - Get log statistics
- `DELETE /api/logs/{id}` - Delete specific log

## 📈 Current Status

✅ **Backend Server** - Running on port 8002 (stable)
✅ **Frontend** - Running on port 3000
✅ **Database** - 82+ chat logs saved
✅ **FAQ System** - 6 active FAQs
✅ **Logging** - Complete chat tracking
✅ **Admin Panel** - Full database access
✅ **API** - All endpoints working

## 🗄️ Database Schema

### ChatLogs
- `id` - Primary key
- `timestamp` - When the chat occurred
- `user_text` - User's message
- `ai_text` - Bot's response
- `intent` - Detected intent
- `source` - Response source (faq, fallback, etc.)
- `success` - Whether the response was successful
- `matched_faq_id` - ID of matched FAQ (if applicable)
- `confidence` - Confidence score
- `tokens_in/out` - Token usage
- `latency_ms` - Response time
- `notes` - Additional metadata (JSON)

### FAQs
- `id` - Primary key
- `question` - FAQ question
- `answer` - FAQ answer
- `category_id` - Category reference
- `is_active` - Whether FAQ is active
- `embedding` - Vector embedding for search
- `created_at/updated_at` - Timestamps

## 🚨 Troubleshooting

### Backend Server Issues
If the backend server stops:
1. Check if port 8002 is available
2. Make sure OPENAI_API_KEY is set
3. Use `python start_backend_robust.py` to restart

### Frontend Connection Issues
If the frontend doesn't connect:
1. Make sure backend is running on port 8002
2. Check frontend/next.config.js for correct API URL

### Database Issues
If database access fails:
1. Make sure backend has been run at least once
2. Check if `backend/app.db` exists
3. Use admin tools to verify database connectivity

## 📝 Development

### Adding New FAQs
1. Go to http://localhost:3000/admin/faqs
2. Click "Add New FAQ"
3. Fill in question, answer, and category
4. Save to add to database

### Viewing Logs
1. Go to http://localhost:3000/admin/logs
2. View all chat interactions
3. Filter by success, intent, date range
4. Export data for analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Use the admin tools for diagnostics
- Review the API documentation at /docs
