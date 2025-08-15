#!/usr/bin/env python3
"""
Generate D&D Monster Portraits - Batch 6 (Monsters 51-60)
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

# BATCH 6: Monsters 51-60 with Detailed Prompts
MONSTERS_BATCH_6 = {
    "Gold Dragon": """
    The most majestic of all dragons, 20 feet tall with scales like liquid gold that shimmer 
    with inner light. Each scale is perfectly formed, creating an armor of precious metal. 
    Its head is noble and wise with backward-swept horns like a crown. Golden whiskers flow 
    from its snout like those of an oriental dragon. Eyes of molten gold show ancient wisdom 
    and benevolence. The dragon's wings spread 120 feet, membrane glowing with golden 
    translucence when backlit. Its body is perfectly proportioned, showing immense power 
    with graceful lines. The dragon stands on a mountain peak at sunrise, golden light 
    making its scales blaze like the sun itself. Clouds part around its form. Its expression 
    is serene but powerful. A faint aura of divine light surrounds it. Photorealistic 
    rendering capturing the ultimate majesty, the divine nature, and the overwhelming 
    presence of the most powerful force for good.
    """,
    
    "Gorgon": """
    A massive bull-like creature 8 feet tall and 12 feet long, but covered entirely in 
    metal plates instead of hide. Its body is made of dark iron that shows rust in places 
    like blood. The head is bovine but more angular, with glowing red eyes and metal horns. 
    Most terrifying is its breath - a green poisonous cloud that turns living creatures 
    to stone. Its hooves strike sparks on stone. The metal plates shift and grind as it 
    moves, creating an awful sound. Steam rises from its nostrils. The gorgon stands among 
    the petrified statues of its victims - warriors frozen mid-charge, their faces showing 
    final terror. Its mouth is open, releasing the deadly green vapor. Muscles of iron 
    cable are visible between the plates. Photorealistic rendering of living metal, the 
    mechanical bull horror, and the deadly petrification it brings.
    """,
    
    "Gray Ooze": """
    A 10-foot wide puddle of thick gray slime that looks like wet cement come to life. 
    Its surface constantly ripples and bubbles as it moves with surprising speed. The ooze 
    is semi-transparent, showing partially dissolved metal and organic matter within its 
    mass. Where it touches metal, the material corrodes and dissolves instantly, creating 
    wisps of acidic smoke. The creature has no features, just an amorphous mass of gray 
    death. It spreads across dungeon stones, seeping through cracks. The surface has an 
    oily sheen that reflects torchlight. Bones float within it at various stages of 
    dissolution. The ooze leaves a trail of corroded stone behind it. Photorealistic 
    rendering of viscous slime, the corrosive nature, and the mindless hunger of this 
    dungeon hazard.
    """,
    
    "Green Hag": """
    A hideous crone standing 6 feet tall with sickly green skin like pond scum. Her face 
    is a nightmare of warts, boils, and twisted features with one eye larger than the other. 
    Stringy black hair like seaweed hangs to her waist, dripping with swamp water. Her 
    fingers are elongated with black claws like iron. She wears tattered robes of moss 
    and marsh plants. Her mouth shows blackened teeth with gaps, and her breath is visible 
    as toxic green vapor. The hag stands in her swamp lair, surrounded by hanging skulls 
    and bottled horrors. Her hunched back gives her a predatory stance. Leeches and bog 
    worms crawl on her skin. Her orange eyes glow with malevolent intelligence and cruel 
    humor. Photorealistic rendering of the corrupted fey, the swamp witch aesthetic, and 
    the supernatural evil of hag-kind.
    """,
    
    "Griffon": """
    A magnificent creature with the head and wings of a golden eagle and the body of a lion. 
    Standing 8 feet tall at the shoulder with a 25-foot wingspan. The eagle head is noble 
    with fierce golden eyes and a sharp curved beak. Golden-brown feathers cover the head, 
    neck, and wings. The lion body is muscular with tawny fur and powerful legs ending in 
    both talons (front) and paws (rear). The creature perches on a mountain cliff, wings 
    partially spread for balance. Its feathers and fur ripple in mountain winds. The tail 
    is leonine with a tuft at the end. Pride and nobility radiate from its bearing. The 
    blend between bird and beast is seamless and natural. Sunlight catches on its feathers 
    creating golden highlights. Photorealistic detail showing the perfect fusion of eagle 
    and lion, the majestic bearing, and the power of this legendary guardian.
    """,
    
    "Grimlock": """
    A 5-foot tall humanoid that evolved in absolute darkness, with gray, almost translucent 
    skin. Most disturbing is its face - where eyes should be, there's only smooth skin. 
    The nose is almost nonexistent, just two small slits. Its ears are enlarged and constantly 
    moving. The mouth is wide with sharp teeth adapted for raw meat. Its body is muscular 
    but hunched from living in caves. Long arms end in powerful hands with thick fingers. 
    The grimlock uses echolocation, its head constantly tilting to listen. It wears crude 
    hide clothing and carries a stone axe. The creature stands in complete darkness, yet 
    moves with confidence. Its skin shows a network of visible veins. The blank face where 
    eyes should be is deeply unsettling. Photorealistic rendering of the blind cave dweller, 
    the evolutionary adaptation to darkness, and the primal horror of the eyeless.
    """,
    
    "Half-Dragon": """
    A humanoid warrior with draconic features, standing 7 feet tall. Half the body shows 
    human characteristics while dragon traits dominate the other - scales cover portions 
    of skin, transitioning from flesh to scales. One eye is human, the other reptilian 
    with a vertical pupil. Small horns protrude from the skull. Wings capable of flight 
    spread from the back. The skin shifts from human tones to colored scales (red, blue, 
    green, black, or gold depending on dragon ancestry). Sharp teeth and an elongated face 
    show the dragon heritage. Clawed hands grip a sword with expertise. The half-dragon 
    wears armor modified for its wings and tail. Its expression shows both human intelligence 
    and draconic pride. A tail extends behind for balance. Photorealistic rendering of the 
    hybrid nature, the blend of human and dragon, and the power of draconic bloodline.
    """,
    
    "Harpy": """
    A vile creature with the upper body of a haggard woman and the lower body, wings, and 
    talons of a vulture. Standing 6 feet tall with a 10-foot wingspan of dirty, molting 
    feathers. The human portion is filthy with matted hair, cruel features, and arms that 
    end in wing joints. The face shows a horrible beauty, alluring yet repulsive. Its mouth 
    opens to reveal sharp teeth and to emit its enchanting song. The bird portions are 
    those of a carrion bird - dark feathers, powerful talons caked with dried blood. 
    The harpy perches on a rocky outcrop littered with bones. Its feathers are ragged 
    and missing in patches. Flies buzz around it. The blend between human and bird is 
    grotesque. Its expression shows hunger and cruelty. Photorealistic rendering of the 
    cursed fusion, the corrupted beauty, and the deadly song of the harpy.
    """,
    
    "Hell Hound": """
    A massive 5-foot tall dog from the infernal planes, with coal-black fur that smolders 
    and smokes. Its eyes burn with orange-red fire. The mouth glows from within with hellfire, 
    and when it barks, flames shoot forth. The body is powerfully muscled like a mastiff 
    but larger and more menacing. Its fur appears to be made of shadow and smoke. Claws 
    of obsidian click on stone. The hell hound's breath creates heat distortion in the air. 
    It stands at the gates of a hellish fortress, chains of red-hot iron around its neck. 
    The ground beneath its paws shows scorch marks. Its teeth are like white-hot metal. 
    An aura of sulfur and brimstone surrounds it. Photorealistic rendering of the infernal 
    canine, the living fire within, and the loyal guardian of the damned.
    """,
    
    "Hill Giant": """
    A 16-foot tall giant with a bulbous, misshapen head and a slovenly appearance. Its skin 
    is ruddy brown and covered in dirt, scars, and crude tattoos. The face is stupid and 
    cruel with small, deep-set eyes, a bulbous nose, and thick lips. Its body is massively 
    fat but with powerful muscles beneath. The giant wears rough hides and furs, poorly 
    stitched together. A massive wooden club reinforced with metal bands is its weapon. 
    Its hair is greasy and unkempt. The giant stands in its crude hill fort made of 
    boulders and logs. Bones and refuse litter the ground. Its expression shows dim 
    intelligence and constant hunger. Flies circle its unwashed form. The hands are 
    massive and dirty with broken nails. Photorealistic detail showing the slovenly nature, 
    the crude strength, and the bullying mentality of the weakest true giant.
    """
}

def main():
    """Generate portraits for Batch 6 monsters"""
    
    print("="*60)
    print("D&D MONSTER PORTRAIT GENERATOR - BATCH 6")
    print("="*60)
    print(f"\nGenerating {len(MONSTERS_BATCH_6)} monster portraits...")
    
    results = []
    
    for monster_name, description in MONSTERS_BATCH_6.items():
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
    print("BATCH 6 GENERATION COMPLETE")
    print("="*60)
    
    successful = [name for name, result in results if result["success"]]
    failed = [name for name, result in results if not result["success"]]
    
    print(f"\nSuccessful: {len(successful)}/{len(MONSTERS_BATCH_6)}")
    for name in successful:
        print(f"  - {name}")
    
    if failed:
        print(f"\nFailed: {len(failed)}")
        for name in failed:
            print(f"  - {name}")
    
    print(f"\nAll portraits saved in: monster_portraits/")

if __name__ == "__main__":
    main()