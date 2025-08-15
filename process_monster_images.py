#!/usr/bin/env python3
"""
Process monster portraits: resize to square video dimensions (640x640), 
copy thumbnails, and organize in game folder.
Does not overwrite existing files.
"""

import os
import sys
from pathlib import Path
from PIL import Image
import shutil

# Configuration
SOURCE_DIR = "monster_portraits"  # Source folder with original images
TARGET_DIR = "web/static/media/monsters"  # Destination folder - CORRECTED PATH
VIDEO_SIZE = 640  # Square video dimensions (640x640)

def ensure_directories():
    """Create necessary directories if they don't exist."""
    Path(TARGET_DIR).mkdir(parents=True, exist_ok=True)
    print(f"[OK] Target directory ready: {TARGET_DIR}")

def get_monster_id_from_filename(filename):
    """Extract monster ID from filename."""
    # Remove extension
    name = Path(filename).stem
    
    # Remove timestamp suffix (e.g., _20250810_153718)
    import re
    # Pattern for _YYYYMMDD_HHMMSS
    timestamp_pattern = r'_\d{8}_\d{6}$'
    name = re.sub(timestamp_pattern, '', name)
    
    # Remove _thumb suffix if present
    if name.endswith('_thumb'):
        name = name[:-6]
    
    return name

def resize_image_to_square(image_path, output_path, size=VIDEO_SIZE):
    """Resize image to square format (640x640) with black padding if needed."""
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create a black background
                background = Image.new('RGB', img.size, (0, 0, 0))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calculate how to fit image into square
            img_ratio = img.width / img.height
            
            if img_ratio > 1:
                # Image is wider - fit to width
                new_width = size
                new_height = int(size / img_ratio)
            else:
                # Image is taller or square - fit to height
                new_height = size
                new_width = int(size * img_ratio)
            
            # Resize the image
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create square black background and paste centered
            final_img = Image.new('RGB', (size, size), (0, 0, 0))
            x_offset = (size - new_width) // 2
            y_offset = (size - new_height) // 2
            final_img.paste(img_resized, (x_offset, y_offset))
            
            # Save the resized image
            final_img.save(output_path, 'JPEG', quality=95)
            return True
    except Exception as e:
        print(f"[ERROR] Failed to resize {image_path}: {e}")
        return False

def copy_thumbnail(source_thumb, target_thumb):
    """Copy existing thumbnail to target directory."""
    try:
        shutil.copy2(source_thumb, target_thumb)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to copy thumbnail: {e}")
        return False

def process_monster_portraits():
    """Main processing function."""
    ensure_directories()
    
    # Check if source directory exists
    if not os.path.exists(SOURCE_DIR):
        print(f"[ERROR] Source directory '{SOURCE_DIR}' not found!")
        print("Please ensure your monster portraits are in the 'monster_portraits' folder.")
        return
    
    # Get all PNG files (main images, not thumbnails)
    main_images = []
    thumbnail_map = {}
    
    for file in Path(SOURCE_DIR).iterdir():
        if file.suffix.lower() == '.png':
            # Skip if it's a preview or special file
            if '_preview' in file.stem:
                continue
            main_images.append(file)
            
            # Look for corresponding thumbnail
            monster_id = get_monster_id_from_filename(file.name)
            # Try to find matching thumbnail
            for thumb_file in Path(SOURCE_DIR).glob(f"{file.stem}_thumb*.jpg"):
                thumbnail_map[file] = thumb_file
                break
            # Also check for simpler thumb pattern
            if file not in thumbnail_map:
                for thumb_file in Path(SOURCE_DIR).glob(f"{monster_id}_thumb*.jpg"):
                    thumbnail_map[file] = thumb_file
                    break
    
    if not main_images:
        print(f"[WARNING] No PNG images found in '{SOURCE_DIR}'")
        return
    
    print(f"\n[INFO] Found {len(main_images)} images to process")
    print(f"[INFO] Found {len(thumbnail_map)} matching thumbnails")
    print("-" * 60)
    
    processed = 0
    skipped = 0
    failed = 0
    thumbs_copied = 0
    thumbs_skipped = 0
    
    for image_file in sorted(main_images):
        monster_id = get_monster_id_from_filename(image_file.name)
        
        # Define output paths
        main_image_path = Path(TARGET_DIR) / f"{monster_id}.jpg"
        thumb_path = Path(TARGET_DIR) / f"{monster_id}_thumb.jpg"
        
        print(f"\nProcessing: {image_file.name}")
        print(f"  Monster ID: {monster_id}")
        
        # Process main image (640x640 square)
        if main_image_path.exists():
            print(f"  [SKIP] Main image already exists: {main_image_path.name}")
            skipped += 1
        else:
            if resize_image_to_square(image_file, main_image_path):
                print(f"  [OK] Created main image (640x640): {main_image_path.name}")
                processed += 1
            else:
                print(f"  [FAIL] Could not create main image")
                failed += 1
                continue
        
        # Copy thumbnail if it exists
        if image_file in thumbnail_map:
            source_thumb = thumbnail_map[image_file]
            if thumb_path.exists():
                print(f"  [SKIP] Thumbnail already exists: {thumb_path.name}")
                thumbs_skipped += 1
            else:
                if copy_thumbnail(source_thumb, thumb_path):
                    print(f"  [OK] Copied thumbnail: {thumb_path.name}")
                    thumbs_copied += 1
                else:
                    print(f"  [FAIL] Could not copy thumbnail")
        else:
            print(f"  [INFO] No thumbnail found for this image")
    
    # Summary
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Main Images:")
    print(f"  Processed: {processed}")
    print(f"  Skipped:   {skipped} (already exist)")
    print(f"  Failed:    {failed}")
    print(f"\nThumbnails:")
    print(f"  Copied:    {thumbs_copied}")
    print(f"  Skipped:   {thumbs_skipped} (already exist)")
    print(f"\nAll files saved to: {TARGET_DIR}")
    
    # List what we have for each monster
    print("\n" + "-" * 60)
    print("MONSTER MEDIA INVENTORY:")
    print("-" * 60)
    
    # Get unique monster IDs
    monster_ids = set()
    for file in Path(TARGET_DIR).iterdir():
        if file.suffix.lower() in {'.jpg', '.mp4'}:
            # Extract base monster ID
            name = file.stem
            if name.endswith('_thumb'):
                name = name[:-6]
            elif name.endswith('_video'):
                name = name[:-6]
            monster_ids.add(name)
    
    # Count totals
    total_with_all = 0
    total_with_video = 0
    total_missing_video = 0
    
    for monster_id in sorted(monster_ids):
        main_img = Path(TARGET_DIR) / f"{monster_id}.jpg"
        thumb = Path(TARGET_DIR) / f"{monster_id}_thumb.jpg"
        video = Path(TARGET_DIR) / f"{monster_id}_video.mp4"
        
        assets = []
        if main_img.exists():
            assets.append("IMG")
        if thumb.exists():
            assets.append("THM")
        if video.exists():
            assets.append("VID")
            total_with_video += 1
        else:
            total_missing_video += 1
        
        if len(assets) == 3:
            total_with_all += 1
        
        if assets:
            status = "[*]" if len(assets) == 3 else "[ ]"
            print(f"  {status} {monster_id}: {', '.join(assets)}")
    
    print("\n" + "-" * 60)
    print("STATISTICS:")
    print("-" * 60)
    print(f"Total monsters: {len(monster_ids)}")
    print(f"Complete (IMG+THM+VID): {total_with_all}")
    print(f"Have videos: {total_with_video}")
    print(f"Missing videos: {total_missing_video}")

if __name__ == "__main__":
    try:
        print("MONSTER IMAGE PROCESSOR")
        print("=" * 60)
        print(f"This script will:")
        print(f"  1. Resize PNG images to 640x640 (square video format)")
        print(f"  2. Copy existing thumbnails")
        print(f"  3. Save to {TARGET_DIR}")
        print(f"  4. NOT overwrite existing files")
        print()
        
        response = input("Continue? (y/n): ").strip().lower()
        if response == 'y':
            process_monster_portraits()
        else:
            print("Cancelled.")
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)