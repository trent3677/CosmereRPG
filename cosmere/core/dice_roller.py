"""
Cosmere RPG Dice Roller
Implements the Plot Die system and dice mechanics
"""

import random
from typing import Dict, List, Tuple, Optional
from enum import Enum

class PlotDieResult(Enum):
    """Plot Die special results"""
    COMPLICATION = 1  # Something goes wrong
    NORMAL_2 = 2
    NORMAL_3 = 3
    NORMAL_4 = 4
    NORMAL_5 = 5
    OPPORTUNITY = 6   # Something goes especially well

class DiceRoller:
    def __init__(self):
        self.last_roll = None
        
    def roll_plot_die(self) -> Tuple[int, PlotDieResult]:
        """Roll a single Plot Die (d6 with special results)"""
        result = random.randint(1, 6)
        plot_result = PlotDieResult(result)
        
        self.last_roll = {
            "type": "plot_die",
            "result": result,
            "plot_result": plot_result
        }
        
        return result, plot_result
    
    def roll_skill_check(self, 
                        skill_modifier: int = 0, 
                        advantage: bool = False,
                        disadvantage: bool = False,
                        skilled: bool = False) -> Dict[str, any]:
        """
        Roll for a skill check in Cosmere RPG
        
        Args:
            skill_modifier: The character's skill modifier
            advantage: Roll an additional die and take the best
            disadvantage: Roll an additional die and take the worst
            skilled: Character has relevant skill training
            
        Returns:
            Dictionary with roll results and total
        """
        rolls = []
        plot_results = []
        
        # Base roll
        base_roll, plot_result = self.roll_plot_die()
        rolls.append(base_roll)
        plot_results.append(plot_result)
        
        # Advantage/Disadvantage
        if advantage or disadvantage:
            extra_roll, extra_plot = self.roll_plot_die()
            rolls.append(extra_roll)
            plot_results.append(extra_plot)
            
            if advantage:
                # Take the higher roll
                chosen_index = 0 if rolls[0] >= rolls[1] else 1
            else:  # disadvantage
                # Take the lower roll
                chosen_index = 0 if rolls[0] <= rolls[1] else 1
                
            final_roll = rolls[chosen_index]
            final_plot = plot_results[chosen_index]
        else:
            final_roll = base_roll
            final_plot = plot_result
        
        # Calculate total
        total = final_roll + skill_modifier
        
        # Skilled bonus (reroll 1s)
        if skilled and final_roll == 1:
            reroll, replot = self.roll_plot_die()
            rolls.append(reroll)
            plot_results.append(replot)
            final_roll = reroll
            final_plot = replot
            total = final_roll + skill_modifier
        
        result = {
            "rolls": rolls,
            "plot_results": [pr.name for pr in plot_results],
            "final_roll": final_roll,
            "final_plot_result": final_plot.name,
            "modifier": skill_modifier,
            "total": total,
            "advantage": advantage,
            "disadvantage": disadvantage,
            "skilled": skilled,
            "is_complication": final_plot == PlotDieResult.COMPLICATION,
            "is_opportunity": final_plot == PlotDieResult.OPPORTUNITY
        }
        
        self.last_roll = result
        return result
    
    def roll_damage(self, damage_dice: int, bonus_damage: int = 0) -> Dict[str, any]:
        """
        Roll damage in Cosmere RPG
        
        Args:
            damage_dice: Number of d6 to roll
            bonus_damage: Flat damage bonus
            
        Returns:
            Dictionary with damage roll details
        """
        rolls = []
        total_damage = bonus_damage
        
        for _ in range(damage_dice):
            roll = random.randint(1, 6)
            rolls.append(roll)
            total_damage += roll
        
        result = {
            "type": "damage",
            "dice": damage_dice,
            "rolls": rolls,
            "bonus": bonus_damage,
            "total": total_damage
        }
        
        self.last_roll = result
        return result
    
    def roll_initiative(self, awareness_modifier: int = 0) -> Dict[str, any]:
        """Roll initiative for combat"""
        result = self.roll_skill_check(skill_modifier=awareness_modifier)
        result["type"] = "initiative"
        return result
    
    def contest_roll(self, 
                    attacker_mod: int, 
                    defender_mod: int,
                    attacker_advantage: bool = False,
                    defender_advantage: bool = False) -> Dict[str, any]:
        """
        Handle contested rolls between two characters
        
        Returns:
            Dictionary with both rolls and the winner
        """
        attacker_roll = self.roll_skill_check(
            skill_modifier=attacker_mod,
            advantage=attacker_advantage
        )
        
        defender_roll = self.roll_skill_check(
            skill_modifier=defender_mod,
            advantage=defender_advantage
        )
        
        # Determine winner
        if attacker_roll["total"] > defender_roll["total"]:
            winner = "attacker"
        elif defender_roll["total"] > attacker_roll["total"]:
            winner = "defender"
        else:
            # Ties go to defender in Cosmere RPG
            winner = "defender"
        
        return {
            "type": "contest",
            "attacker": attacker_roll,
            "defender": defender_roll,
            "winner": winner,
            "margin": abs(attacker_roll["total"] - defender_roll["total"])
        }
    
    def format_roll_result(self, result: Dict[str, any]) -> str:
        """Format a roll result for display"""
        if result.get("type") == "damage":
            return (f"Damage Roll: {result['dice']}d6"
                   f"{'+' + str(result['bonus']) if result['bonus'] else ''} = "
                   f"{result['rolls']} = {result['total']} damage")
        
        elif result.get("type") == "contest":
            return (f"Contested Roll:\n"
                   f"  Attacker: {result['attacker']['total']} "
                   f"(rolled {result['attacker']['final_roll']}+{result['attacker']['modifier']})\n"
                   f"  Defender: {result['defender']['total']} "
                   f"(rolled {result['defender']['final_roll']}+{result['defender']['modifier']})\n"
                   f"  Winner: {result['winner'].capitalize()}")
        
        else:  # Skill check or initiative
            base_text = (f"Roll: 1d6{'+' + str(result['modifier']) if result['modifier'] else ''} = "
                        f"{result['final_roll']}+{result['modifier']} = {result['total']}")
            
            if result['is_complication']:
                base_text += " (COMPLICATION!)"
            elif result['is_opportunity']:
                base_text += " (OPPORTUNITY!)"
                
            if result.get('advantage'):
                base_text += " [Advantage]"
            elif result.get('disadvantage'):
                base_text += " [Disadvantage]"
                
            return base_text