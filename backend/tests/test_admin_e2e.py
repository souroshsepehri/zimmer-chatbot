"""
End-to-end tests that simulate actual user interactions with admin panel
These tests verify the complete workflow from frontend to backend
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models.log import ChatLog
from models.faq import FAQ, Category


class TestAdminPanelE2E:
    """End-to-end tests simulating real admin panel usage"""
    
    def test_complete_faq_workflow(self, test_client: TestClient, test_db: Session):
        """Test complete FAQ management workflow as a user would do"""
        # 1. User opens FAQ page - should load
        response = test_client.get("/admin/faqs")
        assert response.status_code == 200
        
        # 2. User creates a category first
        category_data = {"name": "پشتیبانی", "slug": "support"}
        cat_response = test_client.post("/api/categories", json=category_data)
        assert cat_response.status_code == 200
        category_id = cat_response.json()["id"]
        
        # 3. User creates an FAQ
        faq_data = {
            "question": "چطور می‌توانم با پشتیبانی تماس بگیرم؟",
            "answer": "شما می‌توانید از طریق ایمیل تماس بگیرید.",
            "category_id": category_id
        }
        create_response = test_client.post("/api/faqs", json=faq_data)
        assert create_response.status_code == 200
        faq_id = create_response.json()["id"]
        
        # 4. User views the FAQ list
        list_response = test_client.get("/api/faqs")
        assert list_response.status_code == 200
        faqs = list_response.json().get("items", [])
        assert any(f["id"] == faq_id for f in faqs)
        
        # 5. User edits the FAQ
        update_data = {"answer": "شما می‌توانید از طریق ایمیل یا تلفن تماس بگیرید."}
        update_response = test_client.put(f"/api/faqs/{faq_id}", json=update_data)
        assert update_response.status_code == 200
        assert "تلفن" in update_response.json()["answer"]
        
        # 6. User deletes the FAQ
        delete_response = test_client.delete(f"/api/faqs/{faq_id}")
        assert delete_response.status_code == 200
        
        # 7. Verify FAQ is gone
        get_response = test_client.get(f"/api/faqs/{faq_id}")
        assert get_response.status_code == 404
    
    def test_complete_category_workflow(self, test_client: TestClient, test_db: Session):
        """Test complete category management workflow"""
        # 1. User opens categories page
        response = test_client.get("/admin/categories")
        assert response.status_code == 200
        
        # 2. User creates a category
        category_data = {"name": "فروش", "slug": "sales"}
        create_response = test_client.post("/api/categories", json=category_data)
        assert create_response.status_code == 200
        category_id = create_response.json()["id"]
        
        # 3. User views categories list
        list_response = test_client.get("/api/categories")
        assert list_response.status_code == 200
        categories = list_response.json()
        assert any(c["id"] == category_id for c in categories)
        
        # 4. User creates FAQ in this category
        faq_data = {
            "question": "قیمت محصولات؟",
            "answer": "لطفاً با بخش فروش تماس بگیرید.",
            "category_id": category_id
        }
        faq_response = test_client.post("/api/faqs", json=faq_data)
        assert faq_response.status_code == 200
        
        # 5. User tries to delete category (should fail if FAQs exist)
        delete_response = test_client.delete(f"/api/categories/{category_id}")
        # Should fail because FAQ exists
        assert delete_response.status_code in [400, 409]
    
    def test_admin_dashboard_data_flow(self, test_client: TestClient, test_db: Session):
        """Test that admin dashboard shows correct data"""
        # Create test data
        test_db.add(ChatLog(user_text="Test Q1", ai_text="Test A1", success=True))
        test_db.add(ChatLog(user_text="Test Q2", ai_text="Test A2", success=False))
        test_db.add(FAQ(question="FAQ 1", answer="Answer 1"))
        test_db.add(Category(name="Cat 1", slug="cat-1"))
        test_db.commit()
        
        # User opens admin panel
        panel_response = test_client.get("/admin")
        assert panel_response.status_code == 200
        
        # Dashboard loads stats
        stats_response = test_client.get("/admin/stats")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        
        # Verify stats are correct
        assert stats["total_questions"] == 2
        assert stats["total_faqs"] == 1
        assert stats["success_rate"] == 50.0
        
        # Dashboard stats endpoint
        dashboard_response = test_client.get("/admin/dashboard-stats")
        assert dashboard_response.status_code == 200
        dashboard = dashboard_response.json()
        
        assert dashboard["total_faqs"] == 1
        assert dashboard["total_categories"] == 1
        assert dashboard["total_logs"] == 2
    
    def test_logs_page_functionality(self, test_client: TestClient, test_db: Session):
        """Test that logs page works correctly"""
        # Create multiple logs
        for i in range(5):
            test_db.add(ChatLog(
                user_text=f"Question {i}",
                ai_text=f"Answer {i}",
                success=i % 2 == 0,  # Alternate success
                source="faq" if i < 3 else "llm"
            ))
        test_db.commit()
        
        # User opens logs page
        logs_page = test_client.get("/admin/logs")
        assert logs_page.status_code == 200
        
        # Logs API returns data
        logs_response = test_client.get("/api/logs?page=1&page_size=10")
        assert logs_response.status_code == 200
        logs_data = logs_response.json()
        
        assert "items" in logs_data
        assert len(logs_data["items"]) >= 5
        
        # Logs stats work
        stats_response = test_client.get("/api/logs/stats")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        
        assert stats["total_logs"] == 5
        assert stats["success_rate"] == 60.0  # 3 out of 5 successful
        
        # Recent logs endpoint
        recent_response = test_client.get("/admin/recent-logs?limit=3")
        assert recent_response.status_code == 200
        recent = recent_response.json()
        assert len(recent["logs"]) == 3

