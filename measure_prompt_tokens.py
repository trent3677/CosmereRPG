#!/usr/bin/env python3
"""
Measure the token count of the extracted prompts
"""

import tiktoken

def count_tokens(text, model="gpt-4"):
    """Count tokens using tiktoken."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def main():
    print("=" * 60)
    print("PROMPT TOKEN ANALYSIS")
    print("=" * 60)
    
    # Read AC validation prompt
    with open('prompts/character_validator_ac.txt', 'r') as f:
        ac_prompt = f.read()
    
    # Read inventory validation prompt
    with open('prompts/character_validator_inventory.txt', 'r') as f:
        inv_prompt = f.read()
    
    # Count tokens
    ac_tokens = count_tokens(ac_prompt)
    inv_tokens = count_tokens(inv_prompt)
    
    print(f"\nAC Validation Prompt:")
    print(f"  Characters: {len(ac_prompt):,}")
    print(f"  Tokens: {ac_tokens:,}")
    
    print(f"\nInventory Validation Prompt:")
    print(f"  Characters: {len(inv_prompt):,}")
    print(f"  Tokens: {inv_tokens:,}")
    
    print(f"\nTotal System Prompt Tokens: {ac_tokens + inv_tokens:,}")
    
    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)
    
    print(f"\nThese prompts are relatively small:")
    print(f"  - AC prompt: {ac_tokens} tokens (less than 1K)")
    print(f"  - Inventory prompt: {inv_tokens} tokens (about 2K)")
    print(f"  - Combined: {ac_tokens + inv_tokens} tokens")
    
    print(f"\nThe REAL problem is the character JSON:")
    print(f"  - Eirik's full JSON: 7,837 tokens")
    print(f"  - That's {7837 / (ac_tokens + inv_tokens):.1f}x larger than both prompts combined!")
    
    print(f"\nCompression potential:")
    print(f"  - Prompts: Maybe save 2-2.5K tokens with compression")
    print(f"  - Character data: Could save 7K+ tokens by sending only relevant fields")

if __name__ == "__main__":
    main()