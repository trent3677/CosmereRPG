# Cosmere RPG Adaptation Plan

## Overview
This document outlines the strategy for adapting the NeverEndingQuest D&D 5e system to support Cosmere RPG.

## Core Differences to Address

### 1. Magic System (Investiture vs Spell Slots)
- **D&D 5e**: Spell slots, prepared spells, spell levels
- **Cosmere**: Investiture system with different magic types (Allomancy, Feruchemy, Surgebinding, etc.)
- **Implementation**: Replace spell system with Investiture tracking and power-specific mechanics

### 2. Character Creation
- **D&D 5e**: Race, Class, Background
- **Cosmere**: Heritage, Path, Origin
- **Implementation**: Modify character schemas and creation wizard

### 3. Dice Mechanics
- **D&D 5e**: d20 system with various dice
- **Cosmere**: Plot Die system (d6 with special results)
- **Implementation**: Update dice rolling logic and result interpretation

### 4. Character Progression
- **D&D 5e**: Levels 1-20 with class features
- **Cosmere**: Talent trees and Investiture progression
- **Implementation**: Replace level-up system with talent acquisition

### 5. Combat System
- **D&D 5e**: Action/Bonus Action/Reaction economy
- **Cosmere**: Different action economy with Plot Die integration
- **Implementation**: Modify combat manager for new action types

## Implementation Strategy

### Phase 1: Core System Adaptation
1. Create Cosmere-specific schemas
2. Replace D&D terminology throughout codebase
3. Implement Plot Die mechanics
4. Update character creation flow

### Phase 2: Investiture System
1. Design Investiture tracking system
2. Implement magic-specific mechanics (Allomancy, etc.)
3. Create power selection interfaces
4. Update combat for Investiture abilities

### Phase 3: PDF Integration
1. Build PDF parser for rules extraction
2. Create searchable rules database
3. Implement context-aware rule lookups
4. Add learning mode with rule references

### Phase 4: Enhanced Features
1. Interactive tutorials for new players
2. Character portfolio management
3. Campaign tracking
4. Community content sharing

## Technical Approach

### Schema Modifications
- `schemas/char_schema.json` → `schemas/cosmere_char_schema.json`
- `schemas/spell_repository.json` → `schemas/investiture_powers.json`
- Add new schemas for Cosmere-specific elements

### AI Prompt Updates
- Replace D&D rules in system prompts with Cosmere rules
- Train AI on Cosmere terminology and mechanics
- Update validation prompts for new rule system

### Manager Updates
- `CombatManager`: Adapt for Plot Die and new action economy
- `LevelUpManager` → `TalentManager`: Handle talent progression
- New `InvestitureManager`: Track and manage Investiture usage

### UI Adaptations
- Character sheet redesign for Cosmere stats
- Investiture tracking interface
- Talent tree visualization
- Plot Die rolling interface

## File Structure Changes

```
/workspace/
├── cosmere/                    # Cosmere-specific modules
│   ├── schemas/               # Cosmere game schemas
│   ├── rules/                 # Extracted PDF rules
│   ├── powers/                # Investiture abilities
│   └── managers/              # Cosmere-specific managers
├── data/
│   ├── cosmere_rules.json     # Parsed game rules
│   ├── investiture_powers.json # Power definitions
│   └── talents.json           # Talent trees
└── prompts/
    └── cosmere/               # Cosmere-specific AI prompts
```