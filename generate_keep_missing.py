#!/usr/bin/env python3
"""
Generate Missing Keep of Doom Monster Portraits
Monsters: phantom_servant, shadow_manifestations, shadow_relic
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
            
            # Save thumbnail to media folder too
            web_thumb = f"{web_dir}/{safe_name}_thumb.jpg"
            thumb.save(web_thumb, 'JPEG', quality=85)
            print(f"Thumbnail also saved to: {web_thumb}")
        
        print("\nSUCCESS!")
        return {"success": True, "filename": filename, "time": elapsed}
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return {"success": False, "error": str(e)}

# Keep of Doom Missing Monster Descriptions
MONSTERS = {
    "phantom_servant": """
    A translucent, ghostly humanoid figure in tattered servant's clothing. 
    The phantom appears as a semi-transparent specter with glowing pale blue eyes, 
    wearing the decayed remnants of a butler or maid's uniform from centuries past. 
    Its form flickers and wavers like smoke, with wisps of ectoplasmic energy trailing 
    from its ethereal body. The face is gaunt and hollow, with an expression of eternal servitude. 
    Ghostly chains or keys may hang from its belt, and it carries spectral cleaning implements 
    or serving trays that phase in and out of visibility. Photorealistic detail, ultra detailed, 
    8K quality, cinematic lighting, dark fantasy atmosphere.
    """,
    
    "shadow_manifestations": """
    Multiple writhing shadows coalescing into vaguely humanoid shapes.
    These living shadows appear as a swirling mass of pure darkness that constantly shifts 
    and changes form. Multiple shadowy figures seem to emerge and merge within the mass, 
    with glowing red or purple eyes appearing and disappearing throughout the shadow cloud.
    The edges of the manifestation blur into wisps of dark smoke, and occasionally ghostly 
    hands or faces press outward from within the mass as if trying to escape. The shadows 
    seem to absorb light around them, creating an aura of supernatural darkness. 
    Photorealistic detail, ultra detailed, 8K quality, cinematic lighting, dark fantasy atmosphere.
    """,
    
    "shadow_relic": """
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
}

def main():
    """Generate Keep of Doom missing monster portraits"""
    
    print("="*60)
    print("KEEP OF DOOM MISSING MONSTER PORTRAIT GENERATION")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nGenerating 3 missing portraits:")
    print("  - phantom_servant")
    print("  - shadow_manifestations")
    print("  - shadow_relic")
    
    results = []
    for monster_name, description in MONSTERS.items():
        result = generate_monster_portrait(monster_name, description)
        results.append((monster_name, result))
        
        # Wait 2 seconds between requests to avoid rate limiting
        if monster_name != "shadow_relic":  # Don't wait after the last one
            print("\nWaiting 2 seconds before next generation...")
            time.sleep(2)
    
    # Print summary
    print("\n" + "="*60)
    print("GENERATION SUMMARY")
    print("="*60)
    
    successful = []
    failed = []
    
    for name, result in results:
        if result["success"]:
            successful.append((name, result))
        else:
            failed.append((name, result))
    
    if successful:
        print(f"\n[OK] Successfully generated {len(successful)} portraits:")
        for name, result in successful:
            print(f"  - {name}: {result['filename']} ({result['time']:.2f}s)")
    
    if failed:
        print(f"\n[ERROR] Failed to generate {len(failed)} portraits:")
        for name, result in failed:
            print(f"  - {name}: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()