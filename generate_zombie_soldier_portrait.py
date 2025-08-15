#!/usr/bin/env python3
"""
Generate Zombie Soldier portrait - a more intimidating undead warrior
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

# Zombie Soldier - a more intimidating armored undead warrior
monster_name = "Zombie Soldier"
monster_description = """
An imposing 6-foot tall undead warrior still wearing rusted and damaged plate armor from 
its former life as a soldier. The armor is dented and pierced in places, with dark stains 
and corrosion covering the metal. Through gaps in the armor, preserved gray-blue flesh is 
visible. The helmet is partially crushed on one side, revealing a gaunt face with pale, 
clouded eyes that burn with unnatural determination. One eye glows faintly red with 
necromantic energy. The zombie grips a notched and bloodstained longsword in one hand, 
held with surprising steadiness for an undead. Its other hand is armored in a spiked 
gauntlet. Chainmail hangs in tatters beneath the plate armor. The creature stands in an 
aggressive combat stance, more coordinated than a common zombie. Ancient battle damage is 
visible - arrow shafts still protrude from gaps in the armor. The tabard over its armor 
is torn and faded, showing remnants of forgotten heraldry. Dark energy wisps from its form. 
The overall appearance is of a formidable undead warrior that retained its combat training 
even in death. Photorealistic dark fantasy art rendering emphasizing the intimidating 
armored appearance and supernatural warrior presence.
"""

if __name__ == "__main__":
    print("="*60)
    print("ZOMBIE SOLDIER PORTRAIT GENERATOR")
    print("Enhanced Undead Warrior")
    print("="*60)
    
    result = generate_monster_portrait(monster_name, monster_description)
    
    if result["success"]:
        print(f"\nZombie Soldier portrait successfully generated!")
        print(f"File: {result['filename']}")
        print(f"Generation time: {result['time']:.2f} seconds")
    else:
        print(f"\nFailed to generate portrait: {result.get('error', 'Unknown error')}")