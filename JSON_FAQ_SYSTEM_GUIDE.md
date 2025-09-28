# JSON FAQ System - Implementation Guide

## Overview

I've implemented a comprehensive JSON-based FAQ system that enhances your chatbot with better question management and improved answering capabilities. This system allows for structured question-answer pairs with rich metadata and intelligent answer generation.

## What's Been Added

### 1. Enhanced JSON Schema (`backend/schemas/json_faq.py`)

The new JSON FAQ schema includes:

- **Question Types**: Direct, Contextual, Multi-step, Conditional
- **Question Variants**: Alternative ways to ask the same question
- **Structured Answers**: Multi-component answers with different formats
- **Rich Metadata**: Tags, categories, priority, confidence scores
- **Context Requirements**: What information is needed to answer properly
- **Relationships**: Related FAQs and follow-up questions
- **Usage Tracking**: How often FAQs are used and when

### 2. JSON FAQ Manager (`backend/services/json_faq_manager.py`)

A comprehensive service that handles:

- **CRUD Operations**: Create, read, update, delete JSON FAQs
- **Import/Export**: Bulk operations with JSON files
- **Search & Filtering**: Advanced search with multiple criteria
- **Usage Analytics**: Track FAQ performance and usage
- **Data Validation**: Ensure data integrity and consistency

### 3. API Endpoints (`backend/routers/json_faqs.py`)

New REST API endpoints:

- `POST /api/json-faqs` - Create new JSON FAQ
- `GET /api/json-faqs` - List FAQs with filtering
- `GET /api/json-faqs/{id}` - Get specific FAQ
- `PUT /api/json-faqs/{id}` - Update FAQ
- `DELETE /api/json-faqs/{id}` - Delete FAQ
- `POST /api/json-faqs/import` - Import FAQs from JSON
- `POST /api/json-faqs/import-file` - Import from uploaded file
- `GET /api/json-faqs/export/json` - Export FAQs as JSON
- `GET /api/json-faqs/search/similar` - Search similar questions
- `POST /api/json-faqs/{id}/increment-usage` - Track usage
- `GET /api/json-faqs/stats/overview` - Get statistics

### 4. Sample Data (`backend/sample_json_faqs.json`)

Example FAQs demonstrating the system capabilities with Persian content.

## Key Features

### 1. Question Types

- **Direct**: Simple question-answer pairs
- **Contextual**: Questions requiring context understanding
- **Multi-step**: Questions with multiple steps/processes
- **Conditional**: Questions with conditions or scenarios

### 2. Structured Answers

- **Text**: Simple text responses
- **List**: Bulleted or numbered lists
- **Structured**: Multi-component answers
- **Step-by-step**: Process-oriented responses

### 3. Smart Matching

- **Question Variants**: Multiple ways to ask the same question
- **Semantic Search**: Find relevant FAQs even with different wording
- **Confidence Scoring**: Rate the quality of matches
- **Priority System**: Important FAQs get higher priority

### 4. Analytics & Insights

- **Usage Tracking**: Monitor which FAQs are most helpful
- **Quality Metrics**: Assess answer quality automatically
- **Performance Monitoring**: Track response times and token usage
- **Statistics Dashboard**: Overview of FAQ system performance

## How to Use

### 1. Start the Backend

```bash
cd backend
python app.py
```

### 2. Import Sample Data

```bash
python test_json_faq_system.py
```

### 3. Use Enhanced Chat

Send requests to `/api/chat-enhanced` instead of `/api/chat` for better answers.

### 4. Manage FAQs

Use the API endpoints directly or integrate with your frontend.

## Example Usage

### Creating a JSON FAQ

```json
{
  "question": "چطور می‌تونم سفارش بدم؟",
  "answer": "برای سفارش دادن می‌تونید از طریق وب‌سایت ما اقدام کنید...",
  "question_type": "multi_step",
  "question_variants": [
    {
      "text": "چگونه سفارش دهم؟",
      "language": "fa",
      "confidence": 0.9
    }
  ],
  "category": "سفارشات",
  "tags": ["سفارش", "خرید", "راهنما"],
  "priority": 8,
  "confidence_score": 0.95,
  "follow_up_questions": [
    "آیا می‌تونم سفارشم رو لغو کنم؟",
    "چطور می‌تونم وضعیت سفارشم رو چک کنم؟"
  ],
  "is_active": true
}
```

## Benefits

1. **Better Answers**: More accurate and contextual responses
2. **Structured Data**: Rich metadata for better organization
3. **Scalability**: Easy to manage large numbers of FAQs
4. **Analytics**: Insights into FAQ performance and usage
5. **Flexibility**: Support for different question types and answer formats
6. **Import/Export**: Easy data migration and backup
7. **Quality Control**: Automatic quality assessment and improvement suggestions

## Next Steps

1. **Import Your Existing FAQs**: Convert current FAQs to JSON format
2. **Train the System**: Add more question variants and improve matching
3. **Monitor Performance**: Use analytics to identify areas for improvement
4. **Expand Categories**: Add more categories and tags for better organization
5. **User Feedback**: Implement feedback collection to improve FAQ quality

The system is now ready to provide much better answers to your users with the enhanced JSON FAQ structure!
