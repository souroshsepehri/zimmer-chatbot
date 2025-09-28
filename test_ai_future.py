#!/usr/bin/env python3
"""
Test for AI Future Disabled Error
Checks all components that might cause this error
"""

import os
import sys

def test_ai_future_error():
    """Test for AI future disabled error"""
    print("🔍 TESTING FOR 'AI FUTURE DISABLED' ERROR")
    print("=" * 50)
    
    # Set API key
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")
    
    try:
        print("1. Testing OpenAI client...")
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("✅ OpenAI client created successfully")
        
        print("2. Testing OpenAI API call...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "سلام"}],
            max_tokens=50
        )
        print(f"✅ OpenAI API call successful: {response.choices[0].message.content}")
        
        print("3. Testing backend services...")
        sys.path.append('backend')
        
        from services.intent import IntentDetector
        intent_detector = IntentDetector()
        print("✅ Intent detector created")
        
        from services.retriever import FAQRetriever
        retriever = FAQRetriever()
        print("✅ FAQRetriever created")
        
        from services.answer import AnswerGenerator
        answer_generator = AnswerGenerator()
        print("✅ Answer generator created")
        
        print("4. Testing chat chain...")
        from services.chain import ChatChain
        chat_chain = ChatChain()
        print("✅ Chat chain created")
        
        print("5. Testing complete chat flow...")
        from core.db import get_db
        db = next(get_db())
        
        result = chat_chain.process_message("سلام", db)
        print(f"✅ Chat flow successful: {result['answer'][:50]}...")
        
        print("\n🎉 NO 'AI FUTURE DISABLED' ERRORS FOUND!")
        print("=" * 50)
        print("✅ All components working correctly")
        print("✅ OpenAI API working")
        print("✅ Backend services working")
        print("✅ Chat flow working")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR FOUND: {e}")
        print("This might be the 'AI future disabled' error you're seeing.")
        
        # Check if it's a specific error type
        if "future" in str(e).lower():
            print("🔍 This appears to be a 'future' related error!")
        if "disabled" in str(e).lower():
            print("🔍 This appears to be a 'disabled' related error!")
        if "ai" in str(e).lower():
            print("🔍 This appears to be an 'AI' related error!")
            
        return False

if __name__ == "__main__":
    test_ai_future_error()
