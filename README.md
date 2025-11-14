# Persian Chatbot

A Persian chatbot application with FAQ management, semantic search, and admin panel.

## Quick Start

### Start the Application

```bash
# Simple way
python start.py

# Or from backend directory
cd backend
python app.py
```

The server will start on `http://localhost:8001` (or next available port).

## Features

- ✅ Persian language chatbot
- ✅ **Answering Agent** - Centralized, extensible agent for answering queries
  - Handles different phrasings and tones automatically
  - Smart intent detection
  - LLM integration for answer enhancement
  - Comprehensive logging and observability
  - See [Answering Agent Documentation](backend/docs/ANSWERING_AGENT.md) for details
- ✅ FAQ management with semantic search
- ✅ Admin panel for managing FAQs, categories, and logs
- ✅ Chat logging and analytics
- ✅ Multiple chat endpoints (simple, smart, agent-based)
- ✅ Database integration (SQLite by default)

## Access Points

- **Main Chat Interface**: `http://localhost:8001/`
- **API Documentation**: `http://localhost:8001/docs`
- **Admin Panel**: `http://localhost:8001/admin`
- **FAQ Management**: `http://localhost:8001/admin/faqs`
- **Categories Management**: `http://localhost:8001/admin/categories`
- **Reports/Logs**: `http://localhost:8001/admin/logs`

## API Endpoints

- `POST /api/chat` - Main chat endpoint
- `GET /api/faqs` - List FAQs
- `POST /api/faqs` - Create FAQ
- `GET /api/logs` - Get chat logs
- `GET /api/logs/stats` - Get statistics

## Configuration

Set environment variables or edit `backend/core/config.py`:

- `OPENAI_API_KEY` - Your OpenAI API key
- `DATABASE_URL` - Database connection string (default: SQLite)
- `PORT` - Server port (default: 8001)

## Project Structure

```
backend/
├── app.py              # Main FastAPI application
├── core/               # Core configuration and database
├── models/             # Database models
├── routers/            # API route handlers
├── services/           # Business logic services
│   └── answering_agent.py  # Main Answering Agent (NEW)
├── schemas/            # Pydantic schemas
├── docs/               # Documentation
│   └── ANSWERING_AGENT.md  # Agent documentation
└── static/             # Static files (admin panels)
```

## Answering Agent

The system now uses a centralized **Answering Agent** (`services/answering_agent.py`) that:

- Normalizes and understands questions
- Detects user intent
- Retrieves relevant data from database
- Composes accurate, helpful responses
- Logs all operations for observability

See [docs/ANSWERING_AGENT.md](backend/docs/ANSWERING_AGENT.md) for full documentation.

**Main entry point:**
```python
from services.answering_agent import answer_user_query

result = answer_user_query(user_id="user123", message="سوال شما")
print(result["answer"])
```

## Requirements

See `requirements.txt` for Python dependencies.

## Database

The application uses SQLite by default. Database file: `backend/app.db`

To initialize the database:
```bash
cd backend
python init_database.py
```

## Health Check / Testing

برای بررسی سلامت چت‌بات و اجرای تست‌ها:

```bash
cd backend
python health_check.py
```

این دستور:
- تمام تست‌ها را اجرا می‌کند
- درصد موفقیت را نمایش می‌دهد
- وضعیت هر ماژول را نشان می‌دهد
- لاگ کامل خطاها را در `logs/health_failures.log` ذخیره می‌کند

برای جزئیات بیشتر به `backend/README_HEALTH_CHECK.md` مراجعه کنید.

### اجرای تست‌ها

```bash
# اجرای تمام تست‌ها
cd backend
pytest tests/ -v

# اجرای health check
python health_check.py
```
