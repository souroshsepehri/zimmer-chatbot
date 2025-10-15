#!/usr/bin/env python3
"""
Comprehensive Chatbot Debugger and Diagnostic Tool
Run this script to diagnose and debug your chatbot
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n--- {title} ---")

def print_status(status, message):
    """Print status with color coding"""
    if status == "SUCCESS":
        print(f"[OK] {message}")
    elif status == "ERROR":
        print(f"[ERROR] {message}")
    elif status == "WARNING":
        print(f"[WARNING] {message}")
    elif status == "INFO":
        print(f"[INFO] {message}")
    else:
        print(f"[INFO] {message}")

def check_database():
    """Check database connectivity and content"""
    print_section("Database Check")
    
    try:
        from core.db import get_db
        from models.faq import FAQ, Category
        
        db = next(get_db())
        
        # Check database connection
        print_status("SUCCESS", "Database connection established")
        
        # Count FAQs
        total_faqs = db.query(FAQ).count()
        active_faqs = db.query(FAQ).filter(FAQ.is_active == True).count()
        print_status("INFO", f"Total FAQs: {total_faqs}")
        print_status("INFO", f"Active FAQs: {active_faqs}")
        
        # Count categories
        total_categories = db.query(Category).count()
        print_status("INFO", f"Total Categories: {total_categories}")
        
        # Check for greeting FAQs
        greeting_faqs = db.query(FAQ).filter(FAQ.question.like('%سلام%')).count()
        print_status("INFO", f"Greeting FAQs: {greeting_faqs}")
        
        # Sample FAQs
        sample_faqs = db.query(FAQ).filter(FAQ.is_active == True).limit(3).all()
        if sample_faqs:
            print_status("INFO", "Sample FAQs:")
            for faq in sample_faqs:
                print(f"  - Q: {faq.question[:50]}...")
                print(f"    A: {faq.answer[:50]}...")
        
        db.close()
        return True
        
    except Exception as e:
        print_status("ERROR", f"Database check failed: {e}")
        return False

def check_services():
    """Check chatbot services"""
    print_section("Services Check")
    
    # Test Simple Chatbot
    try:
        from services.simple_chatbot import SimpleChatbot
        simple_bot = SimpleChatbot()
        simple_bot.load_faqs_from_db()
        print_status("SUCCESS", f"Simple Chatbot: {len(simple_bot.faqs)} FAQs loaded")
    except Exception as e:
        print_status("ERROR", f"Simple Chatbot failed: {e}")
    
    # Test Smart Chatbot
    try:
        from services.smart_chatbot import SmartChatbot
        smart_bot = SmartChatbot()
        print_status("SUCCESS", "Smart Chatbot initialized")
    except Exception as e:
        print_status("ERROR", f"Smart Chatbot failed: {e}")
    
    # Test Intent Detector
    try:
        from services.smart_intent_detector import get_smart_intent_detector
        intent_detector = get_smart_intent_detector()
        test_intent = intent_detector.detect_intent("سلام")
        print_status("SUCCESS", f"Intent Detector: {test_intent.intent_type.value}")
    except Exception as e:
        print_status("ERROR", f"Intent Detector failed: {e}")

def test_responses():
    """Test chatbot responses"""
    print_section("Response Testing")
    
    test_messages = [
        "سلام",
        "قیمت محصولات",
        "گارانتی دارید؟",
        "ساعات کاری",
        "چطور سفارش بدم؟"
    ]
    
    try:
        from services.simple_chatbot import SimpleChatbot
        simple_bot = SimpleChatbot()
        simple_bot.load_faqs_from_db()
        
        for message in test_messages:
            try:
                start_time = time.time()
                response = simple_bot.get_answer(message)
                response_time = time.time() - start_time
                
                answer = response.get("answer", "No answer")
                print_status("SUCCESS", f"'{message}' -> '{answer[:50]}...' ({response_time:.3f}s)")
                
            except Exception as e:
                print_status("ERROR", f"'{message}' failed: {e}")
                
    except Exception as e:
        print_status("ERROR", f"Response testing failed: {e}")

def check_logs():
    """Check log files"""
    print_section("Logs Check")
    
    log_files = [
        "logs/debug.log",
        "logs/chatbot_debug.log",
        "logs/chat.log"
    ]
    
    for log_file in log_files:
        log_path = Path(log_file)
        if log_path.exists():
            size = log_path.stat().st_size
            print_status("INFO", f"{log_file}: {size} bytes")
            
            # Show last few lines
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print_status("INFO", f"Last log entry: {lines[-1].strip()}")
            except Exception as e:
                print_status("WARNING", f"Could not read {log_file}: {e}")
        else:
            print_status("WARNING", f"{log_file}: Not found")

def check_configuration():
    """Check configuration"""
    print_section("Configuration Check")
    
    # Check environment variables
    env_vars = [
        "OPENAI_API_KEY",
        "DATABASE_URL",
        "VECTORSTORE_PATH"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "KEY" in var or "PASSWORD" in var:
                masked_value = value[:8] + "..." if len(value) > 8 else "***"
                print_status("SUCCESS", f"{var}: {masked_value}")
            else:
                print_status("SUCCESS", f"{var}: {value}")
        else:
            print_status("WARNING", f"{var}: Not set")
    
    # Check config file
    try:
        from core.config import settings
        print_status("SUCCESS", f"Config loaded: {settings.app_name}")
    except Exception as e:
        print_status("ERROR", f"Config loading failed: {e}")

def run_comprehensive_test():
    """Run comprehensive chatbot test"""
    print_section("Comprehensive Test")
    
    try:
        from services.debugger import debugger
        
        # Start debug session
        session_id = debugger.start_debug_session("comprehensive_test")
        print_status("SUCCESS", f"Debug session started: {session_id}")
        
        # Test messages
        test_messages = [
            "سلام",
            "قیمت",
            "گارانتی",
            "ساعات کاری",
            "سفارش"
        ]
        
        for message in test_messages:
            try:
                start_time = time.time()
                result = debugger.test_chatbot_response(message, "simple")
                response_time = time.time() - start_time
                
                if result["error"]:
                    print_status("ERROR", f"'{message}': {result['error']}")
                else:
                    print_status("SUCCESS", f"'{message}': {result['response'][:50]}... ({response_time:.3f}s)")
                    
            except Exception as e:
                print_status("ERROR", f"'{message}' test failed: {e}")
        
        # End debug session
        debugger.end_debug_session(session_id)
        
        # Get statistics
        stats = debugger.get_debug_statistics(session_id)
        print_status("INFO", f"Test completed: {stats['total_requests']} requests, {stats['success_rate']:.1f}% success rate")
        
    except Exception as e:
        print_status("ERROR", f"Comprehensive test failed: {e}")

def generate_report():
    """Generate diagnostic report"""
    print_section("Generating Report")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "database_check": {},
        "services_check": {},
        "configuration_check": {},
        "recommendations": []
    }
    
    # Database check
    try:
        from core.db import get_db
        from models.faq import FAQ, Category
        db = next(get_db())
        
        report["database_check"] = {
            "accessible": True,
            "total_faqs": db.query(FAQ).count(),
            "active_faqs": db.query(FAQ).filter(FAQ.is_active == True).count(),
            "categories": db.query(Category).count()
        }
        db.close()
    except Exception as e:
        report["database_check"] = {"accessible": False, "error": str(e)}
    
    # Generate recommendations
    if report["database_check"].get("active_faqs", 0) < 5:
        report["recommendations"].append("Add more FAQs to improve chatbot responses")
    
    if not os.getenv("OPENAI_API_KEY"):
        report["recommendations"].append("Set OPENAI_API_KEY environment variable")
    
    # Save report
    report_file = f"diagnostic_report_{int(time.time())}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print_status("SUCCESS", f"Diagnostic report saved: {report_file}")
    
    # Print recommendations
    if report["recommendations"]:
        print_status("INFO", "Recommendations:")
        for rec in report["recommendations"]:
            print(f"  - {rec}")

def main():
    """Main debug function"""
    print_header("Chatbot Debugger & Diagnostic Tool")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Run all checks
    check_database()
    check_services()
    check_configuration()
    check_logs()
    test_responses()
    run_comprehensive_test()
    generate_report()
    
    print_header("Debug Complete")
    print_status("INFO", "All diagnostic checks completed")
    print_status("INFO", "Check the debug interface at: http://localhost:8000/api/debug/interface")
    print_status("INFO", "View debug logs in: logs/debug.log")

if __name__ == "__main__":
    main()
