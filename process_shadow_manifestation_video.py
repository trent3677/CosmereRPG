#!/usr/bin/env python3
"""
Process Shadow Manifestation Video
Using the same compression settings as other monster videos
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

def find_video_file():
    """Find the shadow manifestation video file"""
    possible_names = [
        "shadow_manifestation_animation.mp4",
        "shadow_manifestation.mp4",
        "shadow_manifestations_animation.mp4",
        "shadow_manifestations.mp4",
        "manifestation_animation.mp4"
    ]
    
    for name in possible_names:
        if os.path.exists(name):
            return name
    
    # If not found, list all mp4 files to help identify it
    mp4_files = [f for f in os.listdir('.') if f.endswith('.mp4') and 'manifestation' in f.lower()]
    if mp4_files:
        return mp4_files[0]
    
    return None

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

def main():
    """Process shadow manifestation video"""
    
    print("="*60)
    print("SHADOW MANIFESTATION VIDEO PROCESSING")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not check_ffmpeg():
        print("\n[ERROR] ffmpeg is not installed or not in PATH")
        print("Please install ffmpeg to compress videos")
        return 1
    
    # Find the video file
    print("\nSearching for shadow manifestation video...")
    input_file = find_video_file()
    
    if not input_file:
        print("[ERROR] Could not find shadow manifestation video file")
        print("Looking for files with 'manifestation' in the name")
        return 1
    
    print(f"Found video file: {input_file}")
    
    # Output paths in monsters folder
    output_dir = "web/static/media/monsters"
    os.makedirs(output_dir, exist_ok=True)
    
    # Note: using singular "shadow_manifestation" for consistency
    compressed_file = os.path.join(output_dir, "shadow_manifestation_video.mp4")
    thumbnail_file = os.path.join(output_dir, "shadow_manifestation_thumb.jpg")
    
    print(f"\n{'='*60}")
    print(f"Processing SHADOW MANIFESTATION")
    print(f"{'='*60}")
    
    # Compress video
    if not compress_video(input_file, compressed_file):
        return 1
    
    # Generate thumbnail from compressed video (better quality)
    if not generate_thumbnail(compressed_file, thumbnail_file):
        return 1
    
    print(f"\n[OK] Successfully processed shadow manifestation!")
    print(f"  Video: {compressed_file}")
    print(f"  Thumbnail: {thumbnail_file}")
    
    print("\n" + "="*60)
    print("PROCESSING COMPLETE")
    print("="*60)
    print("\nVideo and thumbnail are ready in web/static/media/monsters/")
    print("The monster will now have animation in the game!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())