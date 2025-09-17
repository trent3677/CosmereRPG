"""
Talent Manager for Cosmere RPG
Loads talents from JSON and applies them to characters.

Talent JSON expected shape (either a list or {"talents": [...] }):
{
  "name": "Windrunner Oath 1",
  "category": "Path",
  "path": "Windrunner",
  "description": "Swear to protect...",
  "effects": {
    "stats": {"willpower": 1},
    "max_investiture": 1
  }
}
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json


class TalentManager:
    def __init__(self, character_manager):
        self._talents: Dict[str, Dict[str, Any]] = {}
        self.character_manager = character_manager

    def load_from_file(self, json_path: str) -> int:
        path = Path(json_path)
        if not path.exists():
            return 0
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        items = data.get('talents', data if isinstance(data, list) else [])
        loaded = 0
        for t in items:
            try:
                self._validate(t)
                self._talents[t['name']] = t
                loaded += 1
            except Exception:
                continue
        return loaded

    def list_talents(self, path_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        talents = list(self._talents.values())
        if path_filter:
            pf = path_filter.strip().lower()
            talents = [t for t in talents if str(t.get('path', '')).lower() == pf]
        return talents

    def apply_talent(self, character_id: str, talent_name: str) -> Dict[str, Any]:
        if talent_name not in self._talents:
            raise ValueError("Unknown talent")
        talent = self._talents[talent_name]
        char = self.character_manager.load_character(character_id)
        if not char:
            raise ValueError("Character not found")

        # Prevent duplicates
        existing = [t.get('name') if isinstance(t, dict) else t for t in char.get('talents', [])]
        if talent_name in existing:
            return char

        # Apply effects
        effects = talent.get('effects', {})
        if 'stats' in effects and isinstance(effects['stats'], dict):
            for k, v in effects['stats'].items():
                try:
                    delta = int(v)
                except Exception:
                    delta = 0
                if k in char.get('stats', {}):
                    char['stats'][k] = int(char['stats'][k]) + delta

        if 'max_investiture' in effects:
            try:
                delta = int(effects['max_investiture'])
            except Exception:
                delta = 0
            inv = char.setdefault('investiture', {"type": "None", "powers": [], "investiture_points": 0, "max_investiture": 0})
            inv['max_investiture'] = int(inv.get('max_investiture', 0)) + delta

        # Recalculate derived stats
        char['derived_stats'] = self.character_manager._calculate_derived_stats(char)

        # Record talent
        char.setdefault('talents', []).append({'name': talent_name, 'category': talent.get('category', ''), 'path': talent.get('path', '')})

        self.character_manager.save_character(char)
        return char

    def _validate(self, talent: Dict[str, Any]) -> None:
        if not isinstance(talent, dict):
            raise ValueError('Talent must be dict')
        if not talent.get('name'):
            raise ValueError('Talent requires name')

