# Cosmere RPG Digital Companion

A digital companion app for the Cosmere RPG that helps players learn the game, create characters, and manage their adventures in Brandon Sanderson's Cosmere universe.

## Features

### Core Functionality
- **Interactive Character Creation**: Step-by-step character builder with rule guidance
- **Character Management**: Track stats, talents, equipment, and Investiture
- **Rules Reference**: Integrated rule lookups with PDF page references
- **Learning Mode**: Interactive tutorials for new players
- **Digital Dice**: Plot Die system with special results handling

### Planned Features
- **Investiture Tracking**: Manage different magic systems (Allomancy, Feruchemy, etc.)
- **Combat Assistant**: Turn tracking and action management
- **Campaign Journal**: Track story progress and character development
- **Quick Reference**: Searchable rules database
- **Offline Support**: Full functionality without internet connection

## Getting Started

### Prerequisites
- Python 3.9+
- PDF files of Cosmere RPG rules (not included)

### Installation
```bash
# Clone the repository
git clone [your-repo-url]
cd cosmere-rpg-app

# Install dependencies
pip install -r requirements.txt

# Set up PDF processing (optional)
python cosmere/tools/setup_pdfs.py
```

### Configuration
1. Copy `config_template.py` to `config.py`
2. Configure your preferences
3. Add PDF files to `cosmere/pdfs/` (optional)

### Running the App
```bash
# Web interface (recommended)
python run_cosmere.py

# Terminal interface
python main_cosmere.py
```

## Project Structure
```
cosmere/
├── core/           # Core game mechanics
├── managers/       # System managers (character, combat, etc.)
├── schemas/        # Cosmere data schemas
├── rules/          # Extracted rule database
├── ui/             # User interface components
└── tools/          # Development tools
```

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License
[Your chosen license]

## Acknowledgments
- Based on NeverEndingQuest architecture
- Cosmere RPG by Brotherwise Games
- The Cosmere by Brandon Sanderson