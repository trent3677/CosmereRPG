"""
Investiture Manager for Cosmere RPG
Tracks Investiture pools and powers for characters.
"""

from typing import Dict, Any, List


class InvestitureManager:
    def __init__(self):
        # In-memory registry; could be persisted later
        self._power_definitions: Dict[str, Dict[str, Any]] = {}

    def register_power(self, power: Dict[str, Any]) -> None:
        """Register a power definition (e.g., name, cost, effect)."""
        name = power.get("name")
        if not name:
            raise ValueError("Power must have a name")
        self._power_definitions[name] = power

    def list_powers(self) -> List[Dict[str, Any]]:
        """List all registered powers."""
        return list(self._power_definitions.values())

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


