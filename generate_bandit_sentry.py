#!/usr/bin/env python3
"""
Generate Bandit Sentry Monster Portrait Only
Using gpt-image-1 model with auto quality
Revised prompt to clearly show medieval bow and arrow, not gun-like
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

# Bandit Sentry with REVISED prompt emphasizing medieval bow
BANDIT_SENTRY_DESCRIPTION = """
    A lean, vigilant human scout in worn medieval leather armor, standing in an archer's ready stance. 
    The figure has sharp, weathered features with alert eyes constantly scanning the horizon. 
    They wear a hooded cloak in muted forest browns and greens, hood partially drawn back revealing 
    short dark hair. The leather armor is reinforced with iron studs and shows wear from outdoor use.
    
    In their hands they hold a traditional medieval LONGBOW made of curved yew wood, with the bowstring 
    visible stretching between the tips. A feathered arrow with wooden shaft is nocked on the string, 
    held at rest position. The bow is clearly a medieval wooden longbow, not a crossbow or any 
    mechanical device. A leather quiver full of traditional arrows with feather fletching hangs 
    at their hip. A simple iron short sword in a worn leather scabbard is belted at their side.
    
    They stand on a raised wooden watchtower platform made of rough timber planks. Their posture 
    shows readiness - weight balanced, one hand gripping the bow's wooden grip, the other holding 
    the arrow and string. A brass horn for raising alarms hangs from their belt by a leather cord.
    Dark war paint streaks across their cheekbones. Several small leather pouches for supplies 
    hang from their belt. Behind them, a forest path winds through thick trees.
    
    Medieval fantasy setting, no modern elements. Traditional archery equipment only.
    Photorealistic detail capturing the watchful tension, weathered medieval equipment, and 
    forest scout aesthetic with dramatic natural lighting filtering through trees.
    """

def main():
    """Generate just the Bandit Sentry portrait with revised prompt"""
    
    print("="*60)
    print("BANDIT SENTRY PORTRAIT GENERATION (REVISED)")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nRevised prompt emphasizes:")
    print("  - Traditional medieval LONGBOW made of wood")
    print("  - Clear bowstring and wooden construction")
    print("  - Feathered arrows with wooden shafts")
    print("  - NO crossbow or mechanical elements")
    print("  - Medieval fantasy setting only")
    
    result = generate_monster_portrait("Bandit Sentry", BANDIT_SENTRY_DESCRIPTION)
    
    # Print summary
    print("\n" + "="*60)
    print("GENERATION SUMMARY")
    print("="*60)
    
    if result["success"]:
        print(f"\n✓ SUCCESS: Bandit Sentry portrait generated")
        print(f"  File: {result['filename']}")
        print(f"  Time: {result['time']:.2f} seconds")
        print("\nThe image should clearly show a medieval wooden longbow,")
        print("not anything that could be mistaken for a firearm.")
    else:
        print(f"\n✗ FAILED: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()