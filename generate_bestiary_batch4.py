#!/usr/bin/env python3
"""
Generate D&D Monster Portraits - Batch 4 (Monsters 31-40)
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

# BATCH 4: Monsters 31-40 with Detailed Prompts
MONSTERS_BATCH_4 = {
    "Dretch": """
    A pathetic 4-foot tall demon, the lowest form of demonic life. Its body is bloated and 
    corpulent with sickly green-gray skin covered in oozing pustules and boils. The head 
    is too small for its body with piggy eyes, no nose, and a mouth full of broken teeth. 
    Two spindly arms end in clawed hands that constantly grasp and clutch. Its legs are 
    short and bowed, barely supporting its bloated weight. The creature's skin constantly 
    weeps pus and slime. Its belly distends grotesquely, showing signs of disease and rot. 
    Small useless wings sprout from its back, too weak to lift its bulk. The dretch stands 
    in the filth of the Abyss, surrounded by refuse and decay. Flies buzz around its form. 
    Its expression shows both stupidity and endless suffering. Photorealistic rendering of 
    diseased flesh, the pathetic nature of the lowest demon, and the horror of eternal 
    torment given form.
    """,
    
    "Drider": """
    A horrifying fusion of dark elf and giant spider, cursed by their goddess. The upper 
    body is that of a dark elf - obsidian black skin, white hair, and red eyes filled with 
    madness and pain. From the waist down, the body of a massive black spider with eight 
    segmented legs covered in coarse hair. The transition point where elf meets spider is 
    disturbing, flesh melding into chitin. The dark elf torso emerges from where the spider's 
    head would be. Eight spider eyes dot the spider body's front. The elf portion wears 
    tattered remnants of once-fine clothing. In its hands, a cruel sword dripping with poison. 
    The spider legs end in sharp points that click on stone. Spinnerets at the rear trail 
    silk. The creature is in an underdark cavern surrounded by webs and cocooned victims. 
    Photorealistic horror showing the curse of transformation, the blend of elf and arachnid, 
    and the tragic monstrosity of a fallen race.
    """,
    
    "Dryad": """
    A nature spirit of ethereal beauty, appearing as a woman made partially of living wood 
    and leaves. Her skin has the texture of smooth bark in some places, soft flesh in others, 
    with the transition seamless and natural. Long hair appears to be made of willow branches 
    and autumn leaves that change color as they cascade down. Her eyes are deep green like 
    forest pools. Delicate features show both human beauty and plant-like qualities. Her body 
    is modestly covered by living vines and leaves that grow from her form. Small flowers 
    bloom along her arms and in her hair. She stands merged partially with an ancient oak 
    tree, her lower body blending into its trunk. Butterflies and birds perch on her 
    outstretched hands. Dappled sunlight filters through forest canopy highlighting her form. 
    Photorealistic rendering of the blend between woman and nature, the ethereal beauty, 
    and the deep connection to the forest.
    """,
    
    "Earth Elemental": """
    A 12-foot tall humanoid form made entirely of animated earth and stone. Its body consists 
    of compacted dirt, rocks, and boulders held together by elemental force. The head is a 
    rough boulder with two glowing amber eyes like molten gems. No other features mark the 
    face. Its arms are massive, ending in club-like fists of solid granite. The legs are 
    thick pillars of compressed earth. Grass and small plants grow from cracks in its form. 
    Veins of precious metals and crystals run through its body, catching light. As it moves, 
    dirt and pebbles constantly fall from its form only to be pulled back by magical force. 
    The elemental rises from disturbed ground, earth and stones swirling up to form its body. 
    Its footsteps leave deep impressions. Photorealistic rendering of living earth, the raw 
    power of animated stone, and the primal force of the elemental plane of earth.
    """,
    
    "Efreeti": """
    A massive 12-foot tall genie of fire, its muscular form wreathed in flames. The skin 
    is dark red like cooling lava with cracks showing molten fire beneath. Horns of obsidian 
    curve from its head, and its eyes burn with orange flame. A beard of fire flows from 
    its chin. The lower body transforms into a pillar of flame and smoke. Brass armor adorned 
    with rubies covers its chest and arms. In one hand, a massive scimitar that glows 
    white-hot. Golden chains and jewelry melt and reform constantly from the heat. The air 
    around it shimmers with heat waves. It stands in a palace of brass and flame, with lava 
    fountains in the background. Smoke rises from its entire form. The flames that comprise 
    its lower body swirl in a hypnotic pattern. Photorealistic rendering of a being of 
    living flame, the overwhelming heat presence, and the cruel nobility of the fire genies.
    """,
    
    "Ettin": """
    A 13-foot tall two-headed giant, each head having its own personality and awareness. 
    The body is massively muscled but filthy, covered in dirt, scars, and crude tattoos. 
    The left head is brutish with a broken nose and missing teeth, while the right head 
    is slightly more cunning with a perpetual sneer. Both heads argue constantly with each 
    other. Each head controls one arm, leading to uncoordinated movements. The giant wears 
    piecemeal armor made from various sources, nothing matching. One hand holds a massive 
    spiked club, the other a rusted battle axe. Its skin is grayish-brown and covered in 
    warts. The creature stands in its filthy lair surrounded by gnawed bones and refuse. 
    Both mouths drool constantly. The eyes show different emotions - one head angry, one 
    suspicious. Photorealistic detail showing the grotesque two-headed nature, the constant 
    internal conflict, and the crude brutality of this giant.
    """,
    
    "Fire Elemental": """
    A living inferno in vaguely humanoid form, 15 feet tall and constantly burning. 
    Its body is made of roaring flames that shift from white-hot at the core to deep red 
    at the edges. Two points of blinding white light serve as eyes within the conflagration. 
    Arms of concentrated fire extend from the central mass, leaving trails of flame with 
    every movement. The core shows different temperatures - blue-white heart, yellow body, 
    orange extremities. Smoke and embers constantly rise from its form. The air around it 
    ripples with extreme heat. Everything flammable near it immediately ignites. The creature 
    moves like a living wildfire, expanding and contracting. Standing on scorched earth with 
    glass formed from melted sand beneath it. Photorealistic rendering of living flame, 
    the hypnotic dance of fire, and the terrifying beauty of pure elemental destruction.
    """,
    
    "Fire Giant": """
    A 16-foot tall giant with coal-black skin and orange eyes that glow like embers. 
    Its hair and beard are bright orange-red like flames. The giant's body is massively 
    muscled from working forges. Its skin shows the texture of cooled lava with cracks 
    revealing inner heat. The giant wears elaborate plate armor of blackened steel with 
    gold trim. A massive two-handed sword rests on its shoulder, the blade still glowing 
    from the forge. Its hands show centuries of smithing work. The giant stands in a 
    volcanic forge, lava flows providing light, anvils and weapons visible. Steam rises 
    from its body. A necklace of dragon teeth shows its prowess. The face shows cruel 
    intelligence and mastery of metallurgy. Photorealistic detail of the volcanic giant, 
    the master craftsman of evil, and the overwhelming physical presence.
    """,
    
    "Flesh Golem": """
    A grotesque 8-foot tall humanoid stitched together from parts of multiple corpses. 
    The skin is a patchwork of different flesh tones badly sewn with thick black thread. 
    One arm is noticeably larger than the other, taken from different bodies. The face 
    is the most disturbing - features that don't match, one blue eye and one brown, scars 
    where parts were attached. Metal bolts protrude from its neck and joints. The creature 
    moves with unnatural, jerky motions. Electricity occasionally arcs between the metal 
    bolts. Its expression is blank but somehow sad. The body shows signs of decay in places 
    with preservative fluid leaking from seams. It wears tattered rags. The hands are 
    massive and scarred. Standing in a laboratory with surgical equipment visible. 
    Photorealistic body horror emphasizing the unnatural assembly, the tragic existence, 
    and the abomination of reanimated flesh.
    """,
    
    "Frost Giant": """
    A 15-foot tall giant with pale blue-white skin and a beard of icicles. Its hair is 
    white as fresh snow, braided with frozen leather. Eyes are pale blue like glacier ice. 
    The giant's body is muscular and scarred from countless battles. It wears armor made 
    from white dragon scales and fur from arctic beasts. A massive greataxe of enchanted 
    ice is held in one hand. Its breath forms clouds of freezing mist. Frost constantly 
    forms on its skin and armor. The giant stands in a frozen wasteland, snow swirling 
    around its form. Ice crystals form in the air near it. Its expression is harsh and 
    merciless like winter itself. Tribal tattoos in blue mark its arms. A necklace of 
    polar bear claws shows its hunting prowess. Photorealistic rendering of the ice giant, 
    the harsh beauty of the frozen north, and the primal power of winter's warriors.
    """
}

def main():
    """Generate portraits for Batch 4 monsters"""
    
    print("="*60)
    print("D&D MONSTER PORTRAIT GENERATOR - BATCH 4")
    print("="*60)
    print(f"\nGenerating {len(MONSTERS_BATCH_4)} monster portraits...")
    
    results = []
    
    for monster_name, description in MONSTERS_BATCH_4.items():
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
    print("BATCH 4 GENERATION COMPLETE")
    print("="*60)
    
    successful = [name for name, result in results if result["success"]]
    failed = [name for name, result in results if not result["success"]]
    
    print(f"\nSuccessful: {len(successful)}/{len(MONSTERS_BATCH_4)}")
    for name in successful:
        print(f"  - {name}")
    
    if failed:
        print(f"\nFailed: {len(failed)}")
        for name in failed:
            print(f"  - {name}")
    
    print(f"\nAll portraits saved in: monster_portraits/")

if __name__ == "__main__":
    main()