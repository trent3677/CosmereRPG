#!/usr/bin/env python3
"""
Measure the actual size of character validator prompts to understand token usage.
"""

import json
import tiktoken
from core.validation.character_validator import AICharacterValidator
from utils.file_operations import safe_read_json

def count_tokens(text, model="gpt-4"):
    """Count tokens using tiktoken."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def main():
    print("=" * 80)
    print("CHARACTER VALIDATOR PROMPT SIZE ANALYSIS")
    print("=" * 80)
    
    # Initialize validator
    validator = AICharacterValidator()
    
    # Get the system prompts
    print("\n1. SYSTEM PROMPTS (Hardcoded in Python):")
    print("-" * 40)
    
    # Main validator prompt
    main_prompt = validator.get_validator_system_prompt()
    main_tokens = count_tokens(main_prompt)
    print(f"\nMain Validator System Prompt:")
    print(f"  - Characters: {len(main_prompt):,}")
    print(f"  - Lines: {main_prompt.count(chr(10)):,}")
    print(f"  - Tokens: {main_tokens:,}")
    
    # Inventory validator prompt
    inventory_prompt = validator.get_inventory_validator_system_prompt()
    inventory_tokens = count_tokens(inventory_prompt)
    print(f"\nInventory Validator System Prompt:")
    print(f"  - Characters: {len(inventory_prompt):,}")
    print(f"  - Lines: {inventory_prompt.count(chr(10)):,}")
    print(f"  - Tokens: {inventory_tokens:,}")
    
    # Load a sample character to measure user prompt size
    print("\n2. USER PROMPT (Character Data):")
    print("-" * 40)
    
    # Try to load Eirik as example
    character_path = "characters/eirik_hearthwise.json"
    character_data = safe_read_json(character_path)
    
    if character_data:
        # Build the actual user prompt
        user_prompt = validator.build_ac_validation_prompt(character_data)
        user_tokens = count_tokens(user_prompt)
        
        print(f"\nUser Prompt for Eirik:")
        print(f"  - Characters: {len(user_prompt):,}")
        print(f"  - Lines: {user_prompt.count(chr(10)):,}")
        print(f"  - Tokens: {user_tokens:,}")
        
        # Show character JSON size
        char_json = json.dumps(character_data, indent=2)
        print(f"\nCharacter JSON Data:")
        print(f"  - Characters: {len(char_json):,}")
        print(f"  - Lines: {char_json.count(chr(10)):,}")
        print(f"  - Tokens: {count_tokens(char_json):,}")
    
    print("\n3. TOTAL API CALL SIZE:")
    print("-" * 40)
    
    if character_data:
        total_tokens = main_tokens + user_tokens
        print(f"\nPer Validation Call:")
        print(f"  - System Prompt: {main_tokens:,} tokens")
        print(f"  - User Prompt: {user_tokens:,} tokens")
        print(f"  - TOTAL: {total_tokens:,} tokens")
        
        # Cost calculation
        input_cost = (total_tokens / 1_000_000) * 2.50  # GPT-4.1 pricing
        print(f"\nCost per validation: ${input_cost:.4f}")
        print(f"Cost for 315 validations: ${input_cost * 315:.2f}")
    
    print("\n4. PROMPT CONTENT ANALYSIS:")
    print("-" * 40)
    
    # Analyze what's in the prompts
    print("\nMain System Prompt Contains:")
    if "Light Armor" in main_prompt and "Heavy Armor" in main_prompt:
        print("  ✓ Complete D&D 5e armor tables")
    if "Example 1:" in main_prompt:
        print("  ✓ Multiple detailed JSON examples")
    if "Fighting Style" in main_prompt:
        print("  ✓ Fighting style rules")
    if "AC Calculation Formula" in main_prompt:
        print("  ✓ AC calculation formulas")
    
    print("\nInventory System Prompt Contains:")
    if "weapon" in inventory_prompt.lower():
        print("  ✓ Weapon categorization rules")
    if "potion" in inventory_prompt.lower():
        print("  ✓ Potion categorization")
    if "currency" in inventory_prompt.lower():
        print("  ✓ Currency consolidation rules")
    
    print("\n5. OPTIMIZATION OPPORTUNITIES:")
    print("-" * 40)
    
    print("\nCurrent Issues:")
    print("  - System prompt is embedded in code (not compressed)")
    print("  - Full character JSON sent every time (including unchanged data)")
    print("  - Same validation rules sent 315+ times")
    print("  - No caching of validation results")
    
    print("\nPotential Savings:")
    compressed_estimate = main_tokens * 0.1  # 90% compression possible
    print(f"  - Compress system prompt: {main_tokens:,} → {int(compressed_estimate):,} tokens (90% reduction)")
    print(f"  - Cache validations: Avoid redundant calls")
    print(f"  - Selective validation: Only send changed fields")
    
    potential_tokens = compressed_estimate + (user_tokens * 0.3)  # Only send relevant data
    potential_cost = (potential_tokens / 1_000_000) * 2.50
    print(f"\nOptimized cost per validation: ${potential_cost:.4f} (vs ${input_cost:.4f})")
    print(f"Potential savings: ${(input_cost - potential_cost) * 315:.2f} for 315 calls")

if __name__ == "__main__":
    main()