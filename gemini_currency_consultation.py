#!/usr/bin/env python3
"""
Consult Gemini about currency consolidation filtering to ensure completeness
"""

import json
import os
from gemini_tool import query_gemini
from utils.file_operations import safe_read_json

def prepare_currency_consultation():
    """Prepare data for Gemini consultation about currency filtering"""
    
    # Load all character files
    character_files = [
        "characters/eirik_hearthwise.json",
        "characters/lyra_nyx_whisperwind.json", 
        "characters/ranger_thane.json",
        "characters/thorin_ironforge.json"
    ]
    
    characters = {}
    for file in character_files:
        if os.path.exists(file):
            char_data = safe_read_json(file)
            if char_data:
                char_name = char_data.get('name', 'Unknown')
                # Extract just equipment for analysis
                characters[char_name] = {
                    'name': char_name,
                    'equipment': char_data.get('equipment', []),
                    'currency': char_data.get('currency', {}),
                    'ammunition': char_data.get('ammunition', [])
                }
                print(f"Loaded {char_name} - {len(characters[char_name]['equipment'])} items")
    
    # Load the extraction function code
    with open('core/validation/character_validator.py', 'r') as f:
        validator_code = f.read()
    
    # Extract the currency consolidation extraction function
    start_marker = "def extract_currency_consolidation_data"
    end_marker = "return consolidation_data"
    
    start_idx = validator_code.find(start_marker)
    end_idx = validator_code.find(end_marker, start_idx) + len(end_marker)
    
    extraction_function = validator_code[start_idx:end_idx] if start_idx > -1 else "Function not found"
    
    # Prepare the consultation prompt
    consultation_prompt = f"""
I'm optimizing a D&D 5e currency consolidation validator to reduce API token usage. The validator identifies loose coins and ammunition in inventory that should be consolidated.

## THE CHALLENGE

The validator needs to:
1. Find loose coins ("5 gold pieces", "bag of 50 gold") and consolidate them into currency
2. Find ammunition items ("20 arrows", "crossbow bolts x 10") and move them to ammunition section
3. Preserve valuables (gems, art objects) as inventory items
4. Handle ambiguous containers properly (don't consolidate locked chests, etc.)

## MY CURRENT FILTERING APPROACH

Here's my extraction function that filters which items to send for consolidation:

```python
{extraction_function}
```

## ACTUAL CHARACTER DATA

Below are the complete equipment lists with currency and ammunition from all characters. Please analyze:

1. **Which currency/ammo items might be missed** by my filter?
2. **Common patterns** I should look for (e.g., "handful of coins", "coin purse")
3. **Items my filter includes unnecessarily** (false positives)
4. **Edge cases** to consider (partial descriptions, non-standard naming)
5. **Recommendations** for improving the filter

Key concerns:
- Missing loose coins with non-standard descriptions
- Missing ammunition with unusual names
- Including items that shouldn't be consolidated (valuables, locked containers)
- Handling containers that might or might not have coins

Character Data:
{json.dumps(characters, indent=2)}

Please provide specific examples from the character data and suggest improvements to the filtering logic.

IMPORTANT: The goal is to send ONLY items that genuinely might be loose currency or ammunition while avoiding sending the entire 85+ item inventory.
"""
    
    return consultation_prompt, characters

def main():
    print("=" * 80)
    print("GEMINI CONSULTATION: CURRENCY CONSOLIDATION FILTERING")
    print("=" * 80)
    
    prompt, characters = prepare_currency_consultation()
    
    print(f"\nLoaded {len(characters)} character equipment lists")
    print("Consulting Gemini about currency consolidation filtering...")
    
    # Save data for Gemini
    with open('all_currency_data_for_analysis.json', 'w') as f:
        json.dump(characters, f, indent=2)
    
    # Query Gemini
    result = query_gemini(
        prompt,
        files=['all_currency_data_for_analysis.json']
    )
    
    print("\n" + "=" * 80)
    print("GEMINI'S ANALYSIS:")
    print("=" * 80)
    print(result)
    
    # Save the consultation
    with open('gemini_currency_consultation_results.md', 'w') as f:
        f.write(f"# Gemini Consultation: Currency Consolidation Filtering\n\n")
        f.write(f"## Question\n{prompt}\n\n")
        f.write(f"## Gemini's Response\n{result}\n")
    
    print("\nConsultation saved to gemini_currency_consultation_results.md")

if __name__ == "__main__":
    main()