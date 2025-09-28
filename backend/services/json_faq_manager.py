import json
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from models.faq import FAQ, Category
from schemas.json_faq import (
    JSONFAQ, JSONFAQCreate, JSONFAQUpdate, JSONFAQResponse,
    JSONFAQListResponse, JSONFAQImport, JSONFAQExport,
    QuestionType, AnswerFormat, QuestionVariant, StructuredAnswer
)
import logging

logger = logging.getLogger(__name__)


class JSONFAQManager:
    """Manager for JSON-based FAQ operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_faq(self, faq_data: JSONFAQCreate) -> JSONFAQResponse:
        """Create a new JSON FAQ"""
        try:
            # Generate unique ID
            faq_id = str(uuid.uuid4())
            
            # Create or get category
            category_id = None
            if faq_data.category:
                category = self._get_or_create_category(faq_data.category)
                category_id = category.id
            
            # Create FAQ record in database
            faq_record = FAQ(
                question=faq_data.question,
                answer=faq_data.answer,
                category_id=category_id,
                is_active=faq_data.is_active
            )
            self.db.add(faq_record)
            self.db.commit()
            self.db.refresh(faq_record)
            
            # Store JSON data in a separate field or table
            json_data = {
                "id": faq_id,
                "question_type": faq_data.question_type.value,
                "question_variants": [variant.dict() for variant in faq_data.question_variants],
                "structured_answer": faq_data.structured_answer.dict() if faq_data.structured_answer else None,
                "tags": faq_data.tags,
                "priority": faq_data.priority,
                "context_requirements": [req.dict() for req in faq_data.context_requirements],
                "conditions": faq_data.conditions,
                "confidence_score": faq_data.confidence_score,
                "related_faqs": faq_data.related_faqs,
                "follow_up_questions": faq_data.follow_up_questions,
                "usage_count": 0,
                "last_used": None,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Store JSON data in FAQ record (using a text field for now)
            faq_record.embedding = json.dumps(json_data).encode('utf-8')
            self.db.commit()
            
            return self._faq_record_to_response(faq_record, json_data)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating JSON FAQ: {e}")
            raise
    
    def get_faq(self, faq_id: str) -> Optional[JSONFAQResponse]:
        """Get a JSON FAQ by ID"""
        try:
            faq_record = self.db.query(FAQ).filter(
                FAQ.embedding.like(f'%"{faq_id}"%')
            ).first()
            
            if not faq_record:
                return None
            
            json_data = self._extract_json_data(faq_record)
            return self._faq_record_to_response(faq_record, json_data)
            
        except Exception as e:
            logger.error(f"Error getting JSON FAQ {faq_id}: {e}")
            return None
    
    def get_faqs(
        self, 
        page: int = 1, 
        page_size: int = 20,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        question_type: Optional[QuestionType] = None,
        search_query: Optional[str] = None
    ) -> JSONFAQListResponse:
        """Get paginated list of JSON FAQs with filters"""
        try:
            query = self.db.query(FAQ)
            
            # Apply filters
            if category:
                query = query.join(FAQ.category).filter(Category.slug == category)
            
            if search_query:
                query = query.filter(
                    or_(
                        FAQ.question.contains(search_query),
                        FAQ.answer.contains(search_query)
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * page_size
            faq_records = query.offset(offset).limit(page_size).all()
            
            # Convert to response format
            items = []
            for faq_record in faq_records:
                json_data = self._extract_json_data(faq_record)
                if json_data:
                    # Apply additional filters on JSON data
                    if question_type and json_data.get("question_type") != question_type.value:
                        continue
                    if tags and not any(tag in json_data.get("tags", []) for tag in tags):
                        continue
                    
                    items.append(self._faq_record_to_response(faq_record, json_data))
            
            # Calculate total pages
            total_pages = (total + page_size - 1) // page_size
            
            return JSONFAQListResponse(
                items=items,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
            
        except Exception as e:
            logger.error(f"Error getting JSON FAQs: {e}")
            raise
    
    def update_faq(self, faq_id: str, faq_data: JSONFAQUpdate) -> Optional[JSONFAQResponse]:
        """Update a JSON FAQ"""
        try:
            faq_record = self.db.query(FAQ).filter(
                FAQ.embedding.like(f'%"{faq_id}"%')
            ).first()
            
            if not faq_record:
                return None
            
            # Update basic fields
            update_data = faq_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field in ['question', 'answer', 'is_active']:
                    setattr(faq_record, field, value)
            
            # Update category if provided
            if faq_data.category:
                category = self._get_or_create_category(faq_data.category)
                faq_record.category_id = category.id
            
            # Update JSON data
            json_data = self._extract_json_data(faq_record)
            if json_data:
                # Update JSON fields
                json_update_fields = [
                    'question_type', 'question_variants', 'structured_answer',
                    'tags', 'priority', 'context_requirements', 'conditions',
                    'confidence_score', 'related_faqs', 'follow_up_questions'
                ]
                
                for field in json_update_fields:
                    if hasattr(faq_data, field) and getattr(faq_data, field) is not None:
                        value = getattr(faq_data, field)
                        if hasattr(value, 'value'):  # Enum
                            json_data[field] = value.value
                        elif hasattr(value, 'dict'):  # Pydantic model
                            json_data[field] = value.dict()
                        else:
                            json_data[field] = value
                
                json_data["updated_at"] = datetime.now().isoformat()
                
                # Save updated JSON data
                faq_record.embedding = json.dumps(json_data).encode('utf-8')
            
            self.db.commit()
            self.db.refresh(faq_record)
            
            return self._faq_record_to_response(faq_record, json_data)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating JSON FAQ {faq_id}: {e}")
            raise
    
    def delete_faq(self, faq_id: str) -> bool:
        """Delete a JSON FAQ"""
        try:
            faq_record = self.db.query(FAQ).filter(
                FAQ.embedding.like(f'%"{faq_id}"%')
            ).first()
            
            if not faq_record:
                return False
            
            self.db.delete(faq_record)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting JSON FAQ {faq_id}: {e}")
            raise
    
    def import_faqs(self, import_data: JSONFAQImport) -> Dict[str, Any]:
        """Import multiple JSON FAQs"""
        results = {
            "imported": 0,
            "skipped": 0,
            "errors": [],
            "details": []
        }
        
        for faq_data in import_data.faqs:
            try:
                if import_data.validate_only:
                    # Just validate
                    JSONFAQCreate(**faq_data.dict())
                    results["details"].append({
                        "question": faq_data.question,
                        "status": "valid"
                    })
                else:
                    # Check if exists
                    existing = self._find_faq_by_question(faq_data.question)
                    if existing and not import_data.overwrite_existing:
                        results["skipped"] += 1
                        results["details"].append({
                            "question": faq_data.question,
                            "status": "skipped - already exists"
                        })
                    else:
                        if existing:
                            # Update existing
                            self.update_faq(existing["id"], JSONFAQUpdate(**faq_data.dict()))
                        else:
                            # Create new
                            self.create_faq(faq_data)
                        results["imported"] += 1
                        results["details"].append({
                            "question": faq_data.question,
                            "status": "imported"
                        })
                        
            except Exception as e:
                results["errors"].append({
                    "question": faq_data.question,
                    "error": str(e)
                })
                results["details"].append({
                    "question": faq_data.question,
                    "status": f"error - {str(e)}"
                })
        
        return results
    
    def export_faqs(self, faq_ids: Optional[List[str]] = None) -> JSONFAQExport:
        """Export JSON FAQs"""
        try:
            if faq_ids:
                # Export specific FAQs
                items = []
                for faq_id in faq_ids:
                    faq = self.get_faq(faq_id)
                    if faq:
                        items.append(faq)
            else:
                # Export all FAQs
                response = self.get_faqs(page=1, page_size=1000)  # Get all
                items = response.items
            
            return JSONFAQExport(
                faqs=items,
                export_metadata={
                    "exported_count": len(items),
                    "export_type": "json_faqs"
                }
            )
            
        except Exception as e:
            logger.error(f"Error exporting JSON FAQs: {e}")
            raise
    
    def search_similar_questions(self, query: str, limit: int = 5) -> List[JSONFAQResponse]:
        """Search for similar questions using text similarity"""
        try:
            # Simple text-based search for now
            # In a real implementation, you might use vector similarity
            faq_records = self.db.query(FAQ).filter(
                or_(
                    FAQ.question.contains(query),
                    FAQ.answer.contains(query)
                )
            ).limit(limit).all()
            
            results = []
            for faq_record in faq_records:
                json_data = self._extract_json_data(faq_record)
                if json_data:
                    results.append(self._faq_record_to_response(faq_record, json_data))
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar questions: {e}")
            return []
    
    def increment_usage(self, faq_id: str) -> bool:
        """Increment usage count for a FAQ"""
        try:
            faq_record = self.db.query(FAQ).filter(
                FAQ.embedding.like(f'%"{faq_id}"%')
            ).first()
            
            if not faq_record:
                return False
            
            json_data = self._extract_json_data(faq_record)
            if json_data:
                json_data["usage_count"] = json_data.get("usage_count", 0) + 1
                json_data["last_used"] = datetime.now().isoformat()
                json_data["updated_at"] = datetime.now().isoformat()
                
                faq_record.embedding = json.dumps(json_data).encode('utf-8')
                self.db.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error incrementing usage for FAQ {faq_id}: {e}")
            return False
    
    def _get_or_create_category(self, category_name: str) -> Category:
        """Get or create a category"""
        slug = category_name.lower().replace(' ', '-')
        category = self.db.query(Category).filter(Category.slug == slug).first()
        
        if not category:
            category = Category(name=category_name, slug=slug)
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
        
        return category
    
    def _extract_json_data(self, faq_record: FAQ) -> Optional[Dict[str, Any]]:
        """Extract JSON data from FAQ record"""
        try:
            if faq_record.embedding:
                json_str = faq_record.embedding.decode('utf-8')
                return json.loads(json_str)
            return None
        except Exception as e:
            logger.error(f"Error extracting JSON data: {e}")
            return None
    
    def _faq_record_to_response(self, faq_record: FAQ, json_data: Dict[str, Any]) -> JSONFAQResponse:
        """Convert FAQ record and JSON data to response format"""
        return JSONFAQResponse(
            id=json_data.get("id", ""),
            question=faq_record.question,
            answer=faq_record.answer,
            question_type=QuestionType(json_data.get("question_type", "direct")),
            question_variants=[
                QuestionVariant(**variant) for variant in json_data.get("question_variants", [])
            ],
            structured_answer=StructuredAnswer(**json_data["structured_answer"]) if json_data.get("structured_answer") else None,
            category=faq_record.category.name if faq_record.category else None,
            tags=json_data.get("tags", []),
            priority=json_data.get("priority", 1),
            confidence_score=json_data.get("confidence_score", 1.0),
            usage_count=json_data.get("usage_count", 0),
            last_used=datetime.fromisoformat(json_data["last_used"]) if json_data.get("last_used") else None,
            related_faqs=json_data.get("related_faqs", []),
            follow_up_questions=json_data.get("follow_up_questions", []),
            is_active=faq_record.is_active,
            created_at=datetime.fromisoformat(json_data["created_at"]) if json_data.get("created_at") else faq_record.created_at,
            updated_at=datetime.fromisoformat(json_data["updated_at"]) if json_data.get("updated_at") else faq_record.updated_at
        )
    
    def _find_faq_by_question(self, question: str) -> Optional[Dict[str, Any]]:
        """Find FAQ by question text"""
        faq_record = self.db.query(FAQ).filter(FAQ.question == question).first()
        if faq_record:
            json_data = self._extract_json_data(faq_record)
            if json_data:
                return {
                    "id": json_data.get("id"),
                    "question": faq_record.question,
                    "json_data": json_data
                }
        return None
