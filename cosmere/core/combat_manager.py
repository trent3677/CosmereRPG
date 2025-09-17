"""
Cosmere Combat Manager
Implements a light-weight combat flow using the Plot Die system.

Concepts:
- Initiative: Each participant rolls initiative via DiceRoller (awareness modifier optional)
- Turn order: Sorted descending by initiative total; ties go to defender precedence by stable ordering
- Action economy: 1 Action per turn; reactions tracked as flags (not implemented in depth yet)
- Actions: skill_check, use_power, note, end_turn
- Conditions: simple list of strings on each participant (placeholder)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class Participant:
    character_id: str
    name: str
    initiative_total: int = 0
    conditions: List[str] = field(default_factory=list)
    has_acted: bool = False


class CosmereCombatManager:
    def __init__(self, dice_roller, investiture_manager, character_manager):
        self.dice_roller = dice_roller
        self.investiture_manager = investiture_manager
        self.character_manager = character_manager
        self.active: bool = False
        self.round_number: int = 0
        self.turn_index: int = 0
        self.participants: List[Participant] = []
        self.log: List[Dict[str, Any]] = []

    def start(self, character_ids: List[str]) -> Dict[str, Any]:
        if not character_ids:
            raise ValueError("No participants provided")
        self.active = True
        self.round_number = 1
        self.turn_index = 0
        self.participants = []
        self.log = []

        # Roll initiative for each participant using awareness as modifier if available
        for cid in character_ids:
            char = self.character_manager.load_character(cid)
            if not char:
                raise ValueError(f"Character not found: {cid}")
            awareness_mod = int(char.get("stats", {}).get("awareness", 0))
            init_result = self.dice_roller.roll_initiative(awareness_modifier=awareness_mod)
            participant = Participant(
                character_id=cid,
                name=char.get("name", cid),
                initiative_total=int(init_result.get("total", 0))
            )
            self.participants.append(participant)

        # Highest initiative first
        self.participants.sort(key=lambda p: p.initiative_total, reverse=True)
        self._log_event("combat_started", {
            "participants": [{"id": p.character_id, "name": p.name, "initiative": p.initiative_total} for p in self.participants]
        })
        return self.state()

    def state(self) -> Dict[str, Any]:
        return {
            "active": self.active,
            "round": self.round_number,
            "turn_index": self.turn_index,
            "turn_character_id": self.participants[self.turn_index].character_id if self.active and self.participants else None,
            "order": [
                {
                    "id": p.character_id,
                    "name": p.name,
                    "initiative": p.initiative_total,
                    "conditions": p.conditions,
                }
                for p in self.participants
            ],
            "log": self.log[-50:],  # tail
        }

    def act(self, actor_id: str, action: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.active:
            raise ValueError("Combat not active")
        current = self.participants[self.turn_index]
        if current.character_id != actor_id:
            raise ValueError("Not this participant's turn")
        payload = payload or {}

        if action == "skill_check":
            # Perform a plot die skill check with optional modifier
            modifier = int(payload.get("modifier", 0))
            advantage = bool(payload.get("advantage", False))
            skilled = bool(payload.get("skilled", False))
            result = self.dice_roller.roll_skill_check(
                skill_modifier=modifier,
                advantage=advantage,
                skilled=skilled,
            )
            self._log_event("skill_check", {"actor": actor_id, "result": result})

        elif action == "use_power":
            # Apply power cost to actor
            power_name = payload.get("power")
            if not power_name:
                raise ValueError("Missing power name")
            char = self.character_manager.load_character(actor_id)
            if not char:
                raise ValueError("Actor not found")
            updated = self.investiture_manager.apply_power_cost(char, power_name)
            self.character_manager.save_character(updated)
            self._log_event("use_power", {"actor": actor_id, "power": power_name, "remaining": updated["investiture"]["investiture_points"]})

        elif action == "attack":
            # Simple physical attack damage resolution: roll damage and reduce by target armor
            target_id = payload.get("target_id")
            if not target_id:
                raise ValueError("Missing target_id")
            damage_dice = int(payload.get("dice", 1))
            bonus = int(payload.get("bonus", 0))
            dmg_result = self.dice_roller.roll_damage(damage_dice=damage_dice, bonus_damage=bonus)
            # Load target and compute mitigation
            target_char = self.character_manager.load_character(target_id)
            if not target_char:
                raise ValueError("Target not found")
            armor = int(target_char.get("derived_stats", {}).get("armor", 0))
            mitigated = max(0, int(dmg_result.get("total", 0)) - armor)
            # Apply HP change
            updated_target = self.character_manager.modify_hp(target_id, -mitigated)
            # Add downed condition if at 0
            if int(updated_target.get("derived_stats", {}).get("hp", 0)) <= 0:
                self._add_condition_to_participant(target_id, "downed")
            self._log_event("attack", {
                "actor": actor_id,
                "target": target_id,
                "rolls": dmg_result.get("rolls", []),
                "bonus": bonus,
                "armor": armor,
                "damage": mitigated,
                "target_hp": updated_target.get("derived_stats", {}).get("hp", 0)
            })

        elif action == "add_condition":
            target_id = payload.get("target_id")
            cond = str(payload.get("condition", "")).strip()
            if not target_id or not cond:
                raise ValueError("Missing target_id or condition")
            self._add_condition_to_participant(target_id, cond)
            self._log_event("condition_added", {"target": target_id, "condition": cond})

        elif action == "remove_condition":
            target_id = payload.get("target_id")
            cond = str(payload.get("condition", "")).strip()
            if not target_id or not cond:
                raise ValueError("Missing target_id or condition")
            self._remove_condition_from_participant(target_id, cond)
            self._log_event("condition_removed", {"target": target_id, "condition": cond})

        elif action == "note":
            self._log_event("note", {"actor": actor_id, "text": str(payload.get("text", ""))})

        elif action == "end_turn":
            # Handled below by advancing turn
            pass

        else:
            raise ValueError("Unknown action")

        # End turn and advance
        self._advance_turn()
        return self.state()

    def finish(self) -> Dict[str, Any]:
        self.active = False
        self._log_event("combat_finished", {})
        return self.state()

    def _advance_turn(self) -> None:
        if not self.participants:
            return
        self.turn_index += 1
        if self.turn_index >= len(self.participants):
            self.turn_index = 0
            self.round_number += 1
            self._log_event("new_round", {"round": self.round_number})

    def _log_event(self, kind: str, data: Dict[str, Any]) -> None:
        self.log.append({"event": kind, **data})

    def _find_participant(self, character_id: str) -> Optional[Participant]:
        for p in self.participants:
            if p.character_id == character_id:
                return p
        return None

    def _add_condition_to_participant(self, character_id: str, condition: str) -> None:
        part = self._find_participant(character_id)
        if part and condition not in part.conditions:
            part.conditions.append(condition)

    def _remove_condition_from_participant(self, character_id: str, condition: str) -> None:
        part = self._find_participant(character_id)
        if part and condition in part.conditions:
            part.conditions.remove(condition)


