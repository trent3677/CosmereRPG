#!/usr/bin/env python3
"""
Process time-of-day images for the adventure box
Creates square thumbnails and moves to appropriate folders
"""

import os
from PIL import Image

def process_time_image(input_file, time_name):
    """Process a time-of-day image"""
    print(f"\nProcessing {time_name}...")
    
    # Open the image
    img = Image.open(input_file)
    print(f"  Original size: {img.size}")
    
    # Create square thumbnail (200x200 for the adventure box)
    # Using center crop to maintain aspect ratio
    width, height = img.size
    min_dimension = min(width, height)
    
    # Calculate crop box for center square
    left = (width - min_dimension) // 2
    top = (height - min_dimension) // 2
    right = left + min_dimension
    bottom = top + min_dimension
    
    # Crop to square
    square_img = img.crop((left, top, right, bottom))
    
    # Resize to 200x200 for adventure box
    display_img = square_img.resize((200, 200), Image.Resampling.LANCZOS)
    
    # Save to web media folder
    output_dir = "web/static/media/environment"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = f"{output_dir}/{time_name}.jpg"
    display_img.save(output_path, 'JPEG', quality=90)
    print(f"  Saved to: {output_path}")
    print(f"  Final size: 200x200")
    
    return output_path

def main():
    """Process all time-of-day images"""
    print("="*60)
    print("TIME-OF-DAY IMAGE PROCESSOR")
    print("="*60)
    
    # Define the images to process
    time_images = [
        ('sunrise.png', 'sunrise'),
        ('midday.png', 'midday'),
        ('sunset.png', 'sunset'),
        ('nightfall.png', 'nightfall')
    ]
    
    processed = []
    
    for input_file, time_name in time_images:
        if os.path.exists(input_file):
            output = process_time_image(input_file, time_name)
            processed.append(output)
        else:
            print(f"Warning: {input_file} not found")
    
    print("\n" + "="*60)
    print("PROCESSING COMPLETE")
    print("="*60)
    print(f"Processed {len(processed)} images")
    print("\nImages ready for use in adventure box:")
    for path in processed:
        print(f"  - {path}")

if __name__ == "__main__":
    main()