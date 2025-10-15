# Persian Chatbot with FAQ Management

A modern Persian chatbot built with FastAPI backend and Next.js frontend, featuring FAQ management, semantic search, and comprehensive logging.

## Features

- 🤖 **Persian Chatbot** - Natural language processing in Persian
- 📚 **FAQ Management** - Add, edit, and manage frequently asked questions
- 🔍 **Semantic Search** - AI-powered search through FAQ database
- 📊 **Comprehensive Logging** - Track all chat interactions and analytics
- 🎨 **Modern UI** - Beautiful, responsive interface with Tailwind CSS
- 🔐 **Admin Panel** - Secure admin interface for managing content
- 🚀 **PM2 Process Management** - Production-ready process management with auto-restart and monitoring

## Tech Stack

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

## Quick Start with PM2

### Prerequisites
- Node.js 18+ installed
- Python 3.9+ installed
- OpenAI API key

### 1. Clone the Repository
```bash
git clone https://github.com/souroshsepehri/chatbot2.git
cd chatbot2
```

### 2. Set Environment Variables
Create a `.env` file in the root directory:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run with PM2
```bash
# Install PM2 globally
npm install -g pm2

# Start all services
npm start
```

This will:
- Install all Python and Node.js dependencies
- Start the backend on http://localhost:8000
- Start the frontend on http://localhost:3000
- Set up automatic process management with PM2
- Configure log rotation and monitoring

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Admin Panel**: http://localhost:3000/admin

## Manual Setup (Without Docker)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

### Backend (.env)
```bash
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///./app.db
VECTORSTORE_PATH=./vectorstore
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## API Endpoints

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

## Database Schema

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

## Development

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

### Customizing Responses
Edit the system prompts in:
- `backend/services/answer.py` - Main response generation
- `backend/services/intent.py` - Intent detection
- `backend/services/chain.py` - Processing chain

## Deployment

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables for Production
```bash
OPENAI_API_KEY=your_production_key
DATABASE_URL=postgresql://user:pass@host:port/db
NEXT_PUBLIC_API_URL=https://your-api-domain.com/api
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Create an issue on GitHub
- Contact: support@zimer.com

## Changelog

### v1.0.0
- Initial release
- Persian chatbot with FAQ management
- Semantic search capabilities
- Comprehensive logging system
- Docker support
- Admin panel