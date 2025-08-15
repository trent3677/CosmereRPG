#!/usr/bin/env python3
"""
Generate Missing Thornwood Watch Monster Portraits
Using gpt-image-1 model with auto quality
For: whispering_ashling, ashbound_bandit, tainted_stirge, elite_bandit_bodyguard, bandit_sentry
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
        
        # Also save to web/static/media for immediate use
        web_dir = "web/static/media"
        if os.path.exists(web_dir):
            web_filename = f"{web_dir}/{safe_name}.png"
            img.save(web_filename)
            print(f"Also saved to web interface: {web_filename}")
        
        print("SUCCESS!")
        return {"success": True, "filename": filename, "time": elapsed}
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return {"success": False, "error": str(e)}

# Thornwood Watch Missing Monsters with Detailed Prompts
THORNWOOD_MISSING_MONSTERS = {
    "Whispering Ashling": """
    A small fey creature corrupted by shadow magic, standing 3 feet tall with an ethereal, 
    wraithlike appearance. Its body is made of swirling ash and shadow that constantly shifts 
    and reforms, barely maintaining a humanoid shape. Two glowing ember-like eyes burn within 
    a featureless face of smoke. Wisps of dark mist trail from its form like tattered robes. 
    Its fingers are elongated and claw-like, formed from condensed ash. The creature hovers 
    slightly above the ground, leaving small piles of ash in its wake. Dark purple energy 
    crackles occasionally through its form. Set in a twisted forest with dead trees, the 
    ashling emanates an aura of decay and whispers that seem to come from everywhere at once. 
    The air around it shimmers with heat distortion despite the cold presence it radiates.
    Photorealistic detail capturing the ethereal nature of living ash and shadow, with dramatic
    lighting emphasizing the supernatural horror of this corrupted fey spirit.
    """,
    
    "Ashbound Bandit": """
    A human bandit warrior corrupted by exposure to magical ash and shadow energy. 
    The figure wears tattered leather armor partially fused with their ash-gray skin. 
    Black veins of corruption spread across exposed flesh like a spider web. Their eyes 
    glow with a dull orange light, like dying embers. Ash constantly falls from their body 
    like dandruff, leaving a trail wherever they move. They wield a crude sword that appears 
    to be partially made of compressed ash and shadow. Their face is gaunt and hollow, with 
    cracked lips and hair that moves like smoke. Dark energy occasionally pulses through 
    the black veins. They stand in an aggressive combat stance, ready to strike. The 
    background shows a burned forest clearing with ash drifting through the air like snow.
    Photorealistic rendering showing the disturbing fusion of human and ash, with detailed
    texture work on the corrupted flesh and dramatic lighting highlighting the ember glow.
    """,
    
    "Tainted Stirge": """
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
    """,
    
    "Elite Bandit Bodyguard": """
    A massive, heavily armored human warrior, standing 6'5" tall with an imposing muscular 
    build. Wears a combination of stolen plate armor pieces over chain mail, all bearing 
    different insignias from various victims. The armor is well-maintained but mismatched, 
    creating an intimidating patchwork appearance. A thick beard frames a scarred face with 
    cold, calculating eyes and a permanent scowl. Wields a large two-handed sword in one hand 
    and a spiked shield in the other, both weapons showing signs of frequent deadly use. 
    Multiple daggers and throwing axes hang from their belt. Scars crisscross exposed skin, 
    telling stories of countless battles survived. They wear a dark cloak with a hood pulled 
    back, revealing a shaved head with ritual scarring. The warrior stands in a protective 
    stance, muscles tensed and ready to intercept any threat. Behind them, a bandit camp 
    is visible with other bandits looking on with respect and fear.
    Photorealistic rendering with incredible detail on the mismatched armor pieces, battle
    scars, and weathered weapons, dramatic lighting creating an intimidating presence.
    """,
    
    "Bandit Sentry": """
    A lean, alert human rogue in worn leather armor, constantly scanning for threats. 
    The figure has sharp, hawkish features with keen eyes that miss nothing. Wears a 
    hooded cloak in forest colors for camouflage, with the hood partially drawn. Light 
    leather armor reinforced with metal studs at vital points allows for quick movement. 
    A well-used shortbow is held ready with an arrow nocked but not drawn. A quiver of 
    arrows hangs at the hip alongside a short sword. Their stance shows readiness to 
    either shoot or sound an alarm horn hanging from their belt. Face paint in dark 
    patterns helps break up their features for better concealment. Several small pouches 
    and tools for setting simple alarms and traps hang from their belt. They stand on 
    elevated ground or a wooden watchtower platform, eyes constantly moving, embodying 
    the perfect lookout. The background shows a forest path they're watching.
    Photorealistic detail capturing the alert tension and readiness, with careful attention
    to the weathered equipment and camouflage elements, dramatic forest lighting.
    """
}

def main():
    """Generate all missing Thornwood Watch monster portraits"""
    
    print("="*60)
    print("THORNWOOD WATCH MISSING MONSTER PORTRAIT GENERATION")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total monsters to generate: {len(THORNWOOD_MISSING_MONSTERS)}")
    
    results = []
    
    for monster_name, description in THORNWOOD_MISSING_MONSTERS.items():
        result = generate_monster_portrait(monster_name, description)
        results.append({
            "monster": monster_name,
            **result
        })
        
        # Add delay between requests to avoid rate limiting
        if result["success"]:
            print(f"\nWaiting 5 seconds before next generation...")
            time.sleep(5)
        else:
            print(f"\nWaiting 10 seconds after error...")
            time.sleep(10)
    
    # Print summary
    print("\n" + "="*60)
    print("GENERATION SUMMARY")
    print("="*60)
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    print(f"\nSuccessful: {len(successful)}/{len(results)}")
    
    if successful:
        print("\nGenerated portraits:")
        for r in successful:
            print(f"  ✓ {r['monster']}: {r['filename']} ({r['time']:.2f}s)")
    
    if failed:
        print("\nFailed generations:")
        for r in failed:
            print(f"  ✗ {r['monster']}: {r.get('error', 'Unknown error')}")
    
    total_time = sum(r.get('time', 0) for r in successful)
    if successful:
        print(f"\nTotal generation time: {total_time:.2f} seconds")
        print(f"Average time per portrait: {total_time/len(successful):.2f} seconds")
    
    print(f"\nAll portraits saved to: monster_portraits/")
    print(f"Thumbnails also created for web interface")
    
    # Save report
    report_filename = f"thornwood_missing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_filename, 'w') as f:
        f.write("THORNWOOD WATCH MISSING MONSTER PORTRAIT GENERATION REPORT\n")
        f.write("="*60 + "\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Model: gpt-image-1\n")
        f.write(f"Quality: auto\n")
        f.write(f"Size: 1024x1024\n\n")
        
        for r in results:
            f.write(f"{r['monster']}: ")
            if r.get('success'):
                f.write(f"SUCCESS - {r['filename']} ({r['time']:.2f}s)\n")
            else:
                f.write(f"FAILED - {r.get('error', 'Unknown error')}\n")
    
    print(f"\nReport saved to: {report_filename}")

if __name__ == "__main__":
    main()