#!/usr/bin/env python3
"""
Config Updater - Automatically updates config.py with new/changed values from config_template.py
Preserves the user's API key while updating all other values to match the template.
"""

import os
import re
import shutil
from datetime import datetime

def update_config():
    """Update config.py to match config_template.py (except API key)."""
    
    # Get the root directory (parent of utils)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_file = os.path.join(root_dir, "config.py")
    template_file = os.path.join(root_dir, "config_template.py")
    
    # Check if files exist
    if not os.path.exists(config_file):
        print("[Config Updater] No config.py found. Creating from template...")
        shutil.copy(template_file, config_file)
        print("[Config Updater] Created config.py - Please add your OPENAI_API_KEY")
        return True
    
    if not os.path.exists(template_file):
        print("[Config Updater] Warning: config_template.py not found.")
        return False
    
    # Read both files
    with open(config_file, 'r') as f:
        config_lines = f.readlines()
    
    with open(template_file, 'r') as f:
        template_lines = f.readlines()
    
    # Extract API key from user's config
    api_key = None
    for line in config_lines:
        match = re.match(r'^OPENAI_API_KEY\s*=\s*(.+)$', line.strip())
        if match:
            api_key = match.group(1)
            break
    
    if not api_key or api_key == '""' or api_key == "''":
        print("[Config Updater] Warning: No valid OPENAI_API_KEY found in config.py")
    
    # Parse template to get all variables
    template_vars = {}
    for i, line in enumerate(template_lines):
        match = re.match(r'^([A-Z_]+)\s*=\s*(.+)$', line.strip())
        if match:
            var_name = match.group(1)
            var_value = match.group(2)
            template_vars[var_name] = (var_value, i, line)
    
    # Parse config to get current variables
    config_vars = {}
    for i, line in enumerate(config_lines):
        match = re.match(r'^([A-Z_]+)\s*=\s*(.+)$', line.strip())
        if match:
            var_name = match.group(1)
            var_value = match.group(2)
            config_vars[var_name] = (var_value, i, line)
    
    # Check what needs updating
    updates_needed = []
    
    # Check for missing or different values (except API key)
    for var_name, (template_value, _, _) in template_vars.items():
        if var_name == 'OPENAI_API_KEY':
            continue  # Skip API key
        
        if var_name not in config_vars:
            updates_needed.append(('ADD', var_name, template_value))
        elif config_vars[var_name][0] != template_value:
            updates_needed.append(('UPDATE', var_name, template_value))
    
    # Check for variables in config that aren't in template (deprecated)
    for var_name in config_vars:
        if var_name != 'OPENAI_API_KEY' and var_name not in template_vars:
            updates_needed.append(('REMOVE', var_name, None))
    
    if not updates_needed:
        print("[Config Updater] Config is up to date!")
        return True
    
    # Create backup
    backup_name = os.path.join(root_dir, f"config.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy(config_file, backup_name)
    print(f"[Config Updater] Created backup: {os.path.basename(backup_name)}")
    
    # Build new config content from template
    new_lines = []
    for line in template_lines:
        # Check if this is the API key line
        if line.strip().startswith('OPENAI_API_KEY'):
            if api_key:
                new_lines.append(f'OPENAI_API_KEY = {api_key}\n')
            else:
                new_lines.append(line)  # Keep template line
        else:
            new_lines.append(line)
    
    # Write updated config
    with open(config_file, 'w') as f:
        f.writelines(new_lines)
    
    # Report changes
    print(f"[Config Updater] Updated config.py with {len(updates_needed)} changes:")
    for action, var_name, value in updates_needed:
        if action == 'ADD':
            print(f"  + Added: {var_name}")
        elif action == 'UPDATE':
            print(f"  ~ Updated: {var_name}")
        elif action == 'REMOVE':
            print(f"  - Removed: {var_name} (deprecated)")
    
    print("[Config Updater] Config update complete!")
    return True

if __name__ == "__main__":
    update_config()