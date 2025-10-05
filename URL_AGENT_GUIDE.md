# URL Agent Guide - Chatbot with Website Reading Capability

## Overview

Your chatbot now has a powerful URL Agent that can read websites and use them as a second database alongside your existing FAQ system. This allows the chatbot to answer questions about any website content you provide.

## Features

### 🌐 Website Reading
- **Web Scraping**: Automatically scrapes website content
- **Smart Content Extraction**: Extracts meaningful text from HTML pages
- **Multi-page Support**: Can scrape entire websites (up to 50 pages by default)
- **Content Chunking**: Breaks large content into searchable chunks

### 🗄️ Dual Database System
- **FAQ Database**: Your existing FAQ system (unchanged)
- **Web Content Database**: New vector store for website content
- **Combined Search**: Search both databases simultaneously
- **Intelligent Ranking**: Results ranked by relevance across both sources

### 🤖 Enhanced Chat Interface
- **URL Management**: Add/remove websites through the interface
- **Source Selection**: Choose to use FAQ, web content, or both
- **Source Attribution**: See which sources were used for each answer
- **Real-time Stats**: Monitor your knowledge base

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set API Key (Required)
```bash
# Windows
set OPENAI_API_KEY=your_openai_api_key_here

# Linux/Mac
export OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Start the Server
```bash
python start_with_url_agent.py
```

### 4. Access the Interface
- **Enhanced Interface**: http://localhost:8002
- **Simple Interface**: http://localhost:8002/simple
- **API Documentation**: http://localhost:8002/docs

## How to Use

### Adding a Website

1. **Through the Web Interface**:
   - Open the enhanced interface
   - Enter the website URL in the sidebar
   - Click "افزودن وب‌سایت" (Add Website)
   - Wait for the scraping to complete

2. **Through the API**:
```bash
curl -X POST "http://localhost:8002/api/add-website" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com", "max_pages": 50}'
```

### Asking Questions

The chatbot can now answer questions using:
- **FAQ Database Only**: Traditional FAQ responses
- **Web Content Only**: Answers based on scraped website content
- **Both Sources**: Combined answers from FAQ and web content

### Example Questions

Once you've added a website, you can ask:
- "What services does this company offer?"
- "How can I contact support?"
- "What are the pricing plans?"
- "Tell me about the company history"

## API Endpoints

### Website Management
- `POST /api/add-website` - Add a website to knowledge base
- `GET /api/websites` - List all websites
- `GET /api/websites/{url}` - Get website information
- `DELETE /api/websites/{url}` - Remove a website

### Chat & Search
- `POST /api/chat-with-url` - Enhanced chat with URL support
- `POST /api/search` - Search both databases
- `POST /api/answer` - Get AI-generated answers

### Statistics
- `GET /api/stats` - Get knowledge base statistics

## Configuration

### Web Scraper Settings
```python
# In backend/services/web_scraper.py
max_pages = 50        # Maximum pages to scrape
delay = 1.0          # Delay between requests (seconds)
```

### Vector Store Settings
```python
# In backend/services/web_vectorstore.py
chunk_size = 1000    # Text chunk size
chunk_overlap = 200  # Overlap between chunks
```

### Retrieval Settings
```python
# In backend/core/config.py
retrieval_top_k = 4      # Number of results to retrieve
retrieval_threshold = 0.82  # Similarity threshold
```

## File Structure

```
backend/
├── services/
│   ├── web_scraper.py      # Website scraping functionality
│   ├── web_vectorstore.py  # Vector store for web content
│   ├── url_agent.py        # Main URL agent orchestrator
│   └── retriever.py        # Existing FAQ retriever
├── routers/
│   └── url_agent.py        # API endpoints for URL agent
└── static/
    └── url_agent_interface.html  # Enhanced web interface
```

## Testing

Run the test script to verify functionality:
```bash
python test_url_agent.py
```

## Troubleshooting

### Common Issues

1. **"No content found" Error**:
   - Check if the website is accessible
   - Some websites block automated scraping
   - Try a different website or check robots.txt

2. **"OpenAI API Key not set"**:
   - Set the OPENAI_API_KEY environment variable
   - Restart the server after setting the key

3. **Slow Performance**:
   - Reduce max_pages in scraper settings
   - Increase delay between requests
   - Check your internet connection

4. **Memory Issues**:
   - Large websites may use significant memory
   - Consider reducing chunk_size or max_pages
   - Monitor system resources

### Performance Tips

1. **Optimize Scraping**:
   - Start with smaller websites for testing
   - Use appropriate max_pages limits
   - Monitor scraping progress

2. **Manage Storage**:
   - Vector stores are stored in `./vectorstore/web_content/`
   - Remove unused websites to free space
   - Regular cleanup of old content

3. **API Usage**:
   - Monitor OpenAI API usage and costs
   - Consider caching frequent queries
   - Use appropriate temperature settings

## Security Considerations

1. **Website Access**:
   - Only scrape websites you have permission to access
   - Respect robots.txt files
   - Use appropriate delays between requests

2. **Content Storage**:
   - Web content is stored locally in vector stores
   - Ensure proper access controls
   - Consider data retention policies

3. **API Security**:
   - Protect your OpenAI API key
   - Consider rate limiting for production use
   - Monitor API usage and costs

## Advanced Usage

### Custom Scraping Rules
Modify `web_scraper.py` to add custom content extraction rules for specific websites.

### Integration with Existing Systems
The URL agent can be integrated with your existing chatbot workflow by modifying the chat chain in `services/chain.py`.

### Batch Website Addition
Create scripts to add multiple websites programmatically using the API endpoints.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the API documentation at `/docs`
3. Test with the provided test script
4. Check server logs for detailed error messages

## Future Enhancements

Potential improvements:
- Support for different content types (PDFs, documents)
- Real-time website monitoring and updates
- Advanced content filtering and preprocessing
- Integration with more AI models
- Multi-language support for non-Persian content
