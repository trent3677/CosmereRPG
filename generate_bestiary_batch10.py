#!/usr/bin/env python3
"""
Generate D&D Monster Portraits - Batch 10 (Final Common SRD Monsters)
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

# BATCH 10: Final Common SRD Monsters with Detailed Prompts
MONSTERS_BATCH_10 = {
    "Rakshasa": """
    A fiendish shapeshifter appearing as a well-dressed humanoid with the disturbing 
    feature of backwards hands - palms where the backs should be. Its true head is that 
    of a tiger with intelligent, malevolent eyes. The rakshasa wears fine silk robes 
    and jewelry befitting nobility. Orange and black striped fur covers its tiger head 
    while the body appears human. Its backwards hands gesture in unnatural ways that 
    unsettle viewers. Sharp fangs show when it smiles. The creature stands in an opulent 
    palace setting, surrounded by illusions and luxury. Magic crackles around its reversed 
    hands. Its expression shows cruel intelligence and contempt for lesser beings. The 
    blend of tiger and human is both regal and wrong. Photorealistic rendering of the 
    shapeshifting fiend, the backwards hands, and the deceptive demon of desire.
    """,
    
    "Remorhaz": """
    A 30-foot long arctic predator resembling a massive centipede with a super-heated 
    body. Its segmented form is covered in white and blue chitinous plates, but its 
    back glows red-hot, melting snow and ice around it. The head features massive mandibles 
    and multiple eyes. Steam constantly rises from its heated segments. The creature 
    burrows through glaciers, its body heat creating tunnels. It emerges from ice and 
    snow, the contrast between its frozen environment and burning body creating clouds 
    of steam. Ice melts and refreezes around its form. The mandibles drip with caustic 
    saliva. Its many legs end in claws that grip ice. Photorealistic rendering of the 
    ice and fire paradox, the thermal predator, and the terror of the frozen wastes.
    """,
    
    "Roc": """
    A gargantuan eagle of legendary proportions, with a 200-foot wingspan and standing 
    30 feet tall. Its feathers are golden-brown with white tips, each primary feather 
    the size of a tree. The beak could swallow an elephant whole. Its talons are like 
    curved swords capable of carrying off whales. The roc perches on a mountain peak 
    that seems small beneath it, with entire trees visible as tiny shrubs far below. 
    Its eyes show the fierce intelligence of an apex predator. Wind from its wings creates 
    storms. The creature holds a mammoth in one talon like a mouse. Clouds part around 
    its massive form. Photorealistic rendering emphasizing the impossible scale, the 
    majesty, and the primal power of the largest bird in existence.
    """,
    
    "Rust Monster": """
    A bizarre insectoid creature the size of a large dog with a body covered in rusty-
    brown chitinous plates. Most distinctive are its two long, feathery antennae that 
    corrode metal on contact. The creature has four legs and a long tail ending in a 
    paddle-like protrusion. Its head features compound eyes and a mouth designed for 
    eating rust. The rust monster is shown approaching a terrified warrior, its antennae 
    reaching for the metal armor which already shows spots of rust spreading. Flakes 
    of corroded metal fall from its mouth. The creature's body has a metallic sheen from 
    its diet. It moves with insect-like quickness. Photorealistic detail showing the 
    unique threat to adventurers, the metal-eater, and the dungeon pest that destroys 
    equipment.
    """,
    
    "Sahuagin": """
    A 7-foot tall aquatic humanoid with the features of a predatory fish. Green scales 
    cover its muscular body, with a lighter belly and darker back. The head is fish-like 
    with large black eyes adapted for deep water, gill slits on the neck, and a mouth 
    full of needle-sharp teeth. Webbed hands and feet end in sharp claws. A fin runs 
    down its spine and tail. The sahuagin carries a trident and net, wearing minimal 
    armor made from shark hide and shells. It stands in shallow water in an underwater 
    cave, bioluminescent algae providing eerie light. Its expression shows cold predatory 
    intelligence. Scars from battles with other sea creatures mark its body. Photorealistic 
    rendering of the sea devil, the underwater raider, and the shark-like humanoid predator.
    """,
    
    "Salamander": """
    A 12-foot long creature from the Elemental Plane of Fire, with the upper body of a 
    muscular humanoid and the lower body of a snake, all wreathed in flames. Its skin 
    is like cooling lava - black with cracks showing molten fire beneath. The humanoid 
    portion wields a superheated metal spear that glows white-hot. Its eyes are pools 
    of liquid flame. The snake portion coils and uncoils, leaving scorch marks. Fire 
    constantly dances along its entire form. The salamander rises from a lava pool in 
    a volcanic forge, working metal with its bare hands. Heat distortion surrounds it. 
    Its expression shows the joy of creation through fire. Photorealistic rendering of 
    the fire elemental smith, the living forge, and the serpent of flame.
    """,
    
    "Satyr": """
    A fey creature with the upper body of a handsome human male and the legs of a goat. 
    Standing 5 feet tall with curly brown hair adorned with vine wreaths and small horns 
    protruding from the forehead. The human portion is lean and athletic with sun-bronzed 
    skin. From the waist down, brown fur covers digitigrade goat legs ending in cloven 
    hooves. The satyr plays pan pipes, its fingers dancing over the reeds. Its expression 
    is mischievous and lustful, with a perpetual smirk. It dances in a forest glade during 
    a celebration, wine jug nearby. Flowers bloom where its hooves touch. The blend between 
    human and goat is natural for this fey being. Photorealistic rendering of the party 
    animal, the fey musician, and the embodiment of wild celebration.
    """,
    
    "Shadow": """
    An undead creature of living darkness, vaguely humanoid in shape but made entirely 
    of animated shadow. Its form constantly shifts and wavers like smoke, with no definite 
    edges. Where eyes should be, two points of darker void seem to draw in light. The 
    shadow glides across surfaces, sometimes three-dimensional, sometimes flat against 
    walls. Its touch drains strength, leaving victims weak. The creature is shown reaching 
    out with elongated fingers of darkness, partly on a wall, partly standing free. Light 
    seems to bend away from it. Other shadows in the area seem drawn to it. Its presence 
    makes the area colder and darker. Photorealistic rendering of animated darkness, the 
    strength-draining undead, and the horror of one's shadow coming to life.
    """,
    
    "Shambling Mound": """
    A 9-foot tall mass of rotting vegetation animated into a vaguely humanoid form. 
    Composed of vines, moss, roots, and compost, constantly dripping with swamp water 
    and decay. Two arm-like appendages of tangled vines extend from the main mass. What 
    might be a head is just a denser collection of vegetation with two dim points of 
    light for eyes. The creature moves with a shuffling gait, leaving a trail of mulch. 
    Insects and small creatures live within its form. Mushrooms and flowers randomly 
    bloom and die on its surface. The shambling mound emerges from a swamp, algae and 
    pond scum draping from it. The smell of decay is almost visible. Photorealistic 
    rendering of animated plant matter, the swamp horror, and the compost heap come to 
    life.
    """,
    
    "Shield Guardian": """
    A 9-foot tall magical construct built to protect a specific master. Its body is made 
    of wood, metal, and stone combined into a humanoid form. The head is stylized and 
    expressionless with glowing eyes matching the amulet worn by its master. Runic symbols 
    cover its body, glowing when it absorbs spells meant for its ward. The guardian's 
    body shows master craftsmanship - articulated joints, reinforced plating, and magical 
    crystals at power points. It stands in eternal vigil, one arm extended as a shield, 
    the other ready to strike. Despite being a construct, there's something noble in its 
    bearing. It shows battle damage from protecting its master, each dent a badge of 
    service. Photorealistic rendering of the magical bodyguard, the constructed protector, 
    and the ultimate defensive companion.
    """,
    
    "Skeleton": """
    An animated human skeleton, yellowed bones held together by necromantic magic. Dark 
    energy glows in its empty eye sockets. The bones show signs of age - cracks, chips, 
    and weathering. It moves with unnatural precision, every motion mechanical. The skeleton 
    carries a rusty sword and wears the tattered remains of ancient armor. Its jaw hangs 
    open in a perpetual grin of death. The creature stands in a dark crypt, other skeletons 
    visible rising from their graves. Dust falls from its joints as it moves. Despite 
    having no muscles, it moves with surprising speed. The absence of flesh makes it more 
    terrifying, a reminder of mortality. Photorealistic rendering of animated bones, the 
    basic undead, and death's foot soldier.
    """,
    
    "Specter": """
    A translucent undead spirit of someone who died violently, bound to the material plane 
    by dark emotions. The specter appears as it did at the moment of death - wounds visible, 
    expression frozen in final terror or rage. Its form is ethereal, allowing the background 
    to show through. A pale blue-green glow emanates from it. The specter's touch passes 
    through armor to drain life force directly. It floats above the ground, tethered to 
    the site of its death. Ectoplasmic wisps trail from its form. Its mouth opens in a 
    silent scream of anguish. The area around it grows cold and lights dim. Photorealistic 
    rendering of ethereal undeath, the life-draining ghost, and the soul trapped by violence.
    """,
    
    "Sphinx": """
    A majestic creature with a human head on a lion's body and eagle wings. The gynosphinx 
    shown has the head of a beautiful woman with intelligence and wisdom in her eyes. Her 
    human features are perfectly proportioned with dark skin and Egyptian styling. The 
    lion body is powerful and golden, with muscles rippling beneath the fur. Eagle wings 
    spread 20 feet wide, each feather perfectly detailed. She reclines on ancient stone 
    steps before a temple, surrounded by hieroglyphs and riddles carved in stone. Her 
    expression is enigmatic, holding secrets of ages. A golden headdress adorns her human 
    head. The blend of human, lion, and eagle is seamless and divine. Photorealistic 
    rendering of the riddle-keeper, the guardian of mysteries, and the test of wisdom.
    """,
    
    "Stirge": """
    A flying pest the size of a housecat with a mosquito-like proboscis and bat wings. 
    Its body is covered in coarse fur with a rusty red color from dried blood. Four legs 
    end in sharp pincers for gripping victims. The wings are leathery and allow surprising 
    agility. Most disturbing is its proboscis - a foot-long needle designed to pierce 
    flesh and drain blood. Multiple stirges swarm together, attacking from above. Their 
    eyes glow red with hunger. The creatures are shown latched onto victims, their bodies 
    swelling with blood. The buzzing of their wings fills the air. Despite their small 
    size, they're terrifying in groups. Photorealistic detail of the blood-drinking pest, 
    the flying parasite, and the dungeon mosquito.
    """,
    
    "Stone Giant": """
    An 18-foot tall giant with skin like gray granite, perfectly adapted to mountain life. 
    Its features are carved and angular like a statue come to life. The giant's body is 
    lean and athletic rather than bulky, built for climbing and throwing. Its hair is 
    dark gray like slate. The giant wears simple clothing of stone-gray cloth and leather. 
    It carries perfectly balanced throwing rocks and a massive stone club. The creature 
    stands on a mountain ledge, blending with the rocky environment. Its expression is 
    stoic and contemplative. Despite its size, it moves with surprising grace. Stone dust 
    falls from its skin. Photorealistic rendering of the mountain giant, the stone-thrower, 
    and the reclusive artist of the peaks.
    """,
    
    "Stone Golem": """
    A 10-foot tall humanoid carved from a single block of stone, animated by powerful 
    magic. Its features are roughly hewn, giving it a primitive appearance. The golem's 
    body shows the chisel marks of its creation. Runes of power are carved into its chest 
    and forehead, glowing faintly. Its movements are slow but unstoppable. The massive 
    fists could pulverize bones. Cracks run through its body from age and battle, some 
    repaired with different colored stone. The golem stands guard in an ancient temple, 
    covered in dust and cobwebs from centuries of vigil. Its eyes are just indentations 
    that somehow convey awareness. Each step shakes the ground. Photorealistic rendering 
    of animated stone, the tireless guardian, and the strength of the earth given form.
    """,
    
    "Succubus": """
    A fiendish temptress appearing as a woman of supernatural beauty with demonic features. 
    Her skin is perfect alabaster or deep crimson, flawless and alluring. Bat-like wings 
    spread from her back, and small horns curve from her forehead. A spaded tail curves 
    behind her. Her eyes shift color based on her target's desires. She wears revealing 
    clothing that seems to be made of shadows and sin. Her expression promises pleasure 
    while hiding deadly intent. She stands in a boudoir of illusion, everything designed 
    to seduce. Despite her beauty, there's something fundamentally wrong - too perfect, 
    too alluring. Her smile shows slightly too-sharp teeth. Photorealistic rendering of 
    supernatural beauty, the corruptor through desire, and the demon of temptation.
    """,
    
    "Tarrasque": """
    The legendary 50-foot tall, 70-foot long titan of destruction. Its body combines the 
    worst aspects of dragon, dinosaur, and demon. Massive armored plates cover its back, 
    impervious to magic and weapons. The head is dragon-like with horns and a mouth that 
    could swallow buildings. Six legs like tree trunks end in claws that crack stone. 
    A massive tail can level city walls. The tarrasque rampages through a city, buildings 
    crumbling beneath it. Its roar shatters glass for miles. The creature is shown at the 
    moment of emerging from underground, the earth exploding around it. Its eyes burn with 
    mindless hunger. This is destruction incarnate, the ender of civilizations. Photorealistic 
    rendering emphasizing the impossible scale, the unstoppable force, and the ultimate 
    monster of legend.
    """,
    
    "Treant": """
    A 30-foot tall animated oak tree with a vaguely humanoid shape. Its trunk forms the 
    body with a wise, ancient face in the bark. Branch-arms can manipulate objects or 
    strike with crushing force. The roots form legs that can plant into earth or walk. 
    Leaves crown its head like hair, changing with seasons. Birds and squirrels live in 
    its branches. Moss and vines drape from its form. The treant stands in an ancient 
    forest it protects, other trees seeming to lean toward it in reverence. Its expression 
    shows centuries of wisdom and patience. When it moves, the ground trembles and leaves 
    fall like rain. Despite being wood, it's impossibly alive and aware. Photorealistic 
    rendering of the forest guardian, the animated tree, and the protector of nature.
    """,
    
    "Troll": """
    A 9-foot tall giant with rubbery green skin, long gangly limbs, and the disturbing 
    ability to regenerate from almost any wound. Its body is thin but wiry with unnatural 
    strength. The face is hideous with a long warty nose, small eyes, and a mouth full of 
    jagged teeth. Coarse black hair hangs in greasy strands. Its fingers and toes end in 
    black claws. The troll's most terrifying feature is visible regeneration - wounds 
    closing, severed parts regrowing. It wears minimal clothing of uncured hides. The 
    creature stands in its lair under a bridge, bones scattered about. Its skin shows 
    countless scars that healed wrong. The expression is both stupid and cunning. Only 
    fire stops its regeneration, making it nearly unkillable. Photorealistic rendering 
    of the regenerating horror, the bridge guardian, and the monster that won't stay dead.
    """,
    
    "Vampire": """
    An undead predator that appears as an aristocratic human of haunting beauty but with 
    subtle wrongness. Pale skin like marble, too perfect to be alive. Eyes that shift from 
    normal to red when hungry. Fangs that extend when feeding. The vampire wears fine 
    clothing from its era, immaculate despite age. No reflection appears in mirrors behind 
    it. It stands in a gothic castle chamber, moonlight streaming through windows but not 
    touching it. Shadows seem to gather around its form. Its expression shows predatory 
    charm and ancient intelligence. A wine glass of blood sits nearby. Bats gather in the 
    rafters above. Despite its beauty, there's a corpse-like stillness when it doesn't 
    consciously move. Photorealistic rendering of undead nobility, the blood drinker, and 
    the seductive predator of the night.
    """,
    
    "Water Elemental": """
    A 12-foot tall vortex of living water in a vaguely humanoid shape. Its body is pure 
    liquid, constantly flowing and reshaping. Light refracts through its form creating 
    rainbow effects. Two whirlpools serve as eyes. Arms of compressed water extend from 
    the main mass. The elemental can shift from calm pool to raging torrent instantly. 
    Fish and debris swirl within its body. It rises from a river, water constantly cycling 
    through its form. Waves and currents are visible within. Droplets constantly break 
    away and return. The sound of rushing water accompanies its movements. Photorealistic 
    rendering of living water, the fluid warrior, and the consciousness of the sea.
    """,
    
    "Wight": """
    An undead warrior raised from death to serve evil, retaining its intelligence and 
    martial skill. The wight appears as a desiccated corpse in ancient armor, skin pulled 
    tight over bones. Its eyes burn with blue flame. Unlike zombies, it moves with deadly 
    precision and tactical awareness. The creature wears the armor it died in, now rusted 
    and damaged. It wields weapons with remembered skill. The wight's touch drains life 
    energy, creating new undead servants. It stands in a barrow tomb, surrounded by lesser 
    undead it commands. Its expression shows malevolent intelligence and hatred for the 
    living. Cold radiates from its form. Photorealistic rendering of the undead commander, 
    the life-draining warrior, and death's general.
    """,
    
    "Wraith": """
    An incorporeal undead of pure darkness and negative energy. The wraith appears as a 
    hovering shadow in a tattered black robe, with no visible body within. Red points of 
    light burn where eyes should be. Its form constantly shifts between solid-looking and 
    completely ethereal. The wraith passes through walls and armor, its touch draining 
    life force directly from the soul. It hovers in a darkened chamber, other shadows 
    seeming to reach toward it. Light dims in its presence. Frost forms on nearby surfaces. 
    Its mere presence causes despair. The creature exists partially in the Shadowfell, 
    making it hard to truly destroy. Photorealistic rendering of incorporeal evil, the 
    soul-drainer, and the shadow of death itself.
    """,
    
    "Wyvern": """
    A dragon-like creature but with only two legs and a venomous stinger tail. Standing 
    15 feet long with a 20-foot wingspan, its scales are dark green to brown. The head 
    is draconic but more bestial, lacking a true dragon's intelligence. Its wings are 
    its primary limbs when on ground, folding to walk on wing-knuckles. The tail is its 
    most dangerous feature - long and flexible ending in a scorpion-like stinger dripping 
    venom. The wyvern perches on a cliff, wings spread for balance. Its mouth shows rows 
    of teeth but no breath weapon. The creature is more animal than intelligent, a lesser 
    cousin to true dragons. Scars show territorial battles. Photorealistic rendering of 
    the two-legged dragon, the venomous flyer, and the mount of evil riders.
    """,
    
    "Zombie": """
    A reanimated corpse in various stages of decay, moving with jerky, unnatural motions. 
    Its skin is gray-green with patches missing, showing muscle and bone beneath. The eyes 
    are clouded white, unseeing but somehow aware. Its clothes are whatever it died in, 
    now tattered and stained. The zombie moves relentlessly forward, arms outstretched, 
    seeking living flesh. Wounds that killed it are still visible. It shows no emotion, 
    no pain, no fatigue. Multiple zombies shamble together in a mindless horde. The smell 
    of decay surrounds them. Flies buzz around their forms. Despite slowness, their 
    relentlessness makes them terrifying. Photorealistic rendering of the walking dead, 
    the mindless undead, and the horror of corpses that won't stay buried.
    """
}

def main():
    """Generate portraits for Batch 10 monsters"""
    
    print("="*60)
    print("D&D MONSTER PORTRAIT GENERATOR - BATCH 10 (FINAL)")
    print("="*60)
    print(f"\nGenerating {len(MONSTERS_BATCH_10)} monster portraits...")
    
    results = []
    
    for monster_name, description in MONSTERS_BATCH_10.items():
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
    print("BATCH 10 GENERATION COMPLETE")
    print("="*60)
    
    successful = [name for name, result in results if result["success"]]
    failed = [name for name, result in results if not result["success"]]
    
    print(f"\nSuccessful: {len(successful)}/{len(MONSTERS_BATCH_10)}")
    for name in successful:
        print(f"  - {name}")
    
    if failed:
        print(f"\nFailed: {len(failed)}")
        for name in failed:
            print(f"  - {name}")
    
    print(f"\nAll portraits saved in: monster_portraits/")
    print("\n" + "="*60)
    print("COMPLETE BESTIARY GENERATION FINISHED!")
    print("="*60)

if __name__ == "__main__":
    main()