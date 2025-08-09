# SPDX-FileCopyrightText: 2024 MoonlightByte
# SPDX-License-Identifier: Fair-Source-1.0
# License: See LICENSE file in the repository root
# This software is subject to the terms of the Fair Source License.

"""
NeverEndingQuest Core Engine - Web Interface
Copyright (c) 2024 MoonlightByte
Licensed under Fair Source License 1.0

This software is free for non-commercial and educational use.
Commercial competing use is prohibited for 2 years from release.
See LICENSE file for full terms.
"""

# ============================================================================
# WEB_INTERFACE.PY - REAL-TIME WEB FRONTEND
# ============================================================================
#
# ARCHITECTURE ROLE: User Interface Layer - Real-Time Web Frontend
#
# This module provides a modern Flask-based web interface with SocketIO integration
# for real-time bidirectional communication between the browser and game engine,
# enabling responsive tabbed character data display and live game state updates.
#
# KEY RESPONSIBILITIES:
# - Flask + SocketIO real-time web server management
# - Tabbed interface design with dynamic character data presentation
# - Queue-based threaded output processing for responsive user experience
# - Real-time game state synchronization across multiple browser sessions
# - Cross-platform browser-based interface compatibility
# - Status broadcasting integration with console and web interfaces
# - Session state management linking web sessions to game state
#

"""
Web Interface for NeverEndingQuest

This module provides a Flask-based web interface for the dungeon master game,
with separate panels for game output and debug information.
"""
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit
import os
import sys
import json
import threading
import queue
import time
import webbrowser
from datetime import datetime
import io
from contextlib import redirect_stdout, redirect_stderr
from openai import OpenAI

# Add parent directory to path so we can import from utils, core, etc.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Install debug interceptor before importing main
from utils.redirect_debug_output import install_debug_interceptor, uninstall_debug_interceptor
install_debug_interceptor()

# Import the main game module and reset logic
import main as dm_main
import utils.reset_campaign as reset_campaign
from core.managers.status_manager import set_status_callback
from utils.enhanced_logger import debug, info, warning, error, set_script_name

# Set script name for logging
set_script_name("web_interface")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dungeon-master-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables for managing output
game_output_queue = queue.Queue()
debug_output_queue = queue.Queue()
user_input_queue = queue.Queue()
game_thread = None
original_stdout = sys.stdout
original_stderr = sys.stderr
original_stdin = sys.stdin

# Status callback function
def emit_status_update(status_message, is_processing):
    """Emit status updates to the frontend"""
    socketio.emit('status_update', {
        'message': status_message,
        'is_processing': is_processing
    })

# Set the status callback
set_status_callback(emit_status_update)

class WebOutputCapture:
    """Captures output and routes it to appropriate queues"""
    def __init__(self, queue, original_stream, is_error=False):
        self.queue = queue
        self.original_stream = original_stream
        self.is_error = is_error
        self.buffer = ""
        self.in_dm_section = False
        self.dm_buffer = []
    
    def write(self, text):
        # Write to original stream for console visibility (with error handling)
        try:
            # Ensure text is a string and handle encoding issues
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='replace')
            elif not isinstance(text, str):
                text = str(text)
            
            self.original_stream.write(text)
            self.original_stream.flush()
        except (BrokenPipeError, OSError, UnicodeEncodeError, AttributeError):
            # Ignore broken pipe errors, encoding errors, and attribute errors during output capture
            pass
        except Exception:
            # Catch any other unexpected errors and continue
            pass
        
        # Buffer text until we have a complete line
        self.buffer += text
        if '\n' in self.buffer:
            lines = self.buffer.split('\n')
            # Process all complete lines
            for line in lines[:-1]:
                # Clean the line of ANSI codes for checking content
                clean_line = self.strip_ansi_codes(line)
                
                # Check if this is a player status/prompt line
                if clean_line.startswith('[') and ('HP:' in clean_line or 'XP:' in clean_line):
                    # This is a player prompt - send to debug
                    debug_output_queue.put({
                        'type': 'debug',
                        'content': clean_line,
                        'timestamp': datetime.now().isoformat()
                    })
                # Check if this starts a Dungeon Master section
                elif "Dungeon Master:" in clean_line:
                    try:
                        # Start capturing DM content
                        self.in_dm_section = True
                        self.dm_buffer = [clean_line]
                    except Exception:
                        # If DM section initialization fails, send to debug instead
                        debug_output_queue.put({
                            'type': 'debug',
                            'content': clean_line,
                            'timestamp': datetime.now().isoformat()
                        })
                elif self.in_dm_section:
                    # Check if we're still in DM section
                    if line.strip() == "":
                        try:
                            # Empty line - still part of DM section, add to buffer
                            self.dm_buffer.append("")
                        except Exception:
                            # If buffer append fails, reset DM section
                            self.in_dm_section = False
                            self.dm_buffer = []
                    elif any(marker in clean_line for marker in ['DEBUG:', 'ERROR:', 'WARNING:']) or \
                         clean_line.startswith('[') and ('HP:' in clean_line or 'XP:' in clean_line) or \
                         clean_line.startswith('>'):
                        # This ends the DM section - send accumulated DM content as single message
                        if self.dm_buffer:
                            try:
                                combined_content = '\n'.join(self.dm_buffer)
                                # Remove "Dungeon Master:" prefix from the beginning if present
                                combined_content = combined_content.replace('Dungeon Master:', '', 1).strip()
                                if combined_content.strip():  # Only send if there's actual content
                                    game_output_queue.put({
                                        'type': 'narration',
                                        'content': combined_content
                                    })
                            except Exception:
                                # If DM content processing fails, send raw content to debug
                                try:
                                    debug_output_queue.put({
                                        'type': 'debug',
                                        'content': f"DM content error: {str(self.dm_buffer)}",
                                        'timestamp': datetime.now().isoformat()
                                    })
                                except Exception:
                                    # If even debug fails, just continue
                                    pass
                        self.in_dm_section = False
                        self.dm_buffer = []
                        # Send this line to debug
                        try:
                            debug_output_queue.put({
                                'type': 'debug',
                                'content': clean_line,
                                'timestamp': datetime.now().isoformat(),
                                'is_error': self.is_error or 'ERROR:' in clean_line
                            })
                        except Exception:
                            # If debug queue fails, just continue
                            pass
                    else:
                        # Still in DM section - check if it's a debug message
                        if any(marker in clean_line for marker in [
                            'Lightweight chat history updated',
                            'System messages removed:',
                            'User messages:',
                            'Assistant messages:',
                            'not found. Skipping',
                            'not found. Returning None',
                            'has an invalid JSON format',
                            'Current Time:',
                            'Time Advanced:',
                            'New Time:',
                            'Days Passed:',
                            'Loading module areas',
                            'Graph built:',
                            '[OK] Loaded'
                        ]):
                            # This is a debug message - send to debug output instead
                            debug_output_queue.put({
                                'type': 'debug',
                                'content': clean_line,
                                'timestamp': datetime.now().isoformat()
                            })
                            # End the DM section and send what we have so far
                            if self.dm_buffer:
                                try:
                                    combined_content = '\n'.join(self.dm_buffer)
                                    combined_content = combined_content.replace('Dungeon Master:', '', 1).strip()
                                    if combined_content.strip():
                                        game_output_queue.put({
                                            'type': 'narration',
                                            'content': combined_content
                                        })
                                except Exception:
                                    # If DM content processing fails, just continue
                                    pass
                            self.in_dm_section = False
                            self.dm_buffer = []
                        else:
                            try:
                                # Not a debug message - add to buffer
                                self.dm_buffer.append(clean_line)
                            except Exception:
                                # If buffer append fails, reset DM section
                                self.in_dm_section = False
                                self.dm_buffer = []
                else:
                    # Not in DM section - check if it's a debug message that should be filtered
                    if any(marker in clean_line for marker in [
                        'Lightweight chat history updated',
                        'System messages removed:',
                        'User messages:',
                        'Assistant messages:',
                        'not found. Skipping',
                        'not found. Returning None',
                        'has an invalid JSON format',
                        'Current Time:',
                        'Time Advanced:',
                        'New Time:',
                        'Days Passed:',
                        'Loading module areas',
                        'Graph built:',
                        '[OK] Loaded'
                    ]):
                        # These are debug messages - send to debug output
                        debug_output_queue.put({
                            'type': 'debug',
                            'content': clean_line,
                            'timestamp': datetime.now().isoformat()
                        })
                    elif line.strip():  # Only send non-empty lines
                        debug_output_queue.put({
                            'type': 'debug',
                            'content': clean_line,
                            'timestamp': datetime.now().isoformat(),
                            'is_error': self.is_error or 'ERROR:' in clean_line
                        })
            # Keep the incomplete line in buffer
            self.buffer = lines[-1]
    
    def strip_ansi_codes(self, text):
        """Remove ANSI escape codes from text"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def flush(self):
        # If we're in a DM section, flush it as single message
        if self.in_dm_section and self.dm_buffer:
            combined_content = '\n'.join(self.dm_buffer)
            # Remove "Dungeon Master:" prefix from the beginning if present
            combined_content = combined_content.replace('Dungeon Master:', '', 1).strip()
            if combined_content.strip():  # Only send if there's actual content
                game_output_queue.put({
                    'type': 'narration',
                    'content': combined_content
                })
            self.in_dm_section = False
            self.dm_buffer = []
        
        if self.buffer:
            # Don't recursively call write() - just add newline to buffer
            self.buffer += '\n'
        try:
            self.original_stream.flush()
        except (BrokenPipeError, OSError, UnicodeEncodeError, AttributeError):
            # Ignore broken pipe errors, encoding errors, and attribute errors during flush
            pass
        except Exception:
            # Catch any other unexpected errors and continue
            pass

class WebInput:
    """Handles input from the web interface"""
    def __init__(self, queue):
        self.queue = queue
    
    def readline(self):
        # Signal that we're ready for input (with error handling)
        try:
            from core.managers.status_manager import status_ready
            status_ready()
        except Exception:
            # If status_ready fails, continue without it
            pass
        
        # Wait for input from the web interface
        retry_count = 0
        max_retries = 1000  # Prevent infinite loops
        
        while retry_count < max_retries:
            try:
                user_input = self.queue.get(timeout=0.1)
                # Ensure input is a string and handle encoding issues
                if isinstance(user_input, str):
                    return user_input + '\n'
                else:
                    # Convert to string if needed
                    return str(user_input) + '\n'
            except queue.Empty:
                retry_count += 1
                continue
            except (BrokenPipeError, OSError, IOError):
                # Handle pipe errors gracefully
                return '\n'  # Return empty input to keep game running
            except Exception:
                # Handle any other unexpected errors
                return '\n'
        
        # If we've retried too many times, return empty input
        return '\n'

@app.route('/')
def index():
    """Serve the main game interface"""
    return render_template('game_interface.html')

@app.route('/static/media/videos/<path:filename>')
def serve_video(filename):
    """Serve video files from the media directory"""
    import os
    from flask import send_file
    video_path = os.path.join(os.path.dirname(__file__), 'static', 'media', 'videos', filename)
    if os.path.exists(video_path):
        return send_file(video_path, mimetype='video/mp4')
    return "Video not found", 404

@app.route('/static/dm_logo.png')
def serve_dm_logo():
    """Serve the DM logo image"""
    import mimetypes
    from flask import send_file
    # Go up one directory to find dm_logo.png at the root
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dm_logo.png')
    return send_file(logo_path, mimetype='image/png')

@app.route('/static/icons/<path:filename>')
def serve_icon(filename):
    """Serve icon images from the icons directory"""
    import mimetypes
    from flask import send_file
    # Ensure the filename ends with .png for security
    if not filename.endswith('.png'):
        return "Not found", 404
    icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'icons', filename)
    if os.path.exists(icon_path):
        return send_file(icon_path, mimetype='image/png')
    return "Not found", 404

@app.route('/spell-data')
def get_spell_data():
    """Serve spell repository data for tooltips"""
    try:
        with open('data/spell_repository.json', 'r') as f:
            spell_data = json.load(f)
        return jsonify(spell_data)
    except FileNotFoundError:
        return jsonify({})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'data': 'Connected to NeverEndingQuest'})
    
    # Send any queued messages
    while not game_output_queue.empty():
        msg = game_output_queue.get()
        emit('game_output', msg)
    
    while not debug_output_queue.empty():
        msg = debug_output_queue.get()
        emit('debug_output', msg)

@socketio.on('user_input')
def handle_user_input(data):
    """Handle input from the user"""
    user_input = data.get('input', '')
    user_input_queue.put(user_input)
    
    # Echo the input back to the game output
    emit('game_output', {
        'type': 'user-input',
        'content': user_input
    })

@socketio.on('action')
def handle_action(data):
    """Handle direct action requests from the UI (save, load, reset)."""
    action_type = data.get('action')
    parameters = data.get('parameters', {})
    debug(f"WEB_REQUEST: Received direct action from client: {action_type}", category="web_interface")

    if action_type == 'listSaves':
        try:
            from updates.save_game_manager import SaveGameManager
            manager = SaveGameManager()
            saves = manager.list_save_games()
            emit('save_list_response', saves)
        except Exception as e:
            print(f"Error listing saves: {e}")
            emit('save_list_response', [])

    elif action_type == 'saveGame':
        try:
            from updates.save_game_manager import SaveGameManager
            manager = SaveGameManager()
            description = parameters.get("description", "")
            save_mode = parameters.get("saveMode", "essential")
            success, message = manager.create_save_game(description, save_mode)
            if success:
                emit('system_message', {'content': f"Game saved: {message}"})
            else:
                emit('error', {'message': f"Save failed: {message}"})
        except Exception as e:
            emit('error', {'message': f"Save failed: {str(e)}"})

    elif action_type == 'restoreGame':
        try:
            from updates.save_game_manager import SaveGameManager
            manager = SaveGameManager()
            save_folder = parameters.get("saveFolder")
            success, message = manager.restore_save_game(save_folder)
            if success:
                emit('restore_complete', {'message': 'Game restored successfully. Server restarting...'})
                socketio.sleep(1)
                print("INFO: Game restore successful. Server is shutting down for restart.")
                os._exit(0)
            else:
                emit('error', {'message': f"Restore failed: {message}"})
        except Exception as e:
            emit('error', {'message': f"Restore failed: {str(e)}"})
    
    elif action_type == 'deleteSave':
        try:
            from updates.save_game_manager import SaveGameManager
            manager = SaveGameManager()
            save_folder = parameters.get("saveFolder")
            success, message = manager.delete_save_game(save_folder)
            if success:
                emit('system_message', {'content': f"Save deleted: {message}"})
            else:
                emit('error', {'message': f"Delete failed: {message}"})
        except Exception as e:
            emit('error', {'message': f"Delete failed: {str(e)}"})

    elif action_type == 'nuclearReset':
        try:
            reset_campaign.perform_reset_logic()
            emit('reset_complete', {'message': 'Campaign has been reset. Reloading...'})
            socketio.sleep(1) 
            print("INFO: Campaign reset complete. Server is shutting down for restart.")
            os._exit(0)
        except Exception as e:
            emit('error', {'message': f'Campaign reset failed: {str(e)}'})

@socketio.on('start_game')
def handle_start_game():
    """Start the game in a separate thread"""
    global game_thread
    
    if game_thread and game_thread.is_alive():
        emit('error', {'message': 'Game is already running'})
        return
    
    # Uninstall debug interceptor to prevent competing stdout redirections
    uninstall_debug_interceptor()
    
    # Set up output capture - both go to debug by default, filtering happens in write()
    sys.stdout = WebOutputCapture(debug_output_queue, original_stdout)
    sys.stderr = WebOutputCapture(debug_output_queue, original_stderr, is_error=True)
    sys.stdin = WebInput(user_input_queue)
    
    # Start the game in a separate thread
    game_thread = threading.Thread(target=run_game_loop, daemon=True)
    game_thread.start()
    
    emit('game_started', {'message': 'Game started successfully'})

@socketio.on('request_player_data')
def handle_player_data_request(data):
    """Handle requests for player data (inventory, stats, NPCs)"""
    try:
        dataType = data.get('dataType', 'stats')
        response_data = None
        
        # Load party tracker to get player name and NPCs
        party_tracker_path = 'party_tracker.json'
        if os.path.exists(party_tracker_path):
            with open(party_tracker_path, 'r', encoding='utf-8') as f:
                party_tracker = json.load(f)
        else:
            emit('player_data_response', {'dataType': dataType, 'data': None, 'error': 'Party tracker not found'})
            return
        
        if dataType == 'stats' or dataType == 'inventory' or dataType == 'spells':
            # Get player name from party tracker
            if party_tracker.get('partyMembers') and len(party_tracker['partyMembers']) > 0:
                from updates.update_character_info import normalize_character_name
                player_name = normalize_character_name(party_tracker['partyMembers'][0])
                
                # Try module-specific path first
                from utils.module_path_manager import ModulePathManager
                current_module = party_tracker.get("module", "").replace(" ", "_")
                path_manager = ModulePathManager(current_module)
                
                try:
                    player_file = path_manager.get_character_path(player_name)
                    if os.path.exists(player_file):
                        with open(player_file, 'r', encoding='utf-8') as f:
                            response_data = json.load(f)
                except:
                    # Fallback to characters directory
                    player_file = path_manager.get_character_path(player_name)
                    if os.path.exists(player_file):
                        with open(player_file, 'r', encoding='utf-8') as f:
                            response_data = json.load(f)
        
        elif dataType == 'npcs':
            # Get NPC data from party tracker
            npcs = []
            from utils.module_path_manager import ModulePathManager
            current_module = party_tracker.get("module", "").replace(" ", "_")
            path_manager = ModulePathManager(current_module)
            
            for npc_info in party_tracker.get('partyNPCs', []):
                npc_name = npc_info['name']
                
                try:
                    # Use fuzzy matching to find the correct NPC file
                    from updates.update_character_info import find_character_file_fuzzy
                    matched_name = find_character_file_fuzzy(npc_name)
                    
                    if matched_name:
                        npc_file = path_manager.get_character_path(matched_name)
                        if os.path.exists(npc_file):
                            with open(npc_file, 'r', encoding='utf-8') as f:
                                npc_data = json.load(f)
                                npcs.append(npc_data)
                except:
                    pass
            
            response_data = npcs
        
        emit('player_data_response', {'dataType': dataType, 'data': response_data})
    
    except Exception as e:
        emit('player_data_response', {'dataType': dataType, 'data': None, 'error': str(e)})

@socketio.on('request_location_data')
def handle_location_data_request():
    """Handle requests for current location information"""
    try:
        # Load party tracker to get current location
        party_tracker_path = 'party_tracker.json'
        if os.path.exists(party_tracker_path):
            with open(party_tracker_path, 'r', encoding='utf-8') as f:
                party_tracker = json.load(f)
            
            world_conditions = party_tracker.get('worldConditions', {})
            location_info = {
                'currentLocation': world_conditions.get('currentLocation', 'Unknown'),
                'currentArea': world_conditions.get('currentArea', 'Unknown'),
                'currentLocationId': world_conditions.get('currentLocationId', ''),
                'currentAreaId': world_conditions.get('currentAreaId', ''),
                'time': world_conditions.get('time', ''),
                'day': world_conditions.get('day', ''),
                'month': world_conditions.get('month', ''),
                'year': world_conditions.get('year', '')
            }
            
            emit('location_data_response', {'data': location_info})
        else:
            emit('location_data_response', {'data': None, 'error': 'Party tracker not found'})
    
    except Exception as e:
        emit('location_data_response', {'data': None, 'error': str(e)})

@socketio.on('request_npc_saves')
def handle_npc_saves_request(data):
    """Handle requests for NPC saving throws"""
    try:
        npc_name = data.get('npcName', '')
        
        # Load the NPC file
        from utils.module_path_manager import ModulePathManager
        from utils.encoding_utils import safe_json_load
        # Get current module from party tracker for consistent path resolution
        try:
            party_tracker = safe_json_load("party_tracker.json")
            current_module = party_tracker.get("module", "").replace(" ", "_") if party_tracker else None
            path_manager = ModulePathManager(current_module)
        except:
            path_manager = ModulePathManager()  # Fallback to reading from file
        
        from updates.update_character_info import normalize_character_name, find_character_file_fuzzy
        
        # Use fuzzy matching to find the correct NPC file
        matched_name = find_character_file_fuzzy(npc_name)
        if matched_name:
            npc_file = path_manager.get_character_path(matched_name)
        else:
            # Fallback to normalized name if no match found
            npc_file = path_manager.get_character_path(normalize_character_name(npc_name))
        if os.path.exists(npc_file):
            with open(npc_file, 'r', encoding='utf-8') as f:
                npc_data = json.load(f)
            
            emit('npc_details_response', {'npcName': npc_name, 'data': npc_data, 'modalType': 'saves'})
        else:
            emit('npc_details_response', {'npcName': npc_name, 'data': None, 'error': 'NPC file not found'})
            
    except Exception as e:
        emit('npc_details_response', {'npcName': npc_name, 'data': None, 'error': str(e)})

@socketio.on('request_npc_skills')
def handle_npc_skills_request(data):
    """Handle requests for NPC skills"""
    try:
        npc_name = data.get('npcName', '')
        
        # Load the NPC file
        from utils.module_path_manager import ModulePathManager
        from utils.encoding_utils import safe_json_load
        # Get current module from party tracker for consistent path resolution
        try:
            party_tracker = safe_json_load("party_tracker.json")
            current_module = party_tracker.get("module", "").replace(" ", "_") if party_tracker else None
            path_manager = ModulePathManager(current_module)
        except:
            path_manager = ModulePathManager()  # Fallback to reading from file
        
        from updates.update_character_info import normalize_character_name, find_character_file_fuzzy
        
        # Use fuzzy matching to find the correct NPC file
        matched_name = find_character_file_fuzzy(npc_name)
        if matched_name:
            npc_file = path_manager.get_character_path(matched_name)
        else:
            # Fallback to normalized name if no match found
            npc_file = path_manager.get_character_path(normalize_character_name(npc_name))
        if os.path.exists(npc_file):
            with open(npc_file, 'r', encoding='utf-8') as f:
                npc_data = json.load(f)
            
            emit('npc_details_response', {'npcName': npc_name, 'data': npc_data, 'modalType': 'skills'})
        else:
            emit('npc_details_response', {'npcName': npc_name, 'data': None, 'error': 'NPC file not found'})
            
    except Exception as e:
        emit('npc_details_response', {'npcName': npc_name, 'data': None, 'error': str(e)})

@socketio.on('request_npc_spells')
def handle_npc_spells_request(data):
    """Handle requests for NPC spellcasting"""
    try:
        npc_name = data.get('npcName', '')
        
        # Load the NPC file
        from utils.module_path_manager import ModulePathManager
        from utils.encoding_utils import safe_json_load
        # Get current module from party tracker for consistent path resolution
        try:
            party_tracker = safe_json_load("party_tracker.json")
            current_module = party_tracker.get("module", "").replace(" ", "_") if party_tracker else None
            path_manager = ModulePathManager(current_module)
        except:
            path_manager = ModulePathManager()  # Fallback to reading from file
        
        from updates.update_character_info import normalize_character_name, find_character_file_fuzzy
        
        # Use fuzzy matching to find the correct NPC file
        matched_name = find_character_file_fuzzy(npc_name)
        if matched_name:
            npc_file = path_manager.get_character_path(matched_name)
        else:
            # Fallback to normalized name if no match found
            npc_file = path_manager.get_character_path(normalize_character_name(npc_name))
        if os.path.exists(npc_file):
            with open(npc_file, 'r', encoding='utf-8') as f:
                npc_data = json.load(f)
            
            emit('npc_details_response', {'npcName': npc_name, 'data': npc_data, 'modalType': 'spells'})
        else:
            emit('npc_details_response', {'npcName': npc_name, 'data': None, 'error': 'NPC file not found'})
            
    except Exception as e:
        emit('npc_details_response', {'npcName': npc_name, 'data': None, 'error': str(e)})

@socketio.on('request_npc_inventory')
def handle_npc_inventory_request(data):
    """Handle requests for NPC inventory"""
    try:
        npc_name = data.get('npcName', '')
        
        # Load the NPC file
        from utils.module_path_manager import ModulePathManager
        from utils.encoding_utils import safe_json_load
        # Get current module from party tracker for consistent path resolution
        try:
            party_tracker = safe_json_load("party_tracker.json")
            current_module = party_tracker.get("module", "").replace(" ", "_") if party_tracker else None
            path_manager = ModulePathManager(current_module)
        except:
            path_manager = ModulePathManager()  # Fallback to reading from file
        
        from updates.update_character_info import normalize_character_name, find_character_file_fuzzy
        
        # Use fuzzy matching to find the correct NPC file
        matched_name = find_character_file_fuzzy(npc_name)
        if matched_name:
            npc_file = path_manager.get_character_path(matched_name)
        else:
            # Fallback to normalized name if no match found
            npc_file = path_manager.get_character_path(normalize_character_name(npc_name))
        if os.path.exists(npc_file):
            with open(npc_file, 'r', encoding='utf-8') as f:
                npc_data = json.load(f)
            
            # Extract equipment for inventory display
            equipment = npc_data.get('equipment', [])
            emit('npc_inventory_response', {'npcName': npc_name, 'data': equipment})
        else:
            emit('npc_inventory_response', {'npcName': npc_name, 'data': None, 'error': 'NPC file not found'})
            
    except Exception as e:
        emit('npc_inventory_response', {'npcName': npc_name, 'data': None, 'error': str(e)})

# Add this entire function to web_interface.py

@socketio.on('request_plot_data')
def handle_plot_data_request():
    """Handle requests for the current module's plot data."""
    try:
        # Step 1: Find out which module is currently active by checking the party tracker.
        party_tracker_path = 'party_tracker.json'
        if not os.path.exists(party_tracker_path):
            emit('plot_data_response', {'data': None, 'error': 'Party tracker not found'})
            return

        with open(party_tracker_path, 'r', encoding='utf-8') as f:
            party_tracker = json.load(f)
        
        current_module = party_tracker.get("module", "").replace(" ", "_")
        if not current_module:
            emit('plot_data_response', {'data': None, 'error': 'Current module not set in party tracker'})
            return

        # Step 2: Use the ModulePathManager to get the correct path to the plot file for that module.
        # This makes sure we always load the plot for the adventure the player is actually on.
        from utils.module_path_manager import ModulePathManager
        path_manager = ModulePathManager(current_module)
        
        # Step 2.5: Check for player-friendly quest file first
        player_quests_path = os.path.join(path_manager.module_dir, f"player_quests_{current_module}.json")
        
        if os.path.exists(player_quests_path):
            # Use player-friendly quest descriptions
            with open(player_quests_path, 'r', encoding='utf-8') as f:
                player_quests_data = json.load(f)
            
            # Convert player quest format back to module_plot format for compatibility
            plot_data = {
                "plotPoints": []
            }
            
            for quest_id, quest_data in player_quests_data.get("quests", {}).items():
                plot_point = {
                    "id": quest_data.get("id"),
                    "title": quest_data.get("title"),
                    "description": quest_data.get("playerDescription", quest_data.get("originalDescription", "")),
                    "status": quest_data.get("status"),
                    "sideQuests": []
                }
                
                # Add side quests
                for sq_id, sq_data in quest_data.get("sideQuests", {}).items():
                    plot_point["sideQuests"].append({
                        "id": sq_data.get("id"),
                        "title": sq_data.get("title"),
                        "description": sq_data.get("playerDescription", ""),
                        "status": sq_data.get("status")
                    })
                
                plot_data["plotPoints"].append(plot_point)
            
            debug(f"WEB_INTERFACE: Using player-friendly quests for {current_module}", category="web_interface")
        else:
            # Fallback to original module_plot.json
            plot_file_path = path_manager.get_plot_path()

            if not os.path.exists(plot_file_path):
                emit('plot_data_response', {'data': None, 'error': f'Plot file not found for module: {current_module}'})
                return
                
            # Step 3: Read the plot file and send its data back to the browser.
            with open(plot_file_path, 'r', encoding='utf-8') as f:
                plot_data = json.load(f)
            
            debug(f"WEB_INTERFACE: Using original plot data for {current_module} (no player quests file)", category="web_interface")
        
        # The 'emit' function sends the data over the web socket connection to the player's browser.
        emit('plot_data_response', {'data': plot_data})

    except Exception as e:
        # If anything goes wrong, send an error message so we can debug it.
        emit('plot_data_response', {'data': None, 'error': str(e)})

# CORRECTLY PLACED STORAGE HANDLER
@socketio.on('request_storage_data')
def handle_request_storage_data():
    """Handles a request from the client to view all player storage."""
    debug("WEB_REQUEST: Received request for storage data from client", category="web_interface")
    try:
        from core.managers.storage_manager import get_storage_manager
        manager = get_storage_manager()
        # Calling view_storage() with no location_id gets ALL storage containers.
        storage_data = manager.view_storage()
        
        if storage_data.get("success"):
            emit('storage_data_response', {'data': storage_data})
        else:
            emit('error', {'message': 'Failed to retrieve storage data.'})
            
    except Exception as e:
        print(f"ERROR handling storage request: {e}")
        emit('error', {'message': 'An internal error occurred while fetching storage data.'})

@socketio.on('user_exit')
def handle_user_exit():
    """Handle intentional user exit - log and clean up"""
    try:
        print("INFO: User has initiated exit from the game")
        emit('exit_acknowledged', {'message': 'Exit acknowledged'})
        # Note: We do NOT shut down the server here
        # Multiple users might be connected, and server shutdown is an admin function
        # The disconnect event will handle any necessary cleanup when the socket closes
    except Exception as e:
        print(f"ERROR handling user exit: {e}")

@socketio.on('toggle_model')
def handle_model_toggle(data):
    """Handle model toggle between GPT-4.1 and GPT-5"""
    try:
        import config
        use_gpt5 = data.get('use_gpt5', False)
        config.USE_GPT5_MODELS = use_gpt5
        
        # Log the change
        debug(f"Model toggled to: {'GPT-5' if use_gpt5 else 'GPT-4.1'}", category="web_interface")
        
        # Send confirmation back to client
        emit('model_toggled', {'use_gpt5': config.USE_GPT5_MODELS}, broadcast=True)
        
    except Exception as e:
        error(f"Error toggling model: {e}", exception=e, category="web_interface")
        emit('error', {'message': f"Failed to toggle model: {str(e)}"})

@socketio.on('test_module_progress')
def handle_test_module_progress():
    """Test handler to simulate module creation progress"""
    import threading
    import time
    
    def simulate_progress():
        """Simulate module creation progress events"""
        stages = [
            {'stage': 0, 'total_stages': 9, 'stage_name': 'Initializing', 'percentage': 0, 'message': 'Starting module creation...'},
            {'stage': 1, 'total_stages': 9, 'stage_name': 'Parsing narrative', 'percentage': 11, 'message': 'Analyzing narrative to extract module parameters...'},
            {'stage': 2, 'total_stages': 9, 'stage_name': 'Configuring builder', 'percentage': 22, 'message': 'Setting up module: Test_Module...'},
            {'stage': 3, 'total_stages': 9, 'stage_name': 'Creating builder', 'percentage': 33, 'message': 'Initializing module builder...'},
            {'stage': 4, 'total_stages': 9, 'stage_name': 'Building module', 'percentage': 44, 'message': 'Starting module generation process...'},
            {'stage': 5, 'total_stages': 9, 'stage_name': 'Creating areas', 'percentage': 55, 'message': 'Generating area layouts and descriptions...'},
            {'stage': 6, 'total_stages': 9, 'stage_name': 'Populating locations', 'percentage': 66, 'message': 'Adding NPCs and encounters...'},
            {'stage': 7, 'total_stages': 9, 'stage_name': 'Finalizing', 'percentage': 77, 'message': 'Finalizing module data...'},
            {'stage': 8, 'total_stages': 9, 'stage_name': 'Complete', 'percentage': 100, 'message': 'Module Test_Module created successfully!'}
        ]
        
        for stage_data in stages:
            socketio.emit('module_creation_progress', stage_data)
            time.sleep(1.5)  # Delay between stages for visual effect
    
    # Run simulation in background thread
    thread = threading.Thread(target=simulate_progress)
    thread.daemon = True
    thread.start()
    
    emit('system_message', {'content': 'Starting module progress test simulation...'})

@socketio.on('generate_image')
def handle_generate_image(data):
    """Handle image generation requests"""
    try:
        prompt = data.get('prompt', '')
        if not prompt:
            emit('image_generation_error', {'message': 'No prompt provided'})
            return
        
        import config
        import requests
        from datetime import datetime
        from utils.file_operations import safe_read_json, safe_write_json
        
        # Initialize OpenAI client
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        # Try to generate image
        try:
            # Generate image using DALL-E 3 with high quality settings
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="hd",
                n=1,
            )
            # Get the image URL
            image_url = response.data[0].url
        except Exception as dalle_error:
            # Check if it's a content policy violation
            if "content_policy_violation" in str(dalle_error) or "400" in str(dalle_error):
                # Silently sanitize and retry
                from utils.prompt_sanitizer import sanitize_prompt
                sanitized_prompt = sanitize_prompt(prompt)
                
                # Retry with sanitized prompt
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=sanitized_prompt,
                    size="1024x1024",
                    quality="hd",
                    n=1,
                )
                image_url = response.data[0].url
            else:
                # Re-raise if it's not a content policy issue
                raise dalle_error
        
        # Save the image locally with metadata
        try:
            # Get current module and game state
            party_data = safe_read_json("party_tracker.json")
            current_module = party_data.get("module", "unknown_module")
            world_conditions = party_data.get("worldConditions", {})
            
            # Get game time
            game_year = world_conditions.get("year", 0)
            game_month = world_conditions.get("month", "Unknown")
            game_day = world_conditions.get("day", 0)
            game_time = world_conditions.get("time", "00:00:00")
            location_id = world_conditions.get("currentLocationId", "unknown")
            location_name = world_conditions.get("currentLocation", "Unknown Location")
            
            # Create images directory for the module
            images_dir = os.path.join("modules", current_module, "images")
            os.makedirs(images_dir, exist_ok=True)
            
            # Generate filename with both timestamps
            real_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            game_timestamp = f"{game_year}_{game_month}_{game_day}_{game_time.replace(':', '')}"
            filename = f"img_{real_timestamp}_game_{game_timestamp}_{location_id}.png"
            filepath = os.path.join(images_dir, filename)
            
            # Download and save the image
            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                print(f"Saved image to: {filepath}")
                
                # Save metadata
                metadata_file = os.path.join(images_dir, "image_metadata.json")
                metadata = safe_read_json(metadata_file) or {"images": []}
                
                metadata["images"].append({
                    "filename": filename,
                    "prompt": prompt,
                    "real_world_time": datetime.now().isoformat(),
                    "game_time": {
                        "year": game_year,
                        "month": game_month,
                        "day": game_day,
                        "time": game_time
                    },
                    "location": {
                        "id": location_id,
                        "name": location_name,
                        "area": world_conditions.get("currentArea", "Unknown Area"),
                        "area_id": world_conditions.get("currentAreaId", "unknown")
                    },
                    "module": current_module,
                    "original_url": image_url
                })
                
                safe_write_json(metadata_file, metadata)
                print(f"Updated image metadata in: {metadata_file}")
            
        except Exception as save_error:
            # Don't fail the whole operation if saving fails
            print(f"Warning: Failed to save image locally: {save_error}")
        
        # Emit the image URL back to the client
        emit('image_generated', {
            'image_url': image_url,
            'prompt': prompt
        })
        
    except Exception as e:
        error_msg = f"Image generation failed: {str(e)}"
        print(f"ERROR: {error_msg}")
        emit('image_generation_error', {'message': error_msg})

def run_game_loop():
    """Run the main game loop with enhanced error handling"""
    try:
        # Start the output sender thread
        output_thread = threading.Thread(target=send_output_to_clients, daemon=True)
        output_thread.start()
        
        # Run the main game
        dm_main.main_game_loop()
    except (BrokenPipeError, OSError) as e:
        # Handle broken pipe errors specifically
        try:
            print(f"Stream error detected: {e}")
        except Exception:
            pass  # If even this fails, continue silently
        
        try:
            # Attempt to reset streams
            sys.stdout = WebOutputCapture(debug_output_queue, original_stdout)
            sys.stderr = WebOutputCapture(debug_output_queue, original_stderr, is_error=True)
            sys.stdin = WebInput(user_input_queue)
            try:
                print("Stream recovery attempted")
            except Exception:
                pass
        except Exception:
            try:
                print("Stream recovery failed")
            except Exception:
                pass
        
        # Send a user-friendly message
        try:
            game_output_queue.put({
                'type': 'info',
                'content': 'Connection restored. You may continue playing.',
                'timestamp': datetime.now().isoformat()
            })
        except Exception:
            pass
    except Exception as e:
        # Handle other errors
        error_msg = f"Game error: {str(e)}"
        try:
            print(f"Game loop error: {error_msg}")
        except Exception:
            pass
        
        try:
            game_output_queue.put({
                'type': 'error',
                'content': error_msg,
                'timestamp': datetime.now().isoformat()
            })
        except Exception:
            pass
    finally:
        # Restore original streams safely
        try:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            sys.stdin = original_stdin
        except Exception:
            # If restoration fails, try to at least restore stdout
            try:
                sys.stdout = original_stdout
            except Exception:
                pass

def send_output_to_clients():
    """Send queued output to all connected clients"""
    while True:
        try:
            # Send game output
            while not game_output_queue.empty():
                try:
                    msg = game_output_queue.get()
                    socketio.emit('game_output', msg)
                except Exception:
                    # If queue operation or emit fails, just continue
                    break
            
            # Send debug output
            while not debug_output_queue.empty():
                try:
                    msg = debug_output_queue.get()
                    socketio.emit('debug_output', msg)
                except Exception:
                    # If queue operation or emit fails, just continue
                    break
        except Exception:
            # If any other error occurs, just continue
            pass
        
        time.sleep(0.1)  # Small delay to prevent CPU spinning

def open_browser():
    """Open the web browser after a short delay"""
    time.sleep(1.5)  # Wait for server to start
    try:
        import config
        port = getattr(config, 'WEB_PORT', 8357)
    except ImportError:
        port = 8357
    webbrowser.open(f'http://localhost:{port}')

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Start browser opening in a separate thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    print("Starting NeverEndingQuest Web Interface...")
    try:
        import config
        port = getattr(config, 'WEB_PORT', 8357)
    except ImportError:
        port = 8357
    print(f"Opening browser at http://localhost:{port}")
    
    # Run the Flask app with SocketIO
    socketio.run(app, 
                host='0.0.0.0',
                port=port,
                debug=False,
                use_reloader=False,
                allow_unsafe_werkzeug=True)
