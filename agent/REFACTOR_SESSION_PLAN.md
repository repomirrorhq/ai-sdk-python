# Groq and Together Provider Refactoring Session
*August 23, 2025*

## Current Status
Both Groq and Together providers are implemented as single `.py` files but should be refactored into directory structures to match the pattern used by other providers in the codebase.

## Current Files to Refactor
1. `src/ai_sdk/providers/groq.py` (449 lines)
2. `src/ai_sdk/providers/together.py` (~450 lines)

## Target Directory Structure

### Groq Provider
```
groq/
├── __init__.py          # Exports and module interface
├── provider.py          # GroqProvider class and create_groq function  
├── language_model.py    # GroqChatLanguageModel class
├── transcription_model.py # GroqTranscriptionModel class (if exists)
├── types.py            # Type definitions and model IDs
└── utils.py            # Helper functions (if needed)
```

### Together AI Provider  
```
togetherai/  # Note: directory name should be consistent
├── __init__.py          # Exports and module interface
├── provider.py          # TogetherAIProvider class and create_together function
├── language_model.py    # TogetherAIChatLanguageModel class  
├── embedding_model.py   # TogetherAIEmbeddingModel class (if exists)
├── types.py            # Type definitions and model IDs
└── utils.py            # Helper functions (if needed)
```

## Refactoring Plan

### Phase 1: Analyze Current Implementation
- [x] Examine groq.py structure (449 lines)
- [x] Examine together.py structure (~450 lines) 
- [x] Identify class boundaries and dependencies
- [x] Plan new directory structure

### Phase 2: Create New Directory Structures
- [ ] Create groq/ directory with proper file layout
- [ ] Create togetherai/ directory with proper file layout
- [ ] Split functionality into appropriate files
- [ ] Maintain all existing functionality

### Phase 3: Update Imports and References
- [ ] Update main providers/__init__.py imports
- [ ] Update any examples that reference old structure
- [ ] Test that imports work correctly

### Phase 4: Cleanup and Testing
- [ ] Remove old single files (groq.py, together.py)
- [ ] Run basic import tests
- [ ] Commit changes with proper documentation

## Key Considerations

1. **Maintain Backward Compatibility**: All existing imports should continue to work
2. **Preserve Functionality**: No features should be lost in the refactoring
3. **Follow Patterns**: Use the same structure as other providers (anthropic/, openai/, etc.)
4. **Clean Separation**: Each file should have a single responsibility

## Expected Benefits

1. **Consistency**: All providers will follow the same directory structure
2. **Maintainability**: Easier to find and modify specific functionality
3. **Extensibility**: Easier to add new model types or features
4. **Code Organization**: Better separation of concerns

## Status
- Started: August 23, 2025
- Current Phase: Phase 1 Complete, Starting Phase 2
- Target Completion: This session