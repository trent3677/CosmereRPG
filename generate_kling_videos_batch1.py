#!/usr/bin/env python3
"""
Generate Kling AI video prompts for D&D Monster Portraits - Batch 1
Checks for existing images and creates 5-second video prompts for Kling 2.1
"""

import os
import glob
from datetime import datetime

# Directory where monster portraits are saved
PORTRAIT_DIR = "monster_portraits"
VIDEO_DIR = "monster_videos"

# Batch 1 Monsters with Kling AI Video Prompts
KLING_PROMPTS_BATCH_1 = {
    "Aboleth": """Ancient fish-like horror floating in dark underwater cavern, its three red eyes pulsing with alien intelligence. Four massive tentacles writhe and coil through murky water, dripping thick mucus. The creature's rubbery gray-green skin glistens as bioluminescent fungi cast eerie light across its bulk. It moves forward slowly, tentacles reaching toward viewer, mouth opening to reveal rows of needle teeth. Water ripples around its massive form. Photorealistic detail with smooth consistent motion, underwater lighting effects, and overwhelming sense of ancient alien menace.""",
    
    "Adult Black Dragon": """Massive black dragon emerging from fetid swamp water, acidic green vapor hissing from its jaws and dissolving the ground beneath. Its obsidian scales gleam with dark purple highlights as it spreads its 80-foot wingspan. The dragon rears up, skull-like head with forward-swept horns raised high, mouth opening wide as acid builds in its throat. Dead trees crack under its weight, bones scatter. Photorealistic detail with smooth consistent motion, realistic acid effects, and terrifying draconic power.""",
    
    "Adult Blue Dragon": """Colossal blue dragon atop desert mesa during lightning storm, electricity crackling between its massive horn and frilled ears. Its sapphire scales shimmer as it spreads its 100-foot wingspan wide. The dragon's mouth opens revealing sword-like teeth as lightning builds in its throat. Sand swirls in cyclones around its claws, lightning courses through wing membranes. The tail blade sweeps menacingly. Photorealistic detail with smooth consistent motion, dynamic lightning effects, and overwhelming elemental fury.""",
    
    "Adult Red Dragon": """Titanic red dragon perched on volcanic mountain, smoke and embers constantly rising from its ruby-scaled body. The dragon spreads its 120-foot wingspan casting enormous shadows as lava flows below. Its mouth opens in mighty roar, showing massive fangs with inferno building in throat. Heat distortion ripples around its form, volcanic fire backlights the scene. Wings beat once sending waves of superheated air. Photorealistic detail with smooth consistent motion, realistic fire effects, and legendary draconic presence.""",
    
    "Air Elemental": """Swirling tornado of living wind rising from ground, debris and leaves caught in its vortex making its shape visible. Lightning flashes within cloudy form as two brilliant white points of light serve as eyes. The cyclone arms extend and retract, whirling at different speeds. Dust devils spin off from main body. The elemental surges forward, growing taller, air pressure changes visible as ripples. Photorealistic detail with smooth consistent motion, realistic wind effects, and raw power of unleashed storm.""",
    
    "Ankheg": """Monstrous insectoid predator erupting from underground tunnel, dirt cascading off brown and yellow chitinous armor. Its massive mandibles spread wide, dripping acidic green fluid that sizzles on ground. Six serrated legs scramble for purchase as it emerges. Compound eyes with hundreds of facets reflect light in alien manner. Antennae twitch sensing vibrations. The creature lurches forward aggressively. Photorealistic detail with smooth consistent motion, realistic acid effects, and predatory insectoid horror.""",
    
    "Banshee": """Translucent elven spirit floating above graveyard ground, long white hair flowing as if underwater. Her gaunt skeletal face with glowing blue eyes opens in endless silent scream. Tattered gown billows around ghostly form, ectoplasmic wisps trailing behind. She drifts forward, elongated claw fingers reaching desperately. Blue-white glow intensifies, tombstones visible through translucent body. Photorealistic detail with smooth consistent motion, ethereal transparency effects, and overwhelming supernatural anguish.""",
    
    "Basilisk": """Eight-legged reptilian monster advancing with unsettling spider-like gait, dark green scales with brown mottling. Its pale yellow eyes glow with sickly light - the deadly gaze that turns victims to stone. The creature's broad flat head sways as it moves, crown of small horns catching light. Mouth opens slightly showing rows of sharp teeth. Behind it, partially petrified victims frozen mid-scream. Heavy tail drags leaving furrows. Photorealistic detail with smooth consistent motion, hypnotic eye glow, and deadly reptilian menace.""",
    
    "Behir": """Massive 40-foot serpentine monster undulating forward, brilliant blue scales crackling with electrical energy. Lightning arcs between its two curved horns and courses down entire length. Twelve legs move in rippling sequence allowing shocking speed. The dragon-like head rears up, mouth opening as electrical breath weapon builds, throat glowing blue-white. Electricity arcs to nearby surfaces. The creature coils and strikes with serpentine grace. Photorealistic detail with smooth consistent motion, dynamic lightning effects, and unique horror of snake with legs.""",
    
    "Beholder": """Floating spherical aberration hovering forward, massive central eye projecting antimagic cone. Ten eyestalks writhe like serpents atop sphere, each different colored eye tracking independently - red, green, blue, yellow rays ready to fire. Massive mouth below central eye opens showing hundreds of needle teeth. The creature rotates slowly, paranoid gaze sweeping area. Chitinous purple hide pulses with veins. Drool drips from maw. Photorealistic detail with smooth consistent motion, multiple independent eye movements, and overwhelming alien paranoia."""
}

def check_image_exists(monster_name):
    """Check if an image exists for the given monster"""
    safe_name = monster_name.lower().replace(" ", "_").replace("-", "_")
    pattern = os.path.join(PORTRAIT_DIR, f"{safe_name}_*.png")
    matches = glob.glob(pattern)
    
    if matches:
        # Return the most recent image
        matches.sort()
        return matches[-1]
    return None

def save_kling_prompt(monster_name, prompt, image_path):
    """Save Kling prompt to a text file for easy copying"""
    os.makedirs("kling_prompts", exist_ok=True)
    safe_name = monster_name.lower().replace(" ", "_").replace("-", "_")
    
    output_file = f"kling_prompts/{safe_name}_kling_prompt.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"MONSTER: {monster_name}\n")
        f.write(f"IMAGE: {image_path}\n")
        f.write(f"{'='*60}\n\n")
        f.write("KLING AI PROMPT:\n")
        f.write(prompt)
        f.write("\n\n")
        f.write("SETTINGS:\n")
        f.write("- Model: Kling 2.1\n")
        f.write("- Duration: 5 seconds\n")
        f.write("- Mode: Image-to-Video\n")
    
    return output_file

def main():
    """Process Batch 1 monsters for Kling video generation"""
    
    print("="*60)
    print("KLING AI VIDEO PROMPT GENERATOR - BATCH 1")
    print("="*60)
    print(f"\nChecking for existing images and generating prompts...\n")
    
    found_count = 0
    missing_count = 0
    
    results = []
    
    for monster_name, kling_prompt in KLING_PROMPTS_BATCH_1.items():
        image_path = check_image_exists(monster_name)
        
        if image_path:
            found_count += 1
            prompt_file = save_kling_prompt(monster_name, kling_prompt, image_path)
            print(f"[FOUND] {monster_name}")
            print(f"  Image: {image_path}")
            print(f"  Prompt saved: {prompt_file}")
            results.append((monster_name, "Found", image_path))
        else:
            missing_count += 1
            print(f"[MISSING] {monster_name} - No image found, skipping")
            results.append((monster_name, "Missing", None))
    
    # Generate batch summary
    print("\n" + "="*60)
    print("BATCH 1 SUMMARY")
    print("="*60)
    print(f"\nTotal monsters: {len(KLING_PROMPTS_BATCH_1)}")
    print(f"Images found: {found_count}")
    print(f"Images missing: {missing_count}")
    
    if found_count > 0:
        print("\n" + "="*60)
        print("READY FOR KLING AI")
        print("="*60)
        print("\nNext steps:")
        print("1. Open each image in Kling AI")
        print("2. Copy the corresponding prompt from kling_prompts/ folder")
        print("3. Generate 5-second video with Kling 2.1")
        print("4. Save videos to monster_videos/ folder")
    
    # Save batch report
    report_file = f"kling_prompts/batch1_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write("BATCH 1 KLING PROMPT GENERATION REPORT\n")
        f.write("="*60 + "\n\n")
        for name, status, path in results:
            f.write(f"{name}: {status}")
            if path:
                f.write(f" - {path}")
            f.write("\n")
        f.write(f"\nTotal: {len(results)}, Found: {found_count}, Missing: {missing_count}\n")
    
    print(f"\nReport saved: {report_file}")

if __name__ == "__main__":
    main()