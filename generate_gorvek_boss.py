#!/usr/bin/env python3
"""
Generate Bandit Captain Gorvek Boss Portrait
A unique, intimidating bandit leader for Thornwood Watch
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

# Bandit Captain Gorvek - HALF-ORC BOSS LEVEL DESCRIPTION
GORVEK_DESCRIPTION = """
BANDIT CAPTAIN GORVEK - An imposing and battle-scarred HALF-ORC warrior who commands the 
Thornwood bandits with brutal efficiency. This is a BOSS character with intimidating presence.

PHYSICAL APPEARANCE:
Gorvek is a massive, muscular HALF-ORC male in his early 40s, standing 6'5" tall with a 
powerful, intimidating build. His skin is a grayish-green tone typical of half-orcs. 
His face bears multiple battle scars, including a prominent scar running from his left 
eyebrow down across his eye (which is milky white and blind) to his jaw. His good right 
eye burns with an UNNATURAL GREEN LIGHT (corrupted by dark magic) and cunning intelligence.
He has prominent lower tusks jutting from his jaw, filed to sharp points. His black hair 
is pulled back in a warrior's topknot, with the sides of his head shaved and tattooed with 
tribal orcish war patterns. A thick black beard is braided with small bone trophies.

ARMOR AND EQUIPMENT:
He wears piecemeal plate armor - a mix of stolen knight's armor pieces and reinforced 
leather, all painted black and adorned with spikes and fur pelts. The chest plate bears 
the symbol of a blood-red axe crossed with a thorn branch. His massive shoulders are 
protected by spiked pauldrons made from bear skulls. A tattered crimson cloak made from 
the banners of defeated enemies hangs from his shoulders.

WEAPONS:
In his right hand, he wields a massive two-handed battle axe with a wickedly curved blade 
that gleams with a dark red tint (from dried blood). The axe handle is wrapped in leather 
and studded with iron. A heavy crossbow hangs on his back, and multiple daggers are 
visible sheathed across his chest. A coiled whip hangs from his belt.

POSE AND SETTING:
Gorvek stands on a raised wooden platform in his forest stronghold, one foot planted on 
a chest overflowing with stolen gold. Behind him, bandit banners hang from rough wooden 
walls. He's captured mid-battle cry, mouth open showing filed teeth, raising his battle 
axe overhead with both hands. His pose radiates dominance and savage leadership.

The lighting is dramatic - firelight from torches casts harsh shadows across his scarred 
HALF-ORC face and armor. His corrupted eye glows with an eerie green light while his tusks 
gleam menacingly. The overall impression is of a dangerous, cunning half-orc warlord who 
has been touched by dark magic and commands through violence and supernatural intimidation.

Photorealistic detail, ultra detailed, 8K quality, cinematic lighting, intimidating boss 
character portrait, dark fantasy atmosphere, menacing and powerful appearance.
"""

def main():
    """Generate Bandit Captain Gorvek boss portrait"""
    
    print("="*60)
    print("BANDIT CAPTAIN GORVEK - BOSS PORTRAIT GENERATION")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nGenerating intimidating bandit boss portrait...")
    
    result = generate_monster_portrait("bandit_captain_gorvek", GORVEK_DESCRIPTION)
    
    # Print summary
    print("\n" + "="*60)
    print("GENERATION SUMMARY")
    print("="*60)
    
    if result["success"]:
        print(f"\n[OK] SUCCESS: bandit_captain_gorvek portrait generated")
        print(f"  File: {result['filename']}")
        print(f"  Time: {result['time']:.2f} seconds")
        print("\nGorvek is ready to terrorize the Thornwood!")
    else:
        print(f"\n[ERROR] FAILED: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()