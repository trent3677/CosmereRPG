#!/usr/bin/env python3
"""
Consult Gemini about inventory filtering to ensure we're not missing misclassifications
"""

import json
import os
from gemini_tool import query_gemini
from utils.file_operations import safe_read_json

def prepare_inventory_consultation():
    """Prepare data for Gemini consultation about inventory filtering"""
    
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
                    'equipment': char_data.get('equipment', [])
                }
                print(f"Loaded {char_name} - {len(characters[char_name]['equipment'])} items")
    
    # Load the extraction function code
    with open('core/validation/character_validator.py', 'r') as f:
        validator_code = f.read()
    
    # Extract the inventory extraction function
    start_marker = "def extract_inventory_data"
    end_marker = "return inventory_data"
    
    start_idx = validator_code.find(start_marker)
    end_idx = validator_code.find(end_marker, start_idx) + len(end_marker)
    
    extraction_function = validator_code[start_idx:end_idx] if start_idx > -1 else "Function not found"
    
    # Load the inventory validation prompt
    with open('prompts/character_validator_inventory.txt', 'r') as f:
        inventory_prompt = f.read()
    
    # Prepare the consultation prompt
    consultation_prompt = f"""
I'm optimizing a D&D 5e inventory validator to reduce API token usage. Currently, I filter items before sending them for validation, but I'm concerned about missing misclassifications.

## THE CHALLENGE

The AI validator needs to correctly categorize items into these types:
- "weapon" - swords, bows, daggers, melee and ranged weapons
- "armor" - armor pieces, shields, cloaks/boots/gloves IF they provide AC
- "ammunition" - arrows, bolts, bullets
- "consumable" - potions, scrolls, food, rations
- "equipment" - tools, torches, rope, containers, utility items
- "miscellaneous" - rings, amulets, truly miscellaneous items

## MY CURRENT FILTERING APPROACH

Here's my extraction function that filters which items to send for validation:

```python
{extraction_function}
```

## THE VALIDATION PROMPT (showing categorization rules)

{inventory_prompt[:3000]}... [truncated for space]

## ACTUAL CHARACTER INVENTORIES

Below are the complete equipment lists from 4 characters. Please analyze:

1. **Which items might be miscategorized** that my filter would miss?
2. **Common misclassification patterns** (e.g., cloaks marked as armor when they're equipment)
3. **Items my filter excludes** that should be included for validation
4. **False positives** - items my filter includes unnecessarily
5. **Recommendations** for improving the filter

Key concerns:
- Cloaks being marked as armor when they don't provide AC
- Rings/amulets marked wrong (equipment vs miscellaneous)
- Tools miscategorized
- Consumables marked as equipment or miscellaneous
- Special items with ambiguous categorization

Character Equipment Lists:
{json.dumps(characters, indent=2)}

Please provide specific examples of items that could be problematic and suggest improvements to the filtering logic.
"""
    
    return consultation_prompt, characters

def main():
    print("=" * 80)
    print("GEMINI CONSULTATION: INVENTORY FILTERING VALIDATION")
    print("=" * 80)
    
    prompt, characters = prepare_inventory_consultation()
    
    print(f"\nLoaded {len(characters)} character equipment lists")
    print("Consulting Gemini about potential misclassification issues...")
    
    # Save equipment data for Gemini
    with open('all_equipment_for_analysis.json', 'w') as f:
        json.dump(characters, f, indent=2)
    
    # Query Gemini
    result = query_gemini(
        prompt,
        files=['all_equipment_for_analysis.json']
    )
    
    print("\n" + "=" * 80)
    print("GEMINI'S ANALYSIS:")
    print("=" * 80)
    print(result)
    
    # Save the consultation
    with open('gemini_inventory_consultation_results.md', 'w') as f:
        f.write(f"# Gemini Consultation: Inventory Filtering\n\n")
        f.write(f"## Question\n{prompt}\n\n")
        f.write(f"## Gemini's Response\n{result}\n")
    
    print("\nConsultation saved to gemini_inventory_consultation_results.md")

if __name__ == "__main__":
    main()