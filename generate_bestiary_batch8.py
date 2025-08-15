#!/usr/bin/env python3
"""
Generate D&D Monster Portraits - Batch 8 (Monsters 71-80)
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

# BATCH 8: Monsters 71-80 with Detailed Prompts
MONSTERS_BATCH_8 = {
    "Lich": """
    An undead wizard of immense power, once human but now a skeletal horror wreathed in 
    dark magic. The skull is intact but yellowed with age, eye sockets burning with 
    pinpoints of red light that pierce the soul. Tattered robes of once-fine material 
    hang from its skeletal frame, embroidered with arcane symbols that still glow with 
    power. Skeletal hands clutch an ornate staff topped with a skull. A golden crown 
    sits upon its skull, and numerous magical rings adorn its finger bones. Dark energy 
    crackles around its form. The lich floats slightly above the ground in its tomb 
    laboratory, surrounded by spell books, magical artifacts, and failed experiments. 
    Its jaw hangs open in an eternal grin of death. Wisps of negative energy flow from 
    its form. The phylactery containing its soul glows somewhere nearby. Photorealistic 
    rendering of undead majesty, arcane power, and the horror of eternal unlife.
    """,
    
    "Lizardfolk": """
    A 6-foot tall reptilian humanoid with green and brown scales covering its entire body. 
    The head is distinctly lizard-like with a long snout filled with sharp teeth, yellow 
    reptilian eyes with vertical pupils, and a crest of spines running from head to tail. 
    Its body is lean and muscular with a long tail used for swimming and balance. Webbed 
    fingers and toes aid in aquatic movement. The lizardfolk carries primitive weapons - 
    a spear and shield made from turtle shell and bone. Its scales glisten with moisture. 
    The creature stands in a swamp setting, partially in water. Its expression is cold 
    and emotionless, showing reptilian indifference. Tribal scarification marks its scales. 
    A necklace of teeth and claws shows hunting prowess. Photorealistic detail of scales, 
    the amphibious adaptation, and the primitive yet dangerous nature of these swamp 
    dwellers.
    """,
    
    "Manticore": """
    A horrifying fusion of lion, human, and scorpion, 10 feet long with a muscular lion's 
    body covered in reddish-brown fur. The face is disturbingly human but stretched over 
    a lion's skull, with three rows of sharp teeth and mad eyes that show cruel intelligence. 
    A thick mane surrounds the human-like face. Most terrifying is its tail - long and 
    segmented like a scorpion's but covered in hundreds of foot-long spikes that it can 
    launch like arrows. Bat-like wings spread from its shoulders, allowing flight. The 
    creature stands on a rocky outcrop, tail arched over its back ready to fire spikes. 
    Its mouth is open showing all three rows of teeth. The human face on the beast body 
    is deeply unsettling. Blood stains its muzzle and claws. Photorealistic horror showing 
    the unnatural fusion, the spike-throwing tail, and the sadistic intelligence.
    """,
    
    "Medusa": """
    Once a beautiful woman, now a cursed creature with living snakes for hair. Her face 
    retains traces of former beauty but is now gaunt with scales patches on her cheeks. 
    Her eyes glow with a sickly green light - meeting her gaze turns victims to stone. 
    Hundreds of snakes writhe where hair should be, each one alive and hissing. Her skin 
    has a greenish tint with patches of scales. She wears tattered Greek-style robes. 
    Her hands end in claw-like nails. The medusa stands in a garden of petrified victims - 
    warriors frozen mid-scream, their faces showing final terror. Some statues are ancient 
    and weathered, others fresh. Her expression shows both tragedy and malevolence. Tears 
    of poison run down her cheeks. The snakes constantly move, each with its own awareness. 
    Photorealistic rendering of cursed beauty, the living snake hair, and the tragic 
    monster who kills with a glance.
    """,
    
    "Mimic": """
    A shapeshifter shown in its true form - an amorphous mass of gray flesh covered in 
    a sticky adhesive. In this image, it's partially transformed into a treasure chest, 
    with parts of its body still showing. The 'lid' of the chest opens to reveal rows 
    of sharp teeth and a massive purple tongue. Multiple eyes appear randomly on its 
    surface. Pseudopods extend from the mass, some shaped like treasure chest hardware, 
    others reaching for prey. The texture is wet and organic despite mimicking wood and 
    metal. The creature is in a dungeon room, having perfectly imitated a chest until 
    disturbed. Gold coins are stuck to its adhesive surface. Parts of previous victims' 
    equipment are partially absorbed into its mass. Photorealistic body horror showing 
    the perfect camouflage predator, the transformation between object and monster.
    """,
    
    "Minotaur": """
    An 8-foot tall muscular humanoid with the head of a massive bull. Its body is that 
    of a powerfully built human covered in short brown fur. The bull head features long 
    curved horns, a ring through its nose, and eyes that burn with rage and maze-madness. 
    Its hands are humanoid but end in thick, hard nails. Hooved feet provide powerful 
    charges. The minotaur wields a massive double-headed axe with deadly skill. Scars 
    crisscross its body from countless battles. It stands in a stone labyrinth, walls 
    marked with claw scratches from its victims' attempts to escape. Its nostrils flare 
    with hot breath. The expression shows bestial fury combined with human cunning. Greek 
    armor pieces partially cover its form. Photorealistic rendering of the bull-man hybrid, 
    the labyrinth guardian, and the classical monster of Greek mythology.
    """,
    
    "Mummy": """
    An ancient preserved corpse animated by dark magic, wrapped in yellowed linen bandages 
    that trail and unravel. Parts of desiccated flesh are visible through gaps - leathery 
    brown skin pulled tight over bones. The face is partially exposed showing hollow 
    eye sockets with pinpoints of red light, a lipless mouth with yellowed teeth, and 
    skin like ancient parchment. Hieroglyphs on the wrappings glow with cursed energy. 
    The mummy moves with jerky, unnatural motions. Dust and sand fall from its form with 
    every step. It carries an ancient Egyptian staff and wears golden amulets. The creature 
    stands in a torch-lit tomb surrounded by canopic jars and hieroglyph-covered walls. 
    A supernatural dread emanates from it. The smell of preservatives and death follows it. 
    Photorealistic rendering of preserved death, ancient curses, and the horror of the 
    walking dead from Egypt's tombs.
    """,
    
    "Naga": """
    A serpentine creature with a human upper body and a 20-foot long snake lower body. 
    The human portion is beautiful and regal, with bronze skin, elegant features, and 
    eyes showing ancient wisdom. The snake portion has emerald green scales with golden 
    patterns. The transition from human to snake at the waist is seamless and natural. 
    The naga wears golden jewelry - arm bands, necklaces, and a ornate headdress with 
    a cobra hood design. Its hands gesture in spellcasting motions. The creature is coiled 
    in an ancient temple, stone serpent carvings surrounding it. Its expression is serene 
    but powerful. The snake body shows incredible muscle control. A forked tongue occasionally 
    flicks out. Photorealistic rendering of the snake-human hybrid, the temple guardian, 
    and the mystical presence of this ancient race.
    """,
    
    "Nightmare": """
    A massive horse from the lower planes, standing 6 feet at the shoulder with a coat 
    of pure black that seems to absorb light. Its mane and tail are made of shadowstuff 
    that flows like smoke. The eyes burn with orange hellfire. Most terrifying are its 
    hooves - they burn with infernal flame, leaving flaming hoofprints. When it breathes, 
    smoke and embers emerge from its nostrils. The nightmare's teeth are sharp like a 
    predator's rather than a normal horse. Its body is powerfully muscled for both speed 
    and combat. The creature rears on a battlefield at night, flames surrounding its hooves. 
    Its mouth is open in a terrifying whinny. The contrast between its shadow-black coat 
    and burning hooves creates a striking image. An aura of fear surrounds it. Photorealistic 
    rendering of the infernal steed, the mount of evil, and the horse that gallops through 
    nightmares.
    """,
    
    "Ochre Jelly": """
    A massive 10-foot wide amoeba-like ooze of mustard-yellow color with the consistency 
    of thick pudding. Its surface constantly undulates and bubbles as it moves. The jelly 
    is semi-transparent, showing partially dissolved organic matter within - bones, armor, 
    and other indigestible materials float in its mass. When it moves, it leaves a trail 
    of acidic slime that etches stone. The creature can squeeze through incredibly small 
    spaces and split when struck. It spreads across a dungeon corridor, seeping through 
    cracks in the walls. The surface has an oily sheen that reflects torchlight. Acidic 
    vapors rise from its form. Where it touches organic material, it immediately begins 
    dissolving. Photorealistic rendering of living acid, the mindless consumer, and the 
    dungeon hazard that dissolves everything organic.
    """
}

def main():
    """Generate portraits for Batch 8 monsters"""
    
    print("="*60)
    print("D&D MONSTER PORTRAIT GENERATOR - BATCH 8")
    print("="*60)
    print(f"\nGenerating {len(MONSTERS_BATCH_8)} monster portraits...")
    
    results = []
    
    for monster_name, description in MONSTERS_BATCH_8.items():
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
    print("BATCH 8 GENERATION COMPLETE")
    print("="*60)
    
    successful = [name for name, result in results if result["success"]]
    failed = [name for name, result in results if not result["success"]]
    
    print(f"\nSuccessful: {len(successful)}/{len(MONSTERS_BATCH_8)}")
    for name in successful:
        print(f"  - {name}")
    
    if failed:
        print(f"\nFailed: {len(failed)}")
        for name in failed:
            print(f"  - {name}")
    
    print(f"\nAll portraits saved in: monster_portraits/")

if __name__ == "__main__":
    main()