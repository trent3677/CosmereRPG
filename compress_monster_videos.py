#!/usr/bin/env python3
"""
compress_monster_videos.py

Compress monster animation videos for web interface use.
Processes raw Kling AI videos (or any MP4) into game-ready format:
- Compresses to 640x640 @ 1Mbps (~1MB for 5 seconds)
- Generates 60x60 thumbnail images
- Saves to standard web/static/media locations

Usage:
    python compress_monster_videos.py
    
Files are saved as:
    web/static/media/videos/[name]_compressed.mp4
    web/static/media/videos/[name].mp4 (copy for compatibility)
    web/static/media/monsters/[name]_thumb.jpg
"""

import os
import subprocess
from datetime import datetime

def compress_video(input_file, output_file):
    """Compress video to match skeleton_compressed.mp4 specs: 640x640, 24fps, ~1Mbps"""
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
    
    print(f"Compressing {input_file} to 640x640 @ 1Mbps...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error compressing {input_file}: {result.stderr}")
        return False
    print(f"Compressed to {output_file}")
    return True

def generate_thumbnail(video_file, thumbnail_file):
    """Generate 60x60 thumbnail from first frame"""
    cmd = [
        'ffmpeg',
        '-i', video_file,
        '-vf', 'scale=60:60:force_original_aspect_ratio=increase,crop=60:60',
        '-frames:v', '1',
        '-q:v', '5',  # JPEG quality
        '-y',
        thumbnail_file
    ]
    
    print(f"Generating 60x60 thumbnail...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error generating thumbnail: {result.stderr}")
        return False
    print(f"Thumbnail saved to {thumbnail_file}")
    return True

def process_animation(source_file, monster_name):
    """Process a single animation file"""
    print(f"\n{'='*60}")
    print(f"Processing: {monster_name}")
    print('='*60)
    
    # Ensure output directories exist
    os.makedirs('web/static/media/videos', exist_ok=True)
    os.makedirs('web/static/media/monsters', exist_ok=True)
    
    # Output paths - matching existing convention
    compressed_video = f'web/static/media/videos/{monster_name}_compressed.mp4'
    thumbnail = f'web/static/media/monsters/{monster_name}_thumb.jpg'
    
    # Remove uncompressed version if it exists
    uncompressed = f'web/static/media/videos/{monster_name}.mp4'
    if os.path.exists(uncompressed):
        size_mb = os.path.getsize(uncompressed) / (1024 * 1024)
        if size_mb > 5:
            print(f"Removing uncompressed file ({size_mb:.1f}MB): {uncompressed}")
            os.remove(uncompressed)
    
    # Compress video
    if not compress_video(source_file, compressed_video):
        print(f"Failed to compress {source_file}")
        return False
    
    # Get file sizes for comparison
    original_size = os.path.getsize(source_file) / (1024 * 1024)  # MB
    compressed_size = os.path.getsize(compressed_video) / (1024 * 1024)  # MB
    compression_ratio = (1 - compressed_size/original_size) * 100
    
    print(f"Original size: {original_size:.2f} MB")
    print(f"Compressed size: {compressed_size:.2f} MB")
    print(f"Compression: {compression_ratio:.1f}% reduction")
    
    # Verify size is similar to skeleton (should be 1-2MB for 5 seconds)
    if compressed_size > 2:
        print(f"WARNING: File larger than expected ({compressed_size:.2f}MB vs ~1.3MB target)")
    
    # Generate thumbnail
    if not generate_thumbnail(compressed_video, thumbnail):
        print(f"Failed to generate thumbnail for {monster_name}")
        return False
    
    # Create main video file (copy of compressed)
    final_video = f'web/static/media/videos/{monster_name}.mp4'
    subprocess.run(['cp', compressed_video, final_video], capture_output=True)
    print(f"Created main video file: {final_video}")
    
    return True

def main():
    """Process all new animation files"""
    
    print("="*60)
    print("MONSTER VIDEO COMPRESSION")
    print("Target: 640x640, 24fps, ~1Mbps (matching skeleton_compressed.mp4)")
    print("="*60)
    
    # Define the animations to process
    animations = [
        ('zombie_animation.mp4', 'zombie'),
        ('animated_weapon_animation.mp4', 'animated_weapon')
    ]
    
    # Process each animation
    success_count = 0
    failed = []
    
    for source_file, monster_name in animations:
        if os.path.exists(source_file):
            if process_animation(source_file, monster_name):
                success_count += 1
            else:
                failed.append(monster_name)
        else:
            print(f"Source file not found: {source_file}")
            failed.append(monster_name)
    
    # Summary
    print("\n" + "="*60)
    print("PROCESSING COMPLETE")
    print("="*60)
    print(f"Successfully processed: {success_count}/{len(animations)}")
    
    if failed:
        print(f"Failed: {', '.join(failed)}")
    
    print("\nFinal files:")
    for _, monster_name in animations:
        compressed = f'web/static/media/videos/{monster_name}_compressed.mp4'
        main = f'web/static/media/videos/{monster_name}.mp4'
        thumb = f'web/static/media/monsters/{monster_name}_thumb.jpg'
        
        if os.path.exists(compressed):
            size = os.path.getsize(compressed) / (1024 * 1024)
            print(f"\n{monster_name}:")
            print(f"  Compressed: {compressed} ({size:.2f}MB)")
            if os.path.exists(main):
                print(f"  Main: {main}")
            if os.path.exists(thumb):
                print(f"  Thumbnail: {thumb}")

if __name__ == "__main__":
    main()