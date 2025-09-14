#!/usr/bin/env python3
"""
Comprehensive API call analysis with detailed breakdowns by function and purpose.
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

def get_model_mapping():
    """Return the model mapping from config variables to actual models."""
    return {
        'config.DM_MAIN_MODEL': 'gpt-4.1-2025-04-14',
        'config.DM_MINI_MODEL': 'gpt-4.1-mini-2025-04-14',
        'config.DM_VALIDATION_MODEL': 'gpt-4.1-2025-04-14',
        'config.DM_SUMMARIZATION_MODEL': 'gpt-4.1-mini-2025-04-14',
        'config.DM_FULL_MODEL': 'gpt-4.1-2025-04-14',
        'config.ACTION_PREDICTION_MODEL': 'gpt-4.1-2025-04-14',
        'config.COMBAT_MAIN_MODEL': 'gpt-4.1-2025-04-14',
        'config.COMBAT_DIALOGUE_SUMMARY_MODEL': 'gpt-4.1-mini-2025-04-14',
        'config.NPC_BUILDER_MODEL': 'gpt-4.1-2025-04-14',
        'config.ADVENTURE_SUMMARY_MODEL': 'gpt-4.1-mini-2025-04-14',
        'config.CHARACTER_VALIDATOR_MODEL': 'gpt-4.1-2025-04-14',
        'config.PLOT_UPDATE_MODEL': 'gpt-4.1-mini-2025-04-14',
        'config.PLAYER_INFO_UPDATE_MODEL': 'gpt-4.1-mini-2025-04-14',
        'config.NPC_INFO_UPDATE_MODEL': 'gpt-4.1-mini-2025-04-14',
        'config.MONSTER_BUILDER_MODEL': 'gpt-4.1-2025-04-14',
        'config.ENCOUNTER_UPDATE_MODEL': 'gpt-4.1-mini-2025-04-14',
        'config.LEVEL_UP_MODEL': 'gpt-4.1-2025-04-14',
        'config.NARRATIVE_COMPRESSION_MODEL': 'gpt-4.1-mini-2025-04-14',
        'config.LOCATION_COMPRESSION_MODEL': 'gpt-4.1-2025-04-14',
        'config.GPT5_MINI_MODEL': 'gpt-5-mini-2025-08-07',
        'config.GPT5_FULL_MODEL': 'gpt-5-2025-08-07'
    }

def categorize_api_calls():
    """Categorize API calls by their purpose."""
    categories = {
        'Main Game Loop': {
            'files': ['main.py'],
            'functions': ['get_ai_response', 'generate_arrival_narration', 'generate_seamless_transition_narration'],
            'description': 'Core game AI responses and narration'
        },
        'Combat System': {
            'files': ['core/managers/combat_manager.py', 'core/managers/initiative_tracker_ai.py'],
            'functions': ['run_combat_simulation', 'check_all_monsters_defeated', 'generate_combat_round_summary', 'summarize_dialogue'],
            'description': 'Combat mechanics, turn management, and combat narration'
        },
        'Character Management': {
            'files': ['core/managers/level_up_manager.py', 'utils/level_up.py', 'updates/update_character_info.py'],
            'functions': ['_get_ai_response', 'get_npc_level_up_changes', 'update_character_info'],
            'description': 'Character progression, level-up, and stats management'
        },
        'Module Generation': {
            'files': ['core/generators/module_builder.py', 'core/generators/module_generator.py', 'core/generators/plot_generator.py'],
            'functions': ['unify_plots', '_generate_enhanced_plot_hooks', 'generate_plot'],
            'description': 'Adventure module creation and plot generation'
        },
        'Content Generation': {
            'files': ['core/generators/npc_builder.py', 'core/generators/monster_builder.py', 'core/generators/area_generator.py', 'core/generators/location_generator.py'],
            'functions': ['generate_npc', 'generate_monster', 'generate_area', 'generate_location'],
            'description': 'NPCs, monsters, areas, and location generation'
        },
        'Action Processing': {
            'files': ['core/ai/action_handler.py', 'utils/action_predictor.py'],
            'functions': ['process_action', 'predict_actions_required', 'run_combat_simulation', 'get_ai_npc_movement_decision'],
            'description': 'Player action processing and validation'
        },
        'Narrative & Summaries': {
            'files': ['core/ai/adv_summary.py', 'core/ai/cumulative_summary.py'],
            'functions': ['generate_adventure_summary', 'generate_enhanced_adventure_summary', 'generate_location_summary'],
            'description': 'Adventure summaries and narrative compression'
        },
        'Web Interface': {
            'files': ['web/web_interface.py'],
            'functions': ['generate_descriptions', 'promote_to_bestiary'],
            'description': 'Web UI specific generation (descriptions, bestiary promotion)'
        },
        'Compression': {
            'files': ['utils/compression/ai_narrative_compressor_agentic.py', 'utils/compression/location_compressor.py'],
            'functions': ['compress_narrative', 'compress_location'],
            'description': 'Token optimization through content compression'
        },
        'Validation': {
            'files': ['core/validation/character_validator.py', 'core/validation/npc_codex_generator.py'],
            'functions': ['validate_character', 'extract_npcs_with_ai'],
            'description': 'Schema validation and data integrity checks'
        }
    }
    return categories

def main():
    model_mapping = get_model_mapping()
    categories = categorize_api_calls()
    
    print("=" * 100)
    print("COMPREHENSIVE API CALL ANALYSIS - NEVERENDINGQUEST")
    print("=" * 100)
    
    print("\n" + "=" * 100)
    print("API CALLS BY FUNCTIONAL CATEGORY")
    print("=" * 100)
    
    for category, info in categories.items():
        print(f"\n### {category}")
        print(f"    Purpose: {info['description']}")
        print(f"    Key Files: {', '.join(info['files'][:3])}")
        print(f"    Main Functions: {', '.join(info['functions'][:3])}")
    
    print("\n" + "=" * 100)
    print("MODEL USAGE SUMMARY")
    print("=" * 100)
    
    print("\n### GPT-4.1 Full Model (gpt-4.1-2025-04-14)")
    print("    Used for: Complex reasoning, JSON generation, validation")
    print("    Categories: Main game loop, Combat, Module generation, Content generation")
    print("    Temperature: 0.1-0.8 (varies by use case)")
    print("    Key uses:")
    print("      - Main DM responses (DM_MAIN_MODEL)")
    print("      - Combat simulation (COMBAT_MAIN_MODEL)")
    print("      - NPC/Monster generation (NPC_BUILDER_MODEL, MONSTER_BUILDER_MODEL)")
    print("      - Module creation (module_builder.py)")
    print("      - Level-up processing (LEVEL_UP_MODEL)")
    print("      - Action prediction (ACTION_PREDICTION_MODEL)")
    
    print("\n### GPT-4.1 Mini Model (gpt-4.1-mini-2025-04-14)")
    print("    Used for: Simple tasks, summaries, updates")
    print("    Categories: Summaries, Updates, Simple conversations")
    print("    Temperature: 0.3-0.7")
    print("    Key uses:")
    print("      - Adventure summaries (ADVENTURE_SUMMARY_MODEL)")
    print("      - Plot updates (PLOT_UPDATE_MODEL)")
    print("      - Character updates (PLAYER_INFO_UPDATE_MODEL, NPC_INFO_UPDATE_MODEL)")
    print("      - Encounter updates (ENCOUNTER_UPDATE_MODEL)")
    print("      - Narrative compression (NARRATIVE_COMPRESSION_MODEL)")
    print("      - Combat dialogue summaries (COMBAT_DIALOGUE_SUMMARY_MODEL)")
    
    print("\n### GPT-5 Models (Optional, USE_GPT5_MODELS=False by default)")
    print("    GPT-5 Mini (gpt-5-mini-2025-08-07): Used for testing in combat")
    print("    GPT-5 Full (gpt-5-2025-08-07): Available but not actively used")
    
    print("\n### Gemini (gemini-1.5-flash)")
    print("    Used for: Large file analysis (>2000 lines)")
    print("    File: gemini_tool.py")
    print("    Special: Handles files too large for GPT models")
    
    print("\n" + "=" * 100)
    print("KEY API CALL PARAMETERS")
    print("=" * 100)
    
    print("\n### Temperature Settings:")
    print("    0.1: Combat actions, validation (deterministic)")
    print("    0.2-0.3: Validation, schema updates")
    print("    0.6-0.7: Content generation (NPCs, monsters, plots)")
    print("    0.8: Creative area/location descriptions")
    
    print("\n### Response Formats:")
    print("    JSON: Combat results, plot updates, module metadata")
    print("    Text: Narration, descriptions, dialogue")
    
    print("\n### Max Tokens:")
    print("    Default: Most calls use default (4096)")
    print("    Custom: Some generation tasks specify higher limits")
    
    print("\n" + "=" * 100)
    print("CRITICAL API CALL LOCATIONS")
    print("=" * 100)
    
    critical_calls = [
        {
            'file': 'main.py:1933-1947',
            'function': 'get_ai_response()',
            'model': 'Variable (routed based on action type)',
            'purpose': 'Main game loop - processes all player actions',
            'notes': 'Uses intelligent routing if enabled'
        },
        {
            'file': 'core/ai/action_handler.py:373',
            'function': 'run_combat_simulation()',
            'model': 'DM_MINI_MODEL',
            'purpose': 'Determines if combat should be initiated',
            'notes': 'Temperature=0.1 for consistency'
        },
        {
            'file': 'core/managers/combat_manager.py:2187-2387',
            'function': 'run_combat_simulation()',
            'model': 'COMBAT_MAIN_MODEL or GPT5_MINI_MODEL',
            'purpose': 'Main combat turn processing',
            'notes': 'Switches models based on USE_GPT5_MODELS flag'
        },
        {
            'file': 'core/generators/npc_builder.py:126',
            'function': 'generate_npc()',
            'model': 'NPC_BUILDER_MODEL',
            'purpose': 'Generate complete NPC with stats and personality',
            'notes': 'Temperature=0.7 for variety'
        },
        {
            'file': 'web/web_interface.py:3386',
            'function': 'generate_descriptions()',
            'model': 'DM_MINI_MODEL',
            'purpose': 'Batch generate NPC/monster descriptions',
            'notes': 'Used in Module Media Generator'
        }
    ]
    
    for call in critical_calls:
        print(f"\n{call['file']} - {call['function']}")
        print(f"    Model: {call['model']}")
        print(f"    Purpose: {call['purpose']}")
        print(f"    Notes: {call['notes']}")
    
    print("\n" + "=" * 100)
    print("API OPTIMIZATION STRATEGIES IN USE")
    print("=" * 100)
    
    print("\n1. **Model Routing (ENABLE_INTELLIGENT_ROUTING=True)**")
    print("   - Routes simple actions to mini model")
    print("   - Complex actions use full model")
    print("   - Saves ~60% on API costs for simple interactions")
    
    print("\n2. **Compression (COMPRESSION_ENABLED=True)**")
    print("   - Compresses conversation history (70-90% reduction)")
    print("   - Location summaries compressed before use")
    print("   - Chunked compression (8 transitions at a time)")
    
    print("\n3. **Caching**")
    print("   - Combat prompts cached when USE_COMPRESSED_COMBAT=True")
    print("   - NPC descriptions cached in compendium")
    print("   - Module summaries cached for transitions")
    
    print("\n4. **Batch Processing**")
    print("   - Module Media Generator batches descriptions")
    print("   - Parallel compression workers (4 by default)")
    
    print("\n" + "=" * 100)
    print("ESTIMATED COSTS PER ACTION TYPE")
    print("=" * 100)
    
    print("\n### Approximate Token Usage:")
    print("    Simple action (mini model): ~500-1000 tokens")
    print("    Complex action (full model): ~2000-4000 tokens")
    print("    Combat turn: ~1500-3000 tokens")
    print("    NPC generation: ~1000-2000 tokens")
    print("    Module generation: ~10000-20000 tokens total")
    
    print("\n### Cost Optimization Tips:")
    print("    1. Keep ENABLE_INTELLIGENT_ROUTING=True")
    print("    2. Use COMPRESSION_ENABLED=True")
    print("    3. USE_COMPRESSED_COMBAT=True for cheaper combat")
    print("    4. Batch operations when possible")
    print("    5. Use mini models for summaries and updates")
    
    # Save summary to file
    summary = {
        'total_api_endpoints': 54,
        'models_in_use': {
            'gpt-4.1-2025-04-14': 'Primary model for complex tasks',
            'gpt-4.1-mini-2025-04-14': 'Secondary model for simple tasks',
            'gpt-5-mini-2025-08-07': 'Optional, for testing',
            'gemini-1.5-flash': 'Large file analysis'
        },
        'optimization_features': {
            'intelligent_routing': True,
            'compression': True,
            'caching': True,
            'batch_processing': True
        },
        'categories': list(categories.keys())
    }
    
    with open('api_analysis_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n\nSummary saved to api_analysis_summary.json")

if __name__ == "__main__":
    main()