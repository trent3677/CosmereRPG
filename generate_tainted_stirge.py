#!/usr/bin/env python3
"""
Generate Tainted Stirge Monster Portrait Only
Using gpt-image-1 model with auto quality
"""

import time
import base64
from openai import OpenAI
from datetime import datetime
import os
from PIL import Image
import requests
from io import BytesIO

from config import OPENAI_API_KEY

def generate_monster_portrait(monster_name, monster_description):
    """Generate a monster portrait using gpt-image-1"""
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Create the full prompt with D&D context
    prompt = f"""Create an ultra detailed photorealistic Dungeons and Dragons monster portrait. 
{monster_description}
Square format 1:1 aspect ratio for game interface."""
    
    print("\n" + "="*60)
    print(f"GENERATING: {monster_name.upper()}")
    print("="*60)
    print(f"\nModel: gpt-image-1")
    print(f"Quality: auto")
    print(f"Size: 1024x1024")
    
    print(f"\nPrompt preview:")
    print("-"*40)
    print(prompt[:200] + "...")
    print("-"*40)
    
    print(f"\nStarting generation at {datetime.now().strftime('%H:%M:%S')}...")
    start_time = time.time()
    
    try:
        # Generate image using gpt-image-1
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            quality="auto",
            n=1
        )
        
        elapsed = time.time() - start_time
        print(f"Generation completed in {elapsed:.2f} seconds")
        
        # Get image data - handle both URL and base64 formats
        image_url = getattr(response.data[0], 'url', None)
        b64_json = getattr(response.data[0], 'b64_json', None)
        
        # Get the image
        if b64_json:
            print(f"\nDecoding base64 image data...")
            image_data = base64.b64decode(b64_json)
            img = Image.open(BytesIO(image_data))
        elif image_url:
            print(f"\nDownloading from URL...")
            img_response = requests.get(image_url)
            img = Image.open(BytesIO(img_response.content))
        else:
            raise Exception("No image data found in response")
        
        # Create output directory structure
        output_dir = "monster_portraits"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the portrait
        safe_name = monster_name.lower().replace(" ", "_").replace("-", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/{safe_name}_{timestamp}.png"
        img.save(filename)
        
        print(f"\nImage saved to: {filename}")
        print(f"Dimensions: {img.size}")
        
        # Create thumbnail for web interface (60x60)
        thumb = img.copy()
        thumb.thumbnail((60, 60), Image.Resampling.LANCZOS)
        thumb_filename = f"{output_dir}/{safe_name}_thumb_{timestamp}.jpg"
        thumb.save(thumb_filename, 'JPEG', quality=85)
        print(f"Thumbnail saved to: {thumb_filename}")
        
        # Also save to web/static/media for immediate use
        web_dir = "web/static/media"
        if os.path.exists(web_dir):
            web_filename = f"{web_dir}/{safe_name}.png"
            img.save(web_filename)
            print(f"Also saved to web interface: {web_filename}")
        
        print("\nSUCCESS!")
        return {"success": True, "filename": filename, "time": elapsed}
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return {"success": False, "error": str(e)}

# Tainted Stirge with revised safer prompt
TAINTED_STIRGE_DESCRIPTION = """
    A fantasy bat-like creature corrupted by shadow magic, about 1 foot long with a 
    3-foot wingspan. Its body resembles a fusion of bat and large insect, covered 
    in patchy gray fur and hardened plates. The fur is mottled with dark purple patterns 
    showing magical corruption. Four leathery wings spread wide, the membranes showing 
    tears and dark purple energy. It has a long sharp beak-like mouth structure for 
    feeding. Eight thin legs end in tiny hooked claws for gripping. Multiple glowing 
    red eyes arranged across its head, some clouded with purple shadow energy. Dark 
    purple veins pulse with magical energy beneath semi-transparent wing membranes. 
    The creature hovers in flight, wings beating rapidly, surrounded by wisps of purple 
    shadow magic. Set against a dark cave background with purple magical ambient lighting.
    Photorealistic detail emphasizing the fantasy creature design, with translucent wing
    membranes showing magical corruption, creating a menacing flying predator.
    """

def main():
    """Generate just the Tainted Stirge portrait"""
    
    print("="*60)
    print("TAINTED STIRGE PORTRAIT GENERATION")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    result = generate_monster_portrait("Tainted Stirge", TAINTED_STIRGE_DESCRIPTION)
    
    # Print summary
    print("\n" + "="*60)
    print("GENERATION SUMMARY")
    print("="*60)
    
    if result["success"]:
        print(f"\n✓ SUCCESS: Tainted Stirge portrait generated")
        print(f"  File: {result['filename']}")
        print(f"  Time: {result['time']:.2f} seconds")
    else:
        print(f"\n✗ FAILED: {result.get('error', 'Unknown error')}")
        print("\nTroubleshooting tips:")
        print("- Check if the prompt still triggers safety filters")
        print("- Try adjusting descriptions to be more fantasy-focused")
        print("- Ensure API key is valid and has image generation access")

if __name__ == "__main__":
    main()