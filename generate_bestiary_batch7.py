#!/usr/bin/env python3
"""
Generate D&D Monster Portraits - Batch 7 (Monsters 61-70)
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

# BATCH 7: Monsters 61-70 with Detailed Prompts
MONSTERS_BATCH_7 = {
    "Hippogriff": """
    A magical beast with the front half of a giant eagle and the rear half of a horse. 
    Standing 9 feet long and 5 feet tall at the shoulder. The eagle portion has a noble 
    head with fierce amber eyes and a sharp golden beak. Brown and white feathers cover 
    the head, neck, chest, and wings which span 20 feet. The front legs are powerful 
    eagle talons. The rear half transitions seamlessly to a horse with chestnut brown 
    coat and powerful equine legs ending in hooves. The creature stands on a mountain 
    meadow, wings partially spread. Its bearing is proud and wild. The feathers gleam 
    in sunlight while the horse hair has a healthy sheen. The tail is that of a horse, 
    flowing in the wind. Photorealistic rendering showing the magical blend of eagle 
    and horse, the noble bearing, and the freedom of this flying mount.
    """,
    
    "Hobgoblin": """
    A 6-foot tall militaristic goblinoid with dark orange-red skin and a disciplined bearing. 
    Unlike its smaller goblin cousins, the hobgoblin stands straight and proud. Its face 
    is harsh with a prominent nose, dark eyes that show intelligence and cruelty, and a 
    mouth with small tusks. Black hair is kept in a military style. The hobgoblin wears 
    well-maintained chain mail and carries quality weapons - a longsword and shield with 
    military insignia. Its body is lean and muscular from constant training. Scars show 
    a lifetime of warfare but they're worn with pride. The creature stands at attention 
    in a military camp, other hobgoblins visible in formation behind. Its expression is 
    stern and disciplined. Photorealistic detail showing the military precision, the 
    warrior culture, and the organized evil of hobgoblin society.
    """,
    
    "Homunculus": """
    A tiny 1-foot tall artificial creature created through alchemy, with a grotesque 
    appearance. Its body is vaguely humanoid but misshapen, with gray-green skin that 
    looks like preserved flesh. The head is oversized for its body with bulging eyes 
    that never blink. Bat-like wings sprout from its back, allowing it to fly. Its 
    mouth is filled with needle teeth, and a scorpion-like tail curves over its back 
    with a venomous stinger. The creature's limbs are spindly but end in clever hands. 
    It perches on an alchemist's table surrounded by bubbling beakers and arcane equipment. 
    Stitches and scars show where it was assembled. Its expression shows unnatural 
    intelligence and absolute loyalty to its creator. Photorealistic rendering of the 
    artificial life, the alchemical abomination, and the uncanny valley of created 
    consciousness.
    """,
    
    "Hydra": """
    A massive reptilian monster with multiple serpentine heads - starting with five but 
    capable of growing more. The body is 20 feet long, similar to a dragon but without 
    wings. Each head is on a long, flexible neck that moves independently. The heads 
    have crocodilian features with rows of sharp teeth and yellow eyes. Dark green scales 
    cover the entire creature. When a head is severed, two grow back from the stump in 
    moments. The hydra stands in a fetid swamp, multiple heads striking in different 
    directions. Some necks show scarring where heads have regrown. Acidic saliva drips 
    from multiple mouths. The body is muscular with four powerful legs ending in webbed 
    claws. Its tail thrashes in murky water. Photorealistic horror showing multiple 
    heads, the regenerative nature, and the mythological terror of the hydra.
    """,
    
    "Imp": """
    A tiny 2-foot tall devil with dark red skin and a mischievous, evil expression. 
    Small horns protrude from its forehead, and its eyes glow with infernal cunning. 
    Bat-like wings allow it to fly silently. Its tail is long and ends in a venomous 
    barb like a scorpion's. The imp's face is impish with a pointed nose and chin, 
    constantly smirking. Its hands and feet end in small but sharp claws. The creature 
    wears no clothing, its diabolic nature evident. It perches on a warlock's shoulder 
    or hides in shadows, ready to cause mischief. Small flames occasionally flicker 
    around its form. Its teeth are needle-sharp when it grins. Despite its small size, 
    malevolent intelligence burns in its eyes. Photorealistic rendering of the miniature 
    devil, the servant of evil, and the corruptor in small packages.
    """,
    
    "Invisible Stalker": """
    An air elemental assassin that's naturally invisible, shown here as a barely visible 
    distortion in the air. The creature is vaguely humanoid, 8 feet tall, made entirely 
    of compressed air currents. Its form is only visible as a shimmer, like heat distortion, 
    showing the outline of a muscular humanoid shape. Dust and debris swirl within its 
    form, giving hints to its shape. When it moves, papers flutter and curtains billow. 
    Its eyes are two points of concentrated air pressure that create slight vortexes. 
    The stalker is shown in a library, books flying off shelves in its wake, dust motes 
    spinning in the air currents that form its body. Footprints appear in dust on the 
    floor. Photorealistic rendering of near-invisibility, the presence of absence, and 
    the terror of an unseen hunter.
    """,
    
    "Iron Golem": """
    A 12-foot tall humanoid construct made entirely of iron plates and gears. Its body 
    is assembled from massive iron pieces riveted together, showing the craftsmanship 
    of its creation. The head is a featureless iron helm with two glowing red slits for 
    eyes. Steam occasionally vents from joints. The golem's limbs are proportionally 
    thick, ending in massive iron fists capable of crushing stone. Gears and pistons 
    are visible at joint points. Mystical runes are etched into its chest plate, glowing 
    faintly with magic. The golem moves with mechanical precision, each step causing 
    the ground to shake. It stands in a wizard's workshop, tools and half-finished 
    constructs visible. Rust streaks parts of its body like blood. The sound of grinding 
    metal accompanies every movement. Photorealistic rendering of animated metal, the 
    mechanical servant, and the unstoppable force of magical automation.
    """,
    
    "Kobold": """
    A small 2-foot tall reptilian humanoid with scales ranging from rusty brown to black. 
    Its head is dragon-like with small horns, orange eyes, and a snout filled with small 
    sharp teeth. The kobold's body is scrawny but wiry, with a long tail for balance. 
    Its hands are clever despite having claws. The creature wears makeshift armor from 
    scavenged materials and carries mining tools as weapons. Despite its small size, 
    it shows cunning intelligence. The kobold stands in a warren tunnel, trap mechanisms 
    visible. Its scales catch torchlight. The expression shows a mix of cowardice and 
    sneaky intelligence. Years of living underground have made its eyes sensitive to light. 
    Small scars and mining dust cover its body. Photorealistic detail showing the small 
    dragon-kin, the trap-maker, and the weak but clever underdog of monsters.
    """,
    
    "Kraken": """
    A colossal sea monster of legendary proportions, its main body alone 100 feet long. 
    Eight massive tentacles, each 120 feet long and 10 feet thick, writhe from its body. 
    Two even longer tentacles serve as primary weapons. The head is elongated like a 
    giant squid's with two enormous eyes, each 10 feet across, showing alien intelligence. 
    Its beak could swallow ships whole. The skin is dark purple-black with a rubbery 
    texture, covered in barnacles and scars from ancient battles. Each tentacle is lined 
    with suckers the size of shields, each containing teeth-like hooks. The kraken rises 
    from a storm-tossed ocean, tentacles wrapped around a sailing ship, crushing it like 
    a toy. Lightning illuminates its massive form. Water cascades off its body. The eyes 
    glow with malevolent intelligence. Photorealistic rendering of the ultimate sea monster, 
    the ship-destroyer, and the terror from the depths.
    """,
    
    "Lamia": """
    A creature with the upper body of a beautiful woman and the lower body of a lion. 
    The human portion is alluring with bronze skin, long dark hair adorned with gold 
    jewelry, and captivating eyes that shift between human and feline. The transition 
    at the waist blends smooth skin into golden-brown fur. The lion body is powerful 
    and sleek with muscular legs ending in massive paws with retractable claws. A long 
    leonine tail swishes behind. She wears ornate jewelry and silks on her human half. 
    Her expression is seductive but predatory. She reclines in desert ruins, ancient 
    pillars and sand surrounding her. Her hands gesture hypnotically. Despite her beauty, 
    there's something unsettling about the blend of human and beast. Photorealistic 
    rendering of the seductive predator, the desert enchantress, and the dangerous 
    beauty of the lamia.
    """
}

def main():
    """Generate portraits for Batch 7 monsters"""
    
    print("="*60)
    print("D&D MONSTER PORTRAIT GENERATOR - BATCH 7")
    print("="*60)
    print(f"\nGenerating {len(MONSTERS_BATCH_7)} monster portraits...")
    
    results = []
    
    for monster_name, description in MONSTERS_BATCH_7.items():
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
    print("BATCH 7 GENERATION COMPLETE")
    print("="*60)
    
    successful = [name for name, result in results if result["success"]]
    failed = [name for name, result in results if not result["success"]]
    
    print(f"\nSuccessful: {len(successful)}/{len(MONSTERS_BATCH_7)}")
    for name in successful:
        print(f"  - {name}")
    
    if failed:
        print(f"\nFailed: {len(failed)}")
        for name in failed:
            print(f"  - {name}")
    
    print(f"\nAll portraits saved in: monster_portraits/")

if __name__ == "__main__":
    main()