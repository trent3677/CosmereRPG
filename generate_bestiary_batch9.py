#!/usr/bin/env python3
"""
Generate D&D Monster Portraits - Batch 9 (Monsters 81-90)
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

# BATCH 9: Monsters 81-90 with Detailed Prompts
MONSTERS_BATCH_9 = {
    "Ogre": """
    A 10-foot tall giant humanoid with a massive, corpulent body covered in warty, 
    greenish-gray hide. Its head is disproportionately large with a jutting jaw filled 
    with yellowed, broken tusks. Small, pig-like eyes show dim intelligence and cruel 
    hunger. The ogre's arms are thick as tree trunks ending in massive hands with dirty, 
    broken nails. Its belly hangs over a crude belt made of skulls. The creature wears 
    poorly stitched animal hides and carries a massive wooden club studded with nails 
    and teeth. Its hair is greasy and matted with filth. The ogre stands in its crude 
    lair, gnawed bones and refuse scattered about. Flies buzz around its unwashed form. 
    Its mouth drools constantly. The expression shows stupid cruelty and endless hunger. 
    Photorealistic rendering of the brutish giant, the dim-witted bully, and the raw 
    physical threat of ogre-kind.
    """,
    
    "Oni": """
    An 8-foot tall demonic ogre mage from Eastern mythology with blue or red skin and 
    a terrifying visage. Two or three horns protrude from its forehead, and its face 
    features a massive mouth with prominent tusks. Wild black hair flows like flames. 
    The oni's body is powerfully muscled and covered in mystical tattoos that glow with 
    magic. It wears samurai-style armor plates over traditional Japanese clothing. In one 
    hand it carries a massive iron-studded club (kanabo), in the other mystical flames 
    dance. The creature can shapeshift and cast spells. Its eyes burn with malevolent 
    intelligence far greater than a common ogre. The oni stands in a Japanese temple 
    it has defiled, sake jars and gold scattered about. Storm clouds gather overhead 
    at its command. Photorealistic rendering of the Japanese demon, the ogre mage, and 
    the blend of physical and magical power.
    """,
    
    "Orc": """
    A 6-foot tall humanoid warrior with gray-green skin and a muscular, scarred body. 
    Its face is pig-like with a snout nose, prominent lower tusks, and small red eyes 
    that burn with hatred. Coarse black hair is tied in warrior braids. The orc's body 
    shows the harsh life of constant warfare - scars, burns, and old wounds. It wears 
    piecemeal armor scavenged from various sources, decorated with teeth and finger bones 
    of enemies. A massive battle axe, notched from use, is gripped in calloused hands. 
    War paint marks its face. The orc stands in a war camp, other orcs visible preparing 
    for raid. Its expression shows savage joy at the prospect of battle. Blood stains 
    its armor and weapons. Photorealistic detail showing the warrior culture, the savage 
    nature, and the endless aggression of orc-kind.
    """,
    
    "Otyugh": """
    A grotesque 8-foot wide aberration that dwells in filth and waste. Its body is a 
    bloated, oval mass of diseased flesh covered in rock-hard patches and oozing pustules. 
    Three thick legs support its bulk. Two long tentacles covered in thorny ridges extend 
    10 feet from its body, used to grab prey. A third tentacle ending in two eyes on 
    stalks rises above. Its mouth is a massive vertical maw in the center of its body, 
    filled with rows of teeth designed to grind anything. The creature wallows in sewage 
    and refuse, feeding on waste and carrion. Flies swarm around it. Its hide is stained 
    with filth and dried blood. Partially eaten corpses lie nearby. The stench is visible 
    as wavy air. Photorealistic horror showing the living garbage disposal, the disease-
    ridden scavenger, and the nightmare of the sewers.
    """,
    
    "Owlbear": """
    A massive terrifying hybrid creature with the body of a huge grizzly bear and the 
    head of a giant owl. Its muscular frame stands 8 feet tall, covered in thick brown 
    fur with patches of dark feathers transitioning around the neck and shoulders. The 
    owl head features enormous amber eyes that glow with predatory intelligence, and a 
    sharp curved beak powerful enough to snap bones. Its massive bear paws end in razor-
    sharp talons. The creature is shown in a forest clearing, standing on its hind legs 
    in an aggressive posture, with one paw raised showing its deadly claws. Dramatic 
    lighting filters through the forest canopy, highlighting the creature's intimidating 
    presence. The scene captures the owlbear mid-roar, its beak open revealing a terrifying 
    maw. Photorealistic detail showing individual feathers and fur texture, with bright 
    vivid colors emphasizing the creature's primal ferocity and unnatural hybrid nature.
    """,
    
    "Pegasus": """
    A magnificent winged horse of pure white, standing 5 feet at the shoulder with a 
    20-foot wingspan. Its coat gleams like fresh snow, perfectly groomed and lustrous. 
    The wings are those of a giant eagle but covered in pristine white feathers that 
    catch sunlight with an almost divine radiance. Its mane and tail flow like silk in 
    an ethereal breeze. The eyes show intelligence beyond a normal horse, deep brown 
    and knowing. The pegasus stands on a mountain peak above the clouds, wings spread 
    majestically. Its bearing is noble and proud. Golden light halos its form. The hooves 
    are polished silver. Muscles ripple beneath the perfect coat. The expression is both 
    gentle and fierce. Photorealistic rendering of the celestial mount, the symbol of 
    freedom, and the divine flying horse of legend.
    """,
    
    "Phase Spider": """
    A 10-foot wide spider with the terrifying ability to phase between dimensions. Its 
    body is pale blue-white with a translucent quality, as if not fully in this reality. 
    Eight long legs shimmer and phase in and out of visibility. The spider's body constantly 
    shifts between solid and ethereal states. Eight eyes glow with otherworldly blue light. 
    Its fangs drip with venom that exists in multiple dimensions simultaneously. The 
    creature is shown partially phased - half its body translucent and ghostly, half 
    solid and threatening. Web strands stretch between dimensions, visible in some places, 
    fading to nothing in others. The spider hunts in a darkened ruin where reality seems 
    thin. Photorealistic rendering of the dimensional predator, the phase-shifting horror, 
    and the spider that attacks from nowhere.
    """,
    
    "Pit Fiend": """
    A 12-foot tall devil general, the most powerful of Hell's warriors. Its body is massively 
    muscled and covered in scales of deep crimson. Huge bat wings spread 20 feet wide, 
    membrane scarred from countless battles. The head is bestial with horns like a ram, 
    eyes that burn with infernal fire, and a mouth full of fangs. Its hands end in terrible 
    claws, and its tail is long and powerful. The pit fiend wears elaborate hell-forged 
    armor decorated with screaming faces. It carries a massive flaming sword and a whip 
    of fire. An aura of fear and flame surrounds it. The devil stands at the gates of a 
    hellish fortress, armies of lesser devils behind it. Lava flows and flames provide 
    backdrop. Its expression shows absolute authority and cruelty. Photorealistic rendering 
    of infernal might, diabolic leadership, and the ultimate devil warrior.
    """,
    
    "Planetar": """
    A 9-foot tall angel warrior with emerald skin that seems to glow with inner light. 
    Massive white wings span 15 feet, each feather perfect and radiant. Its face is 
    impossibly beautiful yet stern, with silver eyes that see all sin and virtue. Long 
    silver hair flows like liquid metal. The planetar wears gleaming plate armor that 
    seems made of condensed starlight. In one hand, a flaming greatsword of pure radiance, 
    in the other, divine light ready to heal or harm. A golden halo of pure energy surrounds 
    its head. The angel hovers above a battlefield between good and evil, ready to smite 
    the wicked. Light bends around its form creating rainbow effects. Its expression shows 
    divine justice tempered with mercy. Photorealistic rendering of celestial power, 
    angelic beauty, and the warrior of heaven.
    """,
    
    "Purple Worm": """
    A colossal 80-foot long worm, 10 feet in diameter, burrowing through solid rock. 
    Its body is segmented like an earthworm but covered in thick purple plates that can 
    deflect weapons. The head is mostly a massive circular maw filled with grinding teeth 
    arranged in concentric rings, capable of swallowing creatures whole. A massive stinger 
    at its tail end drips with deadly poison. The worm erupts from underground, rocks 
    and dirt flying everywhere. Its body shows scars from battles with other underground 
    horrors. Acidic saliva drips from its maw, dissolving stone. The segments pulse with 
    muscular contractions as it moves. The ground trembles with its approach. Photorealistic 
    rendering of the underground terror, the tunnel maker, and the apex predator of the 
    deep earth.
    """
}

def main():
    """Generate portraits for Batch 9 monsters"""
    
    print("="*60)
    print("D&D MONSTER PORTRAIT GENERATOR - BATCH 9")
    print("="*60)
    print(f"\nGenerating {len(MONSTERS_BATCH_9)} monster portraits...")
    
    results = []
    
    for monster_name, description in MONSTERS_BATCH_9.items():
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
    print("BATCH 9 GENERATION COMPLETE")
    print("="*60)
    
    successful = [name for name, result in results if result["success"]]
    failed = [name for name, result in results if not result["success"]]
    
    print(f"\nSuccessful: {len(successful)}/{len(MONSTERS_BATCH_9)}")
    for name in successful:
        print(f"  - {name}")
    
    if failed:
        print(f"\nFailed: {len(failed)}")
        for name in failed:
            print(f"  - {name}")
    
    print(f"\nAll portraits saved in: monster_portraits/")

if __name__ == "__main__":
    main()