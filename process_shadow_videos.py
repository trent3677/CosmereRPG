#!/usr/bin/env python3
"""
Process Shadow Relic and Shadow Servant Videos
Using the same compression settings as compress_monster_videos.py
- Compress to 640x640 @ 1Mbps
- Generate 60x60 thumbnail
- Save to web/static/media/monsters/
"""

import subprocess
import os
import sys
from datetime import datetime

def check_ffmpeg():
    """Check if ffmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def compress_video(input_file, output_file):
    """Compress video to match skeleton_compressed.mp4 specs: 640x640, 24fps, ~1Mbps"""
    print(f"\nCompressing video: {input_file}")
    print(f"Output: {output_file}")
    print("Settings: 640x640 @ 1Mbps, 24fps")
    
    # EXACT same settings from compress_monster_videos.py
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'libx264',
        '-preset', 'slow',
        '-b:v', '1000k',  # Target bitrate ~1Mbps like skeleton
        '-vf', 'scale=640:640:force_original_aspect_ratio=decrease,pad=640:640:(ow-iw)/2:(oh-ih)/2',  # 640x640 square
        '-r', '24',  # 24fps like skeleton
        '-c:a', 'aac',
        '-b:a', '64k',
        '-movflags', '+faststart',
        '-y',  # Overwrite output
        output_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Get file sizes for comparison
        original_size = os.path.getsize(input_file) / (1024 * 1024)  # MB
        compressed_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        compression_ratio = (1 - compressed_size/original_size) * 100
        
        print(f"[OK] Compression complete!")
        print(f"  Original size: {original_size:.2f} MB")
        print(f"  Compressed size: {compressed_size:.2f} MB")
        print(f"  Compression ratio: {compression_ratio:.1f}% reduction")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Compression failed: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def generate_thumbnail(input_file, output_file):
    """Generate 60x60 thumbnail from first frame - EXACT same as compress_monster_videos.py"""
    print(f"\nGenerating 60x60 thumbnail: {output_file}")
    
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-vf', 'scale=60:60:force_original_aspect_ratio=increase,crop=60:60',
        '-frames:v', '1',
        '-q:v', '5',  # JPEG quality
        '-y',
        output_file
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"[OK] Thumbnail created: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Thumbnail generation failed: {e}")
        return False

def process_monster_video(animation_file, monster_name):
    """Process a single monster video file"""
    
    if not os.path.exists(animation_file):
        print(f"[ERROR] Animation file not found: {animation_file}")
        return False
    
    # Output paths in monsters folder
    output_dir = "web/static/media/monsters"
    os.makedirs(output_dir, exist_ok=True)
    
    compressed_file = os.path.join(output_dir, f"{monster_name}_video.mp4")
    thumbnail_file = os.path.join(output_dir, f"{monster_name}_thumb.jpg")
    
    print(f"\n{'='*60}")
    print(f"Processing {monster_name.upper()}")
    print(f"{'='*60}")
    
    # Compress video
    if not compress_video(animation_file, compressed_file):
        return False
    
    # Generate thumbnail from compressed video (better quality)
    if not generate_thumbnail(compressed_file, thumbnail_file):
        return False
    
    print(f"\n[OK] Successfully processed {monster_name}!")
    print(f"  Video: {compressed_file}")
    print(f"  Thumbnail: {thumbnail_file}")
    
    return True

def main():
    """Process shadow relic and shadow servant videos"""
    
    print("="*60)
    print("SHADOW MONSTER VIDEO PROCESSING")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not check_ffmpeg():
        print("\n[ERROR] ffmpeg is not installed or not in PATH")
        print("Please install ffmpeg to compress videos")
        return 1
    
    # Define the videos to process
    videos_to_process = [
        ("shadow_relic_animation.mp4", "shadow_relic"),
        ("shadow_servant_animation.mp4", "phantom_servant")  # Note: using phantom_servant as the monster name
    ]
    
    successful = []
    failed = []
    
    for animation_file, monster_name in videos_to_process:
        if process_monster_video(animation_file, monster_name):
            successful.append(monster_name)
        else:
            failed.append(monster_name)
    
    # Print summary
    print("\n" + "="*60)
    print("PROCESSING SUMMARY")
    print("="*60)
    
    if successful:
        print(f"\n[OK] Successfully processed {len(successful)} videos:")
        for name in successful:
            print(f"  - {name}")
    
    if failed:
        print(f"\n[ERROR] Failed to process {len(failed)} videos:")
        for name in failed:
            print(f"  - {name}")
    
    if not failed:
        print("\nAll videos processed successfully!")
        print("Videos and thumbnails are ready in web/static/media/monsters/")
        return 0
    else:
        print("\nSome videos failed to process. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())