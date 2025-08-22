Always provide a plan before starting to modify code to ensure you are aligned with the user's request.
Beware of feature creep and don't add new features unless specifically asked or approved. Feature creep is the enemy of shipping software.

Don't add emojis or special characters anywhere in the game code.

When planning, always add creating a plan md file in case you get disconnected to the first step of the plan

# Gemini Consultation Protocol - REQUIRED FOR NEW PROJECTS

## When to Consult Gemini First
Before starting ANY new feature, bug fix, or significant code modification, you MUST consult Gemini for project context:

1. **Identify relevant files** based on the user's request
2. **Upload all potentially related files** to Gemini (don't worry about uploading too many)
3. **Ask for comprehensive context** about the systems involved
4. **Get recommendations** on implementation approach

## Required Consultation Pattern
```python
from gemini_tool import query_gemini

prompt = '''
User wants to: [describe the task/problem]

Please analyze these files and provide:
1. Overview of relevant systems and their interactions
2. Key files, functions, and classes involved
3. Current implementation patterns to follow
4. Potential edge cases or issues to watch for
5. Recommended implementation approach
6. Specific file locations for the changes
7. Any related systems that might be affected
'''

result = query_gemini(prompt, files=[
    # Upload ALL potentially relevant files
    'main.py',
    'relevant_module.py',
    'related_prompt.txt',
    'schema_files.json',
    # Include test files, prompts, configs - better too many than too few
])
```

## Benefits of This Approach
- **Faster file discovery** - Gemini can process many files at once
- **Better system understanding** - See how components interact
- **Reduced scanning** - No need to grep through files piece by piece
- **Comprehensive solutions** - Understand full context before coding
- **Catch edge cases early** - Gemini can spot potential issues

## Example Use Cases
- Bug fixes: Upload error logs, related modules, and test files
- New features: Upload existing similar features, schemas, and integration points
- Prompt improvements: Upload all related prompts and their validators
- Refactoring: Upload entire subsystems to understand dependencies

Remember: It's better to give Gemini too much context than too little. Upload liberally!

# Unicode and Special Characters - CRITICAL WARNING
## NEVER USE UNICODE CHARACTERS IN ANY PYTHON CODE
Windows console (cp1252) cannot display Unicode characters and will cause UnicodeEncodeError crashes that break the entire game. This is a CRITICAL requirement.

### BANNED CHARACTERS (NEVER USE THESE):
- ✓ ✗ ✔ ✘ ❌ ✅ (checkmarks/crosses) 
- → ← ↑ ↓ ➜ ⇒ (arrows)
- ● ○ ◆ ◇ ■ □ • ▪ (bullets/shapes)
- 📊 📈 📉 🎉 ⚠️ 🔧 💡 (emojis)
- « » „ " " ' ' (fancy quotes)
- — – (em/en dashes)
- … (ellipsis)
- ANY other non-ASCII character

### REQUIRED ASCII REPLACEMENTS:
- Use [OK] or [PASS] instead of ✓ ✅
- Use [ERROR] or [FAIL] instead of ✗ ❌  
- Use -> or => instead of → ➜
- Use * or - instead of ● •
- Use standard quotes " and ' only
- Use -- instead of — or –
- Use ... instead of …
- Use [WARNING] instead of ⚠️
- Use [INFO] instead of 💡
- Use regular text descriptions instead of ANY emoji

### WHERE THIS APPLIES:
- ALL print() statements
- ALL logging statements (logger.info, logger.debug, etc.)
- ALL string literals that might be displayed
- Test output and debug messages
- Comments can use Unicode but code CANNOT

### EXAMPLES:
```python
# BAD - WILL CRASH:
print("✅ Test passed!")
logger.info("→ Processing file")
print("🎉 Success!")

# GOOD - SAFE:
print("[OK] Test passed!")
logger.info("-> Processing file")
print("Success!")
```

This is not optional - Unicode characters WILL cause the game to crash with encoding errors.

# Schema Validation
Use `python validate_module_files.py` to check schema compatibility after making changes to JSON files or schemas. This ensures all game files remain compatible with their schemas and prevents runtime errors. Aim for 100% validation pass rate.

# Organized Codebase Architecture 

## Directory Structure and Import Patterns
The codebase has been comprehensively reorganized into a logical directory structure with 100% verified import functionality:

### Core Directory Organization
```
core/                     # Core game engine modules (47 files)
├── __init__.py                   # Package initialization
├── ai/                  # AI integration and processing (10 files)
│   ├── action_handler.py         # Command processing and system integration
│   ├── adv_summary.py            # Adventure summary generation  
│   ├── chunked_compression.py    # Conversation compression engine
│   ├── chunked_compression_config.py # Compression settings
│   ├── chunked_compression_integration.py # Compression integration
│   ├── conversation_utils.py     # Conversation tracking and summarization
│   ├── cumulative_summary.py     # AI-powered history compression
│   ├── dm_wrapper.py             # DM AI model wrapper
│   ├── enhanced_dm_wrapper.py    # Enhanced DM functionality
│   └── __init__.py               # Package initialization
├── generators/          # Content generation systems (14 files)
│   ├── area_generator.py         # Location generation with AI
│   ├── chat_history_generator.py # Chat history processing
│   ├── combat_builder.py         # Combat encounter creation
│   ├── combat_history_generator.py # Combat history processing
│   ├── generate_prerolls.py      # Combat dice management system
│   ├── location_generator.py     # Area and location generation
│   ├── location_summarizer.py    # AI-powered location summaries
│   ├── module_builder.py         # Module creation orchestrator
│   ├── module_generator.py       # Core content generation engine
│   ├── module_stitcher.py        # Module integration system
│   ├── monster_builder.py        # Creature creation with AI
│   ├── npc_builder.py            # NPC generation with AI
│   ├── plot_generator.py         # Quest and plot generation
│   └── __init__.py               # Package initialization
├── managers/            # System orchestration (Manager Pattern) (9 files)
│   ├── campaign_manager.py       # Hub-and-spoke campaign orchestration
│   ├── combat_manager.py         # Turn-based combat system
│   ├── initiative_tracker_ai.py  # Combat initiative tracking
│   ├── level_up_manager.py       # Character progression in subprocess
│   ├── location_manager.py       # Location-based features and storage
│   ├── status_manager.py         # Real-time user feedback system
│   ├── storage_manager.py        # Player storage with atomic protection
│   ├── storage_processor.py      # Storage transaction processing
│   └── __init__.py               # Package initialization
├── validation/          # AI-powered validation systems (7 files)
│   ├── character_effects_validator.py # Character effects validation
│   ├── character_validator.py    # Character data validation
│   ├── dm_complex_validator.py   # Complex game state validation
│   ├── dm_response_validator.py  # DM response validation
│   ├── npc_codex_generator.py    # NPC data validation and codex
│   ├── validate_module_files.py  # Module schema validation
│   └── __init__.py               # Package initialization
└── toolkit/             # Module content generation toolkit (6 files)
    ├── monster_generator.py      # Monster creation utilities
    ├── npc_generator.py          # NPC generation tools
    ├── pack_integration.py       # Content pack integration
    ├── pack_manager.py           # Pack management system
    ├── style_manager.py          # Visual style management
    └── video_processor.py        # Video processing utilities

utils/                   # Utility functions and core support (27 files)
├── action_predictor.py           # AI action prediction optimization
├── analyze_module_options.py     # Module analysis tools
├── bestiary_updater.py           # Monster data management
├── calendar_migration.py         # Calendar system utilities
├── encoding_utils.py             # Text encoding and JSON safety
├── enhanced_logger.py            # Comprehensive logging system
├── file_operations.py            # Atomic file operations
├── level_up.py                   # Legacy level up system
├── location_path_finder.py       # Location pathfinding utilities
├── module_context.py             # Module context management
├── module_path_manager.py        # Module-centric path management
├── npc_reconciler.py             # NPC state reconciliation
├── openai_usage_tracker.py       # API usage tracking
├── player_stats.py               # Character statistics and progression
├── plot_formatting.py            # Plot text formatting for AI
├── prompt_sanitizer.py           # Prompt text sanitization
├── quest_player_formatter.py     # Quest formatting utilities
├── reconcile_location_state.py   # Location state reconciliation
├── redirect_debug_output.py      # Debug output redirection
├── reset_campaign.py             # Campaign reset utilities
├── startup_wizard.py             # Character creation wizard
├── sync_party_tracker.py         # Party tracker synchronization
├── time_context.py               # World time management
├── token_estimator.py            # AI token usage estimation
├── token_tracker.py              # Token usage tracking
├── xp.py                         # Experience point calculations
└── __init__.py                   # Package initialization

updates/                 # State update modules (10 files)
├── plot_update.py                # Quest progression updates
├── process_effect_expirations.py # Effect expiration processing
├── save_game_manager.py          # Save/load operations
├── update_character_effects.py   # Character effects updates
├── update_character_info.py      # Character data updates
├── update_encounter.py           # Encounter state updates
├── update_party_tracker.py       # Party tracker updates
├── update_world_time.py          # World time progression
└── __init__.py                   # Package initialization

web/                     # Web interface (2 files)
├── web_interface.py              # Flask server and SocketIO handlers
└── __init__.py                   # Package initialization

prompts/                 # AI system prompts (organized by type)
├── combat/                       # Combat system prompts
│   ├── combat_sim_prompt.txt     # Combat simulation rules
│   └── combat_validation_prompt.txt # Combat validation rules
├── leveling/                     # Character progression prompts
│   ├── level_up_system_prompt.txt # Level up rules and guidance
│   ├── leveling_validation_prompt.txt # Level up validation
│   └── leveling_info.txt         # D&D 5e leveling tables and rules
├── validation/                   # General validation prompts
│   ├── validation_prompt.txt     # Core game validation rules
│   └── validation_prompt copy.txt # Backup validation rules
├── generators/                   # Content generation prompts
│   ├── module_creation_prompt.txt # Module creation guidance
│   └── npc_builder_prompt.txt    # NPC generation rules
└── system_prompt.txt             # Core game rules and AI instructions

modules/conversation_history/     # All conversation files
├── conversation_history.json     # Main conversation history
├── level_up_conversation.json    # Level up session history
├── startup_conversation.json     # Character creation history
├── chat_history.json             # Lightweight chat history
└── combat_conversation_history.json # Combat session history
```

### Import Pattern Standards
**ALWAYS use these import patterns for new code:**

```python
# Core AI systems
from core.ai.action_handler import process_action
from core.ai.conversation_utils import update_conversation_history
from core.ai.chunked_compression_integration import check_and_perform_chunked_compression

# Core Managers (follow Manager Pattern)
from core.managers.combat_manager import CombatManager
from core.managers.storage_manager import StorageManager
from core.managers.level_up_manager import LevelUpSession

# Core Generators
from core.generators.module_builder import ModuleBuilder
from core.generators.location_summarizer import LocationSummarizer

# Core Validation
from core.validation.character_validator import AICharacterValidator
from core.validation.dm_response_validator import validate_dm_response

# Utilities (most commonly used)
from utils.enhanced_logger import debug, info, warning, error, set_script_name
from utils.encoding_utils import safe_json_load, safe_json_dump, sanitize_text
from utils.file_operations import safe_read_json, safe_write_json
from utils.module_path_manager import ModulePathManager

# Updates
from updates.update_character_info import update_character_info
from updates.plot_update import update_plot

# Web interface
from web.web_interface import app, socketio
```

### File Path Standards
**Use these standardized file paths:**

```python
# Conversation files - ALL in modules/conversation_history/
"modules/conversation_history/conversation_history.json"
"modules/conversation_history/level_up_conversation.json"
"modules/conversation_history/startup_conversation.json"

# Prompt files - organized by system type
"prompts/combat/combat_sim_prompt.txt"
"prompts/leveling/level_up_system_prompt.txt" 
"prompts/validation/validation_prompt.txt"
"prompts/generators/npc_builder_prompt.txt"
"prompts/system_prompt.txt"

# Schema files
"schemas/char_schema.json"
"schemas/module_schema.json"

# Module data
"modules/[module_name]/areas/[location_id].json"
"modules/[module_name]/[module_name]_module.json"
```

# Module-Centric Architecture
This system follows a **Module-Centric Design Philosophy** with advanced conversation timeline management:

## Core Principles:
- **Modules as Self-Contained Adventures**: Each module represents a complete, playable adventure
- **Seamless Module Transitions**: Intelligent conversation segmentation preserving chronological adventure history
- **Unified Conversation Timeline**: Hub-and-spoke model maintaining adventure sequence across all modules
- **AI-Powered Context Compression**: Full adventure summaries generated from actual gameplay conversations
- **Smart Boundary Detection**: Two-condition logic for optimal conversation segmentation between modules
- **Automatic Archiving**: Campaign summaries and conversations stored sequentially in dedicated folders
- **Unified Path Management**: ModulePathManager provides consistent file access patterns
- **Forward Compatibility**: System designed around modules/ directory structure with timeline preservation

## Directory Structure:
```
modules/[module_name]/
├── areas/              # Location files (HH001.json, G001.json)
├── characters/         # Unified player/NPC storage  
├── monsters/           # Module-specific creatures
├── encounters/         # Combat encounters
├── module_plot.json    # Plot progression
├── party_tracker.json  # Party state
└── [module_name]_module.json  # Module metadata
```

## Terminology Standards:
- Use "module" not "campaign" in all new code
- Use "ModulePathManager" for file operations
- Reference "module_data" and "module_name" in function parameters
- File naming: "*_module.json" not "*_campaign.json"

This architecture supports both standalone adventures and linked module series while maintaining clean separation of concerns.

## Module Generation Architecture

### Module Builder and Generator Relationship
The module creation system uses an **Orchestrator-Worker Pattern**:

- **module_builder.py (Orchestrator)**: 
  - Acts as the "general contractor" that manages the overall module creation process
  - Called directly by `main.py` when creating new modules
  - Instantiates and coordinates all specialized generators (ModuleGenerator, PlotGenerator, LocationGenerator, AreaGenerator)
  - Does NOT perform actual content generation itself

- **module_generator.py (Worker/Engine)**:
  - The core content generation engine called by module_builder.py
  - Contains all the heavy lifting for module structure creation
  - Implements critical functionality including:
    - Location ID prefix system (A01, B01, C01 to ensure uniqueness across areas)
    - Area connection generation (`_create_bidirectional_connection` method)
    - Validation of duplicate location IDs
  - This is where area connectivity bugs should be fixed, NOT in module_builder.py

### Key Insight
When fixing area transitions or connectivity issues, always check `module_generator.py` first, as it contains the actual implementation. The `module_builder.py` is just the orchestrator that calls it.

## Recent Architectural Patterns

### Manager Pattern Implementation
Follow the established Manager Pattern for all major subsystems:
- **CampaignManager**: Orchestrates campaign-wide operations and hub-and-spoke management
- **ModulePathManager**: Provides file system abstraction for module-centric architecture
- **StorageManager**: Handles player storage system with atomic file protection
- **LocationManager**: Manages location-based features and storage integration
- **CombatManager**: Controls turn-based combat system with AI validation
- **LevelUpManager**: Manages character progression in isolated subprocess
- **StatusManager**: Provides real-time user feedback across all systems

### Atomic Operations Convention
All state-modifying operations MUST use atomic patterns:
```python
# Standard atomic operation pattern:
# 1. Create backup of affected files
# 2. Perform operation with step-by-step validation
# 3. Verify final state integrity
# 4. Clean up backups on success OR restore on failure
```

### AI Integration Patterns
When integrating AI functionality:
- Use specialized AI models for different purposes (DM, validator, content generator)
- Implement validation layers for AI responses
- Provide fallback mechanisms for AI failures
- Use subprocess isolation for complex AI operations (level-up system)

### Session State Management
Maintain session state consistency across:
- Console interface operations
- Web interface real-time updates
- File system modifications
- Module transitions
- Save/load operations

### Web Interface Integration
For web interface features:
- Use SocketIO for real-time bidirectional communication
- Implement queue-based output management for thread safety
- Provide status broadcasting across console and web interfaces
- Maintain session state synchronization between interfaces

# Module Transition System
Advanced conversation timeline management preserving chronological adventure history across modules:

## Transition Processing Architecture:
- **Immediate Detection**: Module transitions detected in `action_handler.py` when `updatePartyTracker` changes module
- **Marker Insertion**: "Module transition: [from] to [to]" marker inserted immediately at point of module change
- **Post-Processing**: `check_and_process_module_transitions()` in `main.py` handles conversation compression
- **AI Summary Integration**: Loads complete AI-generated summaries from `modules/campaign_summaries/` folder

## Two-Condition Boundary Detection:
1. **Previous Module Transition Exists**: Compress conversation between the two module transitions
2. **No Previous Module Transition**: Compress from after last system message to current transition

## Conversation Segmentation Format:
```json
[
  {main system message},
  {"role": "user", "content": "Module summary: === MODULE SUMMARY ===\n\n[Module_Name]:\n------------------------------\n[Full AI-generated summary]"},
  {"role": "user", "content": "Module transition: [from_module] to [to_module]"},
  {new module conversation...}
]
```

## File Structure Integration:
- **Campaign Archives**: `modules/campaign_archives/[Module_Name]_conversation_[sequence].json`
- **Campaign Summaries**: `modules/campaign_summaries/[Module_Name]_summary_[sequence].json`
- **Sequential Numbering**: Automatic sequence tracking for chronological adventure timeline

This system ensures seamless module transitions while preserving complete adventure context and enabling the hub-and-spoke campaign model.

# SRD 5.2.1 Compliance
This project uses SRD content under CC BY 4.0. When coding:
- Use "5th edition" or "5e" instead of "D&D" 
- Add attribution to SRD-derived content: `"_srd_attribution": "Portions derived from SRD 5.2.1, CC BY 4.0"`
- Use generic fantasy settings only

# Tool Command Names
When using command line tools, use these specific command names:
- Use `fdfind` instead of `fd` for file searching
- Use `batcat` instead of `bat` for syntax-highlighted file viewing
- Use `rg` for ripgrep (fast text search)
- All other tools use their standard names: `jq`, `tree`, `fzf`, `black`, `flake8`, `pytest`, `mypy`

Use the Github CLI for this repo as your primary source of open and closed issues.

# Gemini AI Tool
Use `gemini_tool.py` for large-context analysis, planning, and when stuck:

## WHEN TO USE GEMINI:
1. **Planning Complex Features**: Before starting implementation, get a clear plan
2. **When Stuck**: Hit a wall or need fresh perspective on a problem
3. **Large File Analysis**: Files exceeding my read limits (~2000 lines)
4. **Whole-Picture Tasks**: Need to see entire file/system context at once
5. **Multiple File Coordination**: Cross-file feature planning and analysis

## SPECIFIC USE CASES:
- `game_interface.html` changes (50k+ tokens) - send whole file for planning
- Architecture decisions requiring full codebase view
- Debugging issues spanning multiple large files
- HTML/CSS generation (Gemini excels at web tasks)
- Getting "unstuck" on complex problems

## WORKFLOW EXAMPLE:
1. User: "Add feature X to game_interface.html"
2. Claude: `query_gemini("Plan how to add feature X", files=["templates/game_interface.html"])`
3. Gemini: Returns step-by-step plan with specific locations
4. Claude: Execute plan with targeted edits

## USAGE:
```python
from gemini_tool import (query_gemini, plan_feature, analyze_large_file, get_unstuck,
                        suggest_refactoring, generate_tests, write_documentation, 
                        clear_conversation, upload_files_once, query_with_session,
                        cleanup_session, check_token_count, save_all_conversations,
                        load_all_conversations)

# Basic query
result = query_gemini("How should I implement feature X?")

# With large file (automatically uploaded)
result = query_gemini("Plan adding feature Y to this file", files=["templates/game_interface.html"])

# Multiple files
result = query_gemini("How do these systems interact?", files=["system1.py", "system2.py"])

# Skip system prompt to save ~100 tokens
result = query_gemini("Quick question about syntax", use_system_prompt=False)

# Conversation tracking for follow-ups
result = query_gemini("How to add dark mode?", conversation_id="dark-mode-discussion")
followup = query_gemini("What about mobile?", conversation_id="dark-mode-discussion")
clear_conversation("dark-mode-discussion")  # Clean up when done

# File session management - upload once, query multiple times
upload_files_once(["game_interface.html", "game_logic.js"], session_id="ui-analysis")
result1 = query_with_session("Where is player data rendered?", session_id="ui-analysis")
result2 = query_with_session("How are events handled?", session_id="ui-analysis")
result3 = query_with_session("What about the mobile layout?", session_id="ui-analysis")
cleanup_session("ui-analysis")  # Clean up when done

# Token counting (check before sending large requests)
tokens = check_token_count("This is my prompt")
tokens_with_history = check_token_count("Follow-up", conversation_id="existing-chat")

# Conversation persistence
save_all_conversations("my_gemini_chats.pkl")  # Save to disk
load_all_conversations("my_gemini_chats.pkl")  # Restore later

# Helper functions
plan = plan_feature("Add dark mode toggle", files=["templates/game_interface.html"])
analysis = analyze_large_file("game_interface.html", "Where is character data rendered?")
help_me = get_unstuck("Can't figure out why events aren't firing", files=["web_interface.py"])
refactor = suggest_refactoring("game_logic.py", focus="performance", as_json=True)
tests = generate_tests("combat_system.py", specific_function="calculate_damage")
docs = write_documentation("module_builder.py", doc_type="docstrings")
```

## FILE HANDLING:
- Files are automatically uploaded to Gemini
- Supports any file type (text, code, images, etc.)
- Files are cleaned up after query
- No manual file management needed

## MODELS:
- Default: `gemini-2.5-pro` (powerful, best for complex tasks)
- Alternative: `gemini-2.5-flash` (faster, cheaper, good for simple queries)

## PROMPT TIPS:
- Ask for "plan" or "approach" not "implement"
- Be specific about the goal
- Request location hints: "which functions/sections to modify"
- For large files, ask "what line numbers should I focus on?"
- Explicitly say "analysis only" or "no code implementation"

## PERFORMANCE OPTIMIZATIONS:
- **Token Savings**: Set `use_system_prompt=False` for quick queries (saves ~100 tokens)
- **Conversation History**: Use `conversation_id` for related queries to maintain context
- **Specialized Functions**: Use helper functions that optimize prompts for specific tasks

## NEW FEATURES V2:
1. **Native Conversation Format**: Uses Gemini's native conversation structure for better context
2. **File Session Management**: Upload files once, query multiple times without re-uploading
3. **Automatic Retry Logic**: Exponential backoff with jitter for transient failures
4. **Rate Limiting**: Enforces 2 RPM for Gemini Pro to avoid quota errors
5. **Conversation Persistence**: Save/load conversations to disk for continuity
6. **Token Counting**: Check token usage before sending (note: implementation pending API fix)
7. **Enhanced Error Handling**: Specific handling for quota, permission, and API errors
8. **Configuration Flexibility**: Set default model/temperature on initialization
9. **Parallel File Uploads**: Upload multiple files concurrently (5 workers)
10. **JSON Output Support**: Automatic parsing with markdown fallback

## IMPORTANT:
- Gemini Pro has a 2 RPM rate limit - tool automatically waits between requests
- Use file sessions for multiple queries on same files to save time and quota
- Save conversations before ending sessions to preserve context
- Clear conversations and file sessions when done to free memory
- Gemini tends to suggest extra features - keep prompts focused
- Use for planning and analysis, not direct code generation
- Temperature defaults to 0.7 for balanced responses

# Debug Message Format
Debug messages that should appear in the debug screen must use: `print(f"DEBUG: [Category] Message...")`

# AI Agent Coordination System

## CRITICAL MODULE SYSTEM WARNING
**ALWAYS check module_generator.py for area connectivity bugs, NOT module_builder.py**
- module_builder.py = Orchestrator (calls other generators)
- module_generator.py = Worker (contains actual implementation)
- Area connections, location IDs, bidirectional links ALL in module_generator.py

## Agent Decision Tree

### START HERE: What are you doing?

#### 1. BEFORE starting any task -> Consult codebase-expert
```python
# REQUIRED: Get implementation context first
"Where is [feature] implemented?"
"What patterns should I follow for [task]?"
"Which files handle [functionality]?"
```

#### 2. Module/area generation issues -> module-toolkit-expert
```python
# For: connectivity bugs, location IDs, area transitions
"Debug area connection between [A] and [B]"
"Fix duplicate location ID issue"
"Module transition not working"
```

#### 3. After implementing -> quality-control-enforcer
```python
# VALIDATION CHECKLIST:
- [ ] Solution addresses root cause (not workaround)
- [ ] No temporary hacks or bypasses
- [ ] Follows established patterns
- [ ] No technical debt introduced
```

#### 4. Documentation updates -> Specialized agents
- Project docs changed -> claude-md-curator
- README needed -> readme-documentation-expert

## Common Anti-Patterns to Avoid

### MODULE BUGS - Check RIGHT location:
```python
# WRONG: Editing module_builder.py for connectivity
# RIGHT: Fix in module_generator.py._create_bidirectional_connection()

# WRONG: Adding workarounds in action_handler.py
# RIGHT: Fix root cause in module generation
```

### VALIDATION GATES - Required checks:
```python
# Before marking ANY task complete:
1. Run: python validate_module_files.py  # Must pass 100%
2. Test actual gameplay functionality
3. Check no Unicode characters added
4. Verify atomic operations used for state changes
```

## Agent Specializations

### codebase-expert
**Domain**: Architecture, patterns, file locations
**Example Query**: "Show me all files that handle combat damage calculation"

### module-toolkit-expert  
**Domain**: Module generation, areas, locations, connections
**Example Query**: "Why do areas A01 and B01 not connect properly?"

### quality-control-enforcer
**Domain**: Code quality, root cause analysis, technical debt
**Example Query**: "Review this fix for the storage bug - is it addressing the root issue?"

### claude-md-curator
**Domain**: CLAUDE.md accuracy, documentation updates
**Example Query**: "Update docs to reflect new storage_manager patterns"

### readme-documentation-expert
**Domain**: README files, user documentation
**Example Query**: "Create installation guide for new users"

## Multi-Agent Workflow Examples

### Bug Fix Workflow:
```python
1. codebase-expert: "Where is the bug occurring?"
2. [Fix implementation]
3. quality-control-enforcer: "Is this a real fix or workaround?"
4. claude-md-curator: "Update patterns if needed"
```

### New Feature Workflow:
```python
1. codebase-expert: "What's the architecture for this feature?"
2. module-toolkit-expert: "How to integrate with modules?" (if needed)
3. [Implement feature]
4. quality-control-enforcer: "Review implementation quality"
5. readme-documentation-expert: "Document for users"
```

### Module Generation Debug:
```python
1. module-toolkit-expert: "Diagnose connectivity issue"
2. [Fix in module_generator.py]
3. quality-control-enforcer: "Verify fix is complete"
```

## Quality Gates Checklist
Before ANY code changes are finalized:
- [ ] Consulted relevant expert agent for context
- [ ] No Unicode characters in Python code
- [ ] Schema validation passes (validate_module_files.py)
- [ ] Atomic operations used for state changes
- [ ] Root cause addressed (not workaround)
- [ ] Follows Manager Pattern where applicable
- [ ] Import patterns match standards

