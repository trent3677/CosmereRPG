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
# Suppress httpx debug messages on startup
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)

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
import zipfile
from contextlib import redirect_stdout, redirect_stderr
from openai import OpenAI
from PIL import Image

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

# Import toolkit components for API support
try:
    from core.toolkit.pack_manager import PackManager
    from core.toolkit.monster_generator import MonsterGenerator
    from core.toolkit.video_processor import VideoProcessor
    TOOLKIT_AVAILABLE = True
except ImportError:
    TOOLKIT_AVAILABLE = False
    print("Module Toolkit not available - toolkit endpoints disabled")

# Set script name for logging
set_script_name("web_interface")

# Set up Flask with correct template and static paths
# Templates are in both web/templates (for game) and root templates (for toolkit)
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
                        # Debug trace for combat output
                        debug_output_queue.put({
                            'type': 'debug',
                            'content': f"[OUTPUT_TRACE] Started DM section: {clean_line[:100]}...",
                            'timestamp': datetime.now().isoformat()
                        })
                    except Exception:
                        # If DM section initialization fails, send to debug instead
                        debug_output_queue.put({
                            'type': 'debug',
                            'content': f"[OUTPUT_ERROR] DM section init failed: {clean_line}",
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
                                    # Debug trace for successful DM output
                                    debug_output_queue.put({
                                        'type': 'debug',
                                        'content': f"[OUTPUT_TRACE] Sent DM content to game_output: {len(combined_content)} chars",
                                        'timestamp': datetime.now().isoformat()
                                    })
                            except Exception as e:
                                # If DM content processing fails, send raw content to debug
                                try:
                                    debug_output_queue.put({
                                        'type': 'debug',
                                        'content': f"[OUTPUT_ERROR] DM content processing failed: {str(e)} - Buffer: {str(self.dm_buffer)}",
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

@app.route('/static/portraits/<path:filename>')
def serve_portrait(filename):
    """Serve character portrait images."""
    import mimetypes
    from flask import send_file
    # Ensure the filename ends with .png for security
    if not filename.endswith('.png'):
        return "Not found", 404
    portrait_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'portraits', filename)
    if os.path.exists(portrait_path):
        return send_file(portrait_path, mimetype='image/png')
    return "Not found", 404

@app.route('/get_character_data')
def get_character_data():
    """Get character data including class for NPC portraits."""
    try:
        from utils.file_operations import safe_read_json
        
        character_name = request.args.get('character_name')
        if not character_name:
            return jsonify({'error': 'No character name provided'}), 400
        
        # Look for character file in characters folder
        character_path = f'characters/{character_name}.json'
        character_data = safe_read_json(character_path)
        
        if character_data:
            # Return relevant character data
            return jsonify({
                'name': character_data.get('name'),
                'class': character_data.get('class'),
                'race': character_data.get('race'),
                'level': character_data.get('level')
            })
        else:
            return jsonify({'error': 'Character not found'}), 404
            
    except Exception as e:
        error(f"Error getting character data: {e}", exception=e, category="web_interface")
        return jsonify({'error': str(e)}), 500

@app.route('/upload-portrait', methods=['POST'])
def upload_portrait():
    """Handle character portrait upload, cropping, and saving."""
    try:
        if 'portrait' not in request.files:
            return jsonify({'success': False, 'message': 'No file part'})
        
        file = request.files['portrait']
        character_name = request.form.get('characterName')

        if file.filename == '' or not character_name:
            return jsonify({'success': False, 'message': 'No selected file or character name'})

        if file:
            # Create the portraits directory if it doesn't exist
            portraits_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'portraits')
            os.makedirs(portraits_dir, exist_ok=True)

            # Open the image with Pillow
            img = Image.open(file.stream)

            # --- Cropping Logic ---
            width, height = img.size
            if width != height:
                # Find the smaller dimension
                min_dim = min(width, height)
                # Calculate coordinates for a center crop
                left = (width - min_dim) / 2
                top = (height - min_dim) / 2
                right = (width + min_dim) / 2
                bottom = (height + min_dim) / 2
                img = img.crop((left, top, right, bottom))
            
            # Resize to a standard size (e.g., 256x256) for consistency
            img = img.resize((256, 256), Image.Resampling.LANCZOS)

            # Save the processed image as PNG in web static folder
            save_filename = f"{character_name}.png"
            save_path = os.path.join(portraits_dir, save_filename)
            img.save(save_path, 'PNG')
            
            # Also save to the character's module folder for persistence
            try:
                # Get current module from party tracker
                party_tracker_path = 'party_tracker.json'
                if os.path.exists(party_tracker_path):
                    with open(party_tracker_path, 'r', encoding='utf-8') as f:
                        party_tracker = json.load(f)
                        current_module = party_tracker.get('module', '').replace(' ', '_')
                        
                        if current_module:
                            from utils.module_path_manager import ModulePathManager
                            manager = ModulePathManager(current_module)
                            module_portraits_dir = os.path.join(manager.get_module_dir(), 'portraits')
                            os.makedirs(module_portraits_dir, exist_ok=True)
                            module_save_path = os.path.join(module_portraits_dir, save_filename)
                            img.save(module_save_path, 'PNG')
                            info(f"PORTRAIT: Also saved to module folder at {module_save_path}")
            except Exception as e:
                warning(f"PORTRAIT: Could not save to module folder: {e}")
            
            info(f"PORTRAIT: Saved new portrait for {character_name} to {save_path}")
            return jsonify({'success': True, 'message': 'Portrait uploaded successfully'})

    except Exception as e:
        error(f"PORTRAIT: Upload failed", exception=e, category="web_interface")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/spell-data')
def get_spell_data():
    """Serve spell repository data for tooltips"""
    try:
        with open('data/spell_repository.json', 'r') as f:
            spell_data = json.load(f)
        return jsonify(spell_data)
    except FileNotFoundError:
        return jsonify({})

# ============================================================================
# MODULE TOOLKIT API ENDPOINTS
# ============================================================================

@app.route('/toolkit')
def toolkit_interface():
    """Serve the module toolkit interface"""
    if not TOOLKIT_AVAILABLE:
        return "Module Toolkit not available", 503
    return render_template('module_toolkit.html')

@app.route('/api/toolkit/packs')
def get_packs():
    """Get list of available graphic packs"""
    if not TOOLKIT_AVAILABLE:
        # Return an error if the toolkit isn't available, so the frontend knows why it's empty.
        return jsonify({'error': 'Module Toolkit components are not available on the server.'}), 503

    try:
        manager = PackManager()
        packs = manager.list_available_packs()
        return jsonify(packs)
    except Exception as e:
        # This is the most important change.
        # Instead of failing silently, we now send the actual error back to the browser.
        error_message = f"TOOLKIT: Failed to list packs: {e}"
        error(error_message) # Log the error to the server console
        # Return a JSON object with the error and a 500 Internal Server Error status.
        return jsonify({'error': str(e)}), 500

@app.route('/api/toolkit/packs/create', methods=['POST'])
def create_pack():
    """Create a new graphic pack"""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'})
    
    try:
        data = request.json
        manager = PackManager()
        # Pass all the new fields to the manager
        result = manager.create_pack(
            name=data.get('name'),
            display_name=data.get('display_name'),
            style_template=data.get('style', 'custom'),  # Default to custom style
            author=data.get('author', 'Module Toolkit User'),
            description=data.get('description', '')
        )
        return jsonify(result)
    except Exception as e:
        error(f"TOOLKIT: Failed to create pack: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/toolkit/packs/<pack_name>/activate', methods=['POST'])
def activate_pack(pack_name):
    """Activate a graphic pack with optional backup"""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'})
    
    try:
        # Check if backup should be created
        create_backup = request.json.get('create_backup', False) if request.json else False
        
        # If backup requested, create a backup pack from current live game assets FIRST
        if create_backup:
            backup_result = create_live_assets_backup_pack()
            if not backup_result.get('success'):
                warning(f"TOOLKIT: Failed to create live assets backup: {backup_result.get('error')}")
        
        manager = PackManager()
        result = manager.activate_pack(pack_name, create_backup=False)  # Don't need pack backup since we did live backup
        
        # If activation successful, copy all assets to the live game folders
        if result.get('success'):
            # First, copy the monster assets (NO individual backup needed)
            copy_pack_monsters_to_game(pack_name)
            # Then, copy the NPC assets (NO individual backup needed)
            copy_pack_npcs_to_game(pack_name)
        
        return jsonify(result)
    except Exception as e:
        error(f"TOOLKIT: Failed to activate pack: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/toolkit/packs/<pack_name>/export')
def export_pack(pack_name):
    """Export a pack as ZIP file"""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'})
    
    try:
        import tempfile
        manager = PackManager()
        
        # Export to temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            result = manager.export_pack(pack_name, temp_dir)
            if result['success']:
                # Send the ZIP file
                zip_path = result['zip_path']
                with open(zip_path, 'rb') as f:
                    zip_data = f.read()
                
                response = Response(
                    zip_data,
                    mimetype='application/zip',
                    headers={
                        'Content-Disposition': f'attachment; filename={os.path.basename(zip_path)}'
                    }
                )
                return response
            else:
                return jsonify(result), 400
    except Exception as e:
        error(f"TOOLKIT: Failed to export pack: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/toolkit/packs/<pack_name>', methods=['DELETE'])
def delete_pack(pack_name):
    """Delete a graphic pack"""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'})
    
    try:
        manager = PackManager()
        result = manager.delete_pack(pack_name)
        return jsonify(result)
    except Exception as e:
        error(f"TOOLKIT: Failed to delete pack: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/toolkit/packs/<pack_name>/merge', methods=['POST'])
def merge_pack(pack_name):
    """Merges a specified pack into the currently active pack."""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'}), 503

    try:
        # --- BACKEND LOGIC TO BE IMPLEMENTED ---
        # 1. Create an instance of PackManager.
        #    manager = PackManager()
        #
        # 2. Get the currently active pack. This will be the DESTINATION.
        #    active_pack = manager.get_active_pack()
        #    if not active_pack:
        #        return jsonify({'success': False, 'error': 'No active pack found to merge into.'})
        #
        # 3. The `pack_name` from the URL is the SOURCE pack.
        #
        # 4. Call a new method on the manager, e.g., `manager.merge_pack(source_pack_name=pack_name, dest_pack_name=active_pack['name'])`
        #    This method will need to:
        #      a. Get the file paths for both packs.
        #      b. Iterate through all files (monsters, videos) in the source pack.
        #      c. For each file, copy it to the destination pack, overwriting if it exists.
        #      d. After copying, re-scan the destination pack's manifest to update monster/video counts.
        #
        # 5. Return the result from the manager.
        # --- END OF LOGIC TO BE IMPLEMENTED ---

        # For now, return a placeholder success message.
        info(f"TOOLKIT: Placeholder merge request for pack '{pack_name}'")
        return jsonify({'success': True, 'message': f"Placeholder: Successfully merged '{pack_name}' into the active pack."})

    except Exception as e:
        error(f"TOOLKIT: Failed to merge pack '{pack_name}': {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/toolkit/export-monsters-to-pack', methods=['POST'])
def export_monsters_to_pack():
    """Export selected monsters from a source pack to a new custom pack"""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'}), 503
    
    try:
        data = request.json
        pack_name = data.get('pack_name')
        display_name = data.get('display_name')
        author = data.get('author')
        description = data.get('description', '')
        style = data.get('style', 'custom')
        source_pack = data.get('source_pack')
        monster_ids = data.get('monster_ids', [])
        
        if not all([pack_name, display_name, author, source_pack, monster_ids]):
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        info(f"TOOLKIT: Creating new pack '{pack_name}' with {len(monster_ids)} monsters from '{source_pack}'")
        
        import os
        import shutil
        import json
        from datetime import datetime
        
        # Create pack directory
        pack_dir = os.path.join('graphic_packs', pack_name)
        if os.path.exists(pack_dir):
            return jsonify({'success': False, 'error': f'Pack "{pack_name}" already exists'})
        
        os.makedirs(pack_dir)
        monsters_dir = os.path.join(pack_dir, 'monsters')
        os.makedirs(monsters_dir)
        
        # Source pack directory
        source_dir = os.path.join('graphic_packs', source_pack, 'monsters')
        if not os.path.exists(source_dir):
            shutil.rmtree(pack_dir)  # Clean up
            return jsonify({'success': False, 'error': f'Source pack "{source_pack}" not found'})
        
        # Copy monster files
        exported_count = 0
        skipped = []
        
        for monster_id in monster_ids:
            copied = False
            
            # Try to copy image file (jpg or png)
            for ext in ['.jpg', '.png']:
                source_image = os.path.join(source_dir, f'{monster_id}{ext}')
                if os.path.exists(source_image):
                    dest_image = os.path.join(monsters_dir, f'{monster_id}{ext}')
                    shutil.copy2(source_image, dest_image)
                    copied = True
                    
                    # Copy thumbnail if exists
                    source_thumb = os.path.join(source_dir, f'{monster_id}_thumb{ext}')
                    if os.path.exists(source_thumb):
                        dest_thumb = os.path.join(monsters_dir, f'{monster_id}_thumb{ext}')
                        shutil.copy2(source_thumb, dest_thumb)
                    break
            
            # Copy video if exists
            source_video = os.path.join(source_dir, f'{monster_id}_video.mp4')
            if os.path.exists(source_video):
                dest_video = os.path.join(monsters_dir, f'{monster_id}_video.mp4')
                shutil.copy2(source_video, dest_video)
                copied = True
            
            if copied:
                exported_count += 1
            else:
                skipped.append(monster_id)
                warning(f"TOOLKIT: Monster '{monster_id}' not found in source pack")
        
        # Create manifest.json
        manifest = {
            "name": pack_name,
            "display_name": display_name,
            "author": author,
            "description": description,
            "version": "1.0.0",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "style_template": style,
            "total_monsters": exported_count,
            "total_videos": len([f for f in os.listdir(monsters_dir) if f.endswith('_video.mp4')]),
            "monsters": monster_ids,
            "source": f"Exported from {source_pack}"
        }
        
        manifest_path = os.path.join(pack_dir, 'manifest.json')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        info(f"TOOLKIT: Successfully created pack '{pack_name}' with {exported_count} monsters")
        
        return jsonify({
            'success': True,
            'exported_count': exported_count,
            'skipped': skipped,
            'pack_name': pack_name
        })
        
    except Exception as e:
        error(f"TOOLKIT: Failed to export monsters to pack: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/toolkit/packs/preview', methods=['POST'])
def preview_pack():
    """Reads the manifest from a ZIP file without saving it."""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'})
    
    if 'pack' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided for preview'})
    
    file = request.files['pack']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})

    try:
        # Read the file into memory
        zip_in_memory = io.BytesIO(file.read())
        
        with zipfile.ZipFile(zip_in_memory, 'r') as zip_ref:
            # Check for manifest file
            if 'manifest.json' not in zip_ref.namelist():
                return jsonify({'success': False, 'error': 'manifest.json not found in archive.'})
            
            # Read and parse the manifest
            with zip_ref.open('manifest.json') as manifest_file:
                manifest_data = json.load(manifest_file)
                
                # Count assets in the ZIP
                monster_count = 0
                npc_count = 0
                video_count = 0
                
                for filename in zip_ref.namelist():
                    if filename.startswith('monsters/'):
                        if filename.endswith('.mp4'):
                            video_count += 1
                        elif filename.endswith(('.png', '.jpg', '.jpeg')) and '_thumb' not in filename:
                            monster_count += 1
                    elif filename.startswith('npcs/'):
                        if filename.endswith(('.png', '.jpg', '.jpeg')) and '_thumb' not in filename:
                            npc_count += 1
                
                # Add counts to manifest data
                manifest_data['total_monsters'] = monster_count
                manifest_data['total_npcs'] = npc_count
                manifest_data['total_videos'] = video_count
                
                return jsonify({'success': True, 'data': manifest_data})

    except zipfile.BadZipFile:
        return jsonify({'success': False, 'error': 'Invalid .zip file.'})
    except Exception as e:
        error(f"TOOLKIT: Failed to preview pack: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/toolkit/packs/import', methods=['POST'])
def import_pack():
    """Import a pack from ZIP file"""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'})
    
    try:
        if 'pack' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})
        
        file = request.files['pack']
        # Get the target folder name and import options from the form data
        target_folder_name = request.form.get('target_folder_name')
        import_monsters = request.form.get('import_monsters', 'true').lower() == 'true'
        import_npcs = request.form.get('import_npcs', 'true').lower() == 'true'

        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        # Save to temp file
        import tempfile
        tmp_file = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
                tmp_file = tmp.name
                file.save(tmp.name)
            
            # File is now closed, safe to process
            manager = PackManager()
            # Pass the target folder name and import options to the manager
            result = manager.import_pack(
                tmp_file, 
                target_folder_name=target_folder_name,
                import_monsters=import_monsters,
                import_npcs=import_npcs
            )
            
            return jsonify(result)
        finally:
            # Clean up temp file in finally block to ensure it happens
            if tmp_file and os.path.exists(tmp_file):
                try:
                    os.unlink(tmp_file)
                except Exception as cleanup_error:
                    # Log but don't fail if we can't delete temp file
                    error(f"TOOLKIT: Could not delete temp file {tmp_file}: {cleanup_error}")
    except Exception as e:
        error(f"TOOLKIT: Failed to import pack: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/toolkit/monsters')
def get_monsters():
    """Get list of available monsters"""
    if not TOOLKIT_AVAILABLE:
        return jsonify([])
    
    try:
        # Get pack parameter from query string
        pack_name = request.args.get('pack', 'photorealistic')
        
        # Use a temporary generator instance to get monster list
        from config import OPENAI_API_KEY
        generator = MonsterGenerator(api_key=OPENAI_API_KEY)
        monsters = generator.get_monster_list(pack_name=pack_name)
        return jsonify(monsters)
    except Exception as e:
        error(f"TOOLKIT: Failed to get monster list: {e}")
        return jsonify([])

@app.route('/toolkit/pack_image/<pack_name>/<filename>')
def serve_pack_image(pack_name, filename):
    """Serve an image from a graphic pack"""
    from flask import send_from_directory
    import os
    
    # Construct the absolute path to the image - all files in monsters folder now
    pack_dir = os.path.abspath(os.path.join('graphic_packs', pack_name, 'monsters'))
    
    # Check if file exists - NO FALLBACK
    file_path = os.path.join(pack_dir, filename)
    if os.path.exists(file_path):
        return send_from_directory(pack_dir, filename)
    
    # Return 404 if not found - no fallback to other directories
    return '', 404

@app.route('/toolkit/pack_video/<pack_name>/<filename>')
def serve_pack_video(pack_name, filename):
    """Serve a video from a graphic pack"""
    from flask import send_from_directory
    import os
    
    # Construct the absolute path to the video - all files in monsters folder now
    pack_dir = os.path.abspath(os.path.join('graphic_packs', pack_name, 'monsters'))
    
    # Check if file exists - NO FALLBACK
    file_path = os.path.join(pack_dir, filename)
    if os.path.exists(file_path):
        return send_from_directory(pack_dir, filename)
    
    # Return 404 if not found - no fallback to other directories
    return '', 404

@app.route('/api/toolkit/check_existing_images', methods=['POST'])
def check_existing_images():
    """Check if images already exist for the given monsters in a pack"""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'})
    
    try:
        data = request.json
        pack_name = data.get('pack_name')
        monster_ids = data.get('monster_ids', [])
        
        if not pack_name or not monster_ids:
            return jsonify({'success': False, 'error': 'Missing pack_name or monster_ids'})
        
        # Check which files exist
        pack_dir = Path(f"graphic_packs/{pack_name}/monsters")
        existing = []
        
        if pack_dir.exists():
            for monster_id in monster_ids:
                # Check for .jpg files only (the correct format)
                jpg_path = pack_dir / f"{monster_id}.jpg"
                
                if jpg_path.exists():
                    existing.append(monster_id)
        
        return jsonify({
            'success': True,
            'existing': existing,
            'total_checked': len(monster_ids)
        })
    
    except Exception as e:
        error(f"TOOLKIT: Error checking existing images: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/toolkit/generate', methods=['POST'])
def generate_monsters():
    """Start monster generation task"""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'})
    
    try:
        data = request.json
        pack_name = data.get('pack_name')
        style = data.get('style', 'photorealistic')
        model = data.get('model', 'auto')
        monsters = data.get('monsters', [])
        
        # Start generation in background thread
        import uuid
        import asyncio
        task_id = str(uuid.uuid4())
        
        def run_generation():
            try:
                from config import OPENAI_API_KEY
                generator = MonsterGenerator(api_key=OPENAI_API_KEY)
                
                # Create progress callback
                def progress_callback(progress_data):
                    socketio.emit('generation_progress', progress_data)
                
                # Run the async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    generator.batch_generate_pack(
                        pack_name=pack_name,
                        style=style,
                        monsters=monsters,
                        model=model,
                        progress_callback=progress_callback
                    )
                )
                
                socketio.emit('generation_complete', result)
            except Exception as e:
                error(f"TOOLKIT: Generation failed: {e}")
                socketio.emit('generation_error', {'error': str(e)})
        
        # Start in background thread
        thread = threading.Thread(target=run_generation)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'task_id': task_id})
    except Exception as e:
        error(f"TOOLKIT: Failed to start generation: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/toolkit/process-video', methods=['POST'])
def process_video():
    """Process a monster video"""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'})
    
    try:
        if 'video' not in request.files:
            return jsonify({'success': False, 'error': 'No video file provided'})
        
        file = request.files['video']
        monster_id = request.form.get('monster_id')
        pack_name = request.form.get('pack_name')
        
        if not monster_id or not pack_name:
            return jsonify({'success': False, 'error': 'Missing monster_id or pack_name'})
        
        # Save to temp file
        import tempfile
        import time
        
        tmp_file = None
        result = {'success': False, 'error': 'Unknown error'}  # Initialize result
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
                tmp_file = tmp.name
                file.save(tmp_file)
            
            print(f"[INFO] Processing video for {monster_id}")
            print(f"[INFO] Temp file: {tmp_file}")
            print(f"[INFO] File size: {os.path.getsize(tmp_file)} bytes")
            
            processor = VideoProcessor()
            result = processor.process_monster_video(
                input_path=tmp_file,
                monster_id=monster_id,
                pack_name=pack_name,
                skip_compression=False  # Enable compression
            )
            
            # Try to clean up temp file with retries for Windows
            for attempt in range(5):
                try:
                    if tmp_file and os.path.exists(tmp_file):
                        os.unlink(tmp_file)
                    break
                except PermissionError:
                    if attempt < 4:  # Don't sleep on last attempt
                        time.sleep(0.5)  # Wait half a second and retry
                    else:
                        # Log warning but don't fail the request
                        print(f"Warning: Could not delete temp file {tmp_file}")
                        
        except Exception as process_error:
            # Capture the actual error in result
            error(f"TOOLKIT: Video processing error: {process_error}")
            result = {'success': False, 'error': str(process_error)}
            
        return jsonify(result)
    except Exception as e:
        error(f"TOOLKIT: Failed to process video: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/toolkit/add-to-bestiary', methods=['POST'])
def add_to_bestiary():
    """Add missing monsters to the bestiary using GPT-4o-mini"""
    try:
        data = request.json
        module_name = data.get('module_name')
        monster_names = data.get('monster_names', [])
        
        if not module_name or not monster_names:
            return jsonify({'success': False, 'error': 'Missing module_name or monster_names'})
        
        info(f"TOOLKIT: Adding {len(monster_names)} monsters to bestiary from module: {module_name}")
        
        # Start processing in background thread
        import threading
        import asyncio
        
        def run_bestiary_update():
            try:
                from utils.bestiary_updater import BestiaryUpdater
                updater = BestiaryUpdater()
                
                # Send initial progress
                socketio.emit('bestiary_update_progress', {
                    'status': 'started',
                    'message': f'Starting to process {len(monster_names)} monsters...'
                })
                
                # Create new event loop for thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Run the async function (test_mode=False for real updates)
                    loop.run_until_complete(
                        updater.process_missing_monsters(
                            module_name=module_name,
                            monster_names=monster_names,
                            test_mode=False  # Actually update the bestiary
                        )
                    )
                except Exception as e:
                    error(f"TOOLKIT: Error in bestiary update process: {e}")
                    socketio.emit('bestiary_update_error', {
                        'error': f'Process error: {str(e)}'
                    })
                    return
                
                socketio.emit('bestiary_update_complete', {
                    'success': True,
                    'message': f'Successfully added {len(monster_names)} monsters to bestiary',
                    'monsters': monster_names
                })
                info(f"TOOLKIT: Successfully added {len(monster_names)} monsters to bestiary")
            except Exception as e:
                error(f"TOOLKIT: Bestiary update failed: {e}")
                socketio.emit('bestiary_update_error', {
                    'success': False,
                    'error': str(e)
                })
        
        # Start in background thread
        thread = threading.Thread(target=run_bestiary_update)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Started processing {len(monster_names)} monsters in background'
        })
        
    except Exception as e:
        error(f"TOOLKIT: Failed to start bestiary update: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/toolkit/get_style_prompt/<style_id>')
def get_style_prompt(style_id):
    """Get the prompt for a specific style"""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'prompt': ''})
    
    try:
        from core.toolkit.style_manager import StyleManager
        manager = StyleManager()
        prompt = manager.get_style_prompt(style_id)
        return jsonify({'prompt': prompt or ''})
    except Exception as e:
        error(f"TOOLKIT: Failed to get style prompt: {e}")
        return jsonify({'prompt': ''})

@app.route('/toolkit/get_styles')
def get_all_styles():
    """Get all available style templates"""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'builtin': {}, 'custom': {}})
    
    try:
        from core.toolkit.style_manager import StyleManager
        manager = StyleManager()
        styles = manager.get_all_styles()
        
        # Organize by type
        builtin = {k: v for k, v in styles.items() if v['type'] == 'builtin'}
        custom = {k: v for k, v in styles.items() if v['type'] == 'custom'}
        
        return jsonify({'builtin': builtin, 'custom': custom})
    except Exception as e:
        error(f"TOOLKIT: Failed to get styles: {e}")
        return jsonify({'builtin': {}, 'custom': {}})

@app.route('/toolkit/save_style_template', methods=['POST'])
def save_style_template():
    """Save a custom style template"""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'})
    
    try:
        data = request.json
        name = data.get('name')
        prompt = data.get('prompt')
        
        if not name or not prompt:
            return jsonify({'success': False, 'error': 'Name and prompt are required'})
        
        from core.toolkit.style_manager import StyleManager
        manager = StyleManager()
        result = manager.save_custom_style(name, prompt)
        return jsonify(result)
    except Exception as e:
        error(f"TOOLKIT: Failed to save style: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/toolkit/update_style_prompt', methods=['POST'])
def update_style_prompt():
    """Update an existing style's prompt"""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'})
    
    try:
        data = request.json
        style_id = data.get('style_id')
        prompt = data.get('prompt')
        
        if not style_id or not prompt:
            return jsonify({'success': False, 'error': 'Style ID and prompt are required'})
        
        from core.toolkit.style_manager import StyleManager
        manager = StyleManager()
        # Use overwrite_style which handles both builtin and custom styles
        result = manager.overwrite_style(style_id, prompt)
        return jsonify(result)
    except Exception as e:
        error(f"TOOLKIT: Failed to update style: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/toolkit/get_monster_description/<monster_id>')
def get_monster_description(monster_id):
    """Get the description for a specific monster"""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'description': '', 'name': monster_id})
    
    try:
        # Load monster compendium with explicit UTF-8 encoding
        import json
        compendium_path = 'data/bestiary/monster_compendium.json'
        with open(compendium_path, 'r', encoding='utf-8') as f:
            compendium = json.load(f)
        
        # Look for monster in compendium
        monsters = compendium.get('monsters', {})
        if monster_id in monsters:
            monster_data = monsters[monster_id]
            description = monster_data.get('description', '')
            name = monster_data.get('name', monster_id)
            info(f"TOOLKIT: Found {monster_id} - desc length: {len(description)}")
            return jsonify({
                'description': description,
                'name': name
            })
        else:
            # Try with underscores replaced by spaces
            monster_id_alt = monster_id.replace('_', ' ').lower()
            for mid, mdata in monsters.items():
                if mid.lower() == monster_id_alt or mdata.get('name', '').lower() == monster_id_alt:
                    return jsonify({
                        'description': mdata.get('description', ''),
                        'name': mdata.get('name', monster_id)
                    })
        
        return jsonify({'description': '', 'name': monster_id})
    except Exception as e:
        error(f"TOOLKIT: Failed to get monster description: {e}")
        return jsonify({'description': '', 'name': monster_id})

@app.route('/toolkit/update_monster_description', methods=['POST'])
def update_monster_description():
    """Update a monster's description"""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'})
    
    try:
        data = request.json
        monster_id = data.get('monster_id')
        description = data.get('description')
        
        if not monster_id or not description:
            return jsonify({'success': False, 'error': 'Monster ID and description are required'})
        
        # Load and update monster compendium
        import json
        compendium_path = 'data/bestiary/monster_compendium.json'
        with open(compendium_path, 'r') as f:
            compendium = json.load(f)
        
        monsters = compendium.get('monsters', {})
        if monster_id in monsters:
            monsters[monster_id]['description'] = description
        else:
            # Try to find by alternative ID
            monster_id_alt = monster_id.replace('_', ' ').lower()
            found = False
            for mid, mdata in monsters.items():
                if mid.lower() == monster_id_alt or mdata.get('name', '').lower() == monster_id_alt:
                    monsters[mid]['description'] = description
                    found = True
                    break
            
            if not found:
                # Add new monster entry
                monsters[monster_id] = {
                    'name': monster_id.replace('_', ' ').title(),
                    'description': description,
                    'type': 'unknown',
                    'tags': []
                }
        
        # Save updated compendium
        with open(compendium_path, 'w') as f:
            json.dump(compendium, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Monster description updated'})
    except Exception as e:
        error(f"TOOLKIT: Failed to update monster description: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/toolkit/create_pack', methods=['POST'])
def create_pack_toolkit():
    """Create a new graphic pack from toolkit"""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'})
    
    try:
        data = request.json
        manager = PackManager()
        result = manager.create_pack(
            name=data.get('name'),
            style_template=data.get('style_template', 'photorealistic'),
            author=data.get('author', 'Module Toolkit'),
            description=data.get('description', '')
        )
        return jsonify(result)
    except Exception as e:
        error(f"TOOLKIT: Failed to create pack: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/toolkit/settings', methods=['POST'])
def save_toolkit_settings():
    """Save toolkit settings"""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'})
    
    try:
        data = request.json
        active_pack = data.get('active_pack')
        api_key = data.get('api_key')
        
        # Save active pack
        if active_pack:
            manager = PackManager()
            manager.activate_pack(active_pack)
        
        # API key would be saved to config if provided
        # For now, just acknowledge
        
        return jsonify({'success': True})
    except Exception as e:
        error(f"TOOLKIT: Failed to save settings: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/toolkit/modules')
def get_available_modules_api():
    """Get list of available adventure modules."""
    if not TOOLKIT_AVAILABLE:
        return jsonify([]), 503
    
    try:
        # This function already exists and gives us what we need.
        from core.generators.module_stitcher import list_available_modules
        modules = list_available_modules()
        return jsonify(modules)
    except Exception as e:
        error(f"TOOLKIT: Failed to get module list: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/toolkit/modules/<module_name>/monsters')
def get_module_monsters_api(module_name):
    """Get list of monster IDs found in a specific module."""
    if not TOOLKIT_AVAILABLE:
        return jsonify([]), 503
    
    try:
        from utils.module_path_manager import ModulePathManager
        from utils.file_operations import safe_read_json
        import os
        import re

        path_manager = ModulePathManager(module_name)
        monster_ids = set()

        # Build areas directory path
        areas_dir = os.path.join('modules', module_name, 'areas')
        
        # Scan area backup files (_BU.json) for monsters in locations
        if os.path.exists(areas_dir):
            for filename in os.listdir(areas_dir):
                # Only check backup files which contain original unmodified data
                if filename.endswith('_BU.json'):
                    area_path = os.path.join(areas_dir, filename)
                    area_data = safe_read_json(area_path)
                    if area_data and 'locations' in area_data:
                        for location in area_data.get('locations', []):
                            if 'monsters' in location and location['monsters']:
                                for monster in location['monsters']:
                                    if isinstance(monster, dict) and 'name' in monster:
                                        # Normalize the name to match our monster IDs:
                                        # "Bandit Captain Gorvek" -> "bandit_captain_gorvek"
                                        monster_id = monster['name'].lower().replace(' ', '_')
                                        monster_ids.add(monster_id)
                                    elif isinstance(monster, str):
                                        # Handle string format like "1 Tainted Naiad"
                                        # Extract just the monster name
                                        match = re.search(r'\d*\s*(.+?)(?:\s*\(|$)', monster)
                                        if match:
                                            monster_name = match.group(1).strip()
                                            monster_id = monster_name.lower().replace(' ', '_')
                                            monster_ids.add(monster_id)
        
        # Also scan the monsters folder for this module
        monsters_dir = os.path.join('modules', module_name, 'monsters')
        if os.path.exists(monsters_dir):
            for filename in os.listdir(monsters_dir):
                if filename.endswith('.json'):
                    # Extract monster ID from filename
                    # e.g., "bandit_captain_gorvek.json" -> "bandit_captain_gorvek"
                    monster_id = filename[:-5]  # Remove .json extension
                    monster_ids.add(monster_id)

        info(f"TOOLKIT: Found {len(monster_ids)} unique monsters in module {module_name}: {list(monster_ids)[:5]}...")
        return jsonify(list(monster_ids))
        
    except Exception as e:
        error(f"TOOLKIT: Failed to get monsters for module {module_name}: {e}")
        return jsonify({'error': str(e)}), 500

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

@socketio.on('request_party_data')
def handle_party_data_request():
    """Handle requests for party member display (non-combat)."""
    try:
        from utils.file_operations import safe_read_json
        from utils.module_path_manager import ModulePathManager
        from updates.update_character_info import normalize_character_name, find_character_file_fuzzy
        
        # Load party tracker
        party_tracker = safe_read_json("party_tracker.json")
        if not party_tracker:
            emit('party_data_response', {'members': []})
            return
        
        # Get module info for path resolution
        current_module = party_tracker.get("module", "").replace(" ", "_")
        path_manager = ModulePathManager(current_module)
        
        party_members = []
        
        # Add player first
        if party_tracker.get('partyMembers') and len(party_tracker['partyMembers']) > 0:
            player_name = normalize_character_name(party_tracker['partyMembers'][0])
            
            # Try to load player data for HP info
            try:
                player_file = path_manager.get_character_path(player_name)
                if os.path.exists(player_file):
                    player_data = safe_read_json(player_file)
                    if player_data:
                        party_members.append({
                            'name': player_data.get('name', player_name),
                            'type': 'player',
                            'currentHp': player_data.get('currentHp', 0),
                            'maxHp': player_data.get('maxHp', 0)
                        })
            except:
                # Fallback if can't load player data
                party_members.append({
                    'name': player_name,
                    'type': 'player'
                })
        
        # Add NPCs in order
        for npc_info in party_tracker.get('partyNPCs', []):
            npc_name = npc_info['name']
            
            try:
                # Use fuzzy matching to find NPC file
                matched_name = find_character_file_fuzzy(npc_name)
                if matched_name:
                    npc_file = path_manager.get_character_path(matched_name)
                    if os.path.exists(npc_file):
                        npc_data = safe_read_json(npc_file)
                        if npc_data:
                            party_members.append({
                                'name': npc_data.get('name', npc_name),
                                'type': 'npc',
                                'currentHp': npc_data.get('currentHp', 0),
                                'maxHp': npc_data.get('maxHp', 0)
                            })
                            continue
            except:
                pass
            
            # Fallback if can't load NPC data
            party_members.append({
                'name': npc_name,
                'type': 'npc'
            })
        
        emit('party_data_response', {'members': party_members})
        
    except Exception as e:
        error(f"Failed to get party data: {str(e)}", exception=e, category="web_interface")
        emit('party_data_response', {'members': []})

@socketio.on('request_initiative_data')
def handle_initiative_data_request():
    """Handles requests for the current combat initiative order."""
    try:
        from utils.file_operations import safe_read_json
        
        # Check if combat is active via party_tracker.json
        party_tracker = safe_read_json("party_tracker.json")
        if not party_tracker:
            emit('initiative_data_response', {'active': False, 'combatants': []})
            return

        # Get the active combat encounter ID
        active_encounter_id = party_tracker.get("worldConditions", {}).get("activeCombatEncounter")
        if not active_encounter_id:
            # No combat is active
            emit('initiative_data_response', {'active': False, 'combatants': []})
            return

        # Load the specific encounter file
        encounter_file = f"modules/encounters/encounter_{active_encounter_id}.json"
        encounter_data = safe_read_json(encounter_file)
        if not encounter_data or "creatures" not in encounter_data:
            emit('initiative_data_response', {'active': False, 'combatants': []})
            return

        # Filter for living combatants only
        living_combatants = [
            c for c in encounter_data["creatures"] 
            if c.get("status", "unknown").lower() == "alive"
        ]
        
        if not living_combatants:
            # Combat is over if no one is alive
            emit('initiative_data_response', {'active': False, 'combatants': []})
            return

        # Sort by initiative (highest first)
        sorted_combatants = sorted(
            living_combatants, 
            key=lambda x: x.get("initiative", 0), 
            reverse=True
        )

        # Prepare clean data for frontend
        combatant_list = [
            {
                "name": c.get("name"),
                "type": c.get("type"),  # 'player', 'npc', or 'enemy'
                "initiative": c.get("initiative"),
                "currentHp": c.get("currentHitPoints"),
                "maxHp": c.get("maxHitPoints"),
                "monsterType": c.get("monsterType"),  # For enemy type lookup
                "class": c.get("class")  # For NPC class lookup
            }
            for c in sorted_combatants
        ]

        # Send the data to the browser
        emit('initiative_data_response', {
            'active': True, 
            'combatants': combatant_list,
            'round': encounter_data.get('combat_round', 1)
        })

    except Exception as e:
        error(f"Error handling initiative data request: {e}", exception=e, category="web_interface")
        emit('initiative_data_response', {'active': False, 'combatants': []})

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
            # Generate image using DALL-E 3
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
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
        # Handle other errors with more detail
        import traceback
        error_msg = f"Game error: {str(e)}"
        try:
            print(f"Game loop error: {error_msg}")
            print(f"Traceback: {traceback.format_exc()}")
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
    last_token_update = time.time()
    
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
            
            # Try to send token updates every 2 seconds (completely isolated)
            current_time = time.time()
            if current_time - last_token_update > 2:
                last_token_update = current_time  # Update time FIRST to prevent retry loops
                try:
                    # Try to import and get stats
                    from utils.openai_usage_tracker import get_usage_stats
                    stats = get_usage_stats()
                    # Send to UI silently
                    socketio.emit('token_update', {
                        'tpm': stats.get('tpm', 0),
                        'rpm': stats.get('rpm', 0),
                        'total_tokens': stats.get('total_tokens', 0)
                    })
                except:
                    # If anything fails, just send zeros (but don't spam)
                    try:
                        socketio.emit('token_update', {
                            'tpm': 0,
                            'rpm': 0,
                            'total_tokens': 0
                        })
                    except:
                        pass  # Even sending zeros failed, just skip
                        
        except Exception:
            # If any other error occurs, just continue
            pass
        
        time.sleep(0.1)  # Small delay to prevent CPU spinning

def send_output_to_clients_original():
    """Send queued output to all connected clients"""
    last_token_update = time.time()
    
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
            
            # Send token updates every 2 seconds
            current_time = time.time()
            if current_time - last_token_update > 2:
                try:
                    from utils.token_tracker import get_tracker
                    tracker = get_tracker()
                    stats = tracker.get_stats()
                    socketio.emit('token_update', {
                        'tpm': stats['tpm'],
                        'rpm': stats['rpm'],
                        'total_tokens': stats['total_tokens']
                    })
                except (ImportError, AttributeError, Exception):
                    # If token tracking fails for any reason, send zeros to UI
                    # Don't let token errors block the main output processing
                    try:
                        socketio.emit('token_update', {
                            'tpm': 0,
                            'rpm': 0,
                            'total_tokens': 0
                        })
                    except Exception:
                        # If even sending zeros fails, just skip token updates
                        pass
                finally:
                    # Always update the timestamp to prevent infinite retries
                    last_token_update = current_time
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


# ============================================================================
# NPC MANAGEMENT API ENDPOINTS
# ============================================================================

@app.route('/api/toolkit/modules/<module_name>/npcs')
def get_module_npcs(module_name):
    """
    Scans a module for NPCs and checks for portraits in the pack's npcs/ folder
    and optionally in the live game folder.
    """
    if not TOOLKIT_AVAILABLE:
        return jsonify([]), 503
    
    pack_name = request.args.get('pack')
    include_local = request.args.get('include_local', 'false').lower() == 'true'

    if not pack_name:
        return jsonify({'error': 'A target pack must be specified.'}), 400
        
    try:
        import os
        from utils.file_operations import safe_read_json
        
        npcs_found = {}
        
        # Always scan a module to get the list of required NPCs
        areas_dir = os.path.join('modules', module_name, 'areas')
        if os.path.exists(areas_dir):
            for filename in os.listdir(areas_dir):
                if filename.endswith('_BU.json'):
                    area_path = os.path.join(areas_dir, filename)
                    area_data = safe_read_json(area_path)
                    if area_data and 'locations' in area_data:
                        for location in area_data.get('locations', []):
                            if 'npcs' in location and location['npcs']:
                                for npc in location['npcs']:
                                    if isinstance(npc, dict) and 'name' in npc:
                                        npc_name = npc['name']
                                        npc_id = npc_name.lower().replace(' ', '_').replace("'", "").replace("-", "_")
                                        if npc_id not in npcs_found:
                                            npcs_found[npc_id] = {'name': npc_name, 'id': npc_id}
                                    elif isinstance(npc, str):
                                        npc_name = npc
                                        npc_id = npc_name.lower().replace(' ', '_').replace("'", "").replace("-", "_")
                                        if npc_id not in npcs_found:
                                            npcs_found[npc_id] = {'name': npc_name, 'id': npc_id}

        # Check portrait existence based on findings
        npc_list = []
        pack_npcs_dir = os.path.join('graphic_packs', pack_name, 'npcs')
        local_npcs_dir = os.path.join('web', 'static', 'media', 'npcs')  # Correct NPC location
        
        for npc_id, npc_info in npcs_found.items():
            result = {
                'name': npc_info['name'],
                'id': npc_id,
                'has_portrait': False,
                'is_local': False,
                'pack_name': pack_name,
            }

            # Check 1: In the pack's 'npcs' folder
            if os.path.exists(pack_npcs_dir):
                for ext in ['.png', '.jpg', '_thumb.png', '_thumb.jpg']:
                    if os.path.exists(os.path.join(pack_npcs_dir, f'{npc_id}{ext}')):
                        result['has_portrait'] = True
                        break

            # Check 2: In the live 'web/static/media/npcs' folder (if requested)
            if include_local:
                # Check for any NPC asset in the game folder
                if os.path.exists(local_npcs_dir):
                    for ext in ['.png', '.jpg', '_thumb.png', '_thumb.jpg', '_video.mp4']:
                        if os.path.exists(os.path.join(local_npcs_dir, f'{npc_id}{ext}')):
                            result['is_local'] = True
                            break

            npc_list.append(result)
        
        npc_list.sort(key=lambda x: x['name'])
        
        info(f"TOOLKIT: Found {len(npc_list)} NPCs for module '{module_name}' (Include Local: {include_local})")
        return jsonify(npc_list)
        
    except Exception as e:
        error(f"TOOLKIT: Failed to get NPCs for module {module_name}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/toolkit/npcs/fetch-descriptions', methods=['POST'])
def fetch_npc_descriptions():
    """
    Receives a list of NPC names and starts a background task to generate descriptions.
    """
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'}), 503
    
    data = request.json
    module_name = data.get('module_name')
    npcs = data.get('npcs', [])

    if not module_name or not npcs:
        return jsonify({'success': False, 'error': 'Missing module name or NPC list'}), 400

    # Start background thread for description generation
    def generate_descriptions():
        try:
            import time
            from openai import OpenAI
            from utils.file_operations import safe_read_json, safe_write_json
            from utils.encoding_utils import sanitize_text
            
            # Get API key
            try:
                from config import OPENAI_API_KEY
            except ImportError:
                OPENAI_API_KEY = None
                error("TOOLKIT: OpenAI API key not found")
                return
            
            if not OPENAI_API_KEY:
                error("TOOLKIT: OpenAI API key not configured")
                return
                
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            # Load or create descriptions file
            descriptions_file = f'temp/npc_descriptions_{module_name}.json'
            os.makedirs('temp', exist_ok=True)
            
            existing_descriptions = safe_read_json(descriptions_file) or {}
            
            # Extract module context
            module_context = extract_module_context_for_npcs(module_name)
            
            # Generate description for each NPC
            for i, npc_data in enumerate(npcs):
                npc_name = npc_data['name']
                npc_id = npc_data['id']
                
                # Skip if description already exists
                if npc_id in existing_descriptions:
                    info(f"TOOLKIT: Description already exists for {npc_name}, skipping")
                    continue
                
                # Prepare a new, more directive prompt
                prompt = f"""Generate a rich, descriptive prompt for an AI image generator to create a fantasy character portrait.

NPC Name: {npc_name}
Module Context: {module_context[:2500]}

The output should be a single paragraph (150-200 words) that is itself a high-quality image prompt. It must include:
1.  **Physical Appearance:** Race, build, key features.
2.  **Clothing & Gear:** Detailed description of their armor, clothes, and weapons (sheathed or at rest).
3.  **Background/Setting:** A description of the environment (e.g., 'standing in a sun-dappled ancient forest', 'leaning against a table in a rustic tavern', 'in a dimly lit dungeon corridor').
4.  **Atmosphere & Lighting:** Keywords for the mood (e.g., 'cinematic lighting', 'magical aura', 'dust motes in the air', 'soft morning light').

The character must appear friendly, capable, and trustworthy, like a potential party ally. Do NOT use words like 'photorealistic', 'photo', 'cosplay', '3D render'. Focus on descriptive language for a digital painting.

Example Output Format:
"A stunning digital painting of Elara, a female wood elf ranger with emerald green eyes and long braided auburn hair. She wears masterfully crafted green leather armor with leaf-like patterns. A longbow is slung over her shoulder and a sheathed shortsword hangs at her hip. She stands in a misty, ancient forest at dawn, with golden morning light filtering through the canopy, creating a magical and serene atmosphere."
"""

                try:
                    # Call OpenAI API with the new system message and prompt
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are an expert AI prompt engineer specializing in fantasy character art. Your task is to write image generation prompts, not narrative descriptions. The prompts you write will be used to create digital paintings."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.8
                    )
                    
                    description = response.choices[0].message.content
                    description = sanitize_text(description)
                    
                    # Save description
                    existing_descriptions[npc_id] = {
                        'name': npc_name,
                        'description': description,
                        'generated_at': datetime.now().isoformat()
                    }
                    
                    # Write back to file
                    safe_write_json(descriptions_file, existing_descriptions)
                    
                    info(f"TOOLKIT: Generated description for {npc_name} ({i+1}/{len(npcs)})")
                    
                    # Emit progress via SocketIO
                    socketio.emit('npc_description_progress', {
                        'current': i + 1,
                        'total': len(npcs),
                        'npc_name': npc_name,
                        'status': 'success'
                    })
                    
                    # Rate limiting
                    time.sleep(2)  # Wait 2 seconds between requests
                    
                except Exception as e:
                    error(f"TOOLKIT: Failed to generate description for {npc_name}: {e}")
                    socketio.emit('npc_description_progress', {
                        'current': i + 1,
                        'total': len(npcs),
                        'npc_name': npc_name,
                        'status': 'error',
                        'error': str(e)
                    })
            
            info(f"TOOLKIT: Completed description generation for module {module_name}")
            
        except Exception as e:
            error(f"TOOLKIT: Description generation failed: {e}")
    
    # Start background thread
    thread = threading.Thread(target=generate_descriptions)
    thread.daemon = True
    thread.start()
    
    info(f"TOOLKIT: Started description generation for {len(npcs)} NPCs in {module_name}")
    return jsonify({'success': True, 'message': 'Description generation started.'})

def extract_module_context_for_npcs(module_name):
    """Extract context from module for NPC description generation"""
    try:
        from utils.file_operations import safe_read_json
        import os
        
        context_parts = []
        context_parts.append(f"Module: {module_name.replace('_', ' ').title()}\n")
        
        # Read module plot if available
        plot_file = os.path.join('modules', module_name, 'module_plot.json')
        plot_data = safe_read_json(plot_file)
        if plot_data:
            if 'current_quest' in plot_data:
                context_parts.append(f"Current Quest: {plot_data['current_quest']}\n")
            if 'setting' in plot_data:
                context_parts.append(f"Setting: {plot_data['setting']}\n")
        
        # Sample area descriptions for context
        areas_dir = os.path.join('modules', module_name, 'areas')
        if os.path.exists(areas_dir):
            area_count = 0
            for filename in os.listdir(areas_dir):
                if filename.endswith('_BU.json') and area_count < 3:  # Limit to 3 areas
                    area_path = os.path.join(areas_dir, filename)
                    area_data = safe_read_json(area_path)
                    if area_data:
                        area_name = area_data.get('areaName', 'Unknown Area')
                        area_desc = area_data.get('areaDescription', '')[:200]
                        context_parts.append(f"\nArea: {area_name}\n{area_desc}")
                        area_count += 1
        
        return '\n'.join(context_parts)
    except Exception as e:
        error(f"Failed to extract module context: {e}")
        return f"Adventure module: {module_name}"

@app.route('/api/toolkit/npcs/description', methods=['GET', 'POST'])
def handle_npc_description():
    """
    Gets or sets a single NPC's description from the temporary JSON file.
    """
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'}), 503

    if request.method == 'GET':
        module_name = request.args.get('module')
        npc_id = request.args.get('npc_id')
        
        if not module_name or not npc_id:
            return jsonify({'error': 'Missing module or NPC ID'}), 400
        
        try:
            from utils.file_operations import safe_read_json
            
            descriptions_file = f'temp/npc_descriptions_{module_name}.json'
            descriptions = safe_read_json(descriptions_file) or {}
            
            if npc_id in descriptions:
                return jsonify({'description': descriptions[npc_id].get('description', '')})
            else:
                return jsonify({'description': ''})
                
        except Exception as e:
            error(f"TOOLKIT: Failed to load NPC description: {e}")
            return jsonify({'error': str(e)}), 500
    
    if request.method == 'POST':
        data = request.json
        module_name = data.get('module_name')
        npc_id = data.get('npc_id')
        npc_name = data.get('npc_name')
        description = data.get('description')
        
        if not all([module_name, npc_id, description]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        try:
            from utils.file_operations import safe_read_json, safe_write_json
            from utils.encoding_utils import sanitize_text
            
            descriptions_file = f'temp/npc_descriptions_{module_name}.json'
            os.makedirs('temp', exist_ok=True)
            
            descriptions = safe_read_json(descriptions_file) or {}
            descriptions[npc_id] = {
                'name': npc_name,
                'description': sanitize_text(description),
                'updated_at': datetime.now().isoformat()
            }
            
            safe_write_json(descriptions_file, descriptions)
            
            info(f"TOOLKIT: Description for NPC '{npc_name}' (ID: {npc_id}) was updated")
            return jsonify({'success': True})
            
        except Exception as e:
            error(f"TOOLKIT: Failed to save NPC description: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/toolkit/npcs/generate-portraits', methods=['POST'])
def generate_npc_portraits():
    """Generate portrait images for selected NPCs using NPCGenerator"""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'}), 503
    
    data = request.json
    module_name = data.get('module_name')
    pack_name = data.get('pack_name')
    model = data.get('model', 'dall-e-3')
    style = data.get('style', 'photorealistic')
    style_prompt = data.get('style_prompt', '')
    npcs = data.get('npcs', [])
    
    if not all([module_name, pack_name, npcs]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    # Start background thread for portrait generation
    def generate_portraits():
        try:
            from core.toolkit.npc_generator import NPCGenerator
            from utils.file_operations import safe_read_json
            import asyncio
            
            # Get API key
            try:
                from config import OPENAI_API_KEY
            except ImportError:
                OPENAI_API_KEY = None
                error("TOOLKIT: OpenAI API key not found")
                return
            
            if not OPENAI_API_KEY:
                error("TOOLKIT: OpenAI API key not configured")
                return
                
            # Initialize NPC generator
            generator = NPCGenerator(api_key=OPENAI_API_KEY)
            
            # Load descriptions
            descriptions_file = f'temp/npc_descriptions_{module_name}.json'
            descriptions = safe_read_json(descriptions_file) or {}
            
            # Prepare NPC data with descriptions
            npcs_with_descriptions = []
            for npc_data in npcs:
                npc_id = npc_data['id']
                npc_name = npc_data['name']
                
                # Get description
                npc_desc_data = descriptions.get(npc_id, {})
                description = npc_desc_data.get('description', f'A fantasy NPC named {npc_name}')
                
                npcs_with_descriptions.append({
                    'id': npc_id,
                    'name': npc_name,
                    'description': description
                })
            
            # Create progress callback
            def progress_callback(progress_data):
                socketio.emit('npc_portrait_progress', progress_data)
            
            # Run the async batch generation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                generator.batch_generate_portraits(
                    npcs=npcs_with_descriptions,
                    pack_name=pack_name,
                    style=style,
                    model=model,
                    progress_callback=progress_callback
                )
            )
            
            # Update pack manifest to include NPC count
            update_pack_manifest_with_npcs(pack_name)
            
            # Log results
            info(f"TOOLKIT: Completed portrait generation - {len(result['successful'])} successful, {len(result['failed'])} failed")
            
            # Emit completion with detailed results
            socketio.emit('npc_generation_complete', {
                'module_name': module_name,
                'pack_name': pack_name,
                'successful': result.get('successful', []),
                'failed': result.get('failed', []),
                'total': len(result.get('successful', [])) + len(result.get('failed', []))
            })
            
        except Exception as e:
            error(f"TOOLKIT: Portrait generation failed: {e}")
    
    # Start background thread
    thread = threading.Thread(target=generate_portraits)
    thread.daemon = True
    thread.start()
    
    info(f"TOOLKIT: Started portrait generation for {len(npcs)} NPCs")
    return jsonify({'success': True, 'message': 'Portrait generation started.'})

def update_pack_manifest_with_npcs(pack_name):
    """Update pack manifest to include NPC information"""
    try:
        from utils.file_operations import safe_read_json, safe_write_json
        import os
        
        manifest_path = os.path.join('graphic_packs', pack_name, 'manifest.json')
        manifest = safe_read_json(manifest_path) or {}
        
        # Count NPCs
        npcs_dir = os.path.join('graphic_packs', pack_name, 'npcs')
        npc_count = 0
        npc_list = []
        
        if os.path.exists(npcs_dir):
            for filename in os.listdir(npcs_dir):
                if filename.endswith('.png') and not filename.endswith('_thumb.png'):
                    npc_id = filename[:-4]  # Remove .png
                    npc_list.append(npc_id)
                    npc_count += 1
        
        # Update manifest
        manifest['total_npcs'] = npc_count
        manifest['npcs_included'] = sorted(npc_list)
        manifest['last_modified'] = datetime.now().strftime("%Y-%m-%d")
        
        safe_write_json(manifest_path, manifest)
        info(f"TOOLKIT: Updated manifest for pack '{pack_name}' with {npc_count} NPCs")
        
    except Exception as e:
        error(f"TOOLKIT: Failed to update pack manifest: {e}")

def create_live_assets_backup_pack():
    """
    Creates a backup pack from the current live game assets.
    This preserves ALL assets currently in use, regardless of their source.
    """
    try:
        import os
        import shutil
        from datetime import datetime
        import json
        
        # Generate backup pack name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"live_backup_{timestamp}"
        backup_dir = os.path.join('graphic_packs', backup_name)
        
        # Create the backup pack directory
        os.makedirs(backup_dir, exist_ok=True)
        
        # Define source and destination paths
        live_monsters_dir = os.path.join('web', 'static', 'media', 'monsters')
        live_npcs_dir = os.path.join('web', 'static', 'media', 'npcs')
        backup_monsters_dir = os.path.join(backup_dir, 'monsters')
        backup_npcs_dir = os.path.join(backup_dir, 'npcs')
        
        copied_monsters = 0
        copied_npcs = 0
        
        # Copy monster assets if they exist
        if os.path.exists(live_monsters_dir) and os.listdir(live_monsters_dir):
            os.makedirs(backup_monsters_dir, exist_ok=True)
            for filename in os.listdir(live_monsters_dir):
                src_path = os.path.join(live_monsters_dir, filename)
                dest_path = os.path.join(backup_monsters_dir, filename)
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dest_path)
                    copied_monsters += 1
        
        # Copy NPC assets if they exist
        if os.path.exists(live_npcs_dir) and os.listdir(live_npcs_dir):
            os.makedirs(backup_npcs_dir, exist_ok=True)
            for filename in os.listdir(live_npcs_dir):
                src_path = os.path.join(live_npcs_dir, filename)
                dest_path = os.path.join(backup_npcs_dir, filename)
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dest_path)
                    copied_npcs += 1
        
        # Create manifest for the backup pack
        manifest = {
            "name": backup_name,
            "display_name": f"Live Assets Backup ({datetime.now().strftime('%Y-%m-%d %H:%M')})",
            "description": f"Automatic backup of all live game assets. Contains {copied_monsters} monster files and {copied_npcs} NPC files.",
            "is_backup": True,
            "backup_type": "live_assets",
            "backup_date": datetime.now().isoformat(),
            "monster_count": copied_monsters,
            "npc_count": copied_npcs,
            "created_by": "System"
        }
        
        manifest_path = os.path.join(backup_dir, 'manifest.json')
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        info(f"TOOLKIT: Created live assets backup pack '{backup_name}' with {copied_monsters} monsters and {copied_npcs} NPCs")
        
        return {
            "success": True,
            "backup_name": backup_name,
            "monsters": copied_monsters,
            "npcs": copied_npcs
        }
        
    except Exception as e:
        error(f"TOOLKIT: Failed to create live assets backup: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def copy_pack_monsters_to_game(pack_name):
    """
    Replaces live monster assets with assets from the specified pack.
    Note: Backup should be done at pack level before calling this.
    """
    try:
        import os
        import shutil

        # Define source and destination paths
        source_dir = os.path.join('graphic_packs', pack_name, 'monsters')
        live_dir = os.path.join('web', 'static', 'media', 'monsters')

        if not os.path.exists(source_dir):
            info(f"TOOLKIT: Pack '{pack_name}' has no 'monsters' folder. Skipping monster asset copy.")
            return

        # Clear existing live directory
        if os.path.exists(live_dir):
            shutil.rmtree(live_dir)
        
        # Create fresh live directory
        os.makedirs(live_dir, exist_ok=True)

        # 3. Copy all files from the pack's monster folder to the live folder
        copied_count = 0
        for filename in os.listdir(source_dir):
            src_path = os.path.join(source_dir, filename)
            dest_path = os.path.join(live_dir, filename)
            if os.path.isfile(src_path):
                shutil.copy2(src_path, dest_path)
                copied_count += 1
        
        info(f"TOOLKIT: Copied {copied_count} monster files from pack '{pack_name}' to live game folder.")

    except Exception as e:
        error(f"TOOLKIT: Failed to copy monster assets to game folder: {e}")

def copy_pack_npcs_to_game(pack_name):
    """
    Replaces live NPC assets with assets from the specified pack.
    Note: Backup should be done at pack level before calling this.
    """
    try:
        import os
        import shutil
        
        pack_npcs_dir = os.path.join('graphic_packs', pack_name, 'npcs')
        game_npcs_dir = os.path.join('web', 'static', 'media', 'npcs')
        
        if not os.path.exists(pack_npcs_dir):
            info(f"TOOLKIT: Pack '{pack_name}' has no NPCs folder")
            return
        
        # Clear existing live directory
        if os.path.exists(game_npcs_dir):
            shutil.rmtree(game_npcs_dir)
        
        # Create fresh live directory
        os.makedirs(game_npcs_dir, exist_ok=True)
        
        # Copy all NPC files to game folder
        copied_count = 0
        for filename in os.listdir(pack_npcs_dir):
            src_path = os.path.join(pack_npcs_dir, filename)
            dest_path = os.path.join(game_npcs_dir, filename)
            
            # Convert PNG thumbnails to JPG for game use
            if filename.endswith('_thumb.png'):
                from PIL import Image
                img = Image.open(src_path)
                if img.mode == 'RGBA':
                    # Convert RGBA to RGB for JPG
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[3] if len(img.split()) > 3 else None)
                    img = rgb_img
                jpg_filename = filename[:-4] + '.jpg'  # Replace .png with .jpg
                jpg_path = os.path.join(game_npcs_dir, jpg_filename)
                img.save(jpg_path, 'JPEG', quality=85)
                info(f"TOOLKIT: Converted {filename} to {jpg_filename}")
            else:
                # Copy other files as-is
                shutil.copy2(src_path, dest_path)
                copied_count += 1
        
        info(f"TOOLKIT: Copied {copied_count} NPC files from pack '{pack_name}' to game folder")
        
    except Exception as e:
        error(f"TOOLKIT: Failed to copy NPCs to game folder: {e}")

@app.route('/api/toolkit/packs/<pack_name>/npcs/<npc_id>/thumbnail')
def get_npc_thumbnail(pack_name, npc_id):
    """Serve NPC thumbnail image from a specific graphic pack."""
    if not TOOLKIT_AVAILABLE:
        return '', 404
    
    try:
        from flask import send_from_directory
        import os
        
        npcs_dir = os.path.abspath(os.path.join('graphic_packs', pack_name, 'npcs'))
        
        # Try to find a thumbnail first (png or jpg)
        for ext in ['.png', '.jpg']:
            thumb_filename = f'{npc_id}_thumb{ext}'
            thumb_path = os.path.join(npcs_dir, thumb_filename)
            if os.path.exists(thumb_path):
                info(f"TOOLKIT: Serving NPC thumbnail {thumb_filename} from {pack_name}")
                return send_from_directory(npcs_dir, thumb_filename)
        
        # If no thumbnail, try to find the full portrait
        for ext in ['.png', '.jpg']:
            portrait_filename = f'{npc_id}{ext}'
            portrait_path = os.path.join(npcs_dir, portrait_filename)
            if os.path.exists(portrait_path):
                info(f"TOOLKIT: Serving NPC portrait {portrait_filename} from {pack_name}")
                return send_from_directory(npcs_dir, portrait_filename)
        
        # If nothing is found, return a 404
        warning(f"TOOLKIT: No image found for NPC {npc_id} in {pack_name}")
        return '', 404
        
    except Exception as e:
        error(f"TOOLKIT: Failed to serve NPC thumbnail for {npc_id} in {pack_name}: {e}")
        return '', 500

@app.route('/api/toolkit/packs/<pack_name>/npcs/<npc_id>/image')
def get_npc_image(pack_name, npc_id):
    """Serve full NPC image from a specific graphic pack."""
    if not TOOLKIT_AVAILABLE:
        return '', 404
    
    try:
        from flask import send_from_directory
        import os
        
        npcs_dir = os.path.abspath(os.path.join('graphic_packs', pack_name, 'npcs'))
        
        # Try to find the full image (png or jpg)
        for ext in ['.png', '.jpg']:
            image_filename = f'{npc_id}{ext}'
            image_path = os.path.join(npcs_dir, image_filename)
            if os.path.exists(image_path):
                info(f"TOOLKIT: Serving NPC image {image_filename} from {pack_name}")
                return send_from_directory(npcs_dir, image_filename)
        
        warning(f"TOOLKIT: No full image found for NPC {npc_id} in {pack_name}")
        return '', 404
        
    except Exception as e:
        error(f"TOOLKIT: Failed to serve NPC image for {npc_id} in {pack_name}: {e}")
        return '', 500

@app.route('/api/toolkit/packs/<pack_name>/npcs/<npc_id>/video')
def get_npc_video(pack_name, npc_id):
    """Serve NPC video from a specific graphic pack."""
    if not TOOLKIT_AVAILABLE:
        return '', 404
    
    try:
        from flask import send_from_directory
        import os
        
        npcs_dir = os.path.abspath(os.path.join('graphic_packs', pack_name, 'npcs'))
        
        # Try to find video files with different naming patterns
        video_patterns = [
            f'{npc_id}_video.mp4',
            f'{npc_id}_video_low.mp4',
            f'{npc_id}.mp4'
        ]
        
        for video_filename in video_patterns:
            video_path = os.path.join(npcs_dir, video_filename)
            if os.path.exists(video_path):
                info(f"TOOLKIT: Serving NPC video {video_filename} from {pack_name}")
                return send_from_directory(npcs_dir, video_filename)
        
        warning(f"TOOLKIT: No video found for NPC {npc_id} in {pack_name}")
        return '', 404
        
    except Exception as e:
        error(f"TOOLKIT: Failed to serve NPC video for {npc_id} in {pack_name}: {e}")
        return '', 500

@app.route('/api/toolkit/npcs/export-to-pack', methods=['POST'])
def export_npcs_to_pack():
    """Copies selected NPC portraits from the live game folder to a specified pack."""
    if not TOOLKIT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Toolkit not available'}), 503
        
    try:
        import os
        import shutil
        
        data = request.json
        pack_name = data.get('pack_name')
        npc_ids = data.get('npc_ids', [])

        if not pack_name or not npc_ids:
            return jsonify({'success': False, 'error': 'Missing pack name or NPC IDs.'}), 400

        source_dir = os.path.join('web', 'static', 'media', 'npcs')  # Correct NPC location
        dest_dir = os.path.join('graphic_packs', pack_name, 'npcs')
        os.makedirs(dest_dir, exist_ok=True)

        exported_count = 0
        skipped_count = 0

        for npc_id in npc_ids:
            exported = False
            # Try to export any NPC asset found (image, thumbnail, or video)
            for ext in ['.png', '.jpg', '_thumb.png', '_thumb.jpg', '_video.mp4']:
                source_file = os.path.join(source_dir, f"{npc_id}{ext}")
                if os.path.exists(source_file):
                    dest_file = os.path.join(dest_dir, f"{npc_id}{ext}")
                    shutil.copy2(source_file, dest_file)
                    if not exported:  # Count once per NPC, not per file
                        exported_count += 1
                        exported = True
                    info(f"TOOLKIT: Exported NPC asset '{npc_id}{ext}' to pack '{pack_name}'")
            
            if not exported:
                skipped_count += 1
                warning(f"TOOLKIT: Could not find any assets for '{npc_id}' in local game files to export.")

        # After exporting, update the destination pack's manifest
        update_pack_manifest_with_npcs(pack_name)

        info(f"TOOLKIT: Export complete - {exported_count} portraits exported, {skipped_count} skipped")
        return jsonify({
            'success': True,
            'message': f"Exported {exported_count} NPC portraits to '{pack_name}'.",
            'exported_count': exported_count,
            'skipped_count': skipped_count
        })

    except Exception as e:
        error(f"TOOLKIT: Failed to export NPCs to pack: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# MODULE BUILDER SOCKET HANDLERS
# ============================================================================

# In-memory state for the build process to handle cancellation
build_process_thread = None
cancel_build_flag = threading.Event()

@socketio.on('request_module_list')
def handle_request_module_list():
    """Scans for modules using the ModuleStitcher and returns a detailed list."""
    try:
        # This function provides all the necessary details: level, areas, locations, etc.
        from core.generators.module_stitcher import list_available_modules
        
        detailed_modules = list_available_modules()
        info(f"MODULE_BUILDER: Found {len(detailed_modules)} modules to display.")
        
        # The frontend is already set up to handle this detailed data structure.
        emit('module_list_response', detailed_modules)
        
    except Exception as e:
        error(f"Error fetching detailed module list: {e}")
        emit('module_list_response', [])  # Send an empty list on error

def simulate_build_process(params):
    """A target function for a thread that simulates module creation."""
    global cancel_build_flag
    cancel_build_flag.clear()

    stages = [
        (0, "Initializing", "Starting module creation..."),
        (1, "Base Structure", "Generating core module files..."),
        (2, "NPCs", "Creating unique NPCs and factions..."),
        (3, "Monsters", "Populating bestiary for the module..."),
        (4, "Areas", "Designing distinct areas and environments..."),
        (5, "Plots", "Weaving main and side quests..."),
        (6, "Connections", "Building the location graph..."),
        (7, "Finalizing", "Compiling all module data..."),
        (8, "Saving", "Saving module to disk..."),
    ]
    total_stages = len(stages)

    try:
        for i, (stage_num, stage_name, message) in enumerate(stages):
            if cancel_build_flag.is_set():
                socketio.emit('build_cancelled', {'message': 'Build cancelled by user.'})
                return

            percentage = ((i + 1) / total_stages) * 100
            socketio.emit('module_progress', {
                'stage': stage_num,
                'stage_name': stage_name,
                'percentage': percentage,
                'message': message
            })
            time.sleep(2) # Simulate work

        # Simulate creating the folder
        module_dir = os.path.join('modules', params['module_name'])
        os.makedirs(module_dir, exist_ok=True)
        # Create a dummy manifest
        dummy_manifest = {
            "name": params['module_name'],
            "display_name": params['module_name'].replace('_', ' ').title(),
            "description": params['narrative'][:150] + '...',
            "level_range": {"min": 1, "max": 5},
            "area_count": params['num_areas'],
            "location_count": params['num_areas'] * params['locations_per_area']
        }
        with open(os.path.join(module_dir, f"{params['module_name']}_manifest.json"), 'w') as f:
            json.dump(dummy_manifest, f, indent=4)

        socketio.emit('module_complete', {
            'module_name': params['module_name'],
            'message': 'Module generation finished.'
        })

    except Exception as e:
        error(f"Module build failed: {e}")
        socketio.emit('module_error', {'error': str(e)})


@socketio.on('start_build')
def handle_start_build(data):
    """Starts the module build process in a background thread."""
    global build_process_thread
    if build_process_thread and build_process_thread.is_alive():
        emit('module_error', {'error': 'A build is already in progress.'})
        return

    info(f"Starting build for module: {data.get('module_name')}")
    emit('build_started', {'message': 'Build process initiated...'})
    
    build_process_thread = threading.Thread(target=simulate_build_process, args=(data,))
    build_process_thread.start()

@socketio.on('cancel_build')
def handle_cancel_build():
    """Sets a flag to cancel the ongoing build process."""
    global cancel_build_flag
    if build_process_thread and build_process_thread.is_alive():
        info("Cancellation request received for module build.")
        cancel_build_flag.set()
    else:
        emit('module_error', {'error': 'No active build to cancel.'})

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
