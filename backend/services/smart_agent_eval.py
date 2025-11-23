"""
Evaluation framework for comparing SmartAIAgent vs baseline chat services.

This service runs test cases against both SmartAIAgent and baseline services
to compare their performance and behavior.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

import yaml

from services.smart_agent import smart_agent
from services.smart_chatbot import get_smart_chatbot

logger = logging.getLogger(__name__)

# Path to test cases file
TEST_CASES_PATH = Path(__file__).parent.parent / "tests" / "smart_agent_eval_cases.yaml"


def score_case(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the SmartAIAgent response vs expectations and baseline.
    
    Checks:
    - must_contain: all strings must appear in response
    - forbid_contains: none of these should appear
    - should_use_web_content: debug_info should indicate page content was used
    - should_mention_faq: debug_info should indicate FAQ was used
    - should_call_to_action: response should contain CTA phrases
    
    Args:
        result: Result dict from _run_single_case
        
    Returns:
        Dict with score, passed flags, and details
    """
    expectation = result.get("expectation", {})
    smart_result = result.get("smart_agent", {})
    smart_response = smart_result.get("response", "").lower() if isinstance(smart_result, dict) else ""
    smart_debug = smart_result.get("debug_info", {}) if isinstance(smart_result, dict) else {}
    
    score_details = {
        "passed": True,
        "checks": {},
        "total_checks": 0,
        "passed_checks": 0,
    }
    
    # Check must_contain
    must_contain = expectation.get("must_contain", [])
    if must_contain:
        score_details["total_checks"] += len(must_contain)
        for phrase in must_contain:
            phrase_lower = phrase.lower()
            found = phrase_lower in smart_response
            score_details["checks"][f"must_contain_{phrase}"] = found
            if found:
                score_details["passed_checks"] += 1
            else:
                score_details["passed"] = False
    
    # Check forbid_contains
    forbid_contains = expectation.get("forbid_contains", [])
    if forbid_contains:
        score_details["total_checks"] += len(forbid_contains)
        for phrase in forbid_contains:
            phrase_lower = phrase.lower()
            found = phrase_lower in smart_response
            score_details["checks"][f"forbid_contains_{phrase}"] = not found  # Pass if NOT found
            if not found:
                score_details["passed_checks"] += 1
            else:
                score_details["passed"] = False
    
    # Check should_use_web_content
    if expectation.get("should_use_web_content"):
        score_details["total_checks"] += 1
        has_page_content = smart_debug.get("has_page_content", False) or smart_debug.get("web_content_used", False)
        score_details["checks"]["should_use_web_content"] = has_page_content
        if has_page_content:
            score_details["passed_checks"] += 1
        else:
            score_details["passed"] = False
    
    # Check should_mention_faq
    if expectation.get("should_mention_faq"):
        score_details["total_checks"] += 1
        faq_count = smart_debug.get("faq_count", 0)
        has_faq = faq_count > 0
        score_details["checks"]["should_mention_faq"] = has_faq
        if has_faq:
            score_details["passed_checks"] += 1
        else:
            score_details["passed"] = False
    
    # Check should_call_to_action
    if expectation.get("should_call_to_action"):
        score_details["total_checks"] += 1
        cta_phrases = ["فرم مشاوره", "مشاوره", "تماس", "واتساپ", "رزرو"]
        has_cta = any(phrase in smart_response for phrase in cta_phrases)
        score_details["checks"]["should_call_to_action"] = has_cta
        if has_cta:
            score_details["passed_checks"] += 1
        else:
            score_details["passed"] = False
    
    # Calculate score percentage
    if score_details["total_checks"] > 0:
        score_details["score_percentage"] = (score_details["passed_checks"] / score_details["total_checks"]) * 100
    else:
        score_details["score_percentage"] = 0.0
    
    return score_details


async def _run_single_case(case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a single evaluation case:
    - Call SmartAIAgent.get_smart_response(...)
    - Call the baseline chat service (SmartChatbot)
    - Return a combined result payload
    
    Args:
        case: Test case dict from YAML
        
    Returns:
        Dict with case info, smart_agent result, baseline result, and score
    """
    case_id = case.get("id")
    message = case.get("message")
    page_url = case.get("page_url")
    expectation = case.get("expectation") or {}
    
    context = {
        "session_id": f"eval-{case_id}",
        "page_url": page_url,
        "history": [],
    }
    
    # SmartAIAgent
    smart_result = None
    smart_error = None
    try:
        from schemas.smart_agent import SmartAgentRequest
        request = SmartAgentRequest(
            message=message,
            style="auto",
            context=context
        )
        smart_result = await smart_agent.get_smart_response(request)
        # Convert SmartAgentResponse to dict if needed
        if hasattr(smart_result, 'dict'):
            smart_result = smart_result.dict()
        elif hasattr(smart_result, 'model_dump'):
            smart_result = smart_result.model_dump()
    except Exception as e:
        logger.exception(f"Error running SmartAIAgent for case {case_id}: {e}")
        smart_error = str(e)
        smart_result = {
            "response": f"خطا: {smart_error}",
            "error": smart_error,
        }
    
    # Baseline: SmartChatbot (used by /api/smart-chat)
    baseline_result = None
    baseline_error = None
    try:
        chatbot = get_smart_chatbot()
        # SmartChatbot.get_smart_answer doesn't require a db parameter
        # It gets the database session internally via get_db() if needed
        baseline_result = chatbot.get_smart_answer(message)
    except Exception as e:
        logger.exception(f"Error running baseline for case {case_id}: {e}")
        baseline_error = str(e)
        baseline_result = {
            "answer": f"خطا: {baseline_error}",
            "error": baseline_error,
        }
    
    result = {
        "id": case_id,
        "type": case.get("type"),
        "description": case.get("description"),
        "message": message,
        "page_url": page_url,
        "expectation": expectation,
        "smart_agent": smart_result,
        "baseline": baseline_result,
    }
    
    # Add errors if any
    if smart_error:
        result["smart_agent_error"] = smart_error
    if baseline_error:
        result["baseline_error"] = baseline_error
    
    # Score the case
    try:
        score = score_case(result)
        result["score"] = score
    except Exception as e:
        logger.exception(f"Error scoring case {case_id}: {e}")
        result["score"] = {
            "error": str(e),
            "passed": False,
        }
    
    return result


async def run_all_cases() -> List[Dict[str, Any]]:
    """
    Load all test cases and run them sequentially.
    
    Returns:
        List of result dicts, one per test case
    """
    if not TEST_CASES_PATH.exists():
        logger.error(f"Test cases file not found: {TEST_CASES_PATH}")
        return [{
            "error": f"Test cases file not found: {TEST_CASES_PATH}",
        }]
    
    try:
        with open(TEST_CASES_PATH, "r", encoding="utf-8") as f:
            cases = yaml.safe_load(f) or []
    except Exception as e:
        logger.exception(f"Error loading test cases: {e}")
        return [{
            "error": f"Error loading test cases: {e}",
        }]
    
    if not cases:
        logger.warning("No test cases found in YAML file")
        return []
    
    results: List[Dict[str, Any]] = []
    for case in cases:
        try:
            res = await _run_single_case(case)
            results.append(res)
        except Exception as e:
            logger.exception(f"Error running eval case {case.get('id')}: {e}")
            results.append({
                "id": case.get("id"),
                "error": str(e),
            })
    
    return results

