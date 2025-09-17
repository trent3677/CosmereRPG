"""
Cosmere RPG Character Manager
Handles character creation, management, and progression
"""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

class CosmereCharacterManager:
    def __init__(self, data_dir: str = "cosmere/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.characters_dir = self.data_dir / "characters"
        self.characters_dir.mkdir(exist_ok=True)
        
    def create_character(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Cosmere RPG character"""
        # Validate required fields
        required_fields = ["name", "heritage", "path", "origin"]
        for field in required_fields:
            if field not in character_data or not str(character_data[field]).strip():
                raise ValueError(f"Missing required field: {field}")
        
        # Set default values
        character = {
            "id": self._generate_character_id(),
            "name": character_data["name"],
            "heritage": character_data["heritage"],
            "path": character_data["path"],
            "origin": character_data["origin"],
            "level": 1,
            "stats": {
                "strength": 0,
                "speed": 0,
                "intellect": 0,
                "willpower": 0,
                "awareness": 0,
                "persuasion": 0
            },
            "derived_stats": {
                "hp": 10,
                "max_hp": 10,
                "deflect": 10,
                "armor": 0,
                "mental_fortitude": 10,
                "physical_fortitude": 10
            },
            "talents": [],
            "investiture": {
                "type": "None",
                "powers": [],
                "investiture_points": 0,
                "max_investiture": 0
            },
            "equipment": [],
            "notes": []
        }
        
        # Apply any custom stats with validation
        if "stats" in character_data and isinstance(character_data["stats"], dict):
            validated_stats = self._validate_and_coerce_stats(character_data["stats"])
            character["stats"].update(validated_stats)
            
        # Calculate derived stats
        character["derived_stats"] = self._calculate_derived_stats(character)
        
        # Save character
        self._save_character(character)
        
        return character
    
    def _calculate_derived_stats(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived statistics based on core stats"""
        stats = character["stats"]
        
        # Base values + stat modifiers
        derived = {
            "hp": 10 + stats["strength"],
            "max_hp": 10 + stats["strength"],
            "deflect": 10 + stats["speed"],
            "armor": 0,  # From equipment
            "mental_fortitude": 10 + stats["willpower"],
            "physical_fortitude": 10 + stats["strength"]
        }
        
        # Apply heritage bonuses (example)
        if character["heritage"] == "Alethi":
            derived["physical_fortitude"] += 1
        elif character["heritage"] == "Terris":
            derived["mental_fortitude"] += 1
            
        return derived
    
    def load_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Load a character by ID"""
        filepath = self.characters_dir / f"{character_id}.json"
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    
    def save_character(self, character: Dict[str, Any]) -> None:
        """Save character data"""
        self._save_character(character)
    
    def _save_character(self, character: Dict[str, Any]) -> None:
        """Internal save method"""
        filepath = self.characters_dir / f"{character['id']}.json"
        with open(filepath, 'w') as f:
            json.dump(character, f, indent=2)

    def delete_character(self, character_id: str) -> bool:
        """Delete a character file; returns True if deleted"""
        filepath = self.characters_dir / f"{character_id}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False
    
    def _generate_character_id(self) -> str:
        """Generate a unique character ID"""
        import uuid
        return str(uuid.uuid4())[:8]

    def _validate_and_coerce_stats(self, stats: Dict[str, Any]) -> Dict[str, int]:
        """Coerce stats to ints and clamp to a reasonable range (-5..+5)."""
        allowed = ["strength", "speed", "intellect", "willpower", "awareness", "persuasion"]
        result: Dict[str, int] = {}
        for key in allowed:
            if key in stats:
                try:
                    val = int(stats[key])
                except Exception:
                    val = 0
                # Clamp range
                if val < -5:
                    val = -5
                if val > 5:
                    val = 5
                result[key] = val
        return result
    
    def add_talent(self, character_id: str, talent: Dict[str, Any]) -> Dict[str, Any]:
        """Add a talent to a character"""
        character = self.load_character(character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")
            
        character["talents"].append(talent)
        self._save_character(character)
        return character
    
    def update_investiture(self, character_id: str, investiture_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update character's Investiture abilities"""
        character = self.load_character(character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")
            
        character["investiture"].update(investiture_data)
        self._save_character(character)
        return character
    
    def modify_hp(self, character_id: str, change: int) -> Dict[str, Any]:
        """Modify character's current HP"""
        character = self.load_character(character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")
            
        character["derived_stats"]["hp"] = max(0, 
            min(character["derived_stats"]["hp"] + change, 
                character["derived_stats"]["max_hp"]))
        
        self._save_character(character)
        return character
    
    def add_equipment(self, character_id: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """Add an item to character's equipment"""
        character = self.load_character(character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")
            
        character["equipment"].append(item)
        
        # Update armor if applicable
        if item.get("type") == "armor" and "armor_value" in item.get("properties", {}):
            character["derived_stats"]["armor"] = item["properties"]["armor_value"]
            
        self._save_character(character)
        return character
    
    def list_characters(self) -> List[Dict[str, str]]:
        """List all saved characters"""
        characters = []
        for filepath in self.characters_dir.glob("*.json"):
            with open(filepath, 'r') as f:
                char_data = json.load(f)
                characters.append({
                    "id": char_data["id"],
                    "name": char_data["name"],
                    "heritage": char_data["heritage"],
                    "path": char_data["path"],
                    "level": char_data["level"]
                })
        return characters