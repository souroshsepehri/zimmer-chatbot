from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from models.faq import FAQ, Category
from schemas.faq import (
    FAQCreate, FAQUpdate, FAQ as FAQSchema,
    CategoryCreate, CategoryUpdate, Category as CategorySchema,
    FAQListResponse
)
from core.db import get_db
from services.retriever import faq_retriever
import math

router = APIRouter()


# FAQ CRUD endpoints
@router.get("/faqs", response_model=FAQListResponse)
async def get_faqs(
    category: Optional[str] = Query(None, description="Filter by category slug"),
    q: Optional[str] = Query(None, description="Search in question and answer"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get paginated list of FAQs with optional filters"""
    query = db.query(FAQ)
    
    # Apply category filter
    if category:
        query = query.join(FAQ.category).filter(Category.slug == category)
    
    # Apply search filter
    if q:
        search_filter = or_(
            FAQ.question.contains(q),
            FAQ.answer.contains(q)
        )
        query = query.filter(search_filter)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    faqs = query.offset(offset).limit(page_size).all()
    
    # Calculate total pages
    total_pages = math.ceil(total / page_size)
    
    return FAQListResponse(
        items=faqs,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("/faqs", response_model=FAQSchema)
async def create_faq(
    faq_data: FAQCreate,
    db: Session = Depends(get_db)
):
    """Create a new FAQ"""
    # Validate category exists if provided
    if faq_data.category_id:
        category = db.query(Category).filter(Category.id == faq_data.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
    
    faq = FAQ(**faq_data.dict())
    db.add(faq)
    db.commit()
    db.refresh(faq)
    
    return faq


@router.get("/faqs/{faq_id}", response_model=FAQSchema)
async def get_faq(
    faq_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific FAQ by ID"""
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return faq


@router.put("/faqs/{faq_id}", response_model=FAQSchema)
async def update_faq(
    faq_id: int,
    faq_data: FAQUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing FAQ"""
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    
    # Validate category exists if provided
    if faq_data.category_id:
        category = db.query(Category).filter(Category.id == faq_data.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
    
    # Update fields
    update_data = faq_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(faq, field, value)
    
    db.commit()
    db.refresh(faq)
    
    return faq


@router.delete("/faqs/{faq_id}")
async def delete_faq(
    faq_id: int,
    db: Session = Depends(get_db)
):
    """Delete an FAQ"""
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    
    db.delete(faq)
    db.commit()
    
    return {"message": "FAQ deleted successfully"}


@router.post("/faqs/reindex")
async def reindex_faqs(db: Session = Depends(get_db)):
    """Rebuild the FAQ vector index"""
    try:
        faq_retriever.reindex(db)
        return {"message": "FAQ index rebuilt successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reindexing failed: {str(e)}")


# Category CRUD endpoints
@router.get("/categories", response_model=List[CategorySchema])
async def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    categories = db.query(Category).all()
    return categories


@router.post("/categories", response_model=CategorySchema)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new category"""
    # Check if category with same name or slug exists
    existing = db.query(Category).filter(
        or_(Category.name == category_data.name, Category.slug == category_data.slug)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name or slug already exists")
    
    category = Category(**category_data.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category


@router.put("/categories/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing category"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if another category with same name or slug exists
    existing = db.query(Category).filter(
        and_(
            Category.id != category_id,
            or_(Category.name == category_data.name, Category.slug == category_data.slug)
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name or slug already exists")
    
    # Update fields
    update_data = category_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    return category


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Delete a category"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if category has FAQs
    faq_count = db.query(FAQ).filter(FAQ.category_id == category_id).count()
    if faq_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete category with {faq_count} FAQs. Please move or delete FAQs first."
        )
    
    db.delete(category)
    db.commit()
    
    return {"message": "Category deleted successfully"}
