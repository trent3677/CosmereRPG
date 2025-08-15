#!/usr/bin/env python3
"""
Compare monster files from modules with available videos and images
"""

import os
import json
from pathlib import Path

def get_module_monsters(module_path):
    """Get list of monsters from a module"""
    monsters = set()
    monster_dir = Path(module_path) / "monsters"
    if monster_dir.exists():
        for f in monster_dir.glob("*.json"):
            # Clean up monster names
            name = f.stem
            # Skip plural versions if singular exists
            if not name.endswith('s') or name in ['shadows', 'shadow_manifestations']:
                monsters.add(name)
    return monsters

def get_available_media():
    """Get available videos and images"""
    media_dir = Path("web/static/media/monsters")
    videos = set()
    images = set()
    thumbnails = set()
    
    if media_dir.exists():
        for f in media_dir.iterdir():
            if f.name.endswith("_video.mp4"):
                videos.add(f.name.replace("_video.mp4", ""))
            elif f.name.endswith("_thumb.jpg"):
                thumbnails.add(f.name.replace("_thumb.jpg", ""))
            elif f.name.endswith(".png"):
                images.add(f.stem)
    
    return videos, images, thumbnails

def main():
    # Get monsters from each module
    keep_monsters = get_module_monsters("modules/Keep_of_Doom")
    thornwood_monsters = get_module_monsters("modules/The_Thornwood_Watch")
    shadows_monsters = get_module_monsters("modules/Shadows_of_Kharos")
    
    # Get available media
    videos, images, thumbnails = get_available_media()
    
    # Combine all unique monsters
    all_monsters = keep_monsters | thornwood_monsters | shadows_monsters
    
    print("="*70)
    print("MONSTER VIDEO/IMAGE COMPARISON REPORT")
    print("="*70)
    
    # Keep of Doom Analysis
    print("\n=== KEEP OF DOOM ===")
    print(f"Total monsters: {len(keep_monsters)}")
    print("\nMonsters in module:")
    for m in sorted(keep_monsters):
        has_video = "✓" if m in videos else "✗"
        has_image = "✓" if m in images else "✗"
        has_thumb = "✓" if m in thumbnails else "✗"
        print(f"  {m:30} Video:{has_video}  Image:{has_image}  Thumb:{has_thumb}")
    
    keep_missing_video = keep_monsters - videos
    if keep_missing_video:
        print(f"\nMissing videos ({len(keep_missing_video)}):")
        for m in sorted(keep_missing_video):
            print(f"  - {m}")
    
    # Thornwood Watch Analysis
    print("\n=== THORNWOOD WATCH ===")
    print(f"Total monsters: {len(thornwood_monsters)}")
    print("\nMonsters in module:")
    for m in sorted(thornwood_monsters):
        has_video = "✓" if m in videos else "✗"
        has_image = "✓" if m in images else "✗"
        has_thumb = "✓" if m in thumbnails else "✗"
        print(f"  {m:30} Video:{has_video}  Image:{has_image}  Thumb:{has_thumb}")
    
    thornwood_missing_video = thornwood_monsters - videos
    if thornwood_missing_video:
        print(f"\nMissing videos ({len(thornwood_missing_video)}):")
        for m in sorted(thornwood_missing_video):
            print(f"  - {m}")
    
    # Shadows of Kharos Analysis
    if shadows_monsters:
        print("\n=== SHADOWS OF KHAROS ===")
        print(f"Total monsters: {len(shadows_monsters)}")
        print("\nMonsters in module:")
        for m in sorted(shadows_monsters):
            has_video = "✓" if m in videos else "✗"
            has_image = "✓" if m in images else "✗"
            has_thumb = "✓" if m in thumbnails else "✗"
            print(f"  {m:30} Video:{has_video}  Image:{has_image}  Thumb:{has_thumb}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    all_missing_video = all_monsters - videos
    all_missing_image = all_monsters - images
    
    print(f"\nTotal unique monsters across all modules: {len(all_monsters)}")
    print(f"Total with videos: {len(all_monsters & videos)}")
    print(f"Total missing videos: {len(all_missing_video)}")
    print(f"Total missing images: {len(all_missing_image)}")
    
    if all_missing_video:
        print("\n=== ALL MISSING VIDEOS ===")
        for m in sorted(all_missing_video):
            module = []
            if m in keep_monsters:
                module.append("Keep")
            if m in thornwood_monsters:
                module.append("Thornwood")
            if m in shadows_monsters:
                module.append("Shadows")
            print(f"  - {m:30} ({', '.join(module)})")
    
    # Extra videos not in any module
    extra_videos = videos - all_monsters
    if extra_videos:
        print("\n=== EXTRA VIDEOS (not in any module) ===")
        for v in sorted(extra_videos):
            print(f"  - {v}")

if __name__ == "__main__":
    main()