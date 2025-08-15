#!/usr/bin/env python3
"""
Generate Shadow Manifestation Monster Portrait (Singular, Scary Version)
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
        
        # Also save to monster_portraits folder for archival
        archive_dir = "monster_portraits"
        os.makedirs(archive_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_filename = f"{archive_dir}/{safe_name}_{timestamp}.png"
        img.save(archive_filename)
        print(f"Archive copy saved to: {archive_filename}")
        
        print("\nSUCCESS!")
        return {"success": True, "filename": web_filename, "time": elapsed}
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return {"success": False, "error": str(e)}

# Shadow Manifestation Description - SINGULAR, SCARY, WITH CONTRASTING BACKGROUND
SHADOW_MANIFESTATION_DESCRIPTION = """
A terrifying shadow creature manifesting as a single, monstrous entity of pure black darkness,
standing in the Relic Chamber of an ancient keep dungeon.

SETTING: The creature stands in a circular ritual chamber with glowing purple arcane symbols 
on the domed ceiling above. Seven stone pillars carved with ancient scenes form a circle around 
the room, lit by flickering torchlight. The floor has concentric circles carved into gray stone, 
and purple magical energy emanates from a floating shadow relic on a raised dais behind the creature.
The chamber is illuminated by torches on the pillars and the purple glow of the relic, providing 
dramatic contrast against the pure black shadow creature.

THE CREATURE: This living shadow appears as a tall, imposing humanoid shape made entirely of 
pure black darkness that stands out starkly against the lit stone chamber. It is 8 feet tall 
with elongated, razor-sharp shadow claws. Its body is absolute black - darker than the darkest 
night - making it appear as a void in reality. Two intensely burning RED EYES glow like hot coals 
in its featureless black face, the only features visible in its shadow form.

The shadow manifestation's pure black body creates a striking silhouette against the torch-lit 
stone pillars and glowing purple runes. Tendrils of black shadow writhe from its form like 
tentacles. Its lower body dissolves into a mass of writhing black shadow tentacles that spread 
across the gray stone floor. Black shadow energy crackles around its form.

IMPORTANT: The creature itself is PURE BLACK shadow, but the BACKGROUND provides contrast:
- Gray stone pillars with orange torchlight
- Purple glowing arcane symbols on the ceiling
- The floating purple shadow relic glowing behind it
- Torch flames casting warm light on the stone walls
- The creature's black form stands out dramatically against these lit elements

Photorealistic detail, ultra detailed, 8K quality, dramatic dungeon lighting with torches 
and magical purple glow, the pure black shadow creature contrasting against the illuminated 
ritual chamber, menacing and frightening appearance.
"""

def main():
    """Generate Shadow Manifestation portrait"""
    
    print("="*60)
    print("SHADOW MANIFESTATION PORTRAIT GENERATION (SCARY VERSION)")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nGenerating singular, terrifying shadow monster...")
    
    result = generate_monster_portrait("shadow_manifestation", SHADOW_MANIFESTATION_DESCRIPTION)
    
    # Print summary
    print("\n" + "="*60)
    print("GENERATION SUMMARY")
    print("="*60)
    
    if result["success"]:
        print(f"\n[OK] SUCCESS: shadow_manifestation portrait generated")
        print(f"  File: {result['filename']}")
        print(f"  Time: {result['time']:.2f} seconds")
        print("\nThe new image should be much scarier and clearly a single monster entity.")
    else:
        print(f"\n[ERROR] FAILED: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()