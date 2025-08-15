#!/usr/bin/env python3
"""
Generate D&D Monster Portraits - Batch 3 (Monsters 21-30)
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

# BATCH 3: Monsters 21-30 with Detailed Prompts
MONSTERS_BATCH_3 = {
    "Cyclops": """
    A massive 13-foot tall giant with a single enormous eye in the center of its forehead. 
    Its muscular body is covered in grimy, sun-weathered skin with coarse dark hair. 
    The single eye is the size of a dinner plate with a yellow iris and red veins visible. 
    Its face is brutish with a heavy brow ridge above the eye, a flat nose, and a mouth 
    full of yellowed, uneven teeth. Massive hands grip a tree trunk club studded with rocks. 
    The cyclops wears primitive hide clothing and a belt of skulls. Its arms and chest 
    show old battle scars. The creature stands at the entrance to its cave, bones and 
    broken weapons scattered at its feet. Muscles ripple beneath its scarred skin. 
    The single eye focuses with disturbing intelligence despite its primitive appearance. 
    Photorealistic detail showing the weathered skin texture, the unsettling single eye, 
    and the raw physical power of this one-eyed giant.
    """,
    
    "Darkmantle": """
    A cave-dwelling creature resembling a living stalactite crossed with an octopus. 
    Its body is a cone-shaped mass of dark gray flesh, textured to perfectly mimic cave rock. 
    When unfurled, it reveals a membranous underside with eight muscular tentacles radiating 
    from a central mouth filled with crushing teeth. Each tentacle has hundreds of small 
    suckers that grip prey. Two small red eyes peer from beneath the rock-like exterior. 
    The creature is shown both hanging from a cave ceiling disguised as a stalactite and 
    dropping with tentacles spread wide. Its skin texture perfectly matches limestone with 
    mineral deposits and moisture. When attacking, the underside reveals pale, translucent 
    flesh with visible veins. The tentacles wrap around prey with crushing force. A magical 
    darkness emanates from its body. Photorealistic rendering showing the perfect camouflage, 
    the transformation from rock to predator, and the suffocating embrace of its attack.
    """,
    
    "Death Knight": """
    An undead warrior in blackened full plate armor, standing 6 feet tall wreathed in 
    green hellfire. Through the helmet's visor, two pinpoints of red light burn where eyes 
    should be. The armor is ornate but corrupted - once-noble designs now twisted into 
    skulls and screaming faces. Green flames lick from every joint and gap in the armor. 
    A massive two-handed sword wreathed in necrotic energy is held with practiced ease. 
    The cloak is tattered and burns at the edges with supernatural fire. Where the armor 
    is damaged, glimpses of bone and withered flesh are visible. The death knight stands 
    on a battlefield of the slain, green fire reflecting off pools of blood. Frost forms 
    on the ground beneath its feet while hellfire burns above. The presence of undeath 
    is palpable. Photorealistic rendering of the cursed armor, the supernatural flames, 
    and the overwhelming aura of a fallen paladin cursed to eternal undeath.
    """,
    
    "Demilich": """
    A floating skull wreathed in purple magical energy, all that remains of a powerful lich. 
    The skull is ancient yellowed bone with intricate runes carved into every surface. 
    Two gems serve as eyes - a ruby and an emerald - each glowing with malevolent intelligence. 
    Six teeth remain, each replaced with a different precious gemstone that pulses with power. 
    Purple energy constantly flows from the empty sockets and jaw, forming ethereal shapes 
    of screaming souls. The skull floats surrounded by orbiting motes of magical energy. 
    Dust and bone fragments orbit it like planets around a sun. The jaw hangs open in an 
    eternal scream. Ancient spider webs still cling to parts of the skull. The bone shows 
    thousands of years of age with cracks sealed by magical energy. Photorealistic detail 
    of ancient bone, glowing gems, and the terrifying implication of consciousness trapped 
    in a single skull.
    """,
    
    "Deva": """
    A celestial being of divine beauty, 7 feet tall with perfect alabaster skin that seems 
    to glow with inner light. Massive white wings spread 15 feet wide, each feather pristine 
    and luminous. Long golden hair flows as if perpetually in a gentle breeze. The face 
    is impossibly beautiful yet stern, with silver eyes that see into souls. The deva wears 
    flowing robes of white and gold that seem to be made of condensed light. A silver circlet 
    rests on its brow with a star sapphire at the center. In one hand, a flaming sword of 
    pure radiance, in the other, a golden trumpet. A subtle halo of light surrounds its head. 
    The being floats slightly above ground, too pure to touch mortal earth. Rays of divine 
    light stream from behind it. Photorealistic rendering capturing otherworldly beauty, 
    the divine radiance, and the awesome presence of a messenger from the heavens.
    """,
    
    "Dire Wolf": """
    A massive wolf standing 5 feet at the shoulder and 9 feet long, with thick black fur 
    streaked with gray. Its head is enormous with a muzzle full of teeth like daggers. 
    Yellow eyes burn with primal hunger and intelligence beyond a normal wolf. The fur is 
    coarse and matted in places, with old battle scars visible through the coat. Muscles 
    ripple beneath the fur with every movement. Its paws are the size of dinner plates 
    with claws like curved knives. The dire wolf stands in a snowy forest, breath steaming 
    in the cold air. Blood stains its muzzle from a recent kill. Other dire wolves are 
    visible in the background as part of the pack. Its lips are pulled back in a snarl 
    revealing the full array of teeth. The tail is held high in dominance. Photorealistic 
    detail showing individual fur strands, the predatory intensity, and the size that makes 
    this apex predator so feared.
    """,
    
    "Displacer Beast": """
    A panther-like predator with six legs and two tentacles growing from its shoulders, 
    each ending in a pad covered with razor spikes. The creature is 10 feet long with 
    blue-black fur that seems to shimmer and shift. Most disturbing is its displacement 
    ability - the creature appears to be several feet from where it actually is, creating 
    a blurred, shifting afterimage. The tentacles are 8 feet long and whip through the air. 
    Its eyes glow green with an alien intelligence. The six legs allow for incredible speed 
    and agility. The main body shows lean, powerful muscles. The creature is shown mid-leap, 
    its image displaced and duplicated showing where it appears to be versus where it is. 
    The tentacles are spread wide, spikes gleaming. Its mouth is open showing rows of teeth. 
    Photorealistic rendering with the displacement effect creating multiple overlapping images, 
    the alien six-legged form, and the deadly tentacles that make this predator unique.
    """,
    
    "Djinni": """
    A powerful air elemental being, 10 feet tall with blue-tinted skin and a muscular build. 
    The lower body transforms into a whirlwind of clouds and wind. The upper body is humanoid 
    with perfect musculature, adorned with golden jewelry - arm bands, earrings, and a turban 
    with a massive sapphire. The face is noble with a well-groomed beard and eyes that crackle 
    with lightning. Wisps of cloud constantly flow from its form. The djinni holds a massive 
    scimitar that gleams with magical power. Golden silk pants billow before transforming 
    into the whirlwind base. Lightning occasionally arcs across its body. The air around it 
    shimmers with heat distortion and small objects orbit in its wind. It hovers in a palace 
    of clouds with arabic architecture visible. Photorealistic rendering of the muscular form, 
    the transition from flesh to wind, and the overwhelming magical presence of this elemental 
    noble.
    """,
    
    "Doppelganger": """
    A shapeshifter shown in its true form - a gray-skinned humanoid with a featureless face 
    except for large, bulbous white eyes with no pupils. The body is thin and gangly with 
    elongated limbs. Its skin has a rubbery, unnatural texture. The creature is caught 
    mid-transformation, with parts of its body shifting between its true form and a human 
    disguise. One arm is gray and featureless while the other shows human skin forming. 
    The face is particularly disturbing - half blank gray flesh, half forming into a 
    specific person's features. Its fingers are too long with too many joints. The creature 
    wears simple dark clothing that shifts with its form. Standing in front of a mirror, 
    multiple reflections show different faces it has stolen. Photorealistic horror emphasizing 
    the uncanny valley effect, the disturbing transformation, and the paranoia of never 
    knowing who to trust.
    """,
    
    "Dragon Turtle": """
    A colossal sea monster combining dragon and turtle, 30 feet long with a shell 15 feet 
    across. The head is draconic with green scales, fierce golden eyes, and a mouth full 
    of sword-length teeth. Steam constantly rises from its nostrils. The shell is dark green 
    with golden patterns and covered in algae and barnacles from centuries in the ocean. 
    Four massive flippers end in webbed claws. The long tail ends in a rudder-like fin. 
    The creature breaches from ocean waves, water cascading off its shell. Its mouth is 
    open, about to release a blast of scalding steam. The shell shows battle scars and 
    harpoons still embedded from failed hunting attempts. Seaweed drapes from its form. 
    The neck extends showing the blend of turtle and dragon features. Photorealistic 
    rendering of wet scales, the massive shell, and the terrifying combination of dragon 
    power with turtle endurance in an aquatic nightmare.
    """
}

def main():
    """Generate portraits for Batch 3 monsters"""
    
    print("="*60)
    print("D&D MONSTER PORTRAIT GENERATOR - BATCH 3")
    print("="*60)
    print(f"\nGenerating {len(MONSTERS_BATCH_3)} monster portraits...")
    
    results = []
    
    for monster_name, description in MONSTERS_BATCH_3.items():
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
    print("BATCH 3 GENERATION COMPLETE")
    print("="*60)
    
    successful = [name for name, result in results if result["success"]]
    failed = [name for name, result in results if not result["success"]]
    
    print(f"\nSuccessful: {len(successful)}/{len(MONSTERS_BATCH_3)}")
    for name in successful:
        print(f"  - {name}")
    
    if failed:
        print(f"\nFailed: {len(failed)}")
        for name in failed:
            print(f"  - {name}")
    
    print(f"\nAll portraits saved in: monster_portraits/")

if __name__ == "__main__":
    main()