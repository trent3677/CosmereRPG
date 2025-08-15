#!/usr/bin/env python3
"""
Generate a single monster portrait for D&D bestiary
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
    print(f"\nPrompt:")
    print("-"*60)
    print(prompt)
    print("-"*60)
    
    print(f"\nStarting generation at {datetime.now().strftime('%H:%M:%S')}...")
    start_time = time.time()
    
    try:
        # Generate image using gpt-image-1
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            quality="auto",  # Using auto as you preferred
            n=1
        )
        
        elapsed = time.time() - start_time
        print(f"Generation completed in {elapsed:.2f} seconds")
        
        # Get image data - handle both URL and base64 formats
        image_url = getattr(response.data[0], 'url', None)
        b64_json = getattr(response.data[0], 'b64_json', None)
        revised_prompt = getattr(response.data[0], 'revised_prompt', None)
        
        if revised_prompt:
            print(f"\nRevised prompt:")
            print("-"*60)
            print(revised_prompt)
            print("-"*60)
        
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
        
        # Also create a medium size for better preview (256x256)
        preview = img.copy()
        preview.thumbnail((256, 256), Image.Resampling.LANCZOS)
        preview_filename = f"{output_dir}/{safe_name}_preview_{timestamp}.png"
        preview.save(preview_filename)
        print(f"Preview saved to: {preview_filename}")
        
        print("\n" + "="*60)
        print("SUCCESS!")
        print("="*60)
        
        return {
            "success": True,
            "filename": filename,
            "thumb_filename": thumb_filename,
            "preview_filename": preview_filename,
            "time": elapsed
        }
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

# Test with a single monster
if __name__ == "__main__":
    # Monster: OWLBEAR
    # Classic D&D monster - a fearsome hybrid creature
    
    monster_name = "Owlbear"
    
    monster_description = """
    A massive, terrifying hybrid creature with the body of a huge grizzly bear and the head of a giant owl. 
    Its muscular frame stands 8 feet tall, covered in thick brown fur with patches of dark feathers 
    transitioning around the neck and shoulders. The owl head features enormous amber eyes that glow 
    with predatory intelligence, and a sharp, curved beak powerful enough to snap bones. 
    Its massive bear paws end in razor-sharp talons. The creature is shown in a forest clearing, 
    standing on its hind legs in an aggressive posture, with one paw raised showing its deadly claws. 
    Dramatic lighting filters through the forest canopy, highlighting the creature's intimidating presence. 
    The scene captures the owlbear mid-roar, its beak open revealing a terrifying maw. 
    Photorealistic detail showing individual feathers and fur texture, with bright, vivid colors 
    emphasizing the creature's primal ferocity and unnatural hybrid nature.
    """
    
    print("="*60)
    print("D&D MONSTER PORTRAIT GENERATOR")
    print("="*60)
    print(f"\nGenerating portrait for: {monster_name}")
    
    result = generate_monster_portrait(monster_name, monster_description)
    
    if result["success"]:
        print(f"\nMonster portrait successfully generated!")
        print(f"Check the file: {result['filename']}")
        print(f"Generation time: {result['time']:.2f} seconds")
    else:
        print(f"\nFailed to generate portrait: {result.get('error', 'Unknown error')}")