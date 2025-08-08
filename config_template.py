# SPDX-FileCopyrightText: 2024 MoonlightByte
# SPDX-License-Identifier: Fair-Source-1.0
# License: See LICENSE file in the repository root
# This software is subject to the terms of the Fair Source License.

# ============================================================================
# CONFIG_TEMPLATE.PY - SYSTEM CONFIGURATION TEMPLATE
# ============================================================================
# 
# ARCHITECTURE ROLE: Configuration Management - Central System Settings Template
# 
# This template provides the structure for config.py including API keys, model
# selections, file paths, and operational parameters. It implements our
# "Configurable AI Strategy" by allowing model selection per use case.
# 
# KEY RESPONSIBILITIES:
# - API key and authentication management template
# - AI model configuration for different use cases
# - File system path configuration
# - System operational parameters
# - Environment-specific settings
# 
# CONFIGURATION CATEGORIES:
# - AI Models: Different models for DM, combat, validation, generation
# - File Paths: Module directories and schema locations
# - API Settings: Keys, timeouts, and retry parameters
# - System Parameters: Debug modes, logging levels, validation settings
# 
# SECURITY CONSIDERATIONS:
# - API keys should be moved to environment variables in production
# - Sensitive configuration should not be committed to version control
# - Copy this template to config.py and add your actual API key
# 
# ARCHITECTURAL INTEGRATION:
# - Used by all modules requiring AI model access
# - Provides centralized model selection strategy
# - Enables easy switching between different AI configurations
# - Supports our multi-model AI architecture
# 
# This module enables our flexible, multi-model AI strategy while
# maintaining centralized configuration management.
# ============================================================================

# WARNING: Replace with your actual OpenAI API key and move to environment variables in production
OPENAI_API_KEY = "your_openai_api_key_here"

# --- Module folder structure ---
MODULES_DIR = "modules"
DEFAULT_MODULE = "The_Thornwood_Watch"

# --- Main Game Logic Models (used in main.py) ---
DM_MAIN_MODEL = "gpt-4.1-2025-04-14"
DM_SUMMARIZATION_MODEL = "gpt-4.1-mini-2025-04-14"
DM_VALIDATION_MODEL = "gpt-4.1-2025-04-14"

# --- Action Prediction Model (used in action_predictor.py) ---
ACTION_PREDICTION_MODEL = "gpt-4.1-2025-04-14"  # Use full model for accurate action prediction

# --- Combat Simulation Models (used in combat_manager.py) ---
COMBAT_MAIN_MODEL = "gpt-4.1-2025-04-14"
# COMBAT_SCHEMA_UPDATER_MODEL - This was defined but not directly used.
# If needed for update_player_info, update_npc_info, update_encounter called from combat_sim,
# those modules will use their own specific models defined below.
COMBAT_DIALOGUE_SUMMARY_MODEL = "gpt-4.1-mini-2025-04-14"

# --- Utility and Builder Models ---
NPC_BUILDER_MODEL = "gpt-4.1-2025-04-14"                # Used in npc_builder.py
ADVENTURE_SUMMARY_MODEL = "gpt-4.1-mini-2025-04-14"
CHARACTER_VALIDATOR_MODEL = "gpt-4.1-2025-04-14"    # Used in adv_summary.py
PLOT_UPDATE_MODEL = "gpt-4.1-mini-2025-04-14"          # Used in plot_update.py
PLAYER_INFO_UPDATE_MODEL = "gpt-4.1-mini-2025-04-14"   # Used in update_player_info.py
NPC_INFO_UPDATE_MODEL = "gpt-4.1-mini-2025-04-14"      # Used in update_npc_info.py
MONSTER_BUILDER_MODEL = "gpt-4.1-2025-04-14"
ENCOUNTER_UPDATE_MODEL = "gpt-4.1-mini-2025-04-14"
LEVEL_UP_MODEL = "gpt-4.1-2025-04-14"                  # Used in level_up.py

# --- Token Optimization Models ---
DM_MINI_MODEL = "gpt-4.1-mini-2025-04-14"              # Used for simple conversations and plot-only updates
DM_FULL_MODEL = "gpt-4.1-2025-04-14"                   # Used for complex actions requiring JSON operations

# --- Model Routing Settings ---
ENABLE_INTELLIGENT_ROUTING = True                        # Enable/disable action-based model routing
MAX_VALIDATION_RETRIES = 1                              # Retry with full model after this many validation failures

# --- GPT-5 Model Configuration ---
GPT5_MINI_MODEL = "gpt-5-mini-2025-08-07"              # GPT-5 mini model for testing
GPT5_FULL_MODEL = "gpt-5-2025-08-07"                   # GPT-5 full model (fallback after failures)
USE_GPT5_MODELS = False                                 # Toggle for GPT-5 models (default: GPT-4.1)

# --- Web Interface Configuration ---
WEB_PORT = 8357                                         # Port for the web interface (changed from 5000 for security)

# --- END OF FILE config_template.py ---