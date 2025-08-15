#!/usr/bin/env python3
"""
Generate D&D Monster Portraits - Batch 2 (Monsters 11-20)
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

# BATCH 2: Monsters 11-20 with Detailed Prompts
MONSTERS_BATCH_2 = {
    "Black Pudding": """
    A massive amorphous blob of living acid, 15 feet across and 2 feet thick, resembling 
    tar come to life. Its surface is glossy black and constantly rippling with internal 
    movement. The ooze has no features except for the disturbing way it moves with purpose. 
    Its surface occasionally bubbles and pops, releasing wisps of acidic vapor. Where it 
    touches stone floor, the rock dissolves and smokes. Bits of half-dissolved armor, bones, 
    and weapons are visible suspended within its translucent black mass. The creature is 
    shown spreading across a dungeon corridor, squeezing under a door and dissolving the 
    metal hinges. Its body reflects torchlight with an oily rainbow sheen. The edges of 
    the pudding show pseudopods forming and retracting as it moves. Photorealistic rendering 
    emphasizing the viscous, liquid nature of the creature, the way light plays on its 
    surface, and the horrifying implication of a thinking, hunting pool of acid.
    """,
    
    "Bone Devil": """
    A 9-foot tall skeletal fiend with dried, mummified flesh stretched over its bones. 
    Its skull-like head features glowing red eyes and a fanged maw. Most distinctive is 
    its long, scorpion-like tail ending in a venomous stinger dripping with green poison. 
    The devil's body is humanoid but emaciated, ribs visible through papery skin. Four 
    arms extend from its torso, each ending in razor-sharp claws. Tattered wings of skin 
    and bone spread from its back. The creature stands in a hellish landscape of brimstone 
    and flame. Its bones show through translucent flesh, creating a horrifying skeletal 
    appearance while still being covered in skin. Chains and hooks dangle from its body. 
    The tail arches over its head like a scorpion, stinger poised to strike. Hellfire 
    reflects off its pale flesh. Photorealistic detail showing the texture of dried flesh, 
    exposed bone, and the sadistic intelligence burning in its eyes.
    """,
    
    "Bugbear": """
    A massive 7-foot tall goblinoid brute with the features of a bear and goblin combined. 
    Thick, matted brown fur covers its muscular body. Its face is bestial with a pronounced 
    snout, sharp yellowed teeth, and small cruel eyes that gleam with cunning. Large pointed 
    ears stick up through tangled hair. The bugbear's arms are disproportionately long, 
    reaching nearly to its knees, ending in massive hands with dirty claws. It wears 
    piecemeal armor of leather and chain, with various weapons hanging from its belt. 
    The creature stands in ambush position behind dungeon pillars, its stealth belying 
    its size. Scars crisscross its exposed skin. A massive morningstar is gripped in one 
    hand. Despite its bulk, there's a predatory grace to its posture. Photorealistic 
    rendering showing the coarse fur texture, the blend of bear and goblinoid features, 
    and the surprising stealth of this brutal ambush predator.
    """,
    
    "Bulette": """
    A massive armored predator known as a land shark, 10 feet tall and 15 feet long. 
    Its body is covered in thick, overlapping plates of blue-gray armor that can deflect 
    swords. The head is wedge-shaped with a massive jaw filled with rows of triangular teeth. 
    Four powerful legs with enormous claws are built for digging through solid rock. 
    A distinctive dorsal fin of armored plates runs along its back. The creature is shown 
    erupting from underground, dirt and rocks flying everywhere, mouth open to reveal 
    its terrifying array of teeth. Its small, beady black eyes show primitive hunger. 
    The armor plates have scratches and battle damage from years of tunneling. Muscles 
    bulge beneath the armored hide. Its front claws are extended, each the size of swords. 
    Photorealistic detail emphasizing the tank-like armor, the powerful musculature, and 
    the terrifying moment of a bulette breaching from underground like a nightmare shark.
    """,
    
    "Centaur": """
    A noble creature with the upper body of a athletic human warrior and the lower body 
    of a powerful horse. Standing 7 feet tall at the human head, with the horse body 
    adding another 4 feet of height at the withers. The human torso is muscular and 
    sun-bronzed, with long flowing hair adorned with feathers and beads. The horse body 
    is a glossy chestnut brown with white markings on the legs. The centaur holds a 
    masterfully crafted longbow with arrows in a quiver across the human back. Leather 
    bracers protect the human arms. The horse body shows defined muscles beneath the 
    gleaming coat. The centaur stands in a forest clearing, one front hoof pawing the 
    ground. The face shows wisdom and nobility with intense eyes scanning for danger. 
    The blend between human and horse is seamless and natural. Photorealistic rendering 
    capturing both the wild, free nature of the horse and the intelligence and dignity 
    of the human portion.
    """,
    
    "Chimera": """
    A terrifying amalgamation of three creatures - lion, goat, and dragon. The main body 
    is that of a massive lion, 12 feet long with golden-brown fur and rippling muscles. 
    From the center of its back sprouts a goat's head on a long neck, with curved horns 
    and horizontal pupils filled with madness. The tail is replaced by a living dragon's 
    head, scales of deep red, constantly hissing and dripping with acidic saliva. 
    The lion head roars with triple rows of teeth. Dragon wings spread from the shoulders, 
    membrane stretched between bone fingers. All three heads are alert and aggressive, 
    each moving independently. The creature stands on a rocky outcrop, wings spread wide. 
    Fire flickers in the dragon head's throat while the goat head bleats unnaturally. 
    The lion's mane flows in the wind. Each part of the creature is perfectly detailed 
    yet wrongly fused together. Photorealistic horror showing the unnatural fusion of 
    three predators into one monstrous form.
    """,
    
    "Clay Golem": """
    A 8-foot tall humanoid figure sculpted from dark clay, its surface showing the texture 
    of worked earth. The golem's features are roughly formed - a basic humanoid shape with 
    thick limbs and a featureless face except for two glowing indentations for eyes. 
    Ancient Hebrew runes are carved into its forehead and chest, glowing with soft golden 
    light. Its massive fists are the size of anvils. The clay shows fingerprints and tool 
    marks from its creation. Cracks run through its body, some repaired with fresh clay. 
    The golem moves with surprising speed despite its bulk. It stands in an ancient workshop 
    surrounded by potter's tools and mystical symbols. Its surface is uneven, showing both 
    smooth and rough textures. Dust falls from its joints as it moves. Photorealistic 
    rendering emphasizing the earthen texture, the mystical runes, and the uncanny valley 
    effect of something humanoid but clearly not alive.
    """,
    
    "Cloaker": """
    A bizarre aberration resembling a massive manta ray made of living shadow, 12 feet 
    across. Its body is a black leathery cloak with a texture like bat wings. The underside 
    reveals a horrific face with glowing red eyes and rows of needle teeth in a vertical 
    maw. Its wing-like body has barbed edges and a long whip-like tail ending in a stinger. 
    The creature is shown attached to a dungeon ceiling, spreading its wings to drop on 
    unsuspecting prey. When spread, it perfectly mimics a black cloak hanging on a wall. 
    The edges of its body undulate hypnotically. Bone-white claws extend from what would 
    be the cloak's shoulders. Its mouth splits open impossibly wide showing multiple rows 
    of teeth. The texture shows both the leather-like quality and the living flesh beneath. 
    Photorealistic rendering capturing the disturbing blend of clothing and creature, 
    the perfect camouflage, and the moment of horrible revelation when it attacks.
    """,
    
    "Cockatrice": """
    A disturbing hybrid of rooster and dragon, the size of a large turkey but infinitely 
    more dangerous. Its body is that of a golden-feathered rooster with scales instead 
    of feathers on its belly and legs. The wings are leathery like a bat's but edged 
    with colorful feathers. The rooster head has a bright red crest and wattles, but 
    the eyes glow with supernatural menace. Most terrifying is its tail - a long, scaled 
    serpent ending in a barbed stinger. The creature's touch turns victims to stone. 
    It stands among several petrified victims - a warrior frozen mid-swing, a rat turned 
    to granite. Its beak is open in an aggressive crow. The scaled portions shimmer 
    with an iridescent sheen. Its talons are razor sharp. The blend of bird and reptile 
    is seamless yet wrong. Photorealistic detail showing individual feathers transitioning 
    to scales, the deadly grace of its movements, and the supernatural threat it poses.
    """,
    
    "Couatl": """
    A magnificent feathered serpent, 12 feet long with brilliantly colored plumage. 
    Its serpentine body is covered in scales that shimmer with rainbow iridescence, 
    while magnificent wings of tropical bird feathers spread 15 feet wide. The feathers 
    are brilliant emerald green, sapphire blue, and gold. The head is serpentine but 
    noble, with intelligent golden eyes showing ancient wisdom. A crown of longer feathers 
    adorns its head like a headdress. The creature radiates divine light, with a subtle 
    golden aura surrounding its form. It hovers in a jungle temple, sunlight streaming 
    through ancient stone windows highlighting its colors. Its wings move gracefully, 
    each feather perfectly defined. The scales catch light like precious gems. Its 
    expression is benevolent but powerful. Photorealistic rendering emphasizing the 
    brilliant colors, the divine nature of the creature, and the seamless blend of 
    serpent and bird into something transcendent.
    """
}

def main():
    """Generate portraits for Batch 2 monsters"""
    
    print("="*60)
    print("D&D MONSTER PORTRAIT GENERATOR - BATCH 2")
    print("="*60)
    print(f"\nGenerating {len(MONSTERS_BATCH_2)} monster portraits...")
    
    results = []
    
    for monster_name, description in MONSTERS_BATCH_2.items():
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
    print("BATCH 2 GENERATION COMPLETE")
    print("="*60)
    
    successful = [name for name, result in results if result["success"]]
    failed = [name for name, result in results if not result["success"]]
    
    print(f"\nSuccessful: {len(successful)}/{len(MONSTERS_BATCH_2)}")
    for name in successful:
        print(f"  - {name}")
    
    if failed:
        print(f"\nFailed: {len(failed)}")
        for name in failed:
            print(f"  - {name}")
    
    print(f"\nAll portraits saved in: monster_portraits/")

if __name__ == "__main__":
    main()