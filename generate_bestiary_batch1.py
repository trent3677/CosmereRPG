#!/usr/bin/env python3
"""
Generate D&D Monster Portraits - Batch 1 (First 10 Monsters)
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

# BATCH 1: First 10 SRD Monsters with Detailed Prompts
MONSTERS_BATCH_1 = {
    "Aboleth": """
    A massive ancient aberration, a prehistoric fish-like horror measuring 20 feet long. 
    Its rubbery gray-green skin glistens with thick mucus and slime. Three enormous red eyes 
    arranged vertically dominate its bulbous head, each glowing with alien intelligence. 
    Four long, powerful tentacles writhe from its body, each 10 feet long and covered in 
    mucus-secreting pores. The creature floats in dark underwater cavern, surrounded by 
    bioluminescent fungi. Its lamprey-like mouth is filled with rows of needle teeth. 
    The tentacles show pulsing veins beneath translucent skin. Dramatic underwater lighting 
    creates an otherworldly atmosphere with rays of dim light filtering through murky water. 
    Photorealistic detail emphasizing the wet, slimy texture and alien horror of this 
    ancient mind-controlling monstrosity.
    """,
    
    "Adult Black Dragon": """
    A massive dragon with sleek, skull-like head and forward-swept horns like a crown of death. 
    Its scales are glossy obsidian black with hints of dark purple, each scale perfectly defined. 
    The dragon stands 16 feet tall at the shoulder with a 80-foot wingspan. Acidic green vapor 
    drips from its jaws, hissing and dissolving the ground beneath. Its eyes glow with malevolent 
    green light. The dragon is positioned in a fetid swamp, partially submerged in murky water 
    with dead trees and bones scattered around. Its muscular form shows every sinew and scale. 
    The wings are spread menacingly, membrane between the bones showing veins backlit by sickly 
    swamp light. Dramatic lighting emphasizes the contrast between the glossy black scales and 
    the toxic green acid breath. Photorealistic rendering capturing the terrifying majesty and 
    evil intelligence of this apex predator.
    """,
    
    "Adult Blue Dragon": """
    A colossal dragon with a massive horn jutting from its snout and electric blue scales that 
    crackle with lightning. Standing 18 feet tall with a 100-foot wingspan, its scales shimmer 
    from deep sapphire to brilliant electric blue. Lightning constantly arcs between its horn 
    and the frilled ears. The dragon's mouth is open, revealing rows of sword-like teeth with 
    electricity building in its throat. Its muscular body shows incredible detail with each 
    scale catching light differently. The dragon stands atop a desert mesa during a lightning 
    storm, sand swirling around its claws. The wings are fully spread, membrane taut and 
    translucent with lightning coursing through the wing bones. Its tail ends in a massive 
    blade-like tip. Eyes glow white-blue with electrical energy. Photorealistic detail showing 
    the interplay of lightning across its metallic scales, creating an awe-inspiring display 
    of draconic power and elemental fury.
    """,
    
    "Adult Red Dragon": """
    A titanic dragon of legendary proportions, its scales like molten rubies ranging from deep 
    crimson to bright scarlet. Standing 20 feet tall with a 120-foot wingspan, smoke and embers 
    constantly rise from its body. Its head features swept-back horns and a crown of spikes, 
    with eyes like pools of liquid fire. The dragon's mouth is open in a roar, showing massive 
    fangs and the glow of an inferno building in its throat. Its muscular frame ripples with 
    power, each scale edged in gold and orange like cooling lava. The dragon perches atop a 
    volcanic mountain, lava flows visible below. Its wings cast enormous shadows, the membrane 
    showing a network of blood vessels backlit by volcanic fire. Claws like obsidian daggers 
    grip molten rock. The tail ends in a brutal array of spikes. Photorealistic rendering 
    capturing the overwhelming presence of the most feared of all dragons, with heat distortion 
    visible around its body and volcanic atmosphere.
    """,
    
    "Air Elemental": """
    A swirling vortex of living wind and storm, 15 feet tall and constantly in motion. 
    The elemental's form is a tornado-like funnel of compressed air with debris and dust 
    caught in its winds making its shape visible. Lightning occasionally flashes within 
    its cloudy form. At its center, two points of brilliant white light serve as eyes. 
    The creature's "arms" are whirling cyclones that extend from the main vortex. 
    Its base spreads out in spiraling winds that kick up dust and leaves. The air around 
    it shimmers with pressure changes and condensation. Set against a stormy sky with 
    dark clouds, the elemental appears both beautiful and terrifying. Leaves, dust, and 
    small debris orbit within its form at different speeds. Photorealistic rendering 
    showing the translucent, ever-shifting nature of living air, with visible air currents, 
    pressure waves, and the raw power of an unleashed storm.
    """,
    
    "Ankheg": """
    A monstrous insectoid predator, 10 feet long with a chitinous brown and yellow exoskeleton. 
    Its body combines the worst aspects of a centipede and praying mantis. Six powerful legs 
    with serrated edges for digging end in hook-like claws. Its head features massive mandibles 
    dripping with acidic green digestive fluid that sizzles on the ground. Compound eyes with 
    hundreds of facets reflect light in an alien manner. Thick armored plates overlap along 
    its back, with softer pale yellow underbelly visible. The creature is emerging from a 
    tunnel in farmland, dirt cascading off its armor. Antennae twitch constantly, sensing 
    vibrations. Its mandibles are spread wide showing the acid gland in its throat glowing 
    green. The exoskeleton shows battle scars and a weathered texture. Photorealistic detail 
    emphasizing the horrific insectoid features, the wet gleam of acid on its mandibles, and 
    the predatory intelligence in its multifaceted eyes.
    """,
    
    "Banshee": """
    A translucent undead spirit of a once-beautiful elf woman, now twisted by undeath into 
    a horrifying specter. Her ethereal form floats above the ground, long white hair flowing 
    as if underwater. Her face is gaunt and skeletal with hollow, glowing blue eyes filled 
    with eternal anguish. Her mouth is open in an endless silent scream. She wears tattered 
    remnants of an elegant elven gown that flows and billows around her ghostly form. 
    Her hands are elongated with claw-like fingers reaching out desperately. A faint blue-white 
    glow emanates from her entire form with wisps of ectoplasm trailing behind. She appears 
    in a misty graveyard at night with ancient tombstones visible through her translucent body. 
    Photorealistic rendering capturing both her former beauty and current horror, the translucent 
    ethereal quality of her undead form, and the overwhelming sense of sorrow and rage that 
    defines a banshee's existence.
    """,
    
    "Basilisk": """
    An eight-legged reptilian monstrosity, 10 feet long from snout to tail, built like a 
    massive iguana crossed with a crocodile. Its scales are dark green with brown mottling, 
    each scale thick and overlapping like armor. The most terrifying feature is its eyes - 
    pale yellow orbs that glow with a sickly light, the deadly gaze that turns victims to stone. 
    Eight powerful legs arranged like a spider's give it an unsettling gait. Its head is 
    broad and flat with a crown of small horns. The mouth is slightly open showing rows of 
    sharp teeth. The creature stands among partially petrified victims - a warrior frozen 
    mid-scream in stone. Its muscular tail drags behind, leaving furrows in dusty ground. 
    The basilisk's body shows incredible detail - scars, individual scales, and the play 
    of light across its armored hide. Set in a rocky cavern with scattered stone "statues" 
    of its victims. Photorealistic detail emphasizing the reptilian texture and the hypnotic, 
    deadly nature of its petrifying gaze.
    """,
    
    "Behir": """
    A massive serpentine monster, 40 feet long with a dragon-like head and twelve legs along 
    its snake-like body. Its scales are brilliant blue with a lighter blue underbelly, crackling 
    with electrical energy. The head features two curved horns and a mouth filled with 
    razor-sharp teeth. Lightning constantly arcs between its horns and occasionally courses 
    down its entire length. Each of its twelve legs ends in powerful claws capable of gripping 
    cave walls. The creature's body is thick and muscular, undulating like a snake but with 
    the terrifying addition of legs allowing it to move with shocking speed. Its eyes glow 
    electric blue. The behir is shown coiled in a mountain cave, its body wrapped around 
    massive stalagmites, electricity arcing to the cave walls. Its mouth is open displaying 
    the building electrical breath weapon, throat glowing blue-white. Photorealistic rendering 
    showing the interplay of lightning across its scales, the powerful musculature, and the 
    unique horror of a snake with legs.
    """,
    
    "Beholder": """
    A floating spherical aberration, 8 feet in diameter, covered in chitinous dark purple hide. 
    One massive central eye dominates the front, its iris constantly shifting colors as it 
    projects its antimagic cone. Ten eyestalks writhe atop the sphere like serpents, each 
    ending in a smaller eye with a different colored iris - red, green, blue, yellow, orange, 
    violet, white, black, gray, and pink - each representing a different deadly ray. 
    Below the central eye, a massive mouth splits the sphere horizontally, filled with hundreds 
    of needle-sharp teeth arranged in multiple rows. The creature floats in its underground 
    lair surrounded by petrified victims and treasures. Its hide shows a leathery, almost 
    brain-like texture with pulsing veins visible beneath. Each eyestalk moves independently, 
    constantly surveying for threats. Drool drips from its massive maw. The central eye 
    focuses with paranoid intensity. Photorealistic horror emphasizing the alien nature, 
    the multiple eyes all looking in different directions, and the overwhelming sense of 
    paranoia and madness that defines a beholder.
    """
}

def main():
    """Generate portraits for Batch 1 monsters"""
    
    print("="*60)
    print("D&D MONSTER PORTRAIT GENERATOR - BATCH 1")
    print("="*60)
    print(f"\nGenerating {len(MONSTERS_BATCH_1)} monster portraits...")
    
    results = []
    
    for monster_name, description in MONSTERS_BATCH_1.items():
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
    print("BATCH 1 GENERATION COMPLETE")
    print("="*60)
    
    successful = [name for name, result in results if result["success"]]
    failed = [name for name, result in results if not result["success"]]
    
    print(f"\nSuccessful: {len(successful)}/{len(MONSTERS_BATCH_1)}")
    for name in successful:
        print(f"  - {name}")
    
    if failed:
        print(f"\nFailed: {len(failed)}")
        for name in failed:
            print(f"  - {name}")
    
    print(f"\nAll portraits saved in: monster_portraits/")

if __name__ == "__main__":
    main()