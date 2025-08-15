#!/usr/bin/env python3
"""
Process Ashbound Bandit Video
Using the same compression settings as compress_monster_videos.py
- Compress to 640x640 @ 1Mbps
- Generate 60x60 thumbnail
- Save ONLY compressed video and thumbnail to web/static/media
- Do NOT copy the original full-size video
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
        
        print(f"✓ Compression complete!")
        print(f"  Original size: {original_size:.2f} MB")
        print(f"  Compressed size: {compressed_size:.2f} MB")
        print(f"  Compression ratio: {compression_ratio:.1f}% reduction")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Compression failed: {e}")
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
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Get thumbnail size
        thumb_size = os.path.getsize(output_file) / 1024  # KB
        
        print(f"✓ Thumbnail generated!")
        print(f"  Size: {thumb_size:.2f} KB")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Thumbnail generation failed: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def main():
    """Process the ashbound bandit video"""
    
    print("="*60)
    print("ASHBOUND BANDIT VIDEO PROCESSOR")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nUsing compression settings from compress_monster_videos.py:")
    print("  - 640x640 resolution")
    print("  - 1Mbps bitrate")
    print("  - 24fps")
    print("  - 60x60 thumbnail")
    
    # Check for ffmpeg
    if not check_ffmpeg():
        print("\n✗ ERROR: ffmpeg is not installed!")
        print("Please install ffmpeg to process videos:")
        print("  - Windows: Download from https://ffmpeg.org/download.html")
        print("  - Mac: brew install ffmpeg")
        print("  - Linux: sudo apt-get install ffmpeg")
        sys.exit(1)
    
    print("\n✓ ffmpeg is installed")
    
    # Input file
    input_video = "ashbound_bandit.mp4"
    
    if not os.path.exists(input_video):
        print(f"\n✗ ERROR: {input_video} not found in current directory!")
        print("Please ensure the video file is in the root directory.")
        sys.exit(1)
    
    print(f"\n✓ Found input video: {input_video}")
    input_size = os.path.getsize(input_video) / (1024 * 1024)
    print(f"  Size: {input_size:.2f} MB")
    
    # Create output directories (matching compress_monster_videos.py structure)
    os.makedirs('web/static/media/videos', exist_ok=True)
    os.makedirs('web/static/media/monsters', exist_ok=True)
    print(f"\n✓ Output directories ready")
    
    # Output files (matching naming convention from compress_monster_videos.py)
    monster_name = "ashbound_bandit"
    compressed_video = f'web/static/media/videos/{monster_name}_compressed.mp4'
    
    # Also create non-compressed filename for compatibility (but still compressed content)
    standard_video = f'web/static/media/{monster_name}_video.mp4'
    
    # Thumbnail in monsters folder
    thumbnail = f'web/static/media/monsters/{monster_name}_thumb.jpg'
    
    print("\n" + "-"*60)
    print("PROCESSING STEPS:")
    print("-"*60)
    
    # Step 1: Compress video
    print("\n[1/3] Video Compression (to videos/ folder)")
    if compress_video(input_video, compressed_video):
        print("✓ Video compression successful")
    else:
        print("✗ Video compression failed")
        sys.exit(1)
    
    # Step 2: Copy compressed to standard location for compatibility
    print("\n[2/3] Creating compatibility copy in media/ folder")
    try:
        import shutil
        shutil.copy2(compressed_video, standard_video)
        print(f"✓ Copied to {standard_video}")
    except Exception as e:
        print(f"✗ Failed to copy: {e}")
    
    # Step 3: Generate thumbnail
    print("\n[3/3] Thumbnail Generation (to monsters/ folder)")
    if generate_thumbnail(input_video, thumbnail):
        print("✓ Thumbnail generation successful")
    else:
        print("✗ Thumbnail generation failed")
        sys.exit(1)
    
    # Summary
    print("\n" + "="*60)
    print("PROCESSING COMPLETE!")
    print("="*60)
    print("\nFiles created:")
    print(f"  1. {compressed_video} (compressed)")
    print(f"  2. {standard_video} (compatibility copy)")
    print(f"  3. {thumbnail} (60x60 thumbnail)")
    print("\n✓ Original video was NOT copied to media folder")
    print("✓ All files use standard compression settings (640x640, 1Mbps)")
    
    # Instructions for use
    print("\n" + "-"*60)
    print("USAGE IN GAME:")
    print("-"*60)
    print("The monster can now use these files:")
    print(f'  "portrait": "{monster_name}_thumb.jpg",')
    print(f'  "video": "{monster_name}_video.mp4"')
    print("\nFiles match existing naming conventions in web/static/media/")

if __name__ == "__main__":
    main()