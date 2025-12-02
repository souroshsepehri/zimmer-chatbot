"""
Self-check script to verify SmartAIAgent integration with chat_orchestrator.

This script simulates a call to chat_orchestrator with a general question
(no FAQ match) and verifies that:
1. smart_agent.answer() is called
2. The debug structure includes smart_agent_raw with the smart agent output
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from services.chat_orchestrator import chat_orchestrator
from services.smart_agent import smart_agent


async def test_smart_agent_integration():
    """Test that smart agent is properly integrated"""
    print("=" * 60)
    print("Testing SmartAIAgent Integration with ChatOrchestrator")
    print("=" * 60)
    
    # Test message - general question with no FAQ match expected
    test_message = "فرض کن من مشتری Zimmerman هستم، دقیقا چه خدمتی به من میدی؟"
    
    print(f"\n1. Test message: {test_message}")
    print(f"2. Smart agent enabled: {getattr(smart_agent, 'enabled', False)}")
    
    # Simulate a call to chat_orchestrator
    print("\n3. Calling chat_orchestrator.route_message()...")
    try:
        result = await chat_orchestrator.route_message(
            message=test_message,
            context={
                "session_id": "test_session",
                "source": "public-smart-test",
            },
            mode="auto",
        )
        
        print("\n4. Response received:")
        print(f"   - Answer length: {len(result.get('answer', ''))} chars")
        print(f"   - Source: {result.get('source')}")
        print(f"   - Success: {result.get('success')}")
        print(f"   - Intent: {result.get('intent')}")
        print(f"   - Confidence: {result.get('confidence')}")
        
        # Check debug_info
        debug_info = result.get("debug_info", {})
        print(f"\n5. Debug info structure:")
        print(f"   - Has smart_agent_raw: {'smart_agent_raw' in debug_info}")
        print(f"   - Has baseline_raw: {'baseline_raw' in debug_info}")
        print(f"   - Mode: {debug_info.get('mode')}")
        
        # Check smart_agent_raw
        smart_agent_raw = debug_info.get("smart_agent_raw")
        if smart_agent_raw is not None:
            print(f"\n6. Smart agent raw result:")
            print(f"   - Success: {smart_agent_raw.get('success')}")
            print(f"   - Source: {smart_agent_raw.get('source')}")
            print(f"   - Has answer: {bool(smart_agent_raw.get('answer'))}")
            if smart_agent_raw.get('answer'):
                answer_preview = smart_agent_raw.get('answer', '')[:100]
                print(f"   - Answer preview: {answer_preview}...")
            print(f"   - Metadata: {smart_agent_raw.get('metadata', {})}")
            print("   ✅ smart_agent.answer() was called and result is in debug_info")
        else:
            print("\n6. Smart agent raw result: None")
            if not getattr(smart_agent, 'enabled', False):
                print("   ⚠️  Smart agent is disabled (expected if no API key)")
            else:
                print("   ⚠️  Smart agent is enabled but returned None (check logs)")
        
        # Verify the structure matches requirements
        print("\n7. Structure verification:")
        required_fields = ["answer", "source", "success", "intent", "confidence", "debug_info"]
        all_present = all(field in result for field in required_fields)
        print(f"   - All required fields present: {all_present}")
        
        if all_present and "smart_agent_raw" in debug_info:
            print("\n✅ Integration test PASSED")
            print("   - smart_agent.answer() is being called")
            print("   - debug_info includes smart_agent_raw")
            print("   - Response structure is correct")
            return True
        else:
            print("\n❌ Integration test FAILED")
            print("   - Some required fields or structures are missing")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_smart_agent_integration())
    sys.exit(0 if success else 1)














