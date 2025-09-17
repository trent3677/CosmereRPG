"""
Investiture Manager for Cosmere RPG
Tracks Investiture pools and powers for characters.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json


class InvestitureManager:
    def __init__(self):
        # In-memory registry; could be persisted later
        self._power_definitions: Dict[str, Dict[str, Any]] = {}

    def register_power(self, power: Dict[str, Any]) -> None:
        """Register a power definition (e.g., name, cost, effect)."""
        self._validate_power(power)
        name = power["name"]
        self._power_definitions[name] = power

    def list_powers(self, power_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all registered powers, optionally filtered by type."""
        powers = list(self._power_definitions.values())
        if power_type:
            power_type_lower = power_type.strip().lower()
            powers = [p for p in powers if str(p.get("type", "")).lower() == power_type_lower]
        return powers

    def apply_power_cost(self, character: Dict[str, Any], power_name: str) -> Dict[str, Any]:
        """Deduct Investiture cost for a power, if possible; return updated character."""
        power = self._power_definitions.get(power_name)
        if not power:
            raise ValueError(f"Unknown power: {power_name}")

        cost = int(power.get("cost", 0))
        inv = character.setdefault("investiture", {"investiture_points": 0, "max_investiture": 0})
        if inv.get("investiture_points", 0) < cost:
            raise ValueError("Not enough Investiture points")

        inv["investiture_points"] -= cost
        return character

    def load_powers_from_file(self, json_path: str) -> int:
        """Load power definitions from a JSON file. Returns count loaded."""
        path = Path(json_path)
        if not path.exists():
            return 0
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "powers" in data:
            items = data["powers"]
        elif isinstance(data, list):
            items = data
        else:
            raise ValueError("Invalid powers JSON format: expected list or { 'powers': [...] }")
        loaded = 0
        for item in items:
            try:
                self.register_power(item)
                loaded += 1
            except Exception:
                # Skip invalid entries silently for robustness
                continue
        return loaded

    def _validate_power(self, power: Dict[str, Any]) -> None:
        if not isinstance(power, dict):
            raise ValueError("Power must be a dict")
        name = power.get("name")
        if not name or not isinstance(name, str):
            raise ValueError("Power must have a string 'name'")
        cost = power.get("cost", 0)
        try:
            cost_int = int(cost)
        except Exception:
            raise ValueError("Power 'cost' must be an integer")
        if cost_int < 0:
            raise ValueError("Power 'cost' must be >= 0")
        # Optional fields
        if "type" in power and power["type"] is not None and not isinstance(power["type"], str):
            raise ValueError("Power 'type' must be a string if provided")
        if "description" in power and power["description"] is not None and not isinstance(power["description"], str):
            raise ValueError("Power 'description' must be a string if provided")


