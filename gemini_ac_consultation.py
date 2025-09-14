#!/usr/bin/env python3
"""
Consult Gemini about AC field extraction to ensure we're not missing anything
"""

import json
import os
from gemini_tool import query_gemini
from utils.file_operations import safe_read_json

def prepare_consultation():
    """Prepare data for Gemini consultation"""
    
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
                characters[char_name] = char_data
                print(f"Loaded {char_name} - {len(json.dumps(char_data))} chars")
    
    # Load the extraction function code
    with open('core/validation/character_validator.py', 'r') as f:
        validator_code = f.read()
    
    # Extract just the relevant function
    start_marker = "def extract_ac_relevant_data"
    end_marker = "return ac_data"
    
    start_idx = validator_code.find(start_marker)
    end_idx = validator_code.find(end_marker, start_idx) + len(end_marker)
    
    extraction_function = validator_code[start_idx:end_idx] if start_idx > -1 else "Function not found"
    
    # Prepare the consultation prompt
    consultation_prompt = f"""
I'm optimizing a D&D 5e character validator to reduce token usage when validating Armor Class (AC) calculations.

GOAL: Extract ONLY the fields from a character sheet that could possibly affect AC calculation, while ensuring we don't miss anything important.

Here's my current extraction function:

```python
{extraction_function}
```

Below are 4 complete character sheets from the game. Please analyze:

1. Are there any fields in these character sheets that could affect AC that my extraction function might miss?
2. Are there any D&D 5e mechanics for AC calculation that I'm not considering?
3. Is my function including items that definitely DON'T affect AC and could be filtered out?
4. What about racial traits, feats, or special abilities that might affect AC?

Character Sheets:

{json.dumps(characters, indent=2)}

Please provide specific recommendations for improving the extraction function to ensure it captures ALL AC-relevant data while minimizing tokens.

Key D&D 5e AC considerations:
- Base armor and shields
- Dexterity modifier (limited by armor type)
- Fighting Style: Defense (+1 AC)
- Magical items (rings of protection, cloaks of protection, etc.)
- Class features (Monk's Unarmored Defense, Barbarian's Unarmored Defense)
- Racial traits (Tortles natural armor, Warforged integrated protection)
- Spells (Mage Armor, Shield, Barkskin - but only if actively cast)
- Feats (Defensive Duelist, Medium Armor Master)
- Magic items with AC bonuses
"""
    
    return consultation_prompt, characters

def main():
    print("=" * 80)
    print("GEMINI CONSULTATION: AC FIELD EXTRACTION VALIDATION")
    print("=" * 80)
    
    prompt, characters = prepare_consultation()
    
    print(f"\nLoaded {len(characters)} character sheets")
    print("Consulting Gemini about AC extraction completeness...")
    
    # Save characters to file for Gemini to analyze
    with open('all_characters_for_analysis.json', 'w') as f:
        json.dump(characters, f, indent=2)
    
    # Query Gemini
    result = query_gemini(
        prompt,
        files=['all_characters_for_analysis.json']
    )
    
    print("\n" + "=" * 80)
    print("GEMINI'S ANALYSIS:")
    print("=" * 80)
    print(result)
    
    # Save the consultation
    with open('gemini_ac_consultation_results.md', 'w') as f:
        f.write(f"# Gemini Consultation: AC Field Extraction\n\n")
        f.write(f"## Question\n{prompt}\n\n")
        f.write(f"## Gemini's Response\n{result}\n")
    
    print("\nConsultation saved to gemini_ac_consultation_results.md")

if __name__ == "__main__":
    main()