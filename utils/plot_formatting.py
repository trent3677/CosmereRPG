#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 MoonlightByte
# SPDX-License-Identifier: Fair-Source-1.0
# License: See LICENSE file in the repository root
# This software is subject to the terms of the Fair Source License.

"""
Plot Formatting Module
Formats plot data from JSON into readable text for AI DM consumption
"""

def format_plot_for_ai(plot_data):
    """
    Format plot data into readable text for AI DM
    
    Args:
        plot_data (dict): The plot data from module_plot.json
        
    Returns:
        str: Formatted plot status text for AI consumption
    """
    # Handle case where plot_data might be a list or other non-dict type
    if not isinstance(plot_data, dict):
        print(f"WARNING: plot_data is not a dict, it's a {type(plot_data)}: {plot_data}")
        return "=== ADVENTURE PLOT STATUS ===\n\nNo plot data available.\n"
    
    if not plot_data or 'plotPoints' not in plot_data:
        return "=== ADVENTURE PLOT STATUS ===\n\nNo plot data available.\n"
    
    # Header
    output = "=== ADVENTURE PLOT STATUS ===\n\n"
    output += f"ADVENTURE: {plot_data.get('plotTitle', 'Unknown Adventure')}\n"
    output += f"MAIN GOAL: {plot_data.get('mainObjective', 'No objective defined')}\n\n"
    
    # Story Progress
    output += "STORY PROGRESS:\n"
    
    # Separate plot points by status
    completed_points = [p for p in plot_data['plotPoints'] if p.get('status') == 'completed']
    active_points = [p for p in plot_data['plotPoints'] if p.get('status') == 'in progress']  
    upcoming_points = [p for p in plot_data['plotPoints'] if p.get('status') == 'not started']
    
    # Completed plot points
    for point in completed_points:
        output += f"[COMPLETED]: {point.get('title', 'Untitled')} ({point.get('id', 'Unknown')})\n"
        output += f"  - {point.get('description', 'No description')}\n"
        if point.get('plotImpact'):
            output += f"  - Impact: {point['plotImpact']}\n"
        
        # Completed side quests
        completed_sqs = [sq for sq in point.get('sideQuests', []) if sq.get('status') == 'completed']
        if completed_sqs:
            output += "  - Side quests completed:\n"
            for sq in completed_sqs:
                output += f"    * {sq.get('title', 'Untitled')}\n"
        output += "\n"
    
    # Active plot points  
    for point in active_points:
        output += f"[ACTIVE]: {point.get('title', 'Untitled')} ({point.get('id', 'Unknown')})\n"
        output += f"  - {point.get('description', 'No description')}\n"
        if point.get('plotImpact'):
            output += f"  - Current situation: {point['plotImpact']}\n"
        
        # Active and completed side quests for this plot point
        active_sqs = [sq for sq in point.get('sideQuests', []) if sq.get('status') == 'in progress']
        completed_sqs = [sq for sq in point.get('sideQuests', []) if sq.get('status') == 'completed']
        
        if active_sqs:
            output += "  - Side quests in progress:\n"
            for sq in active_sqs:
                output += f"    * {sq.get('title', 'Untitled')}\n"
        if completed_sqs:
            output += "  - Side quests completed:\n"
            for sq in completed_sqs:
                output += f"    * {sq.get('title', 'Untitled')}\n"
        output += "\n"
    
    # Upcoming objectives
    if upcoming_points:
        output += "UPCOMING OBJECTIVES:\n"
        for point in upcoming_points:
            output += f"- {point.get('title', 'Untitled')} ({point.get('id', 'Unknown')}): {point.get('description', 'No description')}\n"
        output += "\n"
    
    return output


def format_plot_for_location(plot_data, current_location_id):
    """
    Format plot data with focus on current location context
    
    Args:
        plot_data (dict): The plot data from module_plot.json
        current_location_id (str): The current area/location ID
        
    Returns:
        str: Formatted plot status with location context
    """
    base_format = format_plot_for_ai(plot_data)
    
    if not current_location_id or not plot_data or 'plotPoints' not in plot_data:
        return base_format
    
    # Find plot points relevant to current location
    current_plot_points = []
    for point in plot_data['plotPoints']:
        if point.get('location') == current_location_id and point.get('status') != 'completed':
            current_plot_points.append(point)
    
    if current_plot_points:
        base_format += "CURRENT LOCATION CONTEXT:\n"
        base_format += f"The party is currently at location {current_location_id} where they can:\n"
        
        for point in current_plot_points:
            base_format += f"- Work on: {point.get('title', 'Untitled')} - {point.get('description', 'No description')}\n"
            
            # Add active side quests for this location
            active_sqs = [sq for sq in point.get('sideQuests', []) if sq.get('status') in ['not started', 'in progress']]
            for sq in active_sqs:
                if current_location_id in sq.get('involvedLocations', []):
                    base_format += f"  * Side quest: {sq.get('title', 'Untitled')}\n"
        
        base_format += "\n"
    
    return base_format