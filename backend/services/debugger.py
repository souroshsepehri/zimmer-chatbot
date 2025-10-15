"""
Comprehensive Chatbot Debugger System
Provides detailed debugging, logging, and diagnostic capabilities
"""

import logging
import json
import time
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
from sqlalchemy.orm import Session
from sqlalchemy import text

from core.db import get_db
from models.faq import FAQ, Category
from .simple_chatbot import SimpleChatbot
from .smart_chatbot import SmartChatbot
from .smart_intent_detector import get_smart_intent_detector, IntentType

# Configure debug logging
debug_logger = logging.getLogger('chatbot_debugger')
debug_logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
Path('logs').mkdir(exist_ok=True)

# Create debug log file handler
debug_handler = logging.FileHandler('logs/debug.log', encoding='utf-8')
debug_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
debug_handler.setFormatter(debug_formatter)
debug_logger.addHandler(debug_handler)

@dataclass
class DebugSession:
    """Debug session information"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

@dataclass
class DebugRequest:
    """Individual request debug information"""
    request_id: str
    session_id: str
    timestamp: datetime
    user_message: str
    response: str
    response_time: float
    intent_detected: Optional[str] = None
    faq_matches: List[Dict] = None
    search_scores: List[float] = None
    error_message: Optional[str] = None
    debug_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.faq_matches is None:
            self.faq_matches = []
        if self.search_scores is None:
            self.search_scores = []
        if self.debug_info is None:
            self.debug_info = {}

class ChatbotDebugger:
    """
    Comprehensive chatbot debugging and monitoring system
    """
    
    def __init__(self):
        self.sessions: Dict[str, DebugSession] = {}
        self.requests: List[DebugRequest] = []
        self.debug_log_file = Path('logs/debug.log')
        self.debug_log_file.parent.mkdir(exist_ok=True)
        
        # Initialize debug logging
        self._setup_debug_logging()
        
        debug_logger.info("ChatbotDebugger initialized")
    
    def _setup_debug_logging(self):
        """Setup comprehensive debug logging"""
        # Create logs directory if it doesn't exist
        Path('logs').mkdir(exist_ok=True)
        
        # Setup detailed logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/chatbot_debug.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def start_debug_session(self, session_id: str = None) -> str:
        """Start a new debug session"""
        if session_id is None:
            session_id = f"session_{int(time.time())}"
        
        session = DebugSession(
            session_id=session_id,
            start_time=datetime.now()
        )
        
        self.sessions[session_id] = session
        debug_logger.info(f"Started debug session: {session_id}")
        
        return session_id
    
    def end_debug_session(self, session_id: str):
        """End a debug session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.end_time = datetime.now()
            
            # Calculate session statistics
            session_requests = [r for r in self.requests if r.session_id == session_id]
            session.total_requests = len(session_requests)
            session.successful_requests = len([r for r in session_requests if r.error_message is None])
            session.failed_requests = len([r for r in session_requests if r.error_message is not None])
            
            if session_requests:
                session.average_response_time = sum(r.response_time for r in session_requests) / len(session_requests)
            
            debug_logger.info(f"Ended debug session: {session_id} - {session.total_requests} requests, {session.successful_requests} successful")
    
    def log_request(self, session_id: str, user_message: str, response: str, 
                   response_time: float, intent_detected: str = None,
                   faq_matches: List[Dict] = None, search_scores: List[float] = None,
                   error_message: str = None, debug_info: Dict[str, Any] = None) -> str:
        """Log a chatbot request with full debug information"""
        
        request_id = f"req_{int(time.time() * 1000)}"
        
        request = DebugRequest(
            request_id=request_id,
            session_id=session_id,
            timestamp=datetime.now(),
            user_message=user_message,
            response=response,
            response_time=response_time,
            intent_detected=intent_detected,
            faq_matches=faq_matches or [],
            search_scores=search_scores or [],
            error_message=error_message,
            debug_info=debug_info or {}
        )
        
        self.requests.append(request)
        
        # Update session
        if session_id in self.sessions:
            self.sessions[session_id].total_requests += 1
            if error_message:
                self.sessions[session_id].failed_requests += 1
                self.sessions[session_id].errors.append(error_message)
            else:
                self.sessions[session_id].successful_requests += 1
        
        # Log to file
        debug_logger.info(f"Request {request_id}: '{user_message}' -> '{response}' ({response_time:.3f}s)")
        if error_message:
            debug_logger.error(f"Request {request_id} error: {error_message}")
        
        return request_id
    
    def diagnose_database(self) -> Dict[str, Any]:
        """Diagnose database health and content"""
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "database_accessible": False,
            "total_faqs": 0,
            "active_faqs": 0,
            "categories": [],
            "sample_faqs": [],
            "errors": []
        }
        
        try:
            db = next(get_db())
            
            # Check database accessibility
            diagnosis["database_accessible"] = True
            
            # Count FAQs
            total_faqs = db.query(FAQ).count()
            active_faqs = db.query(FAQ).filter(FAQ.is_active == True).count()
            diagnosis["total_faqs"] = total_faqs
            diagnosis["active_faqs"] = active_faqs
            
            # Get categories
            categories = db.query(Category).all()
            diagnosis["categories"] = [{"id": c.id, "name": c.name, "slug": c.slug} for c in categories]
            
            # Get sample FAQs
            sample_faqs = db.query(FAQ).filter(FAQ.is_active == True).limit(5).all()
            diagnosis["sample_faqs"] = [
                {
                    "id": f.id,
                    "question": f.question,
                    "answer": f.answer[:100] + "..." if len(f.answer) > 100 else f.answer,
                    "category": f.category.name if f.category else "None"
                }
                for f in sample_faqs
            ]
            
            db.close()
            
        except Exception as e:
            diagnosis["errors"].append(f"Database error: {str(e)}")
            debug_logger.error(f"Database diagnosis error: {e}")
        
        return diagnosis
    
    def diagnose_chatbot_services(self) -> Dict[str, Any]:
        """Diagnose chatbot services health"""
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "simple_chatbot": {"status": "unknown", "faqs_loaded": 0, "error": None},
            "smart_chatbot": {"status": "unknown", "error": None},
            "intent_detector": {"status": "unknown", "error": None}
        }
        
        # Test Simple Chatbot
        try:
            simple_bot = SimpleChatbot()
            simple_bot.load_faqs_from_db()
            diagnosis["simple_chatbot"]["status"] = "healthy"
            diagnosis["simple_chatbot"]["faqs_loaded"] = len(simple_bot.faqs)
        except Exception as e:
            diagnosis["simple_chatbot"]["status"] = "error"
            diagnosis["simple_chatbot"]["error"] = str(e)
            debug_logger.error(f"Simple chatbot diagnosis error: {e}")
        
        # Test Smart Chatbot
        try:
            smart_bot = SmartChatbot()
            diagnosis["smart_chatbot"]["status"] = "healthy"
        except Exception as e:
            diagnosis["smart_chatbot"]["status"] = "error"
            diagnosis["smart_chatbot"]["error"] = str(e)
            debug_logger.error(f"Smart chatbot diagnosis error: {e}")
        
        # Test Intent Detector
        try:
            intent_detector = get_smart_intent_detector()
            test_intent = intent_detector.detect_intent("سلام")
            diagnosis["intent_detector"]["status"] = "healthy"
            diagnosis["intent_detector"]["test_intent"] = test_intent.intent_type.value
        except Exception as e:
            diagnosis["intent_detector"]["status"] = "error"
            diagnosis["intent_detector"]["error"] = str(e)
            debug_logger.error(f"Intent detector diagnosis error: {e}")
        
        return diagnosis
    
    def test_chatbot_response(self, message: str, chatbot_type: str = "simple") -> Dict[str, Any]:
        """Test chatbot response with detailed debugging"""
        test_result = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "chatbot_type": chatbot_type,
            "response": None,
            "response_time": 0,
            "intent_detected": None,
            "faq_matches": [],
            "search_scores": [],
            "error": None,
            "debug_info": {}
        }
        
        start_time = time.time()
        
        try:
            if chatbot_type == "simple":
                chatbot = SimpleChatbot()
                chatbot.load_faqs_from_db()
                
                # Get response
                response_data = chatbot.get_answer(message)
                test_result["response"] = response_data.get("answer", "No response")
                test_result["faq_matches"] = response_data.get("faq_matches", [])
                test_result["search_scores"] = response_data.get("scores", [])
                
            elif chatbot_type == "smart":
                chatbot = SmartChatbot()
                response_data = chatbot.get_response(message)
                test_result["response"] = response_data.get("answer", "No response")
                test_result["intent_detected"] = response_data.get("intent", {}).get("intent_type")
                test_result["faq_matches"] = response_data.get("faq_matches", [])
                test_result["search_scores"] = response_data.get("scores", [])
                test_result["debug_info"] = response_data.get("debug_info", {})
            
            test_result["response_time"] = time.time() - start_time
            
        except Exception as e:
            test_result["error"] = str(e)
            test_result["response_time"] = time.time() - start_time
            debug_logger.error(f"Chatbot test error: {e}")
            debug_logger.error(traceback.format_exc())
        
        return test_result
    
    def get_debug_statistics(self, session_id: str = None) -> Dict[str, Any]:
        """Get comprehensive debug statistics"""
        stats = {
            "timestamp": datetime.now().isoformat(),
            "total_sessions": len(self.sessions),
            "total_requests": len(self.requests),
            "active_sessions": 0,
            "average_response_time": 0,
            "success_rate": 0,
            "error_rate": 0,
            "recent_errors": [],
            "top_intents": {},
            "performance_metrics": {}
        }
        
        # Filter by session if specified
        if session_id:
            requests = [r for r in self.requests if r.session_id == session_id]
            sessions = {k: v for k, v in self.sessions.items() if k == session_id}
        else:
            requests = self.requests
            sessions = self.sessions
        
        if requests:
            # Calculate statistics
            successful_requests = [r for r in requests if r.error_message is None]
            failed_requests = [r for r in requests if r.error_message is not None]
            
            stats["total_requests"] = len(requests)
            stats["success_rate"] = len(successful_requests) / len(requests) * 100
            stats["error_rate"] = len(failed_requests) / len(requests) * 100
            
            if successful_requests:
                stats["average_response_time"] = sum(r.response_time for r in successful_requests) / len(successful_requests)
            
            # Recent errors
            stats["recent_errors"] = [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "message": r.user_message,
                    "error": r.error_message
                }
                for r in failed_requests[-10:]  # Last 10 errors
            ]
            
            # Top intents
            intents = [r.intent_detected for r in requests if r.intent_detected]
            intent_counts = {}
            for intent in intents:
                intent_counts[intent] = intent_counts.get(intent, 0) + 1
            stats["top_intents"] = dict(sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Active sessions
        stats["active_sessions"] = len([s for s in sessions.values() if s.end_time is None])
        
        return stats
    
    def export_debug_data(self, session_id: str = None, format: str = "json") -> str:
        """Export debug data for analysis"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "sessions": {k: asdict(v) for k, v in self.sessions.items()},
            "requests": [asdict(r) for r in self.requests],
            "statistics": self.get_debug_statistics(session_id)
        }
        
        if session_id:
            export_data["sessions"] = {k: v for k, v in export_data["sessions"].items() if k == session_id}
            export_data["requests"] = [r for r in export_data["requests"] if r["session_id"] == session_id]
        
        if format == "json":
            filename = f"debug_export_{int(time.time())}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            return filename
        
        return str(export_data)
    
    def clear_debug_data(self, session_id: str = None):
        """Clear debug data"""
        if session_id:
            # Clear specific session
            if session_id in self.sessions:
                del self.sessions[session_id]
            self.requests = [r for r in self.requests if r.session_id != session_id]
        else:
            # Clear all data
            self.sessions.clear()
            self.requests.clear()
        
        debug_logger.info(f"Cleared debug data for session: {session_id or 'all'}")

# Global debugger instance
debugger = ChatbotDebugger()
