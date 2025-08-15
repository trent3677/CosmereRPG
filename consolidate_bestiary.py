#!/usr/bin/env python3
"""
Consolidate all monster descriptions from generate_*.py files into a unified bestiary
"""

import os
import re
import json
from pathlib import Path
import ast

def extract_monster_descriptions():
    """Extract monster descriptions from all generate_*.py files"""
    monsters = {}
    
    # Get all generate_*.py files
    generate_files = list(Path('.').glob('generate_*.py'))
    
    for file_path in generate_files:
        print(f"Processing {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to find monster descriptions - multiple patterns for different formats
        patterns = [
            # Pattern 1: MONSTER_NAME_DESCRIPTION = """..."""
            r'([A-Z_]+_DESCRIPTION)\s*=\s*"""(.*?)"""',
            # Pattern 2: "Monster Name": """...""" in dictionaries
            r'"([^"]+)":\s*"""(.*?)"""',
            # Pattern 3: MONSTERS = { ... } dictionaries
            r'MONSTERS\s*=\s*{(.*?)}(?=\n\w|\n$|\Z)',
            # Pattern 4: MONSTERS_BATCH_\d+ = { ... }
            r'MONSTERS_BATCH_\d+\s*=\s*{(.*?)}(?=\n\w|\n$|\Z)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            
            for match in matches:
                if len(match) == 2:
                    if pattern == patterns[0]:  # DESCRIPTION pattern
                        # Extract monster name from variable name
                        var_name = match[0]
                        monster_name = var_name.replace('_DESCRIPTION', '').lower()
                        if monster_name == 'gorvek':
                            monster_name = 'bandit_captain_gorvek'
                        elif monster_name == 'shadow_manifestation':
                            monster_name = 'shadow_manifestation'
                        description = match[1].strip()
                    else:  # Direct name: description pattern
                        monster_name = match[0].lower().replace(' ', '_').replace('-', '_')
                        description = match[1].strip()
                    
                    # Clean up description
                    description = clean_description(description)
                    
                    if monster_name and description and len(description) > 50:
                        # Determine type from description
                        monster_type = determine_monster_type(description)
                        
                        # Extract any special tags
                        tags = extract_tags(description)
                        
                        monsters[monster_name] = {
                            "name": format_display_name(monster_name),
                            "type": monster_type,
                            "description": description,
                            "tags": tags,
                            "source_file": str(file_path)
                        }
                
                elif len(match) == 1 and 'MONSTERS' in content:
                    # Handle dictionary format
                    try:
                        # Extract the full dictionary
                        dict_match = re.search(pattern, content, re.DOTALL)
                        if dict_match:
                            dict_str = '{' + dict_match.group(1) + '}'
                            # Try to parse as Python literal
                            dict_str = dict_str.replace('"""', "'''")
                            # This is risky but we'll be careful
                            try:
                                # Use AST to safely evaluate
                                tree = ast.parse(f"data = {dict_str}", mode='eval')
                                # Basic validation - should be a dict
                                if isinstance(tree.body, ast.Dict):
                                    # Manual extraction since ast.literal_eval won't work with multiline strings
                                    monster_dict = extract_dict_manually(dict_str)
                                    for name, desc in monster_dict.items():
                                        monster_name = name.lower().replace(' ', '_').replace('-', '_')
                                        description = clean_description(desc)
                                        if monster_name and description and len(description) > 50:
                                            monsters[monster_name] = {
                                                "name": format_display_name(monster_name),
                                                "type": determine_monster_type(description),
                                                "description": description,
                                                "tags": extract_tags(description),
                                                "source_file": str(file_path)
                                            }
                            except:
                                pass
                    except:
                        pass
    
    return monsters

def extract_dict_manually(dict_str):
    """Manually extract dictionary entries with multiline strings"""
    result = {}
    # Pattern for "name": '''description'''
    pattern = r'"([^"]+)":\s*\'\'\'(.*?)\'\'\'|"([^"]+)":\s*"""(.*?)"""'
    matches = re.findall(pattern, dict_str, re.DOTALL)
    
    for match in matches:
        if match[0] and match[1]:  # First pattern matched
            result[match[0]] = match[1]
        elif match[2] and match[3]:  # Second pattern matched
            result[match[2]] = match[3]
    
    return result

def clean_description(description):
    """Clean up description text"""
    # Remove excessive whitespace
    description = re.sub(r'\s+', ' ', description)
    # Remove leading/trailing whitespace
    description = description.strip()
    # Fix sentence spacing
    description = re.sub(r'\.\s+', '. ', description)
    return description

def determine_monster_type(description):
    """Determine monster type from description"""
    description_lower = description.lower()
    
    type_keywords = {
        "aberration": ["aberration", "alien", "mind flayer", "beholder", "aboleth"],
        "beast": ["animal", "beast", "wolf", "bear", "lion", "tiger"],
        "celestial": ["celestial", "angel", "solar", "deva", "archon"],
        "construct": ["construct", "golem", "animated", "clockwork", "mechanical"],
        "dragon": ["dragon", "drake", "wyrm", "wyvern"],
        "elemental": ["elemental", "fire", "water", "earth", "air"],
        "fey": ["fey", "fairy", "sprite", "pixie", "satyr"],
        "fiend": ["fiend", "demon", "devil", "balor", "pit fiend"],
        "giant": ["giant", "ogre", "troll", "ettin"],
        "humanoid": ["humanoid", "human", "elf", "dwarf", "orc", "goblin", "bandit"],
        "monstrosity": ["monstrosity", "chimera", "hydra", "basilisk", "manticore"],
        "ooze": ["ooze", "slime", "jelly", "pudding", "cube"],
        "plant": ["plant", "tree", "vine", "fungus", "myconid", "shambling", "shrub", "twig"],
        "undead": ["undead", "zombie", "skeleton", "ghost", "vampire", "lich", "wraith", "shadow"]
    }
    
    for monster_type, keywords in type_keywords.items():
        for keyword in keywords:
            if keyword in description_lower:
                return monster_type
    
    return "monstrosity"  # Default type

def extract_tags(description):
    """Extract relevant tags from description"""
    tags = []
    description_lower = description.lower()
    
    tag_keywords = {
        "boss": ["boss", "leader", "captain", "lord", "master"],
        "corrupted": ["corrupted", "tainted", "twisted", "dark magic"],
        "magical": ["magical", "arcane", "enchanted", "spell"],
        "flying": ["flying", "wings", "flies", "airborne"],
        "aquatic": ["aquatic", "underwater", "swim", "marine"],
        "psychic": ["psychic", "mind", "telepathy", "mental"],
        "ancient": ["ancient", "primordial", "prehistoric", "elder"],
        "swarm": ["swarm", "horde", "group", "multiple"],
        "legendary": ["legendary", "mythic", "fabled"],
        "tiny": ["tiny", "diminutive", "small"],
        "large": ["large", "huge", "massive", "giant", "colossal"],
        "incorporeal": ["incorporeal", "ethereal", "ghostly", "spectral", "phantom"]
    }
    
    for tag, keywords in tag_keywords.items():
        for keyword in keywords:
            if keyword in description_lower:
                tags.append(tag)
                break
    
    return list(set(tags))  # Remove duplicates

def format_display_name(monster_name):
    """Format monster name for display"""
    # Special cases
    special_names = {
        "bandit_captain_gorvek": "Bandit Captain Gorvek",
        "malarok_the_corruptor": "Malarok the Corruptor",
        "adult_black_dragon": "Adult Black Dragon",
        "adult_blue_dragon": "Adult Blue Dragon",
        "adult_red_dragon": "Adult Red Dragon"
    }
    
    if monster_name in special_names:
        return special_names[monster_name]
    
    # General formatting
    words = monster_name.split('_')
    formatted_words = []
    
    for word in words:
        if word in ['of', 'the', 'and', 'or', 'a', 'an']:
            formatted_words.append(word)
        else:
            formatted_words.append(word.capitalize())
    
    return ' '.join(formatted_words)

def save_bestiary(monsters):
    """Save the bestiary to JSON file"""
    bestiary = {
        "version": "1.0.0",
        "created": "2025-08-13",
        "total_monsters": len(monsters),
        "monsters": monsters
    }
    
    output_path = Path('data/bestiary/monster_compendium.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(bestiary, f, indent=2, ensure_ascii=False)
    
    print(f"\nBestiary saved to {output_path}")
    print(f"Total monsters consolidated: {len(monsters)}")
    
    # Print summary by type
    type_counts = {}
    for monster in monsters.values():
        monster_type = monster['type']
        type_counts[monster_type] = type_counts.get(monster_type, 0) + 1
    
    print("\nMonsters by type:")
    for monster_type, count in sorted(type_counts.items()):
        print(f"  {monster_type}: {count}")

def main():
    print("Consolidating monster descriptions from generate_*.py files...")
    print("="*60)
    
    monsters = extract_monster_descriptions()
    
    if monsters:
        save_bestiary(monsters)
        
        # Print some examples
        print("\nSample entries:")
        for i, (key, monster) in enumerate(list(monsters.items())[:3]):
            print(f"\n{i+1}. {monster['name']} ({monster['type']})")
            print(f"   Tags: {', '.join(monster['tags']) if monster['tags'] else 'None'}")
            print(f"   Description preview: {monster['description'][:150]}...")
    else:
        print("No monster descriptions found!")

if __name__ == "__main__":
    main()