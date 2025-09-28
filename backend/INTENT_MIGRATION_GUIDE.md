# Intent System Migration Guide

## Overview
The intent detection system has been migrated from a simple LangChain-based approach to an enhanced pipeline-based system that provides better accuracy and reasoning capabilities.

## Changes Made

### 1. Enhanced Intent Detection System
- **File**: `backend/services/intent.py`
- **Class**: `EnhancedIntentDetector` (replaces the old `IntentDetector`)
- **Features**:
  - Multi-step pipeline: Analyze → Validate → Enhance
  - Enhanced confidence scoring with keyword-based adjustments
  - Detailed reasoning for each intent classification
  - Graph-like trace information for debugging

### 2. Updated Schema
- **File**: `backend/schemas/chat.py`
- **Changes**: Added new fields to `IntentResult`:
  - `reasoning`: Explanation for the intent classification
  - `graph_trace`: Number of pipeline steps executed
  - `enhanced`: Boolean indicating if enhancement was applied

### 3. Backward Compatibility
- **File**: `backend/services/intent_old.py`
- **Purpose**: Backup of the original intent system for rollback if needed
- **Usage**: Can be restored by renaming files if issues arise

### 4. Dependencies
- **File**: `backend/requirements.txt`
- **Added**: `langgraph==0.0.62` (for future LangGraph integration)
- **Note**: Current implementation uses enhanced pipeline instead of full LangGraph

## New Features

### Enhanced Confidence Scoring
The system now applies keyword-based confidence adjustments:
- **Smalltalk**: Boosts confidence for common greetings
- **Sales**: Boosts confidence for sales-related keywords
- **Complaint**: Boosts confidence for complaint-related keywords

### Detailed Reasoning
Each intent classification now includes:
- Explanation of why the intent was chosen
- Confidence level with reasoning
- Pipeline step information

### Pipeline Architecture
The new system uses a 3-step pipeline:
1. **Analyze**: LLM-based intent detection
2. **Validate**: Ensure intent label is valid
3. **Enhance**: Apply keyword-based confidence adjustments

## Testing

### Test Files Created
- `backend/test_langgraph_intent.py`: Comprehensive test suite
- `backend/test_intent_comparison.py`: Comparison between old and new systems
- `backend/simple_intent_test.py`: Basic functionality test

### Running Tests
```bash
cd backend
python test_langgraph_intent.py
python test_intent_comparison.py
python simple_intent_test.py
```

## Integration

The new intent system is fully integrated with the existing chat chain:
- **File**: `backend/services/chain.py`
- **Compatibility**: No changes needed - uses same interface
- **Benefits**: Enhanced accuracy and debugging information

## Rollback Procedure

If issues arise, you can rollback to the old system:

1. Rename current intent system:
   ```bash
   mv services/intent.py services/intent_new.py
   ```

2. Restore old system:
   ```bash
   mv services/intent_old.py services/intent.py
   ```

3. Restart the backend service

## Future Enhancements

The system is designed to easily integrate with LangGraph when dependency conflicts are resolved:
- Current pipeline structure mirrors LangGraph concepts
- Easy migration path to full graph-based execution
- Enhanced debugging and monitoring capabilities

## Performance Impact

- **Latency**: Minimal increase due to additional validation steps
- **Accuracy**: Improved through keyword-based enhancements
- **Debugging**: Enhanced with detailed reasoning and trace information
- **Maintainability**: Better structured with clear separation of concerns
