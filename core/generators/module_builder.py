# SPDX-FileCopyrightText: 2024 MoonlightByte
# SPDX-License-Identifier: Fair-Source-1.0
# License: See LICENSE file in the repository root
# This software is subject to the terms of the Fair Source License.

"""
NeverEndingQuest Core Engine - Module Builder
Copyright (c) 2024 MoonlightByte
Licensed under Fair Source License 1.0

This software is free for non-commercial and educational use.
Commercial competing use is prohibited for 2 years from release.
See LICENSE file for full terms.
"""

#!/usr/bin/env python3
"""
Master Module Builder
Orchestrates the generation of a complete 5th edition module by calling generators in the proper sequence.
"""

import json
import os
import shutil
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add parent directories to Python path for imports when run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import all generators - handle both direct execution and module import
try:
    # Try relative imports first (when imported as module)
    from .module_generator import ModuleGenerator
    from .plot_generator import PlotGenerator
    from .location_generator import LocationGenerator
    from .area_generator import AreaGenerator, AreaConfig
except ImportError:
    # Fall back to absolute imports (when run directly)
    from core.generators.module_generator import ModuleGenerator
    from core.generators.plot_generator import PlotGenerator
    from core.generators.location_generator import LocationGenerator
    from core.generators.area_generator import AreaGenerator, AreaConfig

from utils.module_context import ModuleContext
from utils.enhanced_logger import debug, info, warning, error, set_script_name
from utils.npc_reconciler import NpcReconciler

# Set script name for logging
set_script_name("module_builder")

@dataclass
class BuilderConfig:
    """Configuration for the module building process"""
    module_name: str = ""
    num_areas: int = 3
    locations_per_area: int = 15
    output_directory: str = "./modules"
    verbose: bool = True

class ModuleBuilder:
    """Orchestrates the complete module generation process"""
    
    def __init__(self, config: BuilderConfig):
        self.config = config
        self.module_data = {}
        self.areas_data = {}
        self.locations_data = {}
        self.plots_data = {}
        self.context = ModuleContext()
        self.progress_callback = None  # For progress reporting
        
        # Initialize generators
        self.module_gen = ModuleGenerator()
        self.plot_gen = PlotGenerator()
        self.location_gen = LocationGenerator()
        self.area_gen = AreaGenerator()
        
        # Create output directory
        os.makedirs(self.config.output_directory, exist_ok=True)
    
    def log(self, message: str):
        """Log messages if verbose mode is enabled"""
        if self.config.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"DEBUG: [Module Generator] [{timestamp}] {message}")
    
    def save_json(self, data: Dict[str, Any], filename: str):
        """Save JSON data to the output directory"""
        filepath = os.path.join(self.config.output_directory, filename)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        self.log(f"Saved: {filename}")
    
    def create_context_header(self, party_members: List[str]) -> str:
        """Create a context header to prepend to all generator prompts"""
        header = """
CRITICAL CONTEXT INFORMATION:
===========================
"""
        if party_members:
            header += f"""PARTY MEMBERS (Heroes who will PLAY this adventure): {', '.join(party_members)}
- These are the PLAYER CHARACTERS, not NPCs
- Do NOT create NPCs with these names
- They are the protagonists traveling TO your locations

"""
        header += """LOCATION CONTEXT:
- The party is CURRENTLY elsewhere (not in your module)
- Create a NEW location they will TRAVEL TO
- This should be a completely different place from their current location
- Give it a unique name and identity

MODULE INDEPENDENCE RULES:
1. This module represents a NEW DESTINATION
2. Party members listed above are PLAYERS, not NPCs
3. Create all-new locations, not variations of existing ones
4. Never reuse character names from the party as NPCs
===========================

"""
        return header
    
    def build_module(self, initial_concept: str):
        """Build a complete module from an initial concept"""
        self.log("Starting module build process...")
        self.log(f"Initial concept: {initial_concept}")
        
        # Get existing characters for context
        existing_characters = self.get_party_members()
        self.context_header = self.create_context_header(existing_characters)
        
        # Create required directory structure first
        self.create_module_directories()
        
        # Initialize context
        self.context.module_name = self.config.module_name.replace("_", " ")
        self.context.module_id = self.config.module_name
        
        # Step 1: Generate module overview with context
        self.log("Step 1: Generating module overview...")
        contextualized_concept = self.context_header + initial_concept
        self.module_data = self.module_gen.generate_module(contextualized_concept, context=self.context)
        
        # Extract NPCs and factions from module data
        self._extract_module_entities()
        
        # Step 2: Generate areas from the world map
        self.log("Step 2: Generating areas...")
        self.generate_areas()
        
        # Step 3: Generate locations for each area
        self.log("Step 3: Generating locations for each area...")
        self.generate_locations()
        
        # Step 3.5: Apply unique prefixes and create area connections
        self.log("Step 3.5: Finalizing location IDs and connections...")
        self.finalize_locations_and_connections()
        
        # Step 4: Generate plots for each area
        self.log("Step 4: Generating plots for each area...")
        self.generate_plots()
        
        # Step 4.5: Unify plots into module_plot.json
        self.log("Step 4.5: Creating unified module plot...")
        self.unify_plots()
        
        # Step 4.6: Update area plot hooks to reference unified plot
        self.log("Step 4.6: Updating area plot hooks...")
        self.update_area_plot_hooks()
        
        # Step 4.7: Inject the antagonist into the climactic location
        self.log("Step 4.7: Mandating antagonist placement...")
        self._inject_antagonist_into_climactic_location()
        
        # Step 5: Generate initial party tracker
        self.log("Step 5: Creating party tracker...")
        self.create_party_tracker()
        
        # Step 6: Create module summary
        self.log("Step 6: Creating module summary...")
        self.create_module_summary()
        
        # Step 6.5: Reconcile NPC names across all files
        self.log("Step 6.5: Reconciling NPC names for consistency...")
        reconciler = NpcReconciler(self.config.module_name)
        if reconciler.load_context():
            reconciler.reconcile_all_areas()
        
        # Step 7: Validate and save context
        self.log("Step 7: Validating module consistency...")
        self.validate_module()
        
        # Step 8: Create _BU.json backup files for reset functionality
        self.log("Step 8: Creating _BU.json backup files...")
        self.create_bu_backups()
        
        self.log("Module generation complete!")
        self.log(f"Output saved to: {self.config.output_directory}")
    
    def _inject_antagonist_into_climactic_location(self):
        """
        Ensures the main antagonist is placed in the final location of the module.
        This works by reading the generated area files and updating them directly.
        """
        self.log("Injecting main antagonist into climactic location...")

        # 1. Identify the main antagonist from the module data
        antagonist_name = self.module_data.get("mainPlot", {}).get("antagonist")
        if not antagonist_name:
            self.log("  - WARNING: No antagonist found in module data. Skipping injection.")
            return

        # 2. Identify the climactic area by reading the unified plot file
        plot_file_path = os.path.join(self.config.output_directory, "module_plot.json")
        if not os.path.exists(plot_file_path):
            self.log(f"  - WARNING: module_plot.json not found. Cannot determine climactic location.")
            return

        from utils.file_operations import safe_read_json, safe_write_json
        unified_plot = safe_read_json(plot_file_path)
        plot_points = unified_plot.get("plotPoints", [])
        if not plot_points:
            self.log("  - WARNING: No plot points found. Cannot determine climactic location.")
            return

        # The climactic plot point is the last one in the list
        climactic_plot_point = plot_points[-1]
        climactic_area_id = climactic_plot_point.get("location") # This gives us the area ID, e.g., "SD001"

        if not climactic_area_id:
            self.log(f"  - WARNING: No location specified in climactic plot point.")
            return

        # 3. Load the area file
        area_file_path = os.path.join(self.config.output_directory, "areas", f"{climactic_area_id}.json")
        if not os.path.exists(area_file_path):
            self.log(f"  - WARNING: Area file {area_file_path} not found.")
            return
            
        area_data = safe_read_json(area_file_path)
        if not area_data:
            self.log(f"  - WARNING: Could not read area file {area_file_path}.")
            return
        
        # 4. Find the last location in this area
        locations = area_data.get("locations", [])
        if not locations:
            self.log(f"  - WARNING: No locations found in area {climactic_area_id}.")
            return
            
        # The last location is our target
        climactic_location = locations[-1]
        climactic_location_id = climactic_location.get("locationId")

        # 5. Check if antagonist is already there
        npcs = climactic_location.get("npcs", [])
        if any(npc.get("name") == antagonist_name for npc in npcs):
            self.log(f"  - INFO: Antagonist '{antagonist_name}' already present in {climactic_area_id}:{climactic_location_id}.")
            return

        # 6. Create and inject the antagonist NPC
        antagonist_npc_entry = {
            "name": antagonist_name,
            "description": f"The main antagonist of the story, {antagonist_name}.",
            "attitude": "hostile"
        }
        
        climactic_location.setdefault("npcs", []).append(antagonist_npc_entry)
        
        # 7. Save the updated area file
        safe_write_json(area_data, area_file_path)
        self.log(f"  - SUCCESS: Mandated placement of '{antagonist_name}' in {climactic_area_id}:{climactic_location_id}.")

    def generate_areas(self):
        """Generate detailed area files from the module world map"""
        world_map = self.module_data.get("worldMap", [])
        
        for i, region in enumerate(world_map[:self.config.num_areas]):
            area_id = region["mapId"]
            
            # Determine area type based on region description
            area_type = self.determine_area_type(region)
            
            config = AreaConfig(
                area_type=area_type,
                size="medium" if i == 0 else ["small", "medium", "large"][i % 3],
                complexity="moderate",
                danger_level=region["dangerLevel"],
                recommended_level=region["recommendedLevel"],
                num_locations=self.config.locations_per_area
            )
            
            # Add area to context
            self.context.add_area(area_id, region["regionName"], area_type)
            
            # Determine the unique prefix for this area's locations
            prefix = self.get_location_prefix(i)
            
            # Generate area using AreaGenerator
            area_data = self.area_gen.generate_area(
                region["regionName"],
                area_id,
                self.module_data,
                config,
                prefix=prefix
            )
            
            # Validate area consistency after generation
            self.validate_area_consistency(area_data, self.module_data)
            
            self.areas_data[area_id] = area_data
            self.save_json(area_data, f"areas/{area_id}.json")
            
            # Save the map separately
            if "map" in area_data:
                self.save_json(area_data["map"], f"map_{area_id}.json")
            
            # Context will be updated when locations are generated
            self.context.add_area(area_id, region['regionName'], area_data["areaType"])
            
            self.log(f"Generated area: {region['regionName']} ({area_id})")
    
    def determine_area_type(self, region: Dict[str, Any]) -> str:
        """Determine area type based on region description with better pattern matching"""
        description = region.get("regionDescription", "").lower()
        name = region.get("regionName", "").lower()
        
        # Enhanced pattern matching
        if any(word in description + name for word in ["mine", "cave", "dungeon", "ruins", "tomb", "underground", "depths"]):
            return "dungeon"
        elif any(word in description + name for word in ["town", "city", "village", "settlement", "hollow", "borough"]):
            return "town"
        elif any(word in description + name for word in ["forest", "woods", "wilds", "grove", "emerald", "woodland"]):
            return "wilderness"
        elif any(word in description + name for word in ["mountain", "peaks", "marches", "highlands", "cliffs"]):
            return "wilderness" 
        elif any(word in description + name for word in ["swamp", "marsh", "bog", "mire"]):
            return "wilderness"
        else:
            return "mixed"
    
    def validate_area_consistency(self, area_data: Dict[str, Any], module_data: Dict[str, Any]):
        """Validate area descriptions match their names and themes"""
        area_name = area_data.get("areaName", "").lower()
        climate = area_data.get("climate", "")
        terrain = area_data.get("terrain", "")
        
        # Fix obvious mismatches
        if any(word in area_name for word in ["emerald", "wilds", "forest", "woods"]):
            if climate == "desert" or "desert" in terrain:
                self.log(f"WARNING: Fixed climate mismatch for {area_data['areaName']}")
                area_data["climate"] = "temperate"
                area_data["terrain"] = "dense forest with clearings and groves"
        
        if any(word in area_name for word in ["frostward", "marches", "winter", "ice"]):
            if climate == "temperate":
                self.log(f"WARNING: Fixed climate mismatch for {area_data['areaName']}")
                area_data["climate"] = "cold"
                area_data["terrain"] = "frozen tundra and icy peaks"
    
    def get_party_members(self):
        """Get list of existing character names to avoid conflicts"""
        character_names = []
        
        # Try to read from current module's character files first
        try:
            import glob
            # Check current module directory first
            current_module_chars = glob.glob(f"{self.config.output_directory}/characters/*.json")
            
            # If no characters in current module, check all modules
            if not current_module_chars:
                char_files = glob.glob("modules/*/characters/*.json")
            else:
                char_files = current_module_chars
                
            for char_file in char_files:
                try:
                    with open(char_file, 'r') as f:
                        char_data = json.load(f)
                        # Include both player characters and NPCs to avoid naming conflicts
                        char_role = char_data.get('character_role', '')
                        if char_role in ['player', 'npc']:
                            name = char_data.get('name', '').strip()
                            if name and name not in character_names:  # Avoid duplicates
                                character_names.append(name)
                except Exception:
                    continue
        except Exception:
            pass
        
        # No fallback - let each module work with actual characters or none
        if not character_names:
            character_names = []
            self.log("No existing characters detected - module will use generic references")
        
        return character_names
    
    def create_module_directories(self):
        """Create all required module directories"""
        required_dirs = ["characters", "monsters", "encounters", "areas"]
        
        for dir_name in required_dirs:
            dir_path = os.path.join(self.config.output_directory, dir_name)
            os.makedirs(dir_path, exist_ok=True)
            self.log(f"Created directory: {dir_name}/")
        
        # Create empty .gitkeep files to preserve directory structure
        for dir_name in required_dirs:
            gitkeep_path = os.path.join(self.config.output_directory, dir_name, ".gitkeep")
            if not os.path.exists(gitkeep_path):
                with open(gitkeep_path, 'w') as f:
                    f.write("# Keep this directory in git\n")
    
    def generate_area_map(self, area_id: str) -> Dict[str, Any]:
        """Generate a map layout for an area"""
        # For now, create a simple grid map
        # This would be enhanced with the actual map generator
        return {
            "mapId": area_id,
            "mapName": f"Map of {area_id}",
            "totalRooms": self.config.locations_per_area,
            "layout": self.create_simple_layout(self.config.locations_per_area)
        }
    
    def create_simple_layout(self, num_rooms: int) -> List[List[str]]:
        """Create a simple grid layout for demonstration"""
        # This is a placeholder - real implementation would create
        # a proper dungeon layout
        grid_size = int((num_rooms ** 0.5) + 1)
        layout = []
        room_count = 1
        
        for y in range(grid_size):
            row = []
            for x in range(grid_size):
                if room_count <= num_rooms and (x + y) % 2 == 0:
                    row.append(f"R{room_count:02d}")
                    room_count += 1
                else:
                    row.append("   ")
            layout.append(row)
        
        return layout
    
    def generate_locations(self):
        """Generate detailed locations for each area"""
        # Get existing character names to avoid conflicts
        existing_characters = self.get_party_members()
        self.log(f"Avoiding character name conflicts with: {', '.join(existing_characters)}")
        
        for area_id, area_data in self.areas_data.items():
            self.log(f"Generating locations for area {area_id}...")
            
            # Get the plot data for this area
            plot_data = self.plots_data.get(area_id, {})
            
            # Generate locations using the LocationGenerator with context
            location_data = self.location_gen.generate_locations(
                area_data,
                plot_data,
                self.module_data,
                context=self.context,
                excluded_names=existing_characters,
                context_header=self.context_header
            )
            
            # Store locations data
            self.locations_data[area_id] = location_data
            
            # Add locations to area data and save complete area file
            area_data["locations"] = location_data["locations"]
            self.save_json(area_data, f"areas/{area_id}.json")
            
            self.log(f"Generated {len(location_data['locations'])} locations for {area_id}")
    
    def generate_plots(self):
        """Generate plot files for each area"""
        for area_id in self.areas_data:
            self.log(f"Generating plot for area {area_id}...")
            
            area_data = self.areas_data[area_id]
            location_data = self.locations_data[area_id]
            
            # Create area-specific context for plot generation
            area_specific_context = f"""
PLOT GENERATION FOR SPECIFIC AREA:
===================================
AREA NAME: {area_data['areaName']}
AREA TYPE: {area_data.get('areaType', 'unknown')}
AREA DESCRIPTION: {area_data.get('areaDescription', '')}
TERRAIN: {area_data.get('terrain', 'unknown')}

IMPORTANT: This plot must be specific to the {area_data['areaName']} area.
The plot title should reference this specific area, not other locations.
===================================

{self.context_header}"""
            
            plot_data = self.plot_gen.generate_plot(
                self.module_data,
                area_data,
                location_data,
                f"Create a plot specifically for {area_data['areaName']}, a {area_data.get('areaType', 'region')} area",
                context=self.context,
                context_header=area_specific_context
            )
            
            self.plots_data[area_id] = plot_data
            # Individual plot files removed - using centralized module_plot.json instead
            
            # Update context with plot points
            for plot_point in plot_data.get("plotPoints", []):
                self.context.add_plot_point(
                    plot_point["id"],
                    area_id,
                    plot_point.get("location")
                )
            
            self.log(f"Generated plot for {area_id}")
    
    def unify_plots(self):
        """Unify individual area plots into a single module_plot.json using AI"""
        if not self.plots_data:
            self.log("Warning: No plots to unify")
            return
            
        # Import OpenAI at the function level to avoid circular imports
        from openai import OpenAI
        from config import OPENAI_API_KEY, DM_MAIN_MODEL
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Prepare context for unification
        area_summaries = []
        all_plot_points = []
        all_side_quests = []
        
        for area_id, plot_data in self.plots_data.items():
            area_data = self.areas_data[area_id]
            area_summaries.append({
                "area_id": area_id,
                "area_name": area_data["areaName"],
                "area_type": area_data.get("areaType", "unknown"),
                "recommended_level": area_data.get("recommendedLevel", 1),
                "plot_title": plot_data.get("plotTitle", ""),
                "main_objective": plot_data.get("mainObjective", ""),
                "num_plot_points": len(plot_data.get("plotPoints", []))
            })
            
            # Extract plot points and side quests with area context
            for pp in plot_data.get("plotPoints", []):
                pp_with_context = pp.copy()
                pp_with_context["source_area"] = area_id
                pp_with_context["area_name"] = area_data["areaName"]
                all_plot_points.append(pp_with_context)
                
                for sq in pp.get("sideQuests", []):
                    sq_with_context = sq.copy()
                    sq_with_context["source_area"] = area_id
                    sq_with_context["area_name"] = area_data["areaName"]
                    sq_with_context["parent_plot_point"] = pp["id"]
                    all_side_quests.append(sq_with_context)
        
        # Create AI prompt for unification
        prompt = f"""You are an expert 5th edition module designer. Combine these individual area plots into a single, coherent module-wide plot structure.

MODULE CONTEXT:
- Module Name: {self.module_data.get('moduleName', 'Unknown')}
- Module Description: {self.module_data.get('moduleDescription', '')}
- Total Areas: {len(self.areas_data)}

INDIVIDUAL AREA PLOTS TO UNIFY:
{json.dumps(area_summaries, indent=2)}

ALL PLOT POINTS TO REORGANIZE:
{json.dumps(all_plot_points, indent=2)}

UNIFICATION REQUIREMENTS:
1. Create a single overarching plot title that encompasses the entire module
2. Write a main objective that ties all areas together
3. Reorganize plot points into a logical progression that flows between areas
4. Maintain narrative coherence - each plot point should lead naturally to the next
5. Preserve all existing plot points but reorder/renumber them for better flow
6. Update plot point descriptions to reference connections between areas when appropriate
7. Ensure side quests remain attached to their appropriate plot points
8. Update nextPoints arrays to reflect the new unified progression
9. Consider level progression - easier areas should come before harder ones

RETURN FORMAT:
Return a JSON object with this exact structure:
{{
    "plotTitle": "Unified title for the entire module",
    "mainObjective": "Overarching goal that spans all areas",
    "plotPoints": [
        {{
            "id": "PP001",
            "title": "Plot point title",
            "description": "Detailed description that may reference travel between areas",
            "location": "area_id (like HG001, not R01)",
            "nextPoints": ["PP002"],
            "status": "not started",
            "plotImpact": "",
            "sideQuests": [
                {{
                    "id": "SQ001", 
                    "title": "Side quest title",
                    "description": "Side quest description",
                    "involvedLocations": ["area_id"],
                    "status": "not started",
                    "plotImpact": ""
                }}
            ]
        }}
    ],
    "activeQuests": [],
    "completedQuests": [],
    "failedQuests": [],
    "worldEvents": [],
    "dmNotes": []
}}

IMPORTANT: 
- Use area IDs (like HG001) for location fields, not room IDs (like R01)
- Renumber plot points sequentially starting from PP001
- Renumber side quests GLOBALLY and sequentially starting from SQ001 (SQ001, SQ002, SQ003, etc. across ALL plot points)
- Each side quest must have a unique number across the entire module, not restarting from SQ001 for each plot point
- Maintain all existing content but improve flow and connections"""

        try:
            response = client.chat.completions.create(
                model=DM_MAIN_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert 5th edition module designer specializing in creating coherent, engaging adventure narratives."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            unified_plot = json.loads(response.choices[0].message.content)
            
            # Add missing required fields if not present
            required_fields = ["activeQuests", "completedQuests", "failedQuests", "worldEvents", "dmNotes"]
            for field in required_fields:
                if field not in unified_plot:
                    unified_plot[field] = []
            
            # Save the unified plot
            output_path = os.path.join(self.config.output_directory, "module_plot.json")
            self.save_json(unified_plot, "module_plot.json")
            
            self.log(f"Created unified module plot with {len(unified_plot.get('plotPoints', []))} plot points")
            
        except Exception as e:
            self.log(f"Error during plot unification: {e}")
            # Fallback: create a simple unified structure
            self._create_fallback_unified_plot()
    
    def _create_fallback_unified_plot(self):
        """Create a simple unified plot if AI unification fails"""
        unified_plot = {
            "plotTitle": self.module_data.get('moduleName', 'Adventure Module'),
            "mainObjective": f"Complete the challenges across {len(self.areas_data)} interconnected areas",
            "plotPoints": [],
            "activeQuests": [],
            "completedQuests": [],
            "failedQuests": [],
            "worldEvents": [],
            "dmNotes": []
        }
        
        # Simple concatenation of all plot points
        plot_counter = 1
        side_quest_counter = 1
        
        for area_id, plot_data in self.plots_data.items():
            for pp in plot_data.get("plotPoints", []):
                new_pp = {
                    "id": f"PP{plot_counter:03d}",
                    "title": pp.get("title", f"Plot Point {plot_counter}"),
                    "description": pp.get("description", ""),
                    "location": area_id,
                    "nextPoints": [f"PP{plot_counter+1:03d}"] if plot_counter < sum(len(p.get("plotPoints", [])) for p in self.plots_data.values()) else [],
                    "status": "not started",
                    "plotImpact": "",
                    "sideQuests": []
                }
                
                # Add side quests
                for sq in pp.get("sideQuests", []):
                    new_sq = {
                        "id": f"SQ{side_quest_counter:03d}",
                        "title": sq.get("title", f"Side Quest {side_quest_counter}"),
                        "description": sq.get("description", ""),
                        "involvedLocations": [area_id],
                        "status": "not started",
                        "plotImpact": ""
                    }
                    new_pp["sideQuests"].append(new_sq)
                    side_quest_counter += 1
                
                unified_plot["plotPoints"].append(new_pp)
                plot_counter += 1
        
        self.save_json(unified_plot, "module_plot.json")
        self.log(f"Created fallback unified plot with {len(unified_plot['plotPoints'])} plot points")
    
    def update_area_plot_hooks(self):
        """Update area plot hooks to reference unified plot using atomic updates with safety guards"""
        # Load the unified plot we just created
        unified_plot_path = os.path.join(self.config.output_directory, "module_plot.json")
        try:
            with open(unified_plot_path, 'r', encoding='utf-8') as f:
                unified_plot = json.load(f)
        except Exception as e:
            self.log(f"Warning: Could not load unified plot for hook updates: {e}")
            return
        
        # Import here to avoid circular imports
        from openai import OpenAI
        from config import OPENAI_API_KEY, DM_MAIN_MODEL
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Update each area's plot hooks
        for area_id in self.areas_data:
            self._update_single_area_plot_hooks(area_id, unified_plot, client)
    
    def _update_single_area_plot_hooks(self, area_id, unified_plot, client):
        """Atomically update plot hooks for a single area with deep merge and safety guards"""
        # Import here to avoid circular imports
        from utils.file_operations import safe_write_json, safe_read_json
        
        area_file_path = os.path.join(self.config.output_directory, "areas", f"{area_id}.json")
        
        # STEP 1: Create backup before any changes
        backup_path = f"{area_file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            shutil.copy2(area_file_path, backup_path)
            self.log(f"Created backup: {backup_path}")
        except Exception as e:
            self.log(f"Warning: Could not create backup for {area_id}: {e}")
        
        # STEP 2: Load original area data with validation
        try:
            original_area_data = safe_read_json(area_file_path)
            if not original_area_data or not isinstance(original_area_data, dict):
                self.log(f"Error: Invalid area data for {area_id}")
                return
        except Exception as e:
            self.log(f"Error: Could not load area {area_id}: {e}")
            return
        
        # STEP 3: Create in-memory backup
        import copy
        area_backup = copy.deepcopy(original_area_data)
        
        # STEP 4: Extract relevant plot points for this area
        relevant_plot_points = []
        relevant_side_quests = []
        
        for pp in unified_plot.get("plotPoints", []):
            if pp.get("location") == area_id:
                relevant_plot_points.append({
                    "id": pp["id"],
                    "title": pp["title"],
                    "description": pp["description"]
                })
                
                for sq in pp.get("sideQuests", []):
                    if area_id in sq.get("involvedLocations", []):
                        relevant_side_quests.append({
                            "id": sq["id"],
                            "title": sq["title"],
                            "description": sq["description"]
                        })
        
        if not relevant_plot_points:
            self.log(f"No plot points found for area {area_id}, skipping hook updates")
            return
        
        # STEP 5: Generate updated plot hooks using AI
        try:
            updated_hooks = self._generate_enhanced_plot_hooks(
                area_id, 
                original_area_data, 
                relevant_plot_points, 
                relevant_side_quests, 
                client
            )
            
            if not updated_hooks:
                self.log(f"No plot hook updates generated for {area_id}")
                return
                
        except Exception as e:
            self.log(f"Error generating plot hooks for {area_id}: {e}")
            return
        
        # STEP 6: Deep merge updates with original data (ATOMIC OPERATION)
        try:
            updated_area_data = self._deep_merge_area_updates(area_backup, updated_hooks)
            
            # STEP 7: Validate critical fields preserved
            if not self._validate_area_integrity(area_backup, updated_area_data, area_id):
                self.log(f"Error: Area integrity check failed for {area_id}, rolling back")
                return
            
            # STEP 8: Atomic write with safety guards
            safe_write_json(area_file_path, updated_area_data)
            self.log(f"Successfully updated plot hooks for {area_id}")
            
            # STEP 9: Cleanup old backups (keep only 3 most recent)
            self._cleanup_area_backups(area_file_path)
            
        except Exception as e:
            self.log(f"Error during atomic update for {area_id}: {e}")
            # Restore from backup on failure
            try:
                shutil.copy2(backup_path, area_file_path)
                self.log(f"Restored {area_id} from backup due to update failure")
            except:
                self.log(f"Critical error: Could not restore {area_id} from backup")
    
    def _generate_enhanced_plot_hooks(self, area_id, area_data, plot_points, side_quests, client):
        """Generate enhanced plot hooks that reference specific plot points and side quests"""
        # Import here to avoid circular imports
        from config import DM_MAIN_MODEL
        
        # Extract existing plot hooks from all locations in the area
        existing_hooks = []
        for location in area_data.get("locations", []):
            hooks = location.get("plotHooks", [])
            if hooks:
                existing_hooks.extend(hooks)
        
        prompt = f"""You are updating plot hooks for a 5th edition area to reference specific unified plot points.

AREA: {area_data.get('areaName', area_id)} ({area_id})
AREA DESCRIPTION: {area_data.get('areaDescription', '')}

EXISTING PLOT HOOKS TO ENHANCE:
{json.dumps(existing_hooks, indent=2)}

RELEVANT PLOT POINTS FOR THIS AREA:
{json.dumps(plot_points, indent=2)}

RELEVANT SIDE QUESTS FOR THIS AREA:
{json.dumps(side_quests, indent=2)}

TASK: Update the existing plot hooks to specifically reference the unified plot points and side quests.

REQUIREMENTS:
1. Keep the essence and style of existing plot hooks
2. Add specific references to plot point IDs (PP001, PP002, etc.) where appropriate
3. Add references to side quest IDs (SQ001, SQ002, etc.) where appropriate
4. Maintain the narrative tone and area atmosphere
5. Make hooks actionable for DMs
6. Only update plot hooks - do NOT change other area data

RETURN FORMAT:
Return a JSON object with this structure:
{{
  "plotHookUpdates": [
    {{
      "locationId": "R01",
      "plotHooks": [
        "Enhanced hook that mentions PP001 or SQ001 specifically...",
        "Another enhanced hook referencing the unified plot..."
      ]
    }}
  ]
}}

IMPORTANT: 
- Only include locations that need plot hook updates
- Reference specific plot point/side quest IDs where it makes narrative sense
- Preserve the existing hook style and tone
- Make hooks more specific and actionable"""

        try:
            response = client.chat.completions.create(
                model=DM_MAIN_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert 5th edition module designer specializing in creating actionable plot hooks that reference specific plot elements."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.6
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("plotHookUpdates", [])
            
        except Exception as e:
            self.log(f"Error in AI plot hook generation: {e}")
            return []
    
    def _deep_merge_area_updates(self, original_data, hook_updates):
        """Deep merge plot hook updates into area data, preserving all other data"""
        import copy
        result = copy.deepcopy(original_data)
        
        # Create a lookup for location updates
        location_updates = {}
        for update in hook_updates:
            location_id = update.get("locationId")
            if location_id and "plotHooks" in update:
                location_updates[location_id] = update["plotHooks"]
        
        # Update only the plot hooks in matching locations
        for location in result.get("locations", []):
            location_id = location.get("locationId")
            if location_id in location_updates:
                location["plotHooks"] = location_updates[location_id]
        
        return result
    
    def _validate_area_integrity(self, original_data, updated_data, area_id):
        """Validate that critical area fields are preserved during update"""
        critical_fields = ["areaId", "areaName", "areaType", "locations", "map"]
        
        for field in critical_fields:
            if field in original_data and field not in updated_data:
                self.log(f"Critical field '{field}' missing in updated {area_id}")
                return False
            
            # Validate locations array structure
            if field == "locations":
                orig_locations = original_data.get("locations", [])
                updated_locations = updated_data.get("locations", [])
                
                if len(orig_locations) != len(updated_locations):
                    self.log(f"Location count mismatch in {area_id}")
                    return False
                
                # Check that each location preserves critical fields
                for orig_loc, updated_loc in zip(orig_locations, updated_locations):
                    location_critical = ["locationId", "name", "type", "description", "npcs", "monsters"]
                    for loc_field in location_critical:
                        if loc_field in orig_loc and loc_field not in updated_loc:
                            self.log(f"Critical location field '{loc_field}' missing in {area_id}")
                            return False
        
        return True
    
    def _cleanup_area_backups(self, area_file_path):
        """Clean up old area backups, keeping only the 3 most recent"""
        try:
            import glob
            backup_pattern = f"{area_file_path}.backup_*"
            backups = glob.glob(backup_pattern)
            
            if len(backups) > 3:
                # Sort by modification time, keep newest 3
                backups.sort(key=os.path.getmtime, reverse=True)
                for old_backup in backups[3:]:
                    os.remove(old_backup)
                    
        except Exception as e:
            self.log(f"Warning: Could not cleanup old backups: {e}")
    
    def create_party_tracker(self):
        """Create the initial party tracker file"""
        # Use the first area as the starting location
        first_area_id = list(self.areas_data.keys())[0]
        first_area = self.areas_data[first_area_id]
        
        # Get the first location from the locations data
        first_locations_data = self.locations_data.get(first_area_id, {})
        locations_list = first_locations_data.get("locations", [])
        
        if not locations_list:
            # Fallback to a default location
            first_location = {
                "name": "Starting Location",
                "locationId": "R01"
            }
        else:
            first_location = locations_list[0]
        
        party_tracker = {
            "module": self.config.module_name.replace("_", " "),
            "partyMembers": [],  # Will be populated when players join
            "partyNPCs": [],
            "worldConditions": {
                "year": 1492,  # Standard Forgotten Realms year
                "month": "Hammer",  # January equivalent
                "day": 1,
                "time": "08:00:00",
                "weather": "Clear",
                "season": "Winter",
                "dayNightCycle": "Day",
                "moonPhase": "New Moon",
                "currentLocation": first_location["name"],
                "currentLocationId": first_location["locationId"],
                "currentArea": first_area["areaName"],
                "currentAreaId": first_area["areaId"],
                "majorEventsUnderway": [],
                "politicalClimate": "",
                "activeEncounter": "",
                "activeCombatEncounter": "",
                "weatherConditions": "",
                "lastCompletedEncounter": ""
            },
            "activeQuests": []
        }
        
        self.save_json(party_tracker, "party_tracker.json")
        self.log("Created party tracker")
    
    def create_module_summary(self):
        """Create a human-readable module summary"""
        summary = f"""# {self.module_data['moduleName']} - Module Summary

## Overview
{self.module_data['moduleDescription']}

## Module Conflicts
"""
        # Add module conflicts if they exist
        if 'moduleConflicts' in self.module_data:
            for conflict in self.module_data['moduleConflicts']:
                summary += f"- **{conflict['conflictName']}** ({conflict['scope']}): {conflict['description']}\n"
        
        summary += """

## Main Plot
**Objective**: {self.module_data['mainPlot']['mainObjective']}
**Antagonist**: {self.module_data['mainPlot']['antagonist']}

## Areas
"""
        
        for area_id, area_data in self.areas_data.items():
            plot_data = self.plots_data.get(area_id, {})
            summary += f"""
### {area_data['areaName']} ({area_id})
- **Description**: {area_data['areaDescription']}
- **Danger Level**: {area_data['dangerLevel']}
- **Recommended Level**: {area_data['recommendedLevel']}
- **Locations**: {len(area_data['locations'])}
- **Plot**: {plot_data.get('plotTitle', 'TBD')}
- **Objective**: {plot_data.get('mainObjective', 'TBD')}
"""
        
        summary += f"""
## Module Structure
- **Total Areas**: {len(self.areas_data)}
- **Total Locations**: {sum(len(area['locations']) for area in self.areas_data.values())}

## Getting Started
1. Players start in {list(self.areas_data.values())[0]['areaName']}
2. Initial quest hook: {self.plots_data[list(self.areas_data.keys())[0]].get('plotPoints', [{}])[0].get('description', 'TBD')}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        summary_path = os.path.join(self.config.output_directory, "MODULE_SUMMARY.md")
        with open(summary_path, "w") as f:
            f.write(summary)
        
        self.log("Created module summary")
    
    def _extract_module_entities(self):
        """Extract NPCs and other entities from module data"""
        # Extract NPCs from plot stages
        for stage in self.module_data.get("mainPlot", {}).get("plotStages", []):
            for npc_name in stage.get("keyNPCs", []):
                self.context.add_npc(npc_name)
                self.context.add_reference("npc", npc_name, "module:plotStages")
        
        # Note: Faction NPCs removed - location-generated NPCs are sufficient
    
    def validate_module(self):
        """Validate module consistency and save results"""
        issues = self.context.validate_all()
        
        if issues:
            self.log(f"Found {len(issues)} validation issues:")
            for issue in issues:
                self.log(f"  - {issue}")
        else:
            self.log("All validation checks passed!")
        
        # Save context and validation report
        self.context.save(os.path.join(self.config.output_directory, "module_context.json"))
        
        # Create validation report
        report = {
            "validation_date": datetime.now().isoformat(),
            "issues": issues,
            "context_summary": {
                "areas": len(self.context.areas),
                "npcs": len(self.context.npcs),
                "locations": len(self.context.locations),
                "plot_points": len(self.context.plot_scopes)
            }
        }
        self.save_json(report, "validation_report.json")
    
    def create_bu_backups(self):
        """Create _BU.json backup files for all generated module files"""
        import shutil
        import glob
        
        # Get all JSON files in the module directory (excluding subdirectories first)
        module_files = []
        
        # Get files in root module directory
        root_files = glob.glob(os.path.join(self.config.output_directory, "*.json"))
        module_files.extend(root_files)
        
        # Get files in areas subdirectory
        areas_files = glob.glob(os.path.join(self.config.output_directory, "areas", "*.json"))
        module_files.extend(areas_files)
        
        # Get files in monsters subdirectory
        monsters_files = glob.glob(os.path.join(self.config.output_directory, "monsters", "*.json"))
        module_files.extend(monsters_files)
        
        # Get files in encounters subdirectory
        encounters_files = glob.glob(os.path.join(self.config.output_directory, "encounters", "*.json"))
        module_files.extend(encounters_files)
        
        # Create _BU.json backups for each file
        backup_count = 0
        for json_file in module_files:
            # Skip if it's already a backup file or a character file
            if json_file.endswith("_BU.json") or "/characters/" in json_file:
                continue
                
            # Create backup filename
            backup_file = json_file.replace(".json", "_BU.json")
            
            try:
                shutil.copy2(json_file, backup_file)
                backup_count += 1
                self.log(f"  Created backup: {os.path.relpath(backup_file, self.config.output_directory)}")
            except Exception as e:
                self.log(f"  WARNING: Failed to create backup for {json_file}: {e}")
        
        self.log(f"Created {backup_count} _BU.json backup files for reset functionality")
    
    def get_location_prefix(self, area_index: int) -> str:
        """Get the appropriate prefix for location IDs based on area index"""
        # Use letters A-Z for first 26 areas, then AA-AZ, BA-BZ, etc.
        if area_index < 26:
            return chr(65 + area_index)  # A-Z
        else:
            first_letter = chr(65 + (area_index // 26) - 1)
            second_letter = chr(65 + (area_index % 26))
            return first_letter + second_letter
    
    
    def _create_bidirectional_connection(self, area_files: Dict[str, Any], from_area: str, to_area: str):
        """Create bidirectional connections between two areas"""
        if from_area not in area_files or to_area not in area_files:
            return
        
        # Get exit locations (prefer last locations for progression)
        from_locations = area_files[from_area].get("locations", [])
        to_locations = area_files[to_area].get("locations", [])
        
        if not from_locations or not to_locations:
            return
        
        # Select exit points (use last location in from_area and first in to_area)
        exit_loc = from_locations[-1]
        entrance_loc = to_locations[0]
        
        # Validate that both locations have locationId
        if "locationId" not in exit_loc or "locationId" not in entrance_loc:
            print(f"DEBUG: [Module Generator] Warning: Missing locationId in connection between {from_area} and {to_area}")
            return
        
        # Get the final, refined names of the areas
        from_area_name = area_files[from_area].get("areaName")
        to_area_name = area_files[to_area].get("areaName")

        # Update area connectivity in from_area exit
        if "areaConnectivity" not in exit_loc:
            exit_loc["areaConnectivity"] = []
        if "areaConnectivityId" not in exit_loc:
            exit_loc["areaConnectivityId"] = []
        
        # Store the refined area name and the location ID for proper connectivity
        exit_loc["areaConnectivity"].append(to_area_name)  # Use the refined name of the destination area
        exit_loc["areaConnectivityId"].append(entrance_loc["locationId"])
        print(f"DEBUG: [Module Generator] Connected {from_area} location {exit_loc['locationId']} to {to_area} location {entrance_loc['locationId']}")
        
        # Update area connectivity in to_area entrance
        if "areaConnectivity" not in entrance_loc:
            entrance_loc["areaConnectivity"] = []
        if "areaConnectivityId" not in entrance_loc:
            entrance_loc["areaConnectivityId"] = []
        
        entrance_loc["areaConnectivity"].append(from_area_name)  # Use the refined name of the source area
        entrance_loc["areaConnectivityId"].append(exit_loc["locationId"])
    
    def finalize_locations_and_connections(self):
        """
        Creates connections between areas. This must be run AFTER all locations
        have been fully generated. Prefixing is now done during generation.
        """
        # Create connections between areas using the now-unique IDs
        sorted_area_ids = sorted(self.areas_data.keys())
        
        if len(sorted_area_ids) > 1:
            for i in range(len(sorted_area_ids) - 1):
                from_area_id = sorted_area_ids[i]
                to_area_id = sorted_area_ids[i+1]
                
                # The area_files dictionary needs to be built from self.areas_data
                area_files_for_connection = {
                    from_area_id: self.areas_data[from_area_id],
                    to_area_id: self.areas_data[to_area_id]
                }
                
                self._create_bidirectional_connection(area_files_for_connection, from_area_id, to_area_id)
                
                # Save the updated files after adding connections
                self.save_json(self.areas_data[from_area_id], f"areas/{from_area_id}.json")
                self.save_json(self.areas_data[to_area_id], f"areas/{to_area_id}.json")

def main():
    """Interactive module builder"""
    print("5th Edition Module Builder")
    print("=" * 50)
    
    # Get module configuration
    module_name = input("Module name: ").strip()
    if not module_name:
        module_name = "New_Module"
    
    module_name = module_name.replace(" ", "_")
    
    num_areas = input("Number of areas to generate (default 3): ").strip()
    num_areas = int(num_areas) if num_areas else 3
    
    locations_per_area = input("Locations per area (default 15): ").strip()
    locations_per_area = int(locations_per_area) if locations_per_area else 15
    
    # Get initial concept
    print("\nDescribe your module concept:")
    concept = input("> ").strip()
    if not concept:
        concept = "A classic fantasy adventure with dungeons, monsters, and ancient mysteries"
    
    # Configure builder
    config = BuilderConfig(
        module_name=module_name,
        num_areas=num_areas,
        locations_per_area=locations_per_area,
        output_directory=f"./modules/{module_name}"
    )
    
    # Build module
    builder = ModuleBuilder(config)
    builder.build_module(concept)
    
    print(f"\nModule '{module_name}' has been generated!")
    print(f"Output directory: {config.output_directory}")
    print("\nYou can now:")
    print("1. Review the MODULE_SUMMARY.md file")
    print("2. Edit any generated files as needed")
    print("3. Start your adventure with main.py")

def parse_narrative_to_module_params(narrative: str) -> Dict[str, Any]:
    """Use AI to parse a narrative description into module parameters
    
    Args:
        narrative: The rich narrative description of the new module
        
    Returns:
        Dict containing parsed module parameters
    """
    from openai import OpenAI
    import config
    
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    parsing_prompt = """You are a module configuration parser for the world's most popular 5th edition tabletop role-playing game. Extract adventure module parameters from a narrative description.

Look for these elements in the narrative text:
1. Module name - any title, location name, or adventure theme that could serve as the module title
   - Examples: "Shadows of...", "The Lost...", "Curse of...", or prominent location names
   - Convert to title case with underscores: "The_Lost_Temple", "Shadows_of_Darkwood"
   
2. Number of areas - count distinct locations, regions, or major zones described
   - Look for phrases like: "three regions", "explore the castle, the forest, and the caves" (=3)
   - Each major location mentioned is typically one area
   - If unclear, default to 3
   
3. Adventure type - identify the primary environment or mix of environments:
   - "dungeon" = underground, caves, crypts, dungeons
   - "wilderness" = forests, mountains, outdoor exploration  
   - "urban" = cities, towns, political intrigue
   - "nautical" = sea-based, islands, ships
   - "mixed" = combination of above (use this if multiple types)
   
4. Character level range - extract from phrases like:
   - Direct: "for level 4-6 characters", "levels 3 to 5"
   - Indirect: "novice adventurers" (1-3), "seasoned heroes" (5-8), "legendary champions" (15+)
   - If vague or missing, default to 3-5
   
5. Plot themes - extract the main objectives, goals, or story elements:
   - Look for action words: "stop", "rescue", "discover", "defeat", "recover"
   - Keep it concise: "defeat the lich, save the kingdom"
   - Focus on 2-3 main goals, not full descriptions

Return this exact JSON structure:
{
  "module_name": "The_Module_Name_Here",
  "num_areas": 3,
  "locations_per_area": 6,
  "level_range": {"min": 3, "max": 5},
  "adventure_type": "mixed",
  "plot_themes": "defeat evil, rescue prisoners, discover artifact"
}

CRITICAL RULES:
- module_name MUST use underscores, not spaces
- num_areas MUST be a number (not a string)
- locations_per_area should be 5-7 (default 6)
- level_range MUST have both "min" and "max" as numbers
- adventure_type MUST be lowercase: "dungeon", "wilderness", "urban", "nautical", or "mixed"
- plot_themes should be 3-10 words summarizing main goals

Return ONLY the JSON object, no explanations or additional text."""
    
    max_retries = 3
    current_prompt = parsing_prompt
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=config.DM_SUMMARIZATION_MODEL,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": current_prompt},
                    {"role": "user", "content": f"Parse this module narrative:\n\n{narrative}"}
                ]
            )
            
            result = response.choices[0].message.content.strip()
            # Clean up potential code blocks
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
                
            parsed = json.loads(result)
            
            # Validate the required fields exist and have correct types
            required_fields = {
                "module_name": str,
                "num_areas": int,
                "locations_per_area": int,
                "level_range": dict,
                "adventure_type": str,
                "plot_themes": str
            }
            
            # Check all required fields
            validation_errors = []
            for field, expected_type in required_fields.items():
                if field not in parsed:
                    validation_errors.append(f"Missing required field: {field}")
                elif not isinstance(parsed[field], expected_type):
                    validation_errors.append(f"Field {field} should be {expected_type.__name__}, got {type(parsed[field]).__name__}")
            
            # Validate level_range structure
            if "level_range" in parsed and isinstance(parsed["level_range"], dict):
                if "min" not in parsed["level_range"] or "max" not in parsed["level_range"]:
                    validation_errors.append("level_range must have 'min' and 'max' fields")
                elif not isinstance(parsed["level_range"]["min"], int) or not isinstance(parsed["level_range"]["max"], int):
                    validation_errors.append("level_range min and max must be integers")
            
            # Validate adventure_type is valid
            valid_types = ["dungeon", "wilderness", "urban", "nautical", "mixed"]
            if "adventure_type" in parsed and parsed["adventure_type"] not in valid_types:
                validation_errors.append(f"adventure_type must be one of: {', '.join(valid_types)}")
            
            if validation_errors:
                raise ValueError("; ".join(validation_errors))
            
            debug(f"AI_PROCESSING: AI parsed narrative into: {json.dumps(parsed, indent=2)}", category="module_creation")
            return parsed
            
        except (json.JSONDecodeError, ValueError) as e:
            if attempt < max_retries - 1:
                print(f"DEBUG: [Module Generator] Parse attempt {attempt + 1} failed: {e}")
                # Update prompt with error feedback for next attempt
                current_prompt = parsing_prompt + f"\n\nPREVIOUS ERROR: {e}\nPlease ensure all fields are present with correct types."
                continue
            else:
                print(f"DEBUG: [Module Generator] ERROR: Failed to parse after {max_retries} attempts: {e}")
                
        except Exception as e:
            print(f"DEBUG: [Module Generator] ERROR: Unexpected error parsing narrative: {e}")
            break
    
    # Return sensible defaults if all attempts fail
    return {
        "module_name": "New_Adventure",
        "num_areas": 3,
        "locations_per_area": 6,
        "level_range": {"min": 3, "max": 5},
        "adventure_type": "mixed",
        "plot_themes": "adventure,mystery"
    }

def ai_driven_module_creation(params: Dict[str, Any], progress_callback=None) -> tuple[bool, Optional[str]]:
    """AI-driven module creation that accepts a narrative and autonomously creates a module
    
    This function is fully agentic - it can work with just a narrative description
    or accept explicit parameters from the AI DM.
    
    Args:
        params: Dictionary that can contain either:
            - concept: Adventure narrative (required)
            - module_name: If provided, will override AI parsing
            - Other optional params that override AI parsing
            OR just:
            - narrative: Full narrative description (AI will parse all params)
        progress_callback: Optional callback function for progress updates
    
    Returns:
        tuple[bool, Optional[str]]: (success_status, module_name)
            - success_status: True if module was created successfully, False otherwise
            - module_name: Name of the created module if successful, None if failed
    """
    try:
        # Report progress if callback provided
        if progress_callback:
            progress_callback({'stage': 0, 'total_stages': 9, 'stage_name': 'Initializing', 'percentage': 0, 'message': 'Starting module creation...'})
        # Check if we have a narrative to parse
        narrative = params.get("narrative") or params.get("concept")
        if not narrative:
            print(f"DEBUG: [Module Generator] ERROR: No narrative or concept provided")
            return False, None
        
        # Parse narrative with AI to get module parameters
        if progress_callback:
            progress_callback({'stage': 1, 'total_stages': 9, 'stage_name': 'Parsing narrative', 'percentage': 11, 'message': 'Analyzing narrative to extract module parameters...'})
        parsed_params = parse_narrative_to_module_params(narrative)
        
        # Allow explicit parameters to override AI parsing (check both camelCase and snake_case)
        module_name = params.get("module_name") or params.get("moduleName") or parsed_params.get("module_name")
        num_areas = params.get("num_areas") or params.get("numberOfAreas") or parsed_params.get("num_areas", 2)
        locations_per_area = params.get("locations_per_area") or params.get("locationsPerArea") or parsed_params.get("locations_per_area", 12)
        # Handle level range - it might come as a string like "4-6"
        level_range_raw = params.get("level_range") or params.get("levelRange") or parsed_params.get("level_range")
        if isinstance(level_range_raw, str) and "-" in level_range_raw:
            # Parse "4-6" format
            min_level, max_level = level_range_raw.split("-")
            level_range = {"min": int(min_level.strip()), "max": int(max_level.strip())}
        elif isinstance(level_range_raw, dict):
            level_range = level_range_raw
        else:
            level_range = {"min": 3, "max": 5}
        adventure_type = params.get("adventure_type") or params.get("adventureType") or parsed_params.get("adventure_type", "mixed")
        plot_themes = params.get("plot_themes") or params.get("plotThemes") or parsed_params.get("plot_themes", "")
        
        # Validate we have a module name
        if not module_name:
            print(f"DEBUG: [Module Generator] ERROR: No module name found in parameters")
            print(f"DEBUG: [Module Generator] Parameters received: {params}")
            print(f"DEBUG: [Module Generator] Parsed parameters: {parsed_params}")
            return False, None
            
        # Clean module name (replace spaces with underscores)
        module_name = module_name.replace(" ", "_")
        
        # Enhance the concept with AI-provided context
        enhanced_concept = f"{narrative}"
        if adventure_type:
            enhanced_concept += f" This is primarily a {adventure_type} adventure."
        if level_range:
            enhanced_concept += f" Designed for characters level {level_range.get('min', 3)} to {level_range.get('max', 5)}."
        if plot_themes:
            enhanced_concept += f" Key themes include: {plot_themes}."
        
        debug(f"MODULE_CREATION: AI-driven module creation starting for '{module_name}'", category="module_creation")
        
        # Configure builder with AI parameters
        if progress_callback:
            progress_callback({'stage': 2, 'total_stages': 9, 'stage_name': 'Configuring builder', 'percentage': 22, 'message': f'Setting up module: {module_name}...'})
        config = BuilderConfig(
            module_name=module_name,
            num_areas=int(num_areas),
            locations_per_area=int(locations_per_area),
            output_directory=f"./modules/{module_name}",
            verbose=True
        )
        
        # Create and run the builder
        if progress_callback:
            progress_callback({'stage': 3, 'total_stages': 9, 'stage_name': 'Creating builder', 'percentage': 33, 'message': 'Initializing module builder...'})
        builder = ModuleBuilder(config)
        
        # Set progress callback on builder if available
        if progress_callback:
            builder.progress_callback = progress_callback
        
        # Store AI context for generators to use
        # The generators will pick up these values from the enhanced_concept text
        
        # Build the module
        if progress_callback:
            progress_callback({'stage': 4, 'total_stages': 9, 'stage_name': 'Building module', 'percentage': 44, 'message': 'Starting module generation process...'})
        builder.build_module(enhanced_concept)
        
        info(f"SUCCESS: Module '{module_name}' created successfully at {config.output_directory}", category="module_creation")
        
        if progress_callback:
            progress_callback({'stage': 7, 'total_stages': 9, 'stage_name': 'Finalizing', 'percentage': 77, 'message': 'Finalizing module data...'})
        
        # Create a module_plot.json file for the new module (required by the system)
        plot_file_path = os.path.join(config.output_directory, "module_plot.json")
        if not os.path.exists(plot_file_path):
            # Create a unified plot file from area plots
            unified_plot = {
                "plotTitle": builder.module_data.get("moduleName", module_name.replace("_", " ")),
                "mainObjective": builder.module_data.get("mainPlot", {}).get("mainObjective", "Complete the adventure"),
                "plotPoints": []
            }
            
            # Aggregate plot points from all areas
            plot_id_counter = 1
            for area_id, plot_data in builder.plots_data.items():
                for plot_point in plot_data.get("plotPoints", []):
                    # Renumber plot points for unified file
                    plot_point["id"] = f"PP{plot_id_counter:03d}"
                    plot_point["areaId"] = area_id
                    unified_plot["plotPoints"].append(plot_point)
                    plot_id_counter += 1
            
            with open(plot_file_path, "w") as f:
                json.dump(unified_plot, f, indent=2)
            info(f"SUCCESS: Created unified module_plot.json with {len(unified_plot['plotPoints'])} plot points", category="module_creation")
        
        if progress_callback:
            progress_callback({'stage': 8, 'total_stages': 9, 'stage_name': 'Complete', 'percentage': 100, 'message': f'Module {module_name} created successfully!'})
        
        return True, module_name
        
    except Exception as e:
        print(f"DEBUG: [Module Generator] ERROR: AI-driven module creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

if __name__ == "__main__":
    main()