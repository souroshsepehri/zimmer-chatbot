# Answering Agent Documentation

## Overview

The **Answering Agent** is the centralized system for processing and answering user queries. It replaces the previous ad-hoc answering logic with a structured, extensible approach that handles different phrasings, detects intent, retrieves relevant data, and composes accurate responses.

## Main Entry Point

The main function to use is:

```python
from services.answering_agent import answer_user_query

result = answer_user_query(
    user_id="user123",
    message="قیمت محصولات چقدر است؟",
    context={"session_id": "abc123", "category_filter": "pricing"},
    db=db_session  # Optional, will be created if not provided
)

print(result["answer"])
print(f"Intent: {result['intent']}, Confidence: {result['confidence']}")
```

## Architecture

The Answering Agent follows this flow:

1. **Normalize & Understand Question**
   - Handles different phrasings and tones
   - Creates canonical question form
   - Validates input

2. **Detect Intent**
   - Uses smart intent detector if available
   - Falls back to keyword-based detection
   - Returns intent with confidence score

3. **Retrieve Relevant Data**
   - Uses appropriate intent handler
   - Queries database tables (FAQs, Categories, etc.)
   - Uses simple search and semantic search

4. **Compose Answer**
   - Uses retrieved data
   - Optionally enhances with LLM if available
   - Returns structured response

5. **Log Everything**
   - Logs to application logger
   - Logs to database (ChatLog table)
   - Includes metadata for debugging

## Response Format

The `answer_user_query` function returns a dictionary with:

```python
{
    "answer": str,              # The final answer text
    "intent": str,              # Detected intent (e.g., "pricing", "support")
    "confidence": float,         # Confidence score (0-1)
    "source": str,              # Data source ("faq", "database", "llm", "static", "fallback")
    "success": bool,            # Whether a good answer was found
    "matched_ids": List[int],   # IDs of records used (e.g., FAQ IDs)
    "metadata": {
        "original_message": str,
        "normalized_message": str,
        "canonical_question": str,
        "tables_queried": List[str],
        "retrieval_method": str,
        "processing_time_ms": float,
        "llm_used": bool,
        # ... other metadata
    }
}
```

## Intent Handlers

The agent uses intent handlers to process different types of queries. Current handlers:

- **FAQ Intent** (`_handle_faq_intent`): Handles FAQ-related queries
- **Category Intent** (`_handle_category_intent`): Handles category-related queries
- **Greeting Intent** (`_handle_greeting_intent`): Handles greetings
- **Unknown Intent** (`_handle_unknown_intent`): Fallback handler

### Adding New Intent Handlers

To add a new intent handler:

1. Add intent detection in `_detect_intent_enhanced`
2. Create handler method: `_handle_<intent>_intent`
3. Register in `__init__`: `self.intent_handlers["<intent>"] = self._handle_<intent>_intent`

Example:

```python
def _handle_custom_intent(
    self,
    message: str,
    canonical_question: str,
    db: Session,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Handle custom intent queries"""
    # Your logic here
    return {
        "answer": "Custom answer",
        "source": "custom",
        "success": True,
        "confidence": 0.9,
        "matched_ids": [],
        "tables_queried": ["custom_table"],
        "metadata": {}
    }
```

## Question Normalization

The agent automatically normalizes questions to handle different phrasings:

- Trims whitespace
- Removes excessive punctuation
- Normalizes Persian characters
- Removes filler words
- Creates canonical question form

This ensures that:
- "قیمت محصولات چقدر است؟"
- "چقدر محصولات قیمت دارند؟"
- "هزینه محصولات چقدره؟"

All map to similar canonical forms and retrieve the same data.

## Data Retrieval

The agent uses existing services for data retrieval:

- **Simple Retriever** (`simple_faq_retriever`): Fast keyword-based search
- **Semantic Retriever** (`faq_retriever`): Embedding-based semantic search
- **Direct Database Queries**: For categories and other structured data

The agent tries simple search first, then falls back to semantic search if needed.

## LLM Integration

If an LLM is available (via `answer_generator`), the agent can optionally enhance answers:

- Uses LLM to make answers more conversational
- Maintains accuracy from retrieved data
- Only uses LLM if quality check passes

## Logging

All queries are logged with:

- User ID
- Original and normalized messages
- Detected intent and confidence
- Answer and source
- Matched record IDs
- Tables queried
- Processing time
- Full metadata

Logs go to:
- Application logger (for debugging)
- Database `chat_logs` table (for analytics)

## Error Handling

The agent handles errors gracefully:

- Empty messages → Validation error response
- Very long messages → Truncated and processed
- Database errors → Error response, doesn't crash
- Missing services → Falls back to simpler methods
- LLM errors → Uses original answer without enhancement

## Usage Examples

### Basic Usage

```python
from services.answering_agent import answer_user_query
from core.db import get_db

db = next(get_db())
result = answer_user_query(
    user_id="user123",
    message="قیمت محصولات چقدر است؟",
    db=db
)
print(result["answer"])
```

### With Context

```python
result = answer_user_query(
    user_id="user123",
    message="سوالات در دسته قیمت",
    context={
        "session_id": "abc123",
        "category_filter": "pricing",
        "debug": True
    },
    db=db
)
```

### In FastAPI Endpoint

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.answering_agent import answer_user_query
from core.db import get_db

router = APIRouter()

@router.post("/chat")
async def chat(message: str, db: Session = Depends(get_db)):
    result = answer_user_query(
        user_id=None,
        message=message,
        context=None,
        db=db
    )
    return {"answer": result["answer"]}
```

## Testing

Run tests with:

```bash
pytest backend/tests/test_answering_agent.py -v
```

Tests cover:
- Question normalization
- Intent detection
- FAQ retrieval
- Category handling
- Error handling
- Different phrasings
- Logging

## Configuration

The agent uses settings from `core.config`:

- `retrieval_top_k`: Number of results to retrieve
- `retrieval_threshold`: Minimum similarity threshold
- `openai_api_key`: For LLM integration (optional)
- `openai_model`: LLM model to use

## Extending the Agent

### Adding New Data Sources

1. Create retrieval function in appropriate service
2. Add handler method in agent
3. Register in intent handlers

### Adding New Intents

1. Add intent detection logic
2. Create handler method
3. Register in `intent_handlers` dict

### Customizing Answer Composition

Override `_enhance_answer_with_llm` or modify intent handlers to customize how answers are composed.

## Troubleshooting

### Agent returns fallback answers

- Check if FAQs exist in database
- Verify retrieval thresholds aren't too high
- Check logs for retrieval method and scores

### Wrong intent detected

- Review intent detection logic
- Add keywords/patterns for your use case
- Check confidence scores in logs

### Slow responses

- Check processing time in metadata
- Consider caching frequently asked questions
- Optimize database queries

### LLM not working

- Verify `openai_api_key` is set
- Check if `answer_generator` is available
- Review error logs

## Best Practices

1. **Always provide context** when available (session_id, category_filter, etc.)
2. **Use database session** from FastAPI dependency injection when possible
3. **Check success flag** before using answer
4. **Review logs** to understand agent behavior
5. **Test with different phrasings** to ensure robustness

## Future Enhancements

Potential improvements:

- Multi-turn conversation support
- Context from previous messages
- User-specific data retrieval
- A/B testing for answer quality
- Analytics dashboard for agent performance
