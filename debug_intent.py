#!/usr/bin/env python3
"""
Debug intent system
"""

def debug_intent():
    try:
        from services.intent import intent_detector
        
        # Test the LLM directly
        from langchain_core.prompts import ChatPromptTemplate
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "تو یک دسته‌بند نیت کاربر هستی. فقط یکی از برچسب‌ها را با احتمال برگردان. خروجی JSON بده."),
            ("human", "کاربر: سلام")
        ])
        
        formatted_prompt = prompt.format_messages()
        response = intent_detector.llm.invoke(formatted_prompt)
        
        print("Raw response:")
        print(repr(response.content))
        print("\nResponse content:")
        print(response.content)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_intent()
