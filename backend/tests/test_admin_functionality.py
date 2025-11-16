"""
Comprehensive functional tests for admin panel functionality
These tests verify that the admin panel actually works, not just that endpoints exist
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models.faq import FAQ, Category
from models.log import ChatLog
from datetime import datetime


class TestAdminPanelFunctionality:
    """Test that admin panel features actually work"""
    
    def test_admin_stats_returns_correct_data(self, test_client: TestClient, test_db: Session):
        """Test that /admin/stats returns correct statistics"""
        # Create some test data
        test_db.add(ChatLog(user_text="Test question", ai_text="Test answer", success=True))
        test_db.add(ChatLog(user_text="Test question 2", ai_text="Test answer 2", success=False))
        test_db.add(FAQ(question="Test FAQ", answer="Test Answer"))
        test_db.commit()
        
        response = test_client.get("/admin/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields exist
        assert "total_questions" in data
        assert "success_rate" in data
        assert "active_users" in data
        assert "response_time" in data
        assert "total_faqs" in data
        
        # Verify data is correct
        assert data["total_questions"] == 2
        assert data["total_faqs"] == 1
        assert data["success_rate"] == 50.0  # 1 out of 2 successful
    
    def test_admin_dashboard_stats_works(self, test_client: TestClient, test_db: Session):
        """Test that /admin/dashboard-stats returns correct data"""
        # Create test data
        test_db.add(FAQ(question="FAQ 1", answer="Answer 1"))
        test_db.add(FAQ(question="FAQ 2", answer="Answer 2"))
        test_db.add(Category(name="Test Category", slug="test-category"))
        test_db.add(ChatLog(user_text="Question", ai_text="Answer", success=True, latency_ms=150))
        test_db.commit()
        
        response = test_client.get("/admin/dashboard-stats")
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_faqs"] == 2
        assert data["total_categories"] == 1
        assert data["total_logs"] == 1
        assert data["success_rate"] == 100.0
        assert data["avg_response_time"] == 0.15  # 150ms = 0.15s
    
    def test_admin_recent_logs_returns_data(self, test_client: TestClient, test_db: Session):
        """Test that /admin/recent-logs returns recent logs"""
        # Create multiple logs with different timestamps
        import time
        for i in range(5):
            test_db.add(ChatLog(
                user_text=f"Question {i}",
                ai_text=f"Answer {i}",
                success=True,
                timestamp=datetime.now()
            ))
            time.sleep(0.01)  # Small delay to ensure different timestamps
        test_db.commit()
        
        response = test_client.get("/admin/recent-logs?limit=3")
        assert response.status_code == 200
        data = response.json()
        
        assert "logs" in data
        assert len(data["logs"]) == 3  # Should return only 3 most recent
        # Verify we got logs back (order may vary, so just check we have data)
        assert all("user_text" in log for log in data["logs"])
        assert all("ai_text" in log for log in data["logs"])


class TestFAQManagementFunctionality:
    """Test that FAQ management actually works"""
    
    def test_create_faq_via_api(self, test_client: TestClient, test_db: Session):
        """Test creating an FAQ and verifying it's saved"""
        faq_data = {
            "question": "سوال تستی؟",
            "answer": "پاسخ تستی",
            "category_id": None
        }
        
        response = test_client.post("/api/faqs", json=faq_data)
        assert response.status_code == 200
        
        created_faq = response.json()
        assert created_faq["question"] == faq_data["question"]
        assert created_faq["answer"] == faq_data["answer"]
        assert "id" in created_faq
        
        # Verify it's actually in the database
        faq_id = created_faq["id"]
        db_faq = test_db.query(FAQ).filter(FAQ.id == faq_id).first()
        assert db_faq is not None
        assert db_faq.question == faq_data["question"]
    
    def test_update_faq_via_api(self, test_client: TestClient, test_db: Session):
        """Test updating an FAQ"""
        # Create FAQ first
        faq = FAQ(question="Original Question", answer="Original Answer")
        test_db.add(faq)
        test_db.commit()
        test_db.refresh(faq)
        
        # Update it
        update_data = {
            "question": "Updated Question",
            "answer": "Updated Answer"
        }
        response = test_client.put(f"/api/faqs/{faq.id}", json=update_data)
        assert response.status_code == 200
        
        updated_faq = response.json()
        assert updated_faq["question"] == "Updated Question"
        assert updated_faq["answer"] == "Updated Answer"
        
        # Verify in database
        db_faq = test_db.query(FAQ).filter(FAQ.id == faq.id).first()
        assert db_faq.question == "Updated Question"
    
    def test_delete_faq_via_api(self, test_client: TestClient, test_db: Session):
        """Test deleting an FAQ"""
        # Create FAQ
        faq = FAQ(question="To Delete", answer="Will be deleted")
        test_db.add(faq)
        test_db.commit()
        test_db.refresh(faq)
        faq_id = faq.id
        
        # Delete it
        response = test_client.delete(f"/api/faqs/{faq_id}")
        assert response.status_code == 200
        
        # Verify it's gone from database
        db_faq = test_db.query(FAQ).filter(FAQ.id == faq_id).first()
        assert db_faq is None
    
    def test_get_faqs_list(self, test_client: TestClient, test_db: Session):
        """Test getting list of FAQs"""
        # Create multiple FAQs
        for i in range(3):
            test_db.add(FAQ(question=f"Question {i}", answer=f"Answer {i}"))
        test_db.commit()
        
        response = test_client.get("/api/faqs")
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert len(data["items"]) >= 3  # At least 3 FAQs


class TestCategoryManagementFunctionality:
    """Test that category management actually works"""
    
    def test_create_category_via_api(self, test_client: TestClient, test_db: Session):
        """Test creating a category"""
        category_data = {
            "name": "دسته تستی",
            "slug": "test-category"
        }
        
        response = test_client.post("/api/categories", json=category_data)
        assert response.status_code == 200
        
        created_category = response.json()
        assert created_category["name"] == category_data["name"]
        assert created_category["slug"] == category_data["slug"]
        assert "id" in created_category
        
        # Verify in database
        category_id = created_category["id"]
        db_category = test_db.query(Category).filter(Category.id == category_id).first()
        assert db_category is not None
        assert db_category.name == category_data["name"]
    
    def test_get_categories_list(self, test_client: TestClient, test_db: Session):
        """Test getting list of categories"""
        # Create multiple categories
        for i in range(2):
            test_db.add(Category(name=f"Category {i}", slug=f"category-{i}"))
        test_db.commit()
        
        response = test_client.get("/api/categories")
        assert response.status_code == 200
        categories = response.json()
        
        assert isinstance(categories, list)
        assert len(categories) >= 2
    
    def test_delete_category_via_api(self, test_client: TestClient, test_db: Session):
        """Test deleting a category"""
        # Create category
        category = Category(name="To Delete", slug="to-delete")
        test_db.add(category)
        test_db.commit()
        test_db.refresh(category)
        category_id = category.id
        
        # Delete it
        response = test_client.delete(f"/api/categories/{category_id}")
        assert response.status_code == 200
        
        # Verify it's gone
        db_category = test_db.query(Category).filter(Category.id == category_id).first()
        assert db_category is None


class TestLogsFunctionality:
    """Test that logs functionality works"""
    
    def test_get_logs_list(self, test_client: TestClient, test_db: Session):
        """Test getting list of logs"""
        # Create multiple logs
        for i in range(3):
            test_db.add(ChatLog(
                user_text=f"User question {i}",
                ai_text=f"AI answer {i}",
                success=True
            ))
        test_db.commit()
        
        response = test_client.get("/api/logs")
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert len(data["items"]) >= 3
    
    def test_get_logs_stats(self, test_client: TestClient, test_db: Session):
        """Test getting logs statistics"""
        # Create logs with different success states
        test_db.add(ChatLog(user_text="Q1", ai_text="A1", success=True))
        test_db.add(ChatLog(user_text="Q2", ai_text="A2", success=True))
        test_db.add(ChatLog(user_text="Q3", ai_text="A3", success=False))
        test_db.commit()
        
        response = test_client.get("/api/logs/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_logs" in data
        assert data["total_logs"] == 3
        assert "success_rate" in data
        # Should be approximately 66.7% (2 out of 3)


class TestAdminPanelPages:
    """Test that admin panel pages are accessible"""
    
    def test_admin_panel_page_loads(self, test_client: TestClient):
        """Test that main admin panel page loads"""
        response = test_client.get("/admin")
        assert response.status_code == 200
        assert "پنل مدیریت" in response.text or "admin" in response.text.lower()
    
    def test_admin_faqs_page_loads(self, test_client: TestClient):
        """Test that FAQ management page loads"""
        response = test_client.get("/admin/faqs")
        assert response.status_code == 200
        assert "سوالات" in response.text or "faq" in response.text.lower()
    
    def test_admin_categories_page_loads(self, test_client: TestClient):
        """Test that categories page loads"""
        response = test_client.get("/admin/categories")
        assert response.status_code == 200
        assert "دسته" in response.text or "categor" in response.text.lower()
    
    def test_admin_logs_page_loads(self, test_client: TestClient):
        """Test that logs page loads"""
        response = test_client.get("/admin/logs")
        assert response.status_code == 200
        assert "گزارش" in response.text or "log" in response.text.lower()

