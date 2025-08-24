#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Conversation history compressor with caching and parallel processing
Compresses specific sections (campaign context, location summaries) in parallel
"""

import json
import re
import hashlib
from typing import Dict, Any, List, Tuple
from pathlib import Path
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from datetime import datetime

# Import compression functions
sys.path.append('/mnt/c/dungeon_master_v1')
from ai_narrative_compressor_agentic import compress_with_ai
from location_compressor import compress_location
from model_config import COMPRESSION_MAX_WORKERS

class ParallelConversationCompressor:
    def __init__(self, cache_file: str = "modules/conversation_history/compression_cache.json", max_workers: int = None):
        """Initialize with a cache file for storing compressed sections"""
        self.cache_file = cache_file
        self.cache = self.load_cache()
        self.cache_lock = threading.Lock()  # Thread safety for cache
        self.max_workers = max_workers if max_workers is not None else COMPRESSION_MAX_WORKERS
        self.progress_lock = threading.Lock()  # Thread safety for progress tracking
        self.completed_count = 0
        self.total_sections = 0
        
    def load_cache(self) -> Dict[str, Any]:
        """Load existing cache from file"""
        cache_path = Path(self.cache_file)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_cache(self):
        """Save cache to file (thread-safe)"""
        with self.cache_lock:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
    
    def get_section_hash(self, content: str) -> str:
        """Generate hash for content to use as cache key"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _update_progress(self, from_cache: bool):
        """Update progress and emit event via status_manager"""
        with self.progress_lock:
            self.completed_count += 1
            # Try to use status_manager if available
            try:
                from core.managers.status_manager import status_manager
                status_manager.emit_compression_event('compression_progress', {
                    'completed': self.completed_count,
                    'total': self.total_sections,
                    'from_cache': from_cache
                })
            except:
                pass  # Silently ignore if not available
    
    def compress_section(self, section_data: Tuple[int, str, str, str, str]) -> Tuple[int, str, str, Dict[str, Any]]:
        """
        Compress a single section
        Args: (index, section_type, section_id, full_match, narrative)
        Returns: (index, section_id, full_match, compression_result)
        """
        idx, section_type, section_id, full_match, narrative = section_data
        
        content_hash = self.get_section_hash(narrative)
        cache_key = f"{section_id}_{content_hash}"
        
        # Check cache first (thread-safe)
        with self.cache_lock:
            if cache_key in self.cache:
                print(f"  [{idx:3d}] [CACHE HIT] {section_id}")
                # Update progress for cached item
                self._update_progress(from_cache=True)
                return (idx, section_id, full_match, self.cache[cache_key], True)  # Added from_cache flag
        
        # Compress using appropriate method based on type
        print(f"  [{idx:3d}] [COMPRESS] {section_id} ({len(narrative)} chars)...")
        try:
            if section_type == "location":
                # Use location-specific compression
                compressed_text = compress_location(narrative)
                if compressed_text:
                    result = {"blocks": [{"text": compressed_text}]}
                else:
                    print(f"  [{idx:3d}] [ERROR] Failed to compress location {section_id}")
                    self._update_progress(from_cache=False)
                    return (idx, section_id, full_match, {"original": narrative, "compressed": narrative}, False)
            else:
                # Use narrative compression for other types
                result = compress_with_ai(narrative, mode="agentic")
            
            if result and "blocks" in result and len(result["blocks"]) > 0:
                compressed_text = result["blocks"][0]["text"]
                
                cache_entry = {
                    "original": narrative,
                    "compressed": compressed_text,
                    "original_length": len(narrative),
                    "compressed_length": len(compressed_text),
                    "reduction": f"{(1 - len(compressed_text)/len(narrative))*100:.1f}%" if len(narrative) > 0 else "0.0%"
                }
                
                # Update cache (thread-safe)
                with self.cache_lock:
                    self.cache[cache_key] = cache_entry
                
                print(f"  [{idx:3d}] [DONE] {section_id} - Reduced by {cache_entry['reduction']}")
                # Update progress for compressed item
                self._update_progress(from_cache=False)
                return (idx, section_id, full_match, cache_entry, False)
            else:
                print(f"  [{idx:3d}] [ERROR] Failed to compress {section_id}")
                self._update_progress(from_cache=False)
                return (idx, section_id, full_match, {"original": narrative, "compressed": narrative}, False)
                
        except Exception as e:
            print(f"  [{idx:3d}] [ERROR] Exception compressing {section_id}: {e}")
            self._update_progress(from_cache=False)
            return (idx, section_id, full_match, {"original": narrative, "compressed": narrative}, False)
    
    def extract_all_sections(self, conversation: List[Dict[str, Any]]) -> Dict[int, List[Tuple]]:
        """
        Extract all sections from conversation that need compression
        Returns: Dict mapping message index to list of (section_type, section_id, full_match, narrative)
        """
        all_sections = {}
        section_counter = 0
        
        for i, message in enumerate(conversation):
            if "content" in message and isinstance(message["content"], str):
                content = message["content"]
                message_sections = []
                
                # Extract campaign contexts
                context_pattern = r'===\s*CAMPAIGN\s+CONTEXT\s*===\n\n---\s*(.*?)\s*\(Chronicle\s+(\d+)\)\s*---\n(.*?)(?=\n\n===|\n\n\[AI-Generated|$)'
                for match in re.finditer(context_pattern, content, re.DOTALL):
                    campaign_name = match.group(1).strip()
                    chronicle_num = match.group(2)
                    narrative = match.group(3).strip()
                    section_id = f"{campaign_name}_Chronicle_{chronicle_num}"
                    message_sections.append(("context", section_id, match.group(0), narrative))
                    section_counter += 1
                
                # Extract location summaries
                summary_pattern = r'===\s*LOCATION\s+SUMMARY\s*===\n\n(.*?)(?=\n\n===|\n\n\[AI-Generated|$)'
                for match in re.finditer(summary_pattern, content, re.DOTALL):
                    narrative = match.group(1).strip()
                    
                    # Extract location code if present
                    loc_code_match = re.search(r'\(([A-Z]+\d+)\)', narrative[:200])
                    if loc_code_match:
                        section_id = f"Location_{loc_code_match.group(1)}"
                    else:
                        section_id = f"LocationSummary_{self.get_section_hash(narrative)[:8]}"
                    
                    message_sections.append(("summary", section_id, match.group(0), narrative))
                    section_counter += 1
                
                # Extract location entries (Current Location: JSON)
                if content.startswith("Current Location:\n{\"locationId"):
                    # This is a location entry that needs special compression
                    location_json_str = content.split("Current Location:\n", 1)[1]
                    try:
                        location_data = json.loads(location_json_str)
                        location_id = location_data.get('locationId', 'Unknown')
                        section_id = f"LocationEntry_{location_id}"
                        message_sections.append(("location", section_id, content, location_json_str))
                        section_counter += 1
                    except json.JSONDecodeError:
                        pass  # Skip if not valid JSON
                
                if message_sections:
                    all_sections[i] = message_sections
        
        print(f"Found {section_counter} total sections across {len(all_sections)} messages")
        return all_sections
    
    def replace_system_prompt(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Replace the main system prompt with compressed version if applicable"""
        if message.get("role") == "system" and "content" in message:
            content = message["content"]
            
            # Check if this is the main DM system prompt
            if "You are a world-class 5th edition Dungeon" in content:
                # Load the compressed system prompt
                compressed_prompt_file = Path("prompts/system_prompt_compressed.txt")
                if compressed_prompt_file.exists():
                    with open(compressed_prompt_file, 'r', encoding='utf-8') as f:
                        compressed_content = f.read()
                    
                    original_len = len(content)
                    compressed_len = len(compressed_content)
                    reduction = (1 - compressed_len/original_len) * 100
                    
                    print(f"\n[SYSTEM PROMPT] Replacing main system prompt:")
                    print(f"  Original: {original_len:,} chars")
                    print(f"  Compressed: {compressed_len:,} chars")
                    print(f"  Reduction: {reduction:.1f}%")
                    
                    new_message = message.copy()
                    new_message["content"] = compressed_content
                    return new_message
        
        return message
    
    def process_conversation_history(self, conversation_file: str) -> List[Dict[str, Any]]:
        """Process a conversation history file and compress relevant sections in parallel"""
        
        start_time = datetime.now()
        
        with open(conversation_file, 'r', encoding='utf-8') as f:
            conversation = json.load(f)
        
        print(f"Processing {len(conversation)} messages...")
        print(f"Using {self.max_workers} parallel workers")
        print("=" * 60)
        
        # Step 1: Extract all sections that need compression
        all_sections = self.extract_all_sections(conversation)
        
        # Step 2: Prepare work items for parallel processing
        work_items = []
        work_index = 0
        for msg_idx, sections in all_sections.items():
            for section_type, section_id, full_match, narrative in sections:
                work_items.append((work_index, section_type, section_id, full_match, narrative))
                work_index += 1
        
        # Only proceed with compression if there are sections to compress
        if len(work_items) == 0:
            print("No sections require compression.")
            print("-" * 60)
            print("Using existing conversation without compression.")
        else:
            print(f"\nProcessing {len(work_items)} sections in parallel...")
            print("-" * 60)
        
        # Reset progress tracking
        self.completed_count = 0
        self.total_sections = len(work_items)
        
        # Only emit start event if there's work to do
        if len(work_items) > 0:
            try:
                from core.managers.status_manager import status_manager
                status_manager.emit_compression_event('compression_start', {
                    'total_sections': self.total_sections
                })
            except:
                pass
        
        # Step 3: Process sections in parallel
        results = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_item = {executor.submit(self.compress_section, item): item for item in work_items}
            
            # Process completed tasks
            for future in as_completed(future_to_item):
                result = future.result()
                idx, section_id, full_match, compressed_data, from_cache = result
                results[idx] = (section_id, full_match, compressed_data)
        
        # Save cache after all processing
        self.save_cache()
        
        print("-" * 60)
        print("Compression complete. Building output...")
        
        # Step 4: Reassemble conversation with compressed sections
        new_conversation = []
        result_lookup = {}
        
        # Build lookup table for quick access
        work_index = 0
        for msg_idx, sections in all_sections.items():
            for section_type, section_id, full_match, narrative in sections:
                if work_index in results:
                    result_lookup[(msg_idx, full_match)] = results[work_index]
                work_index += 1
        
        # Process each message
        for i, message in enumerate(conversation):
            # First check if this is a system prompt that needs replacement
            if message.get("role") == "system":
                message = self.replace_system_prompt(message)
            
            if i in all_sections and "content" in message:
                # This message has sections to replace
                modified_content = message["content"]
                
                for section_type, section_id, full_match, narrative in all_sections[i]:
                    if (i, full_match) in result_lookup:
                        _, _, compressed_data = result_lookup[(i, full_match)]
                        compressed_text = compressed_data.get('compressed', narrative)
                        
                        # Create appropriate header based on type, preserving identifying info
                        if "context" in section_type.lower():
                            # Extract module name and chronicle from section_id (e.g., "Keep_of_Doom_Chronicle_001")
                            parts = section_id.rsplit('_Chronicle_', 1)
                            if len(parts) == 2:
                                module_name = parts[0].replace('_', ' ')
                                chronicle_num = parts[1]
                                header = f"=== CAMPAIGN CONTEXT (COMPRESSED) ===\n\n--- {module_name} (Chronicle {chronicle_num}) ---"
                            else:
                                header = "=== CAMPAIGN CONTEXT (COMPRESSED) ==="
                        else:
                            # For location summaries, extract location info from the narrative start
                            # Look for pattern like "The Black Lantern Hearth (AD01):" at the beginning
                            location_match = re.match(r'^(.*?\([A-Z]+\d+\)):', narrative)
                            if location_match:
                                location_info = location_match.group(1)
                                header = f"=== LOCATION SUMMARY (COMPRESSED) ===\n\n{location_info}:"
                                # Remove the location info from compressed text if it's duplicated
                                if compressed_text.startswith(location_info):
                                    compressed_text = compressed_text[len(location_info):].lstrip(':').strip()
                            else:
                                header = "=== LOCATION SUMMARY (COMPRESSED) ==="
                        
                        compressed_replacement = f"{header}\n\n{compressed_text}"
                        modified_content = modified_content.replace(full_match, compressed_replacement)
                
                new_message = message.copy()
                new_message["content"] = modified_content
                new_conversation.append(new_message)
            else:
                # No other changes needed for this message
                new_conversation.append(message)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\nTotal processing time: {elapsed:.1f} seconds")
        
        # Calculate compression statistics and emit completion event only if compression occurred
        if self.total_sections > 0:
            try:
                from core.managers.status_manager import status_manager
                original_size = sum(len(json.dumps(m)) for m in conversation)
                compressed_size = sum(len(json.dumps(m)) for m in new_conversation)
                reduction_pct = round((1 - compressed_size/original_size) * 100) if original_size > 0 else 0
                
                status_manager.emit_compression_event('compression_complete', {
                    'reduction_percentage': reduction_pct,
                    'original_size': original_size,
                    'compressed_size': compressed_size
                })
            except:
                pass
        
        return new_conversation

def main():
    """Test the parallel compressor on actual conversation history"""
    
    # Use parallel workers from config with cache in proper location
    compressor = ParallelConversationCompressor()
    
    conversation_file = "modules/conversation_history/conversation_history.json"
    
    if not Path(conversation_file).exists():
        print(f"Error: {conversation_file} not found")
        return
    
    print(f"Parallel Conversation Compressor")
    print("=" * 60)
    print(f"Input: {conversation_file}")
    
    # Load original for comparison
    with open(conversation_file, 'r', encoding='utf-8') as f:
        original_conversation = json.load(f)
    
    # Process and compress
    new_conversation = compressor.process_conversation_history(conversation_file)
    
    # Save compressed conversation
    output_file = "conversation_history_compressed_parallel.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(new_conversation, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"Output: {output_file}")
    
    # Calculate statistics
    original_size = sum(len(json.dumps(m)) for m in original_conversation)
    compressed_size = sum(len(json.dumps(m)) for m in new_conversation)
    
    print(f"\nStatistics:")
    print(f"  Original size: {original_size:,} chars")
    print(f"  Compressed size: {compressed_size:,} chars")
    if original_size > 0:
        print(f"  Overall reduction: {(1 - compressed_size/original_size)*100:.1f}%")
    print(f"  Cache entries: {len(compressor.cache)}")
    
    # Show sample of compressed content
    print("\nSample of compressed content:")
    print("-" * 60)
    for i, msg in enumerate(new_conversation):
        if "COMPRESSED" in msg.get("content", ""):
            sample = msg["content"][:500] + "..." if len(msg["content"]) > 500 else msg["content"]
            print(f"Message {i} ({msg['role']}):")
            print(sample)
            print("-" * 60)
            break

if __name__ == "__main__":
    main()