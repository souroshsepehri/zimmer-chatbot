from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List
from core.db import get_db
from services.json_faq_manager import JSONFAQManager
from schemas.json_faq import (
    JSONFAQCreate, JSONFAQUpdate, JSONFAQResponse,
    JSONFAQListResponse, JSONFAQImport, JSONFAQExport,
    QuestionType
)
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/json-faqs", tags=["JSON FAQs"])


@router.post("/", response_model=JSONFAQResponse)
async def create_json_faq(
    faq_data: JSONFAQCreate,
    db: Session = Depends(get_db)
):
    """Create a new JSON FAQ"""
    try:
        manager = JSONFAQManager(db)
        return manager.create_faq(faq_data)
    except Exception as e:
        logger.error(f"Error creating JSON FAQ: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=JSONFAQListResponse)
async def get_json_faqs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by"),
    question_type: Optional[QuestionType] = Query(None, description="Filter by question type"),
    search: Optional[str] = Query(None, description="Search in questions and answers"),
    db: Session = Depends(get_db)
):
    """Get paginated list of JSON FAQs with filters"""
    try:
        manager = JSONFAQManager(db)
        
        # Parse tags if provided
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        return manager.get_faqs(
            page=page,
            page_size=page_size,
            category=category,
            tags=tag_list,
            question_type=question_type,
            search_query=search
        )
    except Exception as e:
        logger.error(f"Error getting JSON FAQs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{faq_id}", response_model=JSONFAQResponse)
async def get_json_faq(
    faq_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific JSON FAQ by ID"""
    try:
        manager = JSONFAQManager(db)
        faq = manager.get_faq(faq_id)
        if not faq:
            raise HTTPException(status_code=404, detail="JSON FAQ not found")
        return faq
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting JSON FAQ {faq_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{faq_id}", response_model=JSONFAQResponse)
async def update_json_faq(
    faq_id: str,
    faq_data: JSONFAQUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing JSON FAQ"""
    try:
        manager = JSONFAQManager(db)
        faq = manager.update_faq(faq_id, faq_data)
        if not faq:
            raise HTTPException(status_code=404, detail="JSON FAQ not found")
        return faq
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating JSON FAQ {faq_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{faq_id}")
async def delete_json_faq(
    faq_id: str,
    db: Session = Depends(get_db)
):
    """Delete a JSON FAQ"""
    try:
        manager = JSONFAQManager(db)
        success = manager.delete_faq(faq_id)
        if not success:
            raise HTTPException(status_code=404, detail="JSON FAQ not found")
        return {"message": "JSON FAQ deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting JSON FAQ {faq_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import")
async def import_json_faqs(
    import_data: JSONFAQImport,
    db: Session = Depends(get_db)
):
    """Import multiple JSON FAQs"""
    try:
        manager = JSONFAQManager(db)
        results = manager.import_faqs(import_data)
        return {
            "message": "Import completed",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error importing JSON FAQs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import-file")
async def import_json_faqs_from_file(
    file: UploadFile = File(...),
    overwrite_existing: bool = Query(False, description="Overwrite existing FAQs"),
    validate_only: bool = Query(False, description="Only validate, don't import"),
    db: Session = Depends(get_db)
):
    """Import JSON FAQs from uploaded file"""
    try:
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="File must be a JSON file")
        
        content = await file.read()
        data = json.loads(content.decode('utf-8'))
        
        # Validate file structure
        if "faqs" not in data:
            raise HTTPException(status_code=400, detail="File must contain 'faqs' array")
        
        # Convert to import format
        faqs = []
        for faq_data in data["faqs"]:
            faqs.append(JSONFAQCreate(**faq_data))
        
        import_data = JSONFAQImport(
            faqs=faqs,
            overwrite_existing=overwrite_existing,
            validate_only=validate_only
        )
        
        manager = JSONFAQManager(db)
        results = manager.import_faqs(import_data)
        
        return {
            "message": "File import completed",
            "filename": file.filename,
            "results": results
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        logger.error(f"Error importing JSON FAQs from file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/json")
async def export_json_faqs(
    faq_ids: Optional[str] = Query(None, description="Comma-separated FAQ IDs to export"),
    db: Session = Depends(get_db)
):
    """Export JSON FAQs as JSON"""
    try:
        manager = JSONFAQManager(db)
        
        # Parse FAQ IDs if provided
        faq_id_list = None
        if faq_ids:
            faq_id_list = [id.strip() for id in faq_ids.split(",") if id.strip()]
        
        export_data = manager.export_faqs(faq_id_list)
        
        return {
            "export_data": export_data.dict(),
            "message": f"Exported {len(export_data.faqs)} FAQs"
        }
        
    except Exception as e:
        logger.error(f"Error exporting JSON FAQs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/similar")
async def search_similar_questions(
    query: str = Query(..., description="Search query"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Search for similar questions"""
    try:
        manager = JSONFAQManager(db)
        results = manager.search_similar_questions(query, limit)
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching similar questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{faq_id}/increment-usage")
async def increment_faq_usage(
    faq_id: str,
    db: Session = Depends(get_db)
):
    """Increment usage count for a FAQ"""
    try:
        manager = JSONFAQManager(db)
        success = manager.increment_usage(faq_id)
        if not success:
            raise HTTPException(status_code=404, detail="JSON FAQ not found")
        return {"message": "Usage count incremented successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error incrementing usage for FAQ {faq_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview")
async def get_faq_stats(
    db: Session = Depends(get_db)
):
    """Get overview statistics for JSON FAQs"""
    try:
        manager = JSONFAQManager(db)
        
        # Get basic stats
        all_faqs = manager.get_faqs(page=1, page_size=1000)  # Get all
        
        stats = {
            "total_faqs": all_faqs.total,
            "active_faqs": len([f for f in all_faqs.items if f.is_active]),
            "inactive_faqs": len([f for f in all_faqs.items if not f.is_active]),
            "question_types": {},
            "categories": {},
            "total_usage": sum(f.usage_count for f in all_faqs.items),
            "most_used": []
        }
        
        # Count question types
        for faq in all_faqs.items:
            q_type = faq.question_type.value
            stats["question_types"][q_type] = stats["question_types"].get(q_type, 0) + 1
        
        # Count categories
        for faq in all_faqs.items:
            if faq.category:
                stats["categories"][faq.category] = stats["categories"].get(faq.category, 0) + 1
        
        # Get most used FAQs
        sorted_faqs = sorted(all_faqs.items, key=lambda x: x.usage_count, reverse=True)
        stats["most_used"] = [
            {
                "id": faq.id,
                "question": faq.question,
                "usage_count": faq.usage_count
            }
            for faq in sorted_faqs[:5]
        ]
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting FAQ stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
