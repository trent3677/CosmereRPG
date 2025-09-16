#!/usr/bin/env python3
"""
Cosmere RPG Digital Companion - Web Interface Launcher
"""

import os
import sys
import json
from pathlib import Path

# Add cosmere module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_socketio import SocketIO, emit
import logging

# Import Cosmere modules
from cosmere.core.character_manager import CosmereCharacterManager
from cosmere.core.dice_roller import DiceRoller
from cosmere.tools.rule_search import CosmereRuleSearch

# Initialize Flask app
app = Flask(__name__, 
           template_folder='cosmere/templates',
           static_folder='cosmere/static')
app.config['SECRET_KEY'] = 'cosmere-rpg-secret-key-change-in-production'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize managers
character_manager = CosmereCharacterManager()
dice_roller = DiceRoller()
rule_search = CosmereRuleSearch(rules_dir="cosmere/data/rules")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Routes
@app.route('/')
def index():
    """Main app page"""
    return render_template('index.html')

@app.route('/api/characters', methods=['GET', 'POST'])
def handle_characters():
    """Handle character operations"""
    if request.method == 'GET':
        # List all characters
        characters = character_manager.list_characters()
        return jsonify({"success": True, "characters": characters})
    
    elif request.method == 'POST':
        # Create new character
        try:
            character_data = request.json
            character = character_manager.create_character(character_data)
            return jsonify({"success": True, "character": character})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/characters/<character_id>', methods=['GET', 'PUT'])
def handle_character(character_id):
    """Handle individual character operations"""
    if request.method == 'GET':
        character = character_manager.load_character(character_id)
        if character:
            return jsonify({"success": True, "character": character})
        else:
            return jsonify({"success": False, "error": "Character not found"}), 404
    
    elif request.method == 'PUT':
        try:
            character = character_manager.load_character(character_id)
            if not character:
                return jsonify({"success": False, "error": "Character not found"}), 404
            
            # Update character with new data
            update_data = request.json
            character.update(update_data)
            character_manager.save_character(character)
            
            return jsonify({"success": True, "character": character})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/roll', methods=['POST'])
def handle_dice_roll():
    """Handle dice rolling requests"""
    try:
        roll_data = request.json
        roll_type = roll_data.get('type', 'skill')
        
        if roll_type == 'skill':
            result = dice_roller.roll_skill_check(
                skill_modifier=roll_data.get('modifier', 0),
                advantage=roll_data.get('advantage', False),
                disadvantage=roll_data.get('disadvantage', False),
                skilled=roll_data.get('skilled', False)
            )
        elif roll_type == 'damage':
            result = dice_roller.roll_damage(
                damage_dice=roll_data.get('dice', 1),
                bonus_damage=roll_data.get('bonus', 0)
            )
        elif roll_type == 'initiative':
            result = dice_roller.roll_initiative(
                awareness_modifier=roll_data.get('modifier', 0)
            )
        elif roll_type == 'contest':
            result = dice_roller.contest_roll(
                attacker_mod=roll_data.get('attacker_mod', 0),
                defender_mod=roll_data.get('defender_mod', 0),
                attacker_advantage=roll_data.get('attacker_advantage', False),
                defender_advantage=roll_data.get('defender_advantage', False)
            )
        else:
            return jsonify({"success": False, "error": "Unknown roll type"}), 400
        
        # Format the result for display
        formatted = dice_roller.format_roll_result(result)
        result['formatted'] = formatted
        
        # Emit to all connected clients
        socketio.emit('dice_rolled', result)
        
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/rules/search', methods=['GET'])
def handle_rule_search():
    """Search Cosmere rules extracted from PDFs"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({"success": False, "error": "Missing query"}), 400
        results = rule_search.search(query)
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# SocketIO events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Welcome to Cosmere RPG Digital Companion'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('update_hp')
def handle_update_hp(data):
    """Handle HP updates"""
    try:
        character_id = data.get('character_id')
        change = data.get('change', 0)
        
        character = character_manager.modify_hp(character_id, change)
        
        # Broadcast update to all clients
        socketio.emit('character_updated', {
            'character_id': character_id,
            'character': character
        })
        
        emit('hp_updated', {
            'success': True,
            'character': character
        })
    except Exception as e:
        emit('error', {'message': str(e)})

def create_app_structure():
    """Create necessary directories and files"""
    dirs_to_create = [
        'cosmere/templates',
        'cosmere/static/css',
        'cosmere/static/js',
        'cosmere/static/images',
        'cosmere/data/characters',
        'cosmere/data/rules'
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create basic index.html if it doesn't exist
    template_path = Path('cosmere/templates/index.html')
    if not template_path.exists():
        with open(template_path, 'w') as f:
            f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cosmere RPG Digital Companion</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
</head>
<body>
    <div id="app">
        <h1>Cosmere RPG Digital Companion</h1>
        <p>Welcome to your journey through the Cosmere!</p>
        
        <div id="character-section">
            <h2>Characters</h2>
            <button onclick="createNewCharacter()">Create New Character</button>
            <div id="character-list"></div>
        </div>
        
        <div id="dice-section">
            <h2>Dice Roller</h2>
            <button onclick="rollSkillCheck()">Roll Skill Check</button>
            <button onclick="rollDamage()">Roll Damage</button>
            <div id="dice-results"></div>
        </div>
    </div>
    
    <script src="/static/js/app.js"></script>
</body>
</html>''')
    
    # Create basic CSS
    css_path = Path('cosmere/static/css/style.css')
    if not css_path.exists():
        with open(css_path, 'w') as f:
            f.write('''/* Cosmere RPG Styles */
body {
    font-family: Arial, sans-serif;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f5f5f5;
}

h1 {
    color: #2c3e50;
    text-align: center;
}

#app {
    background-color: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

button {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
    margin: 5px;
}

button:hover {
    background-color: #2980b9;
}

#character-section, #dice-section {
    margin-top: 30px;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 5px;
}

#dice-results {
    margin-top: 20px;
    padding: 10px;
    background-color: #ecf0f1;
    border-radius: 5px;
    min-height: 50px;
}''')
    
    # Create basic JavaScript
    js_path = Path('cosmere/static/js/app.js')
    if not js_path.exists():
        with open(js_path, 'w') as f:
            f.write('''// Cosmere RPG App JavaScript
const socket = io();

socket.on('connect', function() {
    console.log('Connected to server');
});

socket.on('dice_rolled', function(data) {
    displayDiceResult(data);
});

function createNewCharacter() {
    // TODO: Implement character creation dialog
    alert('Character creation coming soon!');
}

function rollSkillCheck() {
    fetch('/api/roll', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            type: 'skill',
            modifier: 0
        })
    });
}

function rollDamage() {
    fetch('/api/roll', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            type: 'damage',
            dice: 2,
            bonus: 0
        })
    });
}

function displayDiceResult(result) {
    const resultsDiv = document.getElementById('dice-results');
    resultsDiv.innerHTML = '<strong>Latest Roll:</strong><br>' + result.formatted;
}

// Load characters on page load
window.onload = function() {
    loadCharacters();
};

function loadCharacters() {
    fetch('/api/characters')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayCharacters(data.characters);
            }
        });
}

function displayCharacters(characters) {
    const listDiv = document.getElementById('character-list');
    if (characters.length === 0) {
        listDiv.innerHTML = '<p>No characters yet. Create your first character!</p>';
    } else {
        listDiv.innerHTML = characters.map(char => 
            `<div class="character-card">
                <h3>${char.name}</h3>
                <p>${char.heritage} ${char.path} - Level ${char.level}</p>
            </div>`
        ).join('');
    }
}''')

if __name__ == '__main__':
    create_app_structure()
    
    print("🌟 Starting Cosmere RPG Digital Companion...")
    print("📍 Access the app at: http://localhost:8357")
    print("🎲 Ready to explore the Cosmere!")
    
    try:
        socketio.run(app, host='0.0.0.0', port=8357, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Cosmere RPG app...")
        sys.exit(0)