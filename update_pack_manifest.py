#!/usr/bin/env python3
"""Update pack manifest with existing monster assets"""
import json
import os
from pathlib import Path

def update_photorealistic_pack():
    """Scan and update the photorealistic pack manifest"""
    pack_dir = Path("graphic_packs/photorealistic")
    manifest_path = pack_dir / "manifest.json"
    
    # Load existing manifest
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Scan for monsters
    monsters = {}
    thumbnails_dir = pack_dir / "monsters" / "thumbnails"
    videos_dir = pack_dir / "monsters" / "videos"
    images_dir = pack_dir / "monsters" / "images"
    
    # Get all thumbnails (base reference)
    for thumb_file in thumbnails_dir.glob("*_thumb.jpg"):
        monster_name = thumb_file.stem.replace("_thumb", "")
        
        # Check for corresponding video
        video_file = videos_dir / f"{monster_name}_video.mp4"
        video_path = f"graphic_packs/photorealistic/monsters/videos/{video_file.name}" if video_file.exists() else ""
        
        # Check for full image
        image_file = None
        for ext in ['.png', '.jpg', '.jpeg']:
            potential_image = images_dir / f"{monster_name}{ext}"
            if potential_image.exists():
                image_file = potential_image
                break
        
        image_path = f"graphic_packs/photorealistic/monsters/images/{image_file.name}" if image_file else ""
        
        # Create monster entry
        display_name = monster_name.replace("_", " ").title()
        monsters[display_name] = {
            "id": monster_name,
            "thumbnail_path": f"graphic_packs/photorealistic/monsters/thumbnails/{thumb_file.name}",
            "image_path": image_path,
            "video_path": video_path,
            "has_video": video_file.exists()
        }
    
    # Update manifest
    manifest["monsters"] = monsters
    manifest["total_monsters"] = len(monsters)
    manifest["total_videos"] = sum(1 for m in monsters.values() if m["has_video"])
    
    # Save updated manifest
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Updated photorealistic pack manifest:")
    print(f"  - Total monsters: {len(monsters)}")
    print(f"  - With videos: {manifest['total_videos']}")
    print(f"  - Pack location: {pack_dir}")

if __name__ == "__main__":
    update_photorealistic_pack()