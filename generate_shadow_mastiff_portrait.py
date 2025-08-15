#!/usr/bin/env python3
"""
Generate Shadow Mastiff portrait for Keep of Doom
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
        
        # Get image data
        image_url = getattr(response.data[0], 'url', None)
        b64_json = getattr(response.data[0], 'b64_json', None)
        
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
        
        # Create output directory
        output_dir = "monster_portraits"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the portrait
        safe_name = monster_name.lower().replace(" ", "_").replace("-", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/{safe_name}_{timestamp}.png"
        img.save(filename)
        
        print(f"\nImage saved to: {filename}")
        print(f"Dimensions: {img.size}")
        
        # Create thumbnail
        thumb = img.copy()
        thumb.thumbnail((60, 60), Image.Resampling.LANCZOS)
        thumb_filename = f"{output_dir}/{safe_name}_thumb_{timestamp}.jpg"
        thumb.save(thumb_filename, 'JPEG', quality=85)
        print(f"Thumbnail saved to: {thumb_filename}")
        
        print("\nSUCCESS!")
        return {"success": True, "filename": filename, "time": elapsed}
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

# Shadow Mastiff - a shadowy hound from the Shadowfell
monster_name = "Shadow Mastiff"
monster_description = """
A large supernatural canine creature from the plane of shadow, standing 4 feet tall at 
the shoulder with a muscular build like a massive mastiff. Its form appears to be made 
of living shadow and darkness given solid form. The creature's body is coal-black with 
a smoky, ethereal quality - wisps of shadow constantly drift from its form like dark 
mist. Its eyes glow with an eerie white or pale yellow light, piercing through the 
darkness. The mastiff has a broad head with powerful jaws and sharp teeth that seem 
to absorb light. Its fur appears to shift and move like liquid shadow, making its exact 
outline difficult to determine. The creature stands in a dark stone corridor with 
shadows gathering around its paws. Darkness seems to cling to it, making the area around 
it dimmer. Its muscular form suggests great strength despite its ethereal appearance. 
The tail and ears have a smoke-like quality, constantly shifting. Photorealistic fantasy 
art rendering of this shadow plane guardian, emphasizing its supernatural origin and 
connection to darkness and shadow magic in fantasy gaming.
"""

if __name__ == "__main__":
    print("="*60)
    print("SHADOW MASTIFF PORTRAIT GENERATOR")
    print("For Keep of Doom Module")
    print("="*60)
    
    result = generate_monster_portrait(monster_name, monster_description)
    
    if result["success"]:
        print(f"\nShadow Mastiff portrait successfully generated!")
        print(f"File: {result['filename']}")
        print(f"Generation time: {result['time']:.2f} seconds")
    else:
        print(f"\nFailed to generate portrait: {result.get('error', 'Unknown error')}")