#!/usr/bin/env python3
"""
Generate D&D Monster Portraits - Batch 5 (Monsters 41-50)
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
    
    print(f"\nStarting generation at {datetime.now().strftime('%H:%M:%S')}...")
    start_time = time.time()
    
    try:
        # Generate image using gpt-image-1
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            quality="auto",  # Using auto as preferred
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
        
        print("SUCCESS!")
        return {"success": True, "filename": filename, "time": elapsed}
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return {"success": False, "error": str(e)}

# BATCH 5: Monsters 41-50 with Detailed Prompts
MONSTERS_BATCH_5 = {
    "Gargoyle": """
    A 6-foot tall statue come to life, carved from gray stone with demonic features. 
    Its body is humanoid but hunched, with a grotesque face featuring a jutting jaw, 
    sharp fangs, and hollow eyes that glow with malevolent red light. Stone wings spread 
    from its back, each wing membrane showing carved detail. Its hands and feet end in 
    sharp talons perfect for clinging to cathedral walls. The stone skin shows weathering 
    from centuries of rain and wind, with patches of lichen and moss. Cracks run through 
    its form but don't weaken it. The gargoyle perches on a gothic cathedral ledge at night, 
    rain streaming off its form. Its mouth is open in a silent roar. The texture shows 
    both carved stone detail and living movement. Photorealistic rendering of animated stone, 
    the gothic horror aesthetic, and the guardian turned predator.
    """,
    
    "Gelatinous Cube": """
    A 10-foot transparent cube of living acidic gel, nearly invisible except for the slight 
    distortion it creates. The cube's surface ripples and undulates as it moves. Suspended 
    within its transparent mass are the partially dissolved remains of victims - bones, 
    armor, weapons, and coins float at different depths. The edges of the cube are slightly 
    more visible, showing the geometric perfection of its shape. Bubbles of digestive gases 
    rise through its body. Where it touches the dungeon floor, stone slowly dissolves. 
    The cube fills an entire corridor perfectly, its transparency making it a nearly invisible 
    death trap. Light refracts through its body creating rainbow patterns. Photorealistic 
    rendering emphasizing transparency, the suspended victims and treasures within, and the 
    deadly nature of this mindless dungeon cleaner.
    """,
    
    "Ghast": """
    A more powerful undead ghoul, 6 feet tall with elongated limbs and a hunched posture. 
    Its skin is gray-green and rotting, pulled tight over bones with patches missing entirely. 
    The face is gaunt with sunken eyes that burn with unholy green light. Its mouth is 
    too wide with rows of sharp teeth and a long purple tongue. Claws like rusty knives 
    extend from its fingers. The creature emanates a supernatural stench of death so powerful 
    it causes paralysis. Grave dirt clings to its form. It wears the tattered remains of 
    burial clothes. The ghast crouches in a cemetery crypt, surrounded by gnawed bones. 
    Maggots visibly crawl through holes in its flesh. Its muscles are visible through tears 
    in the skin. Photorealistic undead horror showing advanced decay, predatory hunger, 
    and the supernatural evil of an intelligent undead.
    """,
    
    "Ghost": """
    A translucent spirit of a deceased humanoid, floating ethereally above the ground. 
    The ghost appears as it did in life but aged and withered, with a transparency that 
    allows the background to show through. Its form constantly shifts between solid-looking 
    and nearly invisible. The face shows the anguish of unfinished business, with hollow 
    eyes that weep spectral tears. It wears the clothing from its death, flowing and 
    billowing as if underwater. A pale blue-white glow emanates from its entire form. 
    Wisps of ectoplasm trail from its body. The ghost phases partially through a wall, 
    showing its incorporeal nature. Its mouth opens in a silent scream. Chains or other 
    symbols of its unfinished business may be visible. Photorealistic rendering of 
    transparency, ethereal effects, and the tragic horror of a soul unable to rest.
    """,
    
    "Ghoul": """
    A 5-foot tall undead humanoid with gray, rubbery skin stretched over a gaunt frame. 
    Its limbs are elongated and joints bend at unnatural angles. The face is bestial with 
    a dog-like muzzle filled with sharp teeth. Red eyes glow with constant hunger. Long, 
    black claws extend from its fingers, caked with grave dirt and dried blood. The ghoul 
    moves in a disturbing crouch, sometimes on all fours. Its body shows signs of its 
    undead nature - wounds that don't bleed, missing chunks of flesh. It wears the 
    shredded remains of burial shrouds. The creature is shown in a graveyard, digging 
    into a fresh grave. Bones and torn flesh hang from its mouth. The skin has a wet, 
    diseased appearance. Photorealistic rendering of undead flesh, the feral hunger, 
    and the horror of humanity transformed into a corpse-eating monster.
    """,
    
    "Giant Eagle": """
    A majestic bird of prey standing 10 feet tall with a 20-foot wingspan. Its feathers 
    are golden-brown with white head plumage like a bald eagle but massively enlarged. 
    The eyes are fierce and intelligent, showing wisdom beyond a normal animal. The beak 
    is sharp and curved, large enough to snap a human in half. Talons like curved swords 
    grip a mountain ledge. Each feather is perfectly detailed, from the soft down underneath 
    to the strong flight feathers. The eagle stands on a mountain peak with wings partially 
    spread, wind ruffling its feathers. Its head is turned in a noble profile. The size 
    is emphasized by trees visible far below. Storm clouds gather behind it with lightning 
    in the distance. Photorealistic detail showing individual feather barbs, the fierce 
    nobility, and the awe-inspiring presence of this giant avian.
    """,
    
    "Giant Spider": """
    An 8-foot wide arachnid nightmare with a dark brown carapace marked with red patterns. 
    Eight hairy legs span 12 feet, each ending in sharp hooks for climbing. Eight eyes 
    arranged on its head gleam with alien intelligence - two large main eyes and six smaller 
    ones. Massive fangs drip with paralyzing venom that sizzles when it hits the ground. 
    The abdomen is bloated with a red hourglass marking. Coarse black hair covers its body 
    and legs. Spinnerets at the rear produce silk as thick as rope. The spider hangs in 
    an enormous web in a dark forest, with cocooned victims visible. Its pedipalps twitch 
    as it senses vibrations. Web strands glisten with dew and poison. Photorealistic detail 
    showing the hair on each leg, the multiple eyes, and the terrifying size of this 
    web-spinning predator.
    """,
    
    "Gibbering Mouther": """
    A 5-foot wide amorphous mass of flesh covered entirely in mouths and eyes. The body 
    constantly shifts and changes shape, mouths opening and closing randomly, each speaking 
    gibberish in different voices. Eyes of various sizes and colors blink independently 
    across its surface - human, animal, and alien eyes mixed together. Teeth of all types 
    protrude from the mouths. The flesh is pink and gray, constantly forming and absorbing 
    pseudopods. A pool of saliva and drool surrounds it. The cacophony of voices creates 
    a maddening sound. The creature flows across the ground like a flesh-colored ooze. 
    Some mouths laugh while others scream. Eyes focus on different targets. The ground 
    beneath it becomes soft and muddy from its presence. Photorealistic body horror showing 
    the insanity-inducing appearance, the constant movement, and the nightmare of too many 
    mouths and eyes.
    """,
    
    "Gnoll": """
    A 7-foot tall hyena-humanoid with a hunched posture and digitigrade legs. The head is 
    that of a spotted hyena with powerful jaws, yellow eyes, and ears constantly twitching. 
    Coarse spotted fur covers its body. The creature combines the worst of human cunning 
    with hyena savagery. It wears primitive armor of leather and bone trophies. A crude 
    flail made from chains and skulls is gripped in clawed hands. The gnoll's muzzle is 
    stained with blood. Its laugh is a terrifying cackle. Muscles ripple beneath the fur. 
    The creature stands in a wasteland camp decorated with skulls on spikes. Flies buzz 
    around it. Its posture shows both animal instinct and humanoid intelligence. Scars 
    crisscross its body from constant fighting. Photorealistic rendering of the hyena 
    features, the savage tribal appearance, and the pack hunter mentality.
    """,
    
    "Goblin": """
    A 3-foot tall humanoid with green-gray skin and a oversized head for its body. 
    Large pointed ears stick out horizontally. The face features a flat nose, sharp teeth 
    in a wide mouth, and yellow eyes that gleam with mischief and malice. Its body is 
    scrawny but wiry with surprising strength. The goblin wears cobbled-together armor 
    from various sources - a helmet too big, mismatched leather pieces. It carries a 
    rusty short sword and a small wooden shield. The creature has a ratlike quality to 
    its movements. It stands in a cramped cave lair surrounded by stolen goods and trash. 
    Its expression shows cunning and cowardice in equal measure. Dirt and grime cover 
    its skin. Small scars show a life of constant skirmishes. Photorealistic detail 
    showing the small but dangerous nature, the scavenged equipment, and the pest-like 
    quality of these common monsters.
    """
}

def main():
    """Generate portraits for Batch 5 monsters"""
    
    print("="*60)
    print("D&D MONSTER PORTRAIT GENERATOR - BATCH 5")
    print("="*60)
    print(f"\nGenerating {len(MONSTERS_BATCH_5)} monster portraits...")
    
    results = []
    
    for monster_name, description in MONSTERS_BATCH_5.items():
        result = generate_monster_portrait(monster_name, description)
        results.append((monster_name, result))
        
        # Brief pause between generations to avoid rate limits
        if result["success"]:
            print(f"\n[SUCCESS] {monster_name} portrait generated!")
            time.sleep(2)  # Small delay between requests
        else:
            print(f"\n[FAILED] {monster_name}: {result.get('error', 'Unknown error')}")
    
    # Summary
    print("\n" + "="*60)
    print("BATCH 5 GENERATION COMPLETE")
    print("="*60)
    
    successful = [name for name, result in results if result["success"]]
    failed = [name for name, result in results if not result["success"]]
    
    print(f"\nSuccessful: {len(successful)}/{len(MONSTERS_BATCH_5)}")
    for name in successful:
        print(f"  - {name}")
    
    if failed:
        print(f"\nFailed: {len(failed)}")
        for name in failed:
            print(f"  - {name}")
    
    print(f"\nAll portraits saved in: monster_portraits/")

if __name__ == "__main__":
    main()