#!/usr/bin/env python3
"""
Generate Shadow Relic Monster Portrait
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
    print(prompt[:300] + "...")
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
        
        # Save directly to monsters folder
        web_dir = "web/static/media/monsters"
        os.makedirs(web_dir, exist_ok=True)
        
        # Save the portrait
        safe_name = monster_name.lower().replace(" ", "_").replace("-", "_")
        web_filename = f"{web_dir}/{safe_name}.png"
        img.save(web_filename)
        print(f"\nImage saved to: {web_filename}")
        print(f"Dimensions: {img.size}")
        
        # Create thumbnail for web interface (60x60)
        thumb = img.copy()
        thumb.thumbnail((60, 60), Image.Resampling.LANCZOS)
        web_thumb = f"{web_dir}/{safe_name}_thumb.jpg"
        thumb.save(web_thumb, 'JPEG', quality=85)
        print(f"Thumbnail saved to: {web_thumb}")
        
        print("\nSUCCESS!")
        return {"success": True, "filename": web_filename, "time": elapsed}
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return {"success": False, "error": str(e)}

# Shadow Relic Description
SHADOW_RELIC_DESCRIPTION = """
An ancient corrupted artifact wreathed in living shadows.
The relic appears as an ornate obsidian or dark metal object (such as a crown, amulet, 
or crystalline orb) that pulses with malevolent energy. Tendrils of pure shadow emanate 
from the relic, writhing and reaching outward like living tentacles. The artifact itself 
is covered in sinister runes that glow with a dim purple or green light. Dark energy 
crackles around it like black lightning, and the shadows it casts seem to move independently 
of any light source. The relic hovers slightly above the ground, surrounded by a vortex 
of swirling darkness and shadow fragments. Photorealistic detail, ultra detailed, 
8K quality, cinematic lighting, dark fantasy atmosphere.
"""

def main():
    """Generate Shadow Relic portrait"""
    
    print("="*60)
    print("SHADOW RELIC PORTRAIT GENERATION")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    result = generate_monster_portrait("shadow_relic", SHADOW_RELIC_DESCRIPTION)
    
    # Print summary
    print("\n" + "="*60)
    print("GENERATION SUMMARY")
    print("="*60)
    
    if result["success"]:
        print(f"\n[OK] SUCCESS: shadow_relic portrait generated")
        print(f"  File: {result['filename']}")
        print(f"  Time: {result['time']:.2f} seconds")
    else:
        print(f"\n[ERROR] FAILED: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()