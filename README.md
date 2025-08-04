# NeverEndingQuest

**Version 0.1.0 (Alpha)**

An AI-powered Dungeon Master assistant for running 5th edition campaigns with infinite adventure potential. Built with innovative conversation compression and hub-and-spoke campaign architecture to overcome AI context limitations, enabling truly persistent worlds where every decision matters.

## Key Innovation: Overcoming AI Context Limitations

NeverEndingQuest solves the fundamental challenge of AI memory constraints through:
- **Intelligent Conversation Compression**: Automatically compresses gameplay into AI-generated chronicles
- **Hub-and-Spoke Campaign Architecture**: Modular adventures with persistent context across regions
- **Living World Memory**: NPCs remember your entire relationship history across thousands of interactions

## Table of Contents

- [Quick Start](#quick-start)
- [How It Overcomes AI Limitations](#how-it-overcomes-ai-limitations)
- [Installation](#installation)
- [Features Overview](#features-overview)
- [How It Works](#how-it-works)
- [Architecture & Design Philosophy](#architecture--design-philosophy)
- [Advanced Features](#advanced-features)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Community Module Safety](#community-module-safety)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [🎮 Playtesting Call to Action](#-playtesting-call-to-action)
- [Contributing](#contributing)
- [License](#license)
- [Recent Updates](#recent-updates)


## Quick Start

**Get playing in under 5 minutes!** The AI startup wizard handles everything automatically:

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Add your OpenAI API key**: Copy `config_template.py` to `config.py` and add your key
3. **Launch the game**: `python run_web.py` - opens the web interface in your browser
4. **Start your adventure**: The AI will guide you through character creation and module selection

> **Note**: While a console mode exists (`python main.py`), the game is designed for the **web interface** which provides the optimal experience with real-time updates, character sheets, and enhanced UI.

## 📄 **Licensing**

NeverEndingQuest is licensed under the **Fair Source License 1.0** with comprehensive protection for its innovative systems:

### 🔒 **Fair Source License (5-year term)**
The entire codebase including AI prompts, conversation compression, and all game systems are protected.
- ✅ **Free for personal, educational, and non-commercial use**
- ✅ **Community contributions welcome**  
- ✅ **Modify and customize freely for your campaigns**
- ❌ **Commercial competing use prohibited for 5 years**
- ⏰ **Becomes Apache 2.0 (fully open source) after 5 years**

### 📚 **D&D Content (CC-BY 4.0)**
Game mechanics use SRD 5.2.1 content from Wizards of the Coast.
- ✅ **SRD content used with proper attribution**
- ⚠️ **This is unofficial Fan Content**
- ℹ️ **Not affiliated with Wizards of the Coast**

See [LICENSING.md](LICENSING.md) for complete details, FAQ, and legal information.

The system automatically:
- Detects available adventure modules
- Selects appropriate starting locations
- Creates your character through AI interview
- Sets up the game world with weather and atmosphere

### Developer Playthroughs & Mechanics Guides
Learn advanced gameplay mechanics and creative problem-solving through these detailed module walkthroughs:
- [**The Thornwood Watch Developer Guide**](modules/The_Thornwood_Watch/PLAYER_GUIDE.md) - Master environmental spellcasting, NPC recruitment, stealth tactics, and non-violent boss solutions
- [**Keep of Doom Developer Guide**](modules/Keep_of_Doom/PLAYER_GUIDE.md) - Learn puzzle-solving, lore-based bypasses, tactical combat prioritization, and how to establish your own stronghold

These guides showcase the flexibility of the AI DM and demonstrate how observation, creativity, and strategic thinking lead to unique solutions beyond simple combat.

### The Adventure Continues: Automatic Module Creation
After completing both The Thornwood Watch and Keep of Doom, the game seamlessly continues through its innovative **AI-driven module generation system**. When players express interest in new adventures, the AI DM creates entirely new modules tailored to the party's level and interests.

**Example: The Birth of Shadows of Kharos**
Following the defeat of the cursed knight and establishment of a stronghold, our heroes found themselves in Harrow's Hollow's tavern. When talk turned to new adventures - specifically mentions of coastal mysteries and haunted lighthouses - the AI DM responded by procedurally generating an entirely new module: **Shadows of Kharos**.

The AI seamlessly wove this new adventure into the existing narrative, creating a level 4-6 coastal mystery featuring:
- The storm-wracked Isle of Kharos with its cursed lighthouse
- Three interconnected areas: Marrow's Rest village, the Abbey Ruins & Lighthouse, and the Drowned Catacombs  
- A compelling plot involving a missing abbess, undead mariners, and an ancient drowned king
- Full integration with the existing world, maintaining all character relationships and consequences

This demonstrates the system's ability to create infinite adventures - each module builds upon your previous accomplishments while introducing fresh challenges. The AI analyzes party composition, level, expressed interests, and past decisions to craft perfectly tailored experiences that feel like natural continuations of your epic journey.

## How It Overcomes AI Limitations

### The Context Window Challenge
Traditional AI systems have limited memory - typically 100-200k tokens. In a text-heavy RPG, this means:
- Conversations get truncated after a few hours of play
- NPCs "forget" your previous interactions
- Story continuity breaks between sessions
- Module transitions lose important context

### Our Solution: Intelligent Conversation Compression

NeverEndingQuest implements a sophisticated compression pipeline that maintains full contextual understanding:

#### 1. **Living Summary Generation**
- Each module generates a comprehensive living summary upon exit that captures the complete adventure
- AI analyzes the entire module conversation and creates beautifully written fantasy prose summaries
- Living summaries are completely regenerated (not appended) on each visit to incorporate new experiences
- Original events preserved in elevated narrative form while reducing tokens by 85-90%
- **Visit Evolution**: Summaries become richer and more detailed with each return visit
- **Single File System**: Always `[Module_Name]_summary_001.json` - never increments, always regenerates

#### 2. **Hub-and-Spoke Architecture with Module-Specific Conversations**
```
Module Structure:
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Thornwood   │────►│   Keep of   │────►│ Silver Vein │
│   Watch     │◄────│    Doom     │◄────│  Whispers   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                    │                    │
       └────────────────────┴────────────────────┘
                    Shared Context
                 (Character History)

Module Conversation Management:
┌─────────────────┐     ┌─────────────────┐
│ Current Module  │────►│ Module Archive  │
│ Conversation    │     │ (Auto-saved)    │
└─────────────────┘     └─────────────────┘
         ↓                       ↓
┌─────────────────┐     ┌─────────────────┐
│ New Module      │◄────│ Previous Conv.  │
│ (Fresh Start)   │     │ (Auto-restored) │
└─────────────────┘     └─────────────────┘
```

- Each module is a self-contained geographic region with its own conversation history
- **Module-Specific Conversations**: When leaving a module, conversations are archived and cleared
- **Automatic Restoration**: Returning to a module restores its specific conversation history
- **Prevents Infinite Buildup**: Each module maintains its own context bubble, preventing token explosion
- Return to any location with full memory of past events specific to that module

#### 3. **Living World Persistence with Smart Summary Management**
- **NPC Memory**: Characters remember your entire relationship history through living summaries
- **Decision Consequences**: Past choices affect future module availability
- **World State Tracking**: Completed quests permanently change the world
- **Cross-Module Continuity**: Items, relationships, and reputation carry forward
- **Living Summary System**: Each module maintains a single, evolving summary that updates with each visit
- **Visit Tracking**: System tracks `visitCount`, `firstVisitDate`, and `lastVisitDate` for each module
- **Smart Context Injection**: Previous module summaries are injected as campaign context, excluding the current module to prevent duplication

#### 4. **Module-Specific Conversation Management**
```
Active Module Conversation Structure:
┌─────────────────┐
│ System Prompts  │ (Base rules & character setup)
└────────┬────────┘
         ▼
┌─────────────────┐
│ Campaign Context│ (Living summaries from OTHER modules)
│ Living Summary  │ • Module 1 - visitCount: 3, complete history
│ Living Summary  │ • Module 2 - visitCount: 1, complete history  
│ (Current module │ • [Current module excluded to prevent duplication]
│  excluded)      │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Module-Specific │ (This module's conversation history)
│ Conversation    │ • Restored from archive (if returning)
│                 │ • Fresh start (if first visit)
│ "DM: You stand  │ • Full conversation context maintained
│  at the castle  │ • No token contamination from other modules
│  gates..."      │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Current Action  │ (What's happening right now)
└─────────────────┘

Module Transition & Living Summary Process:
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Module A Active │────►│ Archive & Update│────►│ Clear & Load    │
│ Conversation    │     │ Living Summary  │     │ Module B        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                        │
         ▼                       ▼                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Detect Module   │     │ Save to:        │     │ Module B Active │
│ Transition      │     │ • campaign_     │     │ Conversation    │
│ (via location   │     │   archives/     │     │ (Restored from  │
│  change)        │     │ • Update living │     │  archive or     │
│                 │     │   summary_001   │     │  fresh start)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘

Living Summary Evolution:
Visit 1: ┌─────────────────┐ → ┌─────────────────┐
         │ Fresh Module    │   │ Module_summary_ │
         │ Conversation    │   │ 001.json        │
         └─────────────────┘   │ visitCount: 1   │
                               │ Complete summary│
                               └─────────────────┘
                                       ↓
Visit 2: ┌─────────────────┐ → ┌─────────────────┐
         │ Return Visit    │   │ Module_summary_ │
         │ + New Adventures│   │ 001.json        │
         └─────────────────┘   │ visitCount: 2   │
                               │ REGENERATED     │
                               │ Enhanced summary│
                               └─────────────────┘

Combat Isolation (unchanged):
┌─────────────────┐     ┌─────────────────┐
│ Main Timeline   │────►│ Combat Instance │
│                 │     │ (Isolated)      │
│ "Roll for       │     │ ┌─────────────┐ │
│  initiative..." │     │ │Combat Prompt│ │
│                 │     │ └──────┬──────┘ │
│                 │     │        ▼        │
│                 │◄────│ ┌─────────────┐ │
│ "Victory!"      │     │ │ Turn-by-Turn│ │
└─────────────────┘     │ │ Resolution  │ │
                        │ └──────┬──────┘ │
                        │        ▼        │
                        │ ┌─────────────┐ │
                        │ │  Summary    │ │
                        │ └─────────────┘ │
                        └─────────────────┘
```

- **Module-Specific Conversations**: Each module maintains its own conversation bubble, preventing token explosion across adventures
- **Living Summary Evolution**: Single `_summary_001.json` per module regenerated completely on each visit with enhanced context
- **Automatic Archive/Restore**: Module conversations saved to `campaign_archives/` on exit, restored on return
- **Smart Context Injection**: Campaign summaries from OTHER modules injected as context (current module excluded)
- **Visit Tracking**: Each summary tracks `visitCount`, `firstVisitDate`, and `lastVisitDate` for rich progression metadata
- **Combat Isolation**: Each combat runs in its own context bubble, then returns a summary
- **Token Efficiency**: Module separation prevents infinite context growth while maintaining complete adventure history
- **Zero Context Contamination**: Visiting other modules briefly doesn't permanently expand your main adventure's context
- **Complete History Preservation**: Full conversation context restored when returning to any previously visited module

### Real-World Example
```
FIRST VISIT TO THORNWOOD WATCH:
Session 1-5: 50,000 tokens of gameplay in Thornwood Watch
    ↓ (Module Exit - Travel to Keep of Doom)
Archive Process:
• Full conversation → campaign_archives/Thornwood_Watch_conversation_001.json
• Living Summary → campaign_summaries/Thornwood_Watch_summary_001.json
  - visitCount: 1, firstVisitDate: 2024-01-15
  - Complete adventure summary (5,000 tokens)
• Clear conversation history (ready for new module)

KEEP OF DOOM MODULE:
• Fresh conversation context (0 tokens to start)
• Campaign context injected: Thornwood Watch summary (5,000 tokens)
• Session 6-10: New adventures without Thornwood's 50k tokens
    ↓ (Return to Thornwood Watch after 6 months)

RETURN VISIT TO THORNWOOD WATCH:
Archive Restoration:
• Load: Thornwood_Watch_conversation_001.json (full 50k token history restored)
• Campaign context: Keep of Doom summary (excludes current Thornwood summary)
• Session continues exactly where it left off with full NPC memory
    ↓ (Exit after new adventures)
Living Summary Update:
• REGENERATE Thornwood_Watch_summary_001.json (not append!)
  - visitCount: 2, lastVisitDate: 2024-07-20
  - Enhanced summary incorporating both visits (6,000 tokens)

Result: Each module maintains complete history while preventing token explosion
Total per module: ~10,000 tokens (not 150,000+ from all adventures combined!)
```

### Module Transition System Details

The enhanced module transition system ensures optimal performance and narrative continuity:

#### 5-Step Transition Process
1. **Immediate Detection**: Module changes detected instantly when `updatePartyTracker` changes current module
2. **Archive & Summarize**: Current conversation archived to `campaign_archives/[Module_Name]_conversation_[sequence].json` and living summary regenerated in `campaign_summaries/[Module_Name]_summary_001.json`
3. **Clear Conversation**: Current conversation history cleared to prevent token buildup
4. **Restore Destination**: Load archived conversation for destination module (if returning) or start fresh (if first visit)
5. **Inject Campaign Context**: Inject living summaries from OTHER modules as campaign context (current module excluded)

#### Module-Specific Conversation Management
Each module maintains its own "conversation bubble" that:
- **Prevents Token Explosion**: Brief visits don't permanently add to main conversation
- **Enables Quick Transitions**: Visit a shop in another module without context penalty
- **Maintains Narrative Focus**: Each adventure keeps its own story thread
- **Restores Completely**: Full conversation returns when you revisit

#### Living Summary System
- **Single File Per Module**: `[Module_Name]_summary_001.json` (always _001, never increments)
- **Complete Regeneration**: Entire summary recreated fresh on each module exit
- **Visit Metadata**: Tracks `visitCount`, `firstVisitDate`, `lastVisitDate`
- **Rich Context**: Full adventure narrative available for other modules to reference

Example Living Summary Evolution:
```json
// After First Visit (visitCount: 1)
{
  "module_name": "Thornwood_Watch",
  "visitCount": 1,
  "firstVisitDate": "2024-01-15",
  "lastVisitDate": "2024-01-15",
  "summary": "The party arrived at Rangers' Outpost and successfully defended it from bandit attacks. They formed strong relationships with Captain Thorne and the local rangers, securing the trade routes and establishing themselves as protectors of the Thornwood region."
}

// After Return Visit (visitCount: 2) - COMPLETELY REGENERATED
{
  "module_name": "Thornwood_Watch", 
  "visitCount": 2,
  "firstVisitDate": "2024-01-15",
  "lastVisitDate": "2024-07-20",
  "summary": "FIRST EXPEDITION: The party arrived as unknown adventurers and defended Rangers' Outpost from bandit attacks, earning the trust of Captain Thorne and establishing themselves as protectors of the region.\n\nRETURN AS HEROES: Six months later, the party returned as renowned heroes. The outpost had flourished under their protection, with new recruits and expanded defenses. Captain Thorne welcomed them warmly, and the party discovered new threats emerging from deeper in the Thornwood, leading to advanced adventures involving ancient druidic mysteries and corrupted forest spirits."
}
```

### Benefits
- **Truly Infinite Campaigns**: Play for hundreds of hours without context loss across multiple adventures
- **Persistent Relationships**: NPCs remember you after months of real-time play through living summaries
- **Coherent Storytelling**: Every adventure builds on previous experiences with complete cross-module continuity
- **Zero Context Contamination**: Each module maintains its own conversation bubble, preventing token explosion
- **Seamless Module Returns**: Full conversation history restored when revisiting any module
- **Living World Evolution**: Summaries grow richer with each visit, tracking your expanding impact
- **Optimized Performance**: Module separation prevents infinite context growth while preserving complete history
- **Smart Context Management**: Campaign summaries provide relevant background without duplication
- **Visit Progression Tracking**: Rich metadata shows your journey across the world over time
- **Reduced API Costs**: Efficient token management through intelligent conversation separation

## Installation

### Prerequisites
- Python 3.9 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Windows, macOS, or Linux

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/MoonlightByte/NeverEndingQuest.git
   cd NeverEndingQuest
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure OpenAI API**
   ```bash
   cp config_template.py config.py
   # Edit config.py and add your OpenAI API key
   ```

4. **Start playing**
   ```bash
   # Terminal interface
   python main.py
   
   # Web interface (recommended)
   python run_web.py
   ```

### Verify Installation
Run `python main.py` - you should see the AI startup wizard begin character creation.

## Features Overview

### Context Management Innovations
- **[Conversation Compression](#intelligent-conversation-compression)**: Overcomes AI token limits with 85-90% compression
- **[Hub-and-Spoke Design](#hub-and-spoke-architecture)**: Modular adventures with persistent shared context
- **[Living World Memory](#living-world-persistence)**: NPCs and locations remember everything
- **[Chronicle System](#chronicle-generation)**: Beautiful AI-generated summaries preserve your adventures

### Core Gameplay
- **[AI Dungeon Master](#ai-dungeon-master)**: Complete 5e campaign management with intelligent storytelling
- **[Character System](#character-management)**: Full character creation, progression, and inventory management
- **[Combat System](#combat-system)**: Turn-based combat with AI tactical decisions
- **[Module System](#module-system)**: Self-contained adventures with seamless transitions

### Advanced Features  
- **[NPC Party Recruitment](#npc-party-recruitment-system)**: Ask any NPC to join your party with realistic AI evaluation
- **[Player Housing & Storage](#player-housing--hub-system)**: Establish bases and store items across the world
- **[Module Generation](#module-generation--management)**: AI creates new adventures based on your choices
- **[Community Modules](#community-module-safety)**: Download and integrate player-created content safely

### Technical Features
- **Web Interface**: Modern browser-based interface with separate panels
- **Save System**: Automatic progress saving with backup protection
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Schema Validation**: All game files follow strict 5e schemas for consistency

## How It Works

NeverEndingQuest provides a complete solo D&D experience with persistent world memory that grows with your adventures. Through intelligent conversation compression and modular design, the system maintains a "lived-in" contextual understanding where every NPC remembers you, every decision has consequences, and the world evolves based on your actions.

**Design Philosophy**: The AI is intentionally flexible - you can convince it, negotiate with it, or play creatively. The software provides structure for consistent gameplay while maintaining the creative freedom that makes RPGs magical.

### What Makes It Special

#### **Lived-In Contextual Understanding**
Unlike traditional AI systems that "forget" after a few interactions, NeverEndingQuest creates a truly persistent world:

- **Relationship Memory**: That shopkeeper you helped in session 1? They'll remember and offer discounts 50 sessions later
- **Consequence Persistence**: Saving a village affects trade routes, NPC attitudes, and available quests across all modules
- **World Evolution**: Completed adventures permanently change the world state - defeated villains stay defeated
- **Character Growth**: NPCs reference shared experiences, inside jokes, and memorable moments from your entire journey

#### **How Context Accumulates**
```
First Visit to Thornwood (5 hours play) → 30,000 tokens
  ↓ Module Completion
Chronicle Summary → 3,000 tokens

Return Visit Six Months Later:
- Full chronicle loaded
- NPCs remember everything
- World shows your impact
- New adventures build on history
Total Context: 8,000 tokens (not 60,000!)
```

This creates a living world where:
- **Bartender**: "Hey, aren't you the one who saved us from those bandits last spring?"
- **Guard Captain**: "After what you did for Thornwood, you're always welcome here."
- **Merchant**: "I've expanded my shop thanks to the trade routes you secured!"
- **Quest Giver**: "Since you dealt with the corruption, new problems have emerged..."

### Available Adventure Modules

The system includes progressive adventures, both pre-built and dynamically generated:

**Pre-Built Modules:**
- **The Thornwood Watch** (Level 1-2): Starting adventure defending Rangers' Outpost
- **Keep of Doom** (Level 3-5): Intermediate adventure in Harrow's Hollow  

**AI-Generated Modules:**
- **Shadows of Kharos** (Level 4-6): Coastal mystery on a haunted island (generated based on player interest)
- Additional modules created dynamically as your adventure continues

### Creating New Adventures

Generate complete modules with:
```bash
python core/generators/module_builder.py
```
The AI helps create areas, locations, plots, and NPCs that integrate seamlessly with your existing world.

## Architecture & Design Philosophy

For a deep dive into how NeverEndingQuest works under the hood, including:
- The conversation compression pipeline that enables infinite adventures
- How the modular system maintains story continuity
- Context management strategies for AI memory
- Technical implementation details

See the comprehensive [Architecture Documentation](ARCHITECTURE.md).

## How the Campaign World Works

### Location-Based Module System
The game uses a revolutionary **geographic boundary system** instead of traditional campaign chapters:

- **Modules as Geographic Regions**: Each adventure module represents a geographic area network (village + forest + dungeon)
- **Organic World Growth**: The world map expands naturally as you add new modules - no predetermined geography needed
- **Automatic Transitions**: When you travel to a new area, the system automatically detects if you're entering a different module
- **Living World Memory**: Every location remembers your visits and the world evolves based on accumulated decisions

### How Modules Connect
```
Example World Evolution:
Keep_of_Doom: Harrow's Hollow (village) → Gloamwood (forest) → Shadowfall Keep (ruins)
+ Crystal_Peaks: Frostspire Village (mountain town) → Ice Caverns (frozen depths)
= AI Connection: "Mountain paths from Harrow's Hollow lead to Frostspire Village"
```

The AI analyzes area descriptions and themes to suggest natural narrative bridges between modules.

### Adventure Continuity
- **Chronicle System**: When you leave a module, the system generates a beautiful prose summary of your adventure
- **Context Accumulation**: Return visits include full history of previous adventures in that region
- **Character Relationships**: NPCs remember you across modules and adventures continue to evolve
- **Consequence Tracking**: Major decisions affect future adventures and available story paths

### 🌍 Community Module Compatibility

**Maximum compatibility with community content!** The system is designed for seamless integration:

- **Universal Module Support**: Any properly formatted module works automatically - no configuration needed
- **Intelligent Conflict Resolution**: Automatically resolves duplicate area IDs, location conflicts, and naming collisions
- **Safety Validation**: Multi-layer content review ensures family-friendly and schema-compliant modules
- **AI Auto-Integration**: Analyzes module themes and generates natural narrative connections to your world
- **Level-Based Discovery**: New modules appear in progression based on your character's advancement
- **Plug-and-Play**: Simply drop modules in the `modules/` directory and they integrate on next startup

### Module Creation & Sharing
- **Module Builder**: Create new adventure modules with integrated areas, plots, and NPCs
- **AI-Assisted Creation**: AI helps generate cohesive module content that integrates seamlessly
- **Community Standards**: Built-in validation ensures your modules work perfectly for other players
- **Organic Integration**: New modules connect naturally to existing worlds without manual configuration

## Key Features

### Context Management System
- **Conversation Compression Pipeline**: Reduces gameplay sessions by 85-90% while preserving all story elements
- **Chronicle Generation**: AI transforms thousands of messages into beautiful fantasy prose summaries
- **Hub-and-Spoke Architecture**: Isolated modules share persistent character context and world state
- **Living World Memory**: Complete NPC relationship history and consequence tracking across all adventures
- **Automatic Compression Triggers**: Manages token limits seamlessly (12 transitions trigger, 6 compressed)

### Module Generation & Management
- **Complete Module Builder**: Generate entire adventure modules with areas, locations, plots, and NPCs
- **Context-Aware Generation**: Maintains consistency across all generated content
- **Schema Compliance**: All files follow strict 5th edition JSON schemas
- **Community Module Support**: Framework for sharing and auto-integrating downloaded adventures
- **Safety Validation**: Automatic content review and conflict resolution for community modules
- **AI Autonomous Creation**: When current adventures conclude, AI analyzes party history to craft new contextual modules
- **Narrative-Driven Generation**: AI parses rich narrative descriptions to extract module parameters automatically

### Gameplay Features
- **Interactive Storytelling**: Dynamic narratives respond to accumulated player decisions across modules
- **Combat System**: Turn-based combat with validation and AI simulation
- **Character Management**: Unified character system supporting players, NPCs, and monsters
- **World Exploration**: Navigate detailed locations with dynamic state and cross-module connections
- **Plot Management**: Authoritative module_plot.json tracks main quests, side quests, and progression
- **NPC System**: Persistent NPCs with personalities, goals, cross-module relationship tracking, and **party recruitment**
- **Time Tracking**: Complete world time and condition management with realistic progression

### Advanced Player Systems

#### **🏠 Player Housing & Hub System**
- **Establish Hubs**: Transform any location into a permanent base of operations
- **Hub Services**: Rest, storage, gathering, training, research facilities automatically available
- **Ownership Types**: Party-owned, shared arrangements, or individual strongholds
- **Hub Persistence**: Return from any adventure to your established bases
- **Multi-Hub Support**: Maintain multiple bases across different regions and modules

**Hub Types Available:**
- **Strongholds**: Fortified keeps and castles for defensive operations
- **Settlements**: Villages and towns for commerce and community building
- **Taverns**: Social hubs for information gathering and party meetings
- **Specialized Facilities**: Wizard towers, temples, guildhalls with unique services

#### **📦 Player Storage System**
- **Natural Language Storage**: Use intuitive commands like "I store my gold in a chest here"
- **Location-Based Containers**: Create storage at any location using available containers
- **Persistent Storage**: Items remain safely stored across sessions and module transitions
- **Party Accessibility**: All party members can access shared storage by default
- **Automatic Inventory Management**: System handles all inventory transfers with full safety protocols

**Storage Features:**
- **Container Types**: Chests, lockboxes, barrels, crates, strongboxes
- **Smart Organization**: AI helps organize items by type and importance
- **Secure Storage**: Containers tied to specific locations for security
- **Visual Integration**: Storage automatically appears in location descriptions

#### **👥 NPC Party Recruitment System**

**Build your party by recruiting NPCs you meet during your adventures!**

- **Ask Anyone**: Approach any NPC and ask them to join your party
- **AI Evaluation**: The AI considers the NPC's personality, goals, current situation, and relationship with you
- **Natural Roleplay**: Use persuasion, offer payment, complete quests, or appeal to their motivations
- **Persistent Companions**: Recruited NPCs travel with you across modules and remember shared experiences
- **Dynamic Relationships**: Party NPCs develop bonds with each other and react to your decisions
- **Full Character Sheets**: NPCs become full party members with stats, equipment, and progression

**Recruitment Examples:**
- *"Who can you spare to help us?"* → Scout volunteers and AI evaluates if they can leave their duties
- *"Mira, would you like to join us? We could use a skilled healer on our journey."* → AI considers her personality and current situation
- *"Gareth, we're heading to dangerous lands. Your sword arm would be welcome."* → AI weighs his courage against his responsibilities
- *"Can anyone help with this mission?"* → Multiple NPCs may volunteer, but only appropriate ones will actually join

**NPC Party Features:**
- **Smart Recruitment**: NPCs evaluate your requests based on their personality, duties, and relationship with you
- **Realistic Responses**: Some NPCs may decline if they can't leave their post or don't trust you yet
- **Natural Conversation**: Ask for help, and NPCs will respond in character - no special commands needed
- **Combat Participation**: NPCs fight alongside you with full AI tactical decisions
- **Skill Contributions**: NPCs use their unique abilities to solve problems and overcome challenges
- **Story Integration**: Party NPCs contribute to roleplay and have their own character arcs
- **Cross-Module Continuity**: Your companions remember adventures across different modules
- **Character Development**: NPCs grow and change based on shared experiences

#### **🎲 AI-Driven Module Auto-Generation**
- **Contextual Adventures**: AI analyzes party history to create personalized modules
- **Seamless Integration**: New modules connect naturally to existing world geography
- **Dynamic Scaling**: Adventures adjust to party level and accumulated experience
- **Narrative Continuity**: References previous adventures and established relationships

**Auto-Generation Triggers:**
- **Adventure Completion**: New modules generated when current adventures conclude
- **Player Interest**: AI detects story hooks and creates relevant content
- **World Events**: Major decisions trigger consequences in new regions
- **Party Progression**: Level advancement unlocks higher-tier adventure options

#### **🌍 Living Campaign World Integration**
- **Isolated Module Architecture**: Each module operates independently while maintaining world coherence
- **AI Travel Narration**: Seamless transitions between modules with atmospheric descriptions
- **World Registry**: Central tracking of all modules, areas, and their relationships
- **Cross-Module Consequences**: Actions in one module affect opportunities in others

## Project Structure

**Note: The codebase has been reorganized for better maintainability. All core functionality is now organized into logical directories.**

### 📁 Directory Organization
```
/
├── core/                    # Core game engine modules
│   ├── ai/                 # AI integration (action_handler, dm_wrapper, etc.)
│   ├── generators/         # Content generation (module_builder, npc_builder, etc.)
│   ├── managers/           # System management (combat_manager, storage_manager, etc.)
│   └── validation/         # Data validation systems
├── utils/                  # Utility functions and helpers
├── updates/               # State update modules
├── web/                   # Web interface
├── modules/               # Adventure modules and game data
│   ├── conversation_history/  # All conversation files
│   ├── campaign_archives/     # Archived module conversations
│   ├── campaign_summaries/    # Living AI-generated summaries
│   └── [module_name]/        # Individual adventure modules
├── prompts/               # AI system prompts
├── schemas/               # JSON validation schemas
└── data/                  # Game data files
```

### Core Systems
- `main.py` - Main game loop and player interaction
- `core/generators/module_builder.py` - Automated module generation system
- `core/generators/module_stitcher.py` - Organic module integration
- `core/managers/campaign_manager.py` - Hub-and-spoke campaign orchestration
- `core/managers/combat_manager.py` - Combat system management
- `core/ai/dm_wrapper.py` - AI Dungeon Master logic

### Content Generation
- `core/generators/module_generator.py` - Module overview generation
- `core/generators/area_generator.py` - Area and map generation
- `core/generators/location_generator.py` - Detailed location generation
- `core/generators/plot_generator.py` - Plot and quest generation
- `core/generators/npc_builder.py` - NPC generation system
- `core/generators/monster_builder.py` - Monster creation tools

### Game Management
- `core/ai/conversation_utils.py` - Conversation tracking
- `core/managers/storage_manager.py` - Player storage system
- `core/ai/action_handler.py` - Command processing
- `utils/player_stats.py` - Character statistics
- `updates/` - Various state update modules

### Data Files
- `schemas/*_schema.json` - JSON schemas for validation
- `modules/conversation_history/` - Conversation history files
- `modules/` - Generated module data
- `*.json` - Character, location, and game state files
- `player_storage.json` - Central player storage repository
- `storage_action_schema.json` - Storage operation validation schema

## Configuration

The system uses OpenAI GPT models configured in `config.py`:

- `DM_MAIN_MODEL` - Primary model for narration and generation
- `DM_SUMMARIZATION_MODEL` - Conversation and event summarization
- `DM_VALIDATION_MODEL` - Combat and rule validation
- `DM_COMBAT_NARRATOR_MODEL` - Combat narration and description
- Various other specialized models for different tasks

## Requirements

- Python 3.9+
- OpenAI API key
- Required packages listed in `requirements.txt`

## Community Module Safety

The module stitcher includes comprehensive safety protocols for community-created content:

### Automatic Safety Validation
- **Content Review**: AI analyzes all module content for family-friendly appropriateness
- **File Security**: Blocks executable files, oversized content, and malicious patterns
- **Schema Compliance**: Validates JSON structure against 5th edition schemas
- **ID Conflict Resolution**: Automatically resolves duplicate area/location identifiers

### How It Works
```
New module detected → Security scan → Content safety check → Schema validation → Conflict resolution → Integration
```

### For Module Creators
- Use unique area IDs to avoid conflicts (avoid common patterns like HH001)
- Keep files under 10MB and use only JSON/text formats
- Create family-friendly content appropriate for all ages
- Follow provided JSON schemas for compatibility

### For Players
- Download modules from trusted sources
- System provides multiple safety layers automatically
- All community modules undergo validation before integration
- Backup saves before adding new modules as good practice

## Usage Examples

### Generate a Module
```bash
python core/generators/module_builder.py
# Follow prompts to create areas, locations, plots, and NPCs
# System ensures consistency and schema compliance
```

### Start Playing
```bash
python main.py
# System automatically detects and integrates any new modules
# Begin adventure in your generated or downloaded module
```

### Add Community Modules
```bash
# Simply place module folder in modules/ directory
# System automatically detects, validates, and integrates on next startup
# AI generates narrative connections to existing world
```

### Player Housing & Storage Examples

#### **Establish a Hub**
```
Player: "I want to claim this keep as our base of operations"
AI: *Establishes Shadowfall Keep as a party stronghold with full services*
```

#### **Natural Language Storage**
```
Player: "I store my extra gold in a chest in the treasury"
AI: *Creates storage container and transfers 500 gold coins*

Player: "What's in our storage here?"
AI: *Lists all containers and contents at current location*

Player: "I get my healing potions from the chest we made"
AI: *Retrieves potions and updates inventory automatically*
```

#### **NPC Party Recruitment**
```
Player: "Elara, you've helped us so much. Would you consider joining our party?"
AI: *Elara considers your shared adventures and her own goals*
AI: "I've grown fond of you all, and these dark times require brave souls to stand together. Yes, I'll join you."
*Elara is added to your party with full character sheet and equipment*

Player: "Marcus, we're heading to the Shadowlands. Your knowledge of undead could save lives."
AI: *Marcus weighs the danger against his scholarly interests*
AI: "The chance to study the necromantic energies there... yes, I'll come. But I'm not much of a fighter."
*Marcus joins as a support character with unique magical knowledge*
```

#### **Hub Services**
```
Player: "I want to rest at our stronghold"
AI: *Provides full rest benefits and hub-specific services*

Player: "Let's gather at the tavern we established"
AI: *Transitions party to hub location with full context*
```

### AI Module Generation Examples

#### **Contextual Adventure Creation**
```
AI: *Analyzes party completed Keep_of_Doom module*
AI: *Detects themes: undead, curses, heroic rescue*
AI: *Generates "Whispers of the Shadowlands" - related but escalated adventure*
```

#### **Dynamic World Building**
```
Player: "We've heard rumors of trouble in the northern mountains"
AI: *Creates mountain-themed module tied to established lore*
AI: *Connects via travel narration from current location*
```

#### **AI Flexibility Examples**

**The AI adapts to your playstyle - strict or creative, it's your choice:**

```
Player: "I try to convince the shopkeeper that I'm nobility and deserve a discount"
AI: *Evaluates your charisma, background, and story context*
AI: "The shopkeeper seems skeptical but your confident bearing impresses them. 10% discount!"

Player: "I search the dragon's lair thoroughly for any hidden treasure"
AI: "Roll a perception check... Natural 20! You notice loose stones hiding a secret compartment with an ancient artifact."

Player: "This quest is taking forever. Can we just say we completed it?"
AI: "I understand you want to move the story along. Let's fast-forward through the completion and focus on the interesting parts!"

Player: "I want that legendary sword the NPC mentioned. Can I convince them to give it to me?"
AI: *Considers story logic, your relationship, and what would be interesting*
AI: "It won't be easy, but if you can prove yourself worthy through a specific quest, they might consider it..."
```

**Remember: The AI wants you to have fun! It provides structure for consistency but adapts to your preferred style of play.**

## Troubleshooting

### Common Issues

#### Installation Problems
- **"Module not found" errors**: Ensure you've installed requirements with `pip install -r requirements.txt`
- **OpenAI API errors**: Verify your API key is correct in `config.py` and has sufficient credits
- **Python version**: Requires Python 3.9+ - check with `python --version`

#### Game Startup Issues
- **No modules found**: Ensure the `modules/` directory exists with adventure modules
- **Character creation fails**: Check that you have a valid OpenAI API key and internet connection
- **Web interface won't start**: Try `python -m http.server` to test basic Python web functionality

#### Performance Issues
- **Slow AI responses**: This is normal - AI processing takes 10-30 seconds per response
- **Memory usage**: Large conversation histories use more memory - restart periodically for long sessions
- **File corruption**: The system creates automatic backups - check for `.backup` files if needed

#### Windows-Specific
- **Unicode errors**: Windows console has encoding limitations - use the web interface for best experience
- **Path issues**: Use forward slashes or raw strings for file paths
- **Permission errors**: Run as administrator if experiencing file access issues

### Getting Help
- Check the [GitHub Issues](https://github.com/MoonlightByte/NeverEndingQuest/issues) for known problems
- Create a new issue with your error message and system information
- Include your Python version and operating system in bug reports

## 🎮 Playtesting Call to Action

**We need YOUR help testing different character classes!**

### Current Testing Status
- ✅ **Fighter** - Well-tested, combat mechanics working smoothly
- ✅ **Cleric** - Extensively tested, spellcasting and healing validated
- 🔶 **Rogue** - *Needs testing*: Sneak attack, stealth mechanics, skill checks
- 🔶 **Wizard** - *Needs testing*: Spell slot management, ritual casting, spell preparation
- 🔶 **Druid** - *Needs testing*: Wild shape, nature spells, concentration mechanics
- 🔶 **Barbarian** - *Needs testing*: Rage mechanics, damage resistance
- 🔶 **Ranger** - *Needs testing*: Favored enemy, tracking, dual wielding
- 🔶 **Warlock** - *Needs testing*: Pact magic, invocations, short rest recovery
- 🔶 **Monk** - *Needs testing*: Ki points, martial arts, stunning strike
- 🔶 **Paladin** - *Needs testing*: Divine smite, lay on hands, auras
- 🔶 **Sorcerer** - *Needs testing*: Metamagic, sorcery points, wild magic
- 🔶 **Bard** - *Needs testing*: Bardic inspiration, jack of all trades

### How You Can Help
1. **Create a character** using one of the untested classes
2. **Play through at least one combat encounter** to test class abilities
3. **Report issues** with class features, spell casting, or special abilities
4. **Share feedback** on the game flow and AI responses for your class

### What We're Looking For
- **Combat Mechanics**: Do class abilities trigger correctly?
- **Resource Management**: Are spell slots, ki points, rage uses tracked properly?
- **AI Understanding**: Does the DM correctly interpret and apply class features?
- **Balance**: Does combat feel appropriately challenging for your class?
- **Edge Cases**: Any weird interactions or bugs with specific abilities?

### How to Report Feedback
Create an issue on GitHub with:
- Your character class and level
- Description of what didn't work as expected
- Steps to reproduce the issue
- Screenshots or combat logs if available

**Your playtesting helps make NeverEndingQuest better for everyone!** 🎲

## Contributing

We welcome contributions to NeverEndingQuest! This project thrives on community involvement.

### How to Contribute

#### For Developers
1. **Fork the repository** and create a feature branch
2. **Follow the code style** established in existing files
3. **Test your changes** thoroughly before submitting
4. **Update documentation** for any new features
5. **Submit a pull request** with a clear description of changes

#### For Content Creators
- **Create adventure modules** using the module builder
- **Share your modules** with the community
- **Report balance issues** or suggest improvements
- **Write documentation** or tutorials

#### For Players
- **Report bugs** with detailed reproduction steps
- **Suggest features** based on your gameplay experience
- **Share feedback** on game balance and AI behavior
- **Help new players** in discussions

### Development Setup
```bash
# Fork and clone your fork
git clone https://github.com/yourusername/NeverEndingQuest.git
cd NeverEndingQuest

# Create development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8  # Add linting tools

# Run tests
python -m pytest

# Format code
black .
```

### Contribution Guidelines
- **Code Style**: Follow existing patterns and use meaningful variable names
- **Documentation**: Update README and docstrings for new features
- **Testing**: Add tests for new functionality when possible
- **Compatibility**: Ensure changes work across Windows, macOS, and Linux
- **Licensing**: All contributions will be under Fair Source License 1.0 (transitioning to Apache 2.0 after 5 years)

### Areas Needing Help
- **Web interface improvements** - Better UI/UX design
- **Performance optimization** - Faster AI response times
- **Module creation tools** - Better module builder interface
- **Documentation** - More tutorials and examples
- **Testing** - Automated test coverage
- **Platform support** - Mobile interfaces, voice integration

## License

NeverEndingQuest is licensed under the Fair Source License 1.0 with a 5-year transition to Apache 2.0.
See the LICENSE and LICENSING.md files for complete details.

### Fair Source License Summary
- ✅ **Free for personal, educational, and non-commercial use**
- ✅ **Modify and customize for your campaigns**
- ❌ **Cannot create competing commercial services**
- ⏰ **Becomes fully open source (Apache 2.0) after 5 years**

### SRD Attribution

Game mechanics and content are derived from the System Reference Document 5.2.1 ("SRD 5.2.1") 
by Wizards of the Coast LLC and available at https://dnd.wizards.com/resources/systems-reference-document. 

The SRD 5.2.1 is licensed under the Creative Commons Attribution 4.0 International License 
available at https://creativecommons.org/licenses/by/4.0/legalcode.

This work is not affiliated with, endorsed, sponsored, or specifically approved by 
Wizards of the Coast LLC. This is unofficial Fan Content permitted under the 
Creative Commons Attribution 4.0 International License and the Fair Source License.

## Recent Updates

### Major Features Added
- **AI-Powered Startup Wizard**: Automatic module detection, level-based selection, and AI reasoning for optimal starting locations
- **NPC Party Recruitment**: Ask any NPC to join your party with AI evaluation and persistent companions
- **Hub & Housing System**: Transform any location into a permanent base with full services
- **Player Storage System**: Complete natural language storage with atomic file protection
- **Module Level Progression**: Intelligent 1-2 → 3-5 → 6-8 level-based adventure flow
- **Community Module Compatibility**: Universal module support with automatic conflict resolution
- **AI Auto-Generation**: Contextual module creation based on party history and preferences
- **Isolated Module Architecture**: Clean module separation with AI travel narration

### Technical Improvements
- **Enhanced Module Stitcher**: Fixed areas/ subdirectory scanning with automatic ID conflict resolution
- **Centralized AI Configuration**: Removed all hardcoded GPT models, now uses config.py for consistency
- **Startup Wizard Architecture**: Complete rewrite with proper error handling and Windows compatibility
- **Module Path Management**: Implemented `ModulePathManager` for centralized file path handling
- **Combat System Fixes**: Fixed monster file loading in combat to use module directories
- **Directory Structure**: All module-specific files now stored in organized module folders
- **Legacy Cleanup**: Moved old files to legacy folder, cleaning up root directory
- **Validation System**: Relaxed combat validation to focus on major errors only
- **Equipment Syncing**: Verified arrow transfer sync between character files

### Conversation Compression Improvements (v1.5)
- **Module-Specific Conversation History**: Each module maintains separate conversation context to prevent infinite buildup
- **Living Summary System**: Single, continuously updated summary per module instead of sequential files
- **Smart Context Injection**: Campaign summaries exclude current module to prevent duplication
- **Automatic Archive/Restore**: Module conversations archived on exit, restored on return
- **Visit Tracking**: Added metadata tracking for module visits (count, first/last visit dates)
- **Improved Transition Detection**: Module changes detected immediately via `updatePartyTracker`
- **Campaign Archive Structure**: Organized storage in `campaign_archives/` and `campaign_summaries/`

### Safety & Protection
- **Atomic File Operations**: Backup/restore functionality prevents data corruption
- **Schema Validation**: All operations validated against JSON schemas
- **Context Contamination Prevention**: AI prompts prevent module creation conflicts
- **Character File Protection**: Inventory changes safely backed up before modification

## Future Development

- Web interface for easier interaction
- Voice integration for immersive gameplay
- Image generation for scenes and characters
- Additional ruleset support (Pathfinder, etc.)
- Multi-player support
- Campaign sharing and templates

---

*Created by MoonlightByte*
*Contributors: Claude AI Assistant*
