#!/usr/bin/env python3
"""
Analyze token compression potential using domain-specific language replacements.
Find optimal single-token replacements for word patterns in prompts.
"""

import json
import re
from collections import Counter
from typing import Dict, List, Tuple
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens using OpenAI's tiktoken for specific model."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def get_single_token_chars(model: str = "gpt-4") -> List[str]:
    """Get characters that encode to exactly 1 token."""
    encoding = tiktoken.encoding_for_model(model)
    single_token_chars = []
    
    # Test various Unicode ranges for single-token characters
    # Start with less common Unicode blocks to avoid conflicts
    ranges_to_test = [
        (0x2500, 0x257F),  # Box Drawing
        (0x2580, 0x259F),  # Block Elements  
        (0x25A0, 0x25FF),  # Geometric Shapes
        (0x2600, 0x26FF),  # Miscellaneous Symbols
        (0x2700, 0x27BF),  # Dingbats
        (0x2190, 0x21FF),  # Arrows
        (0x2200, 0x22FF),  # Mathematical Operators
        (0x2300, 0x23FF),  # Miscellaneous Technical
        (0x2400, 0x243F),  # Control Pictures
        (0x2460, 0x24FF),  # Enclosed Alphanumerics
        (0x3040, 0x309F),  # Hiragana
        (0x30A0, 0x30FF),  # Katakana
    ]
    
    for start, end in ranges_to_test:
        for code_point in range(start, min(end + 1, start + 100)):  # Limit to 100 per range
            try:
                char = chr(code_point)
                if len(encoding.encode(char)) == 1:
                    single_token_chars.append(char)
            except:
                pass
    
    return single_token_chars

def find_compressible_patterns(text: str, min_freq: int = 3) -> List[Tuple[str, int, int]]:
    """Find multi-token patterns that appear frequently.
    Returns list of (pattern, frequency, tokens_used)."""
    
    encoding = tiktoken.encoding_for_model("gpt-4")
    
    # Split into words and analyze token counts
    words = re.findall(r'\b[\w\-\']+\b|[^\w\s]+', text.lower())
    
    # Find patterns of different lengths
    patterns = []
    
    # Single words
    word_freq = Counter(words)
    for word, freq in word_freq.items():
        if freq >= min_freq:
            token_count = len(encoding.encode(word))
            if token_count > 1:  # Only worth replacing multi-token patterns
                patterns.append((word, freq, token_count))
    
    # Multi-word phrases (2-5 words)
    for n in range(2, 6):
        phrases = []
        for i in range(len(words) - n + 1):
            phrase = ' '.join(words[i:i+n])
            phrases.append(phrase)
        
        phrase_freq = Counter(phrases)
        for phrase, freq in phrase_freq.items():
            if freq >= min_freq:
                token_count = len(encoding.encode(phrase))
                if token_count > 1:
                    patterns.append((phrase, freq, token_count))
    
    # Sort by compression potential (tokens_saved * frequency)
    patterns.sort(key=lambda x: (x[2] - 1) * x[1], reverse=True)
    
    return patterns

def calculate_compression(text: str, patterns: List[Tuple[str, int, int]], 
                         replacements: List[str]) -> Dict:
    """Calculate compression using single-token replacements."""
    
    original_tokens = count_tokens(text)
    compressed_text = text.lower()
    
    total_tokens_saved = 0
    replacement_map = {}
    
    # Apply replacements
    for i, (pattern, freq, token_count) in enumerate(patterns[:len(replacements)]):
        replacement_char = replacements[i]
        
        # Calculate savings: (original_tokens - 1) * frequency
        tokens_saved = (token_count - 1) * freq
        total_tokens_saved += tokens_saved
        
        replacement_map[pattern] = {
            'replacement': replacement_char,
            'frequency': freq,
            'original_tokens': token_count,
            'tokens_saved': tokens_saved
        }
        
        # Apply replacement
        compressed_text = compressed_text.replace(pattern, replacement_char)
    
    compressed_tokens = count_tokens(compressed_text)
    
    # Need to account for dictionary overhead
    # Each mapping needs: pattern + replacement char
    dictionary_overhead = 0
    for pattern, info in replacement_map.items():
        # Rough estimate: pattern tokens + 2 tokens for mapping syntax
        dictionary_overhead += count_tokens(pattern) + 2
    
    return {
        'original_tokens': original_tokens,
        'compressed_tokens': compressed_tokens,
        'tokens_saved': total_tokens_saved,
        'compression_ratio': (1 - compressed_tokens / original_tokens) * 100,
        'dictionary_overhead': dictionary_overhead,
        'net_tokens_saved': total_tokens_saved - dictionary_overhead,
        'net_compression_ratio': (total_tokens_saved - dictionary_overhead) / original_tokens * 100,
        'replacements_used': len(replacement_map),
        'replacement_map': replacement_map
    }

def analyze_prompt_compression(file_path: str, prompt_name: str):
    """Analyze compression potential for a specific prompt file."""
    
    print(f"\n{'='*80}")
    print(f"ANALYZING: {prompt_name}")
    print(f"File: {file_path}")
    print(f"{'='*80}")
    
    # Load prompt
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            prompt_text = f.read()
    except Exception as e:
        print(f"Error loading file: {e}")
        return
    
    original_tokens = count_tokens(prompt_text)
    print(f"Original prompt tokens: {original_tokens:,}")
    
    # Find single-token replacements
    print("\nFinding single-token replacement characters...")
    single_tokens = get_single_token_chars()
    print(f"Found {len(single_tokens)} single-token characters available")
    
    # Find compressible patterns
    print("\nFinding compressible patterns...")
    patterns = find_compressible_patterns(prompt_text, min_freq=3)
    print(f"Found {len(patterns)} frequent multi-token patterns")
    
    # Show top patterns
    print("\nTop 20 patterns by compression potential:")
    print(f"{'Pattern':<40} {'Freq':<6} {'Tokens':<8} {'Saves':<8}")
    print("-" * 70)
    for pattern, freq, tokens in patterns[:20]:
        saves = (tokens - 1) * freq
        print(f"{pattern[:40]:<40} {freq:<6} {tokens:<8} {saves:<8}")
    
    # Calculate compression with different strategies
    print("\nCOMPRESSION ANALYSIS:")
    print("-" * 70)
    
    strategies = [
        ("50 replacements", 50),
        ("100 replacements", 100),
        ("200 replacements", 200),
        ("Maximum replacements", min(len(patterns), len(single_tokens)))
    ]
    
    for strategy_name, num_replacements in strategies:
        if num_replacements > len(single_tokens):
            num_replacements = len(single_tokens)
        if num_replacements > len(patterns):
            num_replacements = len(patterns)
            
        results = calculate_compression(prompt_text, patterns, single_tokens[:num_replacements])
        
        print(f"\n{strategy_name}:")
        print(f"  Original tokens: {results['original_tokens']:,}")
        print(f"  Compressed tokens: {results['compressed_tokens']:,}")
        print(f"  Dictionary overhead: {results['dictionary_overhead']:,} tokens")
        print(f"  Gross compression: {results['compression_ratio']:.1f}%")
        print(f"  Net tokens saved: {results['net_tokens_saved']:,}")
        print(f"  Net compression: {results['net_compression_ratio']:.1f}%")
    
    # Domain-specific insights
    print("\nDOMAIN-SPECIFIC PATTERNS:")
    print("-" * 70)
    
    # D&D specific patterns
    dnd_patterns = [p for p, f, t in patterns if any(
        keyword in p for keyword in [
            'character', 'player', 'spell', 'attack', 'damage', 'roll',
            'saving throw', 'ability', 'action', 'bonus', 'level',
            'hit points', 'armor class', 'initiative', 'proficiency'
        ]
    )]
    
    print(f"D&D mechanics patterns found: {len(dnd_patterns)}")
    if dnd_patterns:
        print("Top D&D patterns:")
        for pattern in dnd_patterns[:10]:
            pattern_data = next((p for p in patterns if p[0] == pattern), None)
            if pattern_data:
                print(f"  - '{pattern}' ({pattern_data[1]} occurrences, {pattern_data[2]} tokens)")
    
    return results

def create_compression_dictionary(patterns: List[Tuple[str, int, int]], 
                                 replacements: List[str]) -> str:
    """Create a compression dictionary for the DSL."""
    
    dictionary = "# Domain-Specific Language Compression Dictionary\n\n"
    dictionary += "## Replacement Mappings\n\n"
    
    for i, (pattern, freq, tokens) in enumerate(patterns[:len(replacements)]):
        replacement = replacements[i]
        savings = (tokens - 1) * freq
        dictionary += f"{replacement} := {pattern}  # Saves {savings} tokens\n"
    
    return dictionary

if __name__ == "__main__":
    print("TOKEN COMPRESSION ANALYSIS USING DOMAIN-SPECIFIC LANGUAGE")
    print("="*80)
    
    # Analyze system prompt
    results_system = analyze_prompt_compression(
        "prompts/system_prompt.txt",
        "SYSTEM PROMPT"
    )
    
    # Analyze validation prompt
    results_validation = analyze_prompt_compression(
        "prompts/validation/validation_prompt.txt", 
        "VALIDATION PROMPT"
    )
    
    # Combined analysis
    print("\n" + "="*80)
    print("COMBINED COMPRESSION POTENTIAL")
    print("="*80)
    
    # Load both prompts
    with open("prompts/system_prompt.txt", 'r') as f:
        system_text = f.read()
    with open("prompts/validation/validation_prompt.txt", 'r') as f:
        validation_text = f.read()
    
    combined_text = system_text + "\n\n" + validation_text
    combined_tokens = count_tokens(combined_text)
    
    print(f"Combined original tokens: {combined_tokens:,}")
    print(f"System prompt: {count_tokens(system_text):,} tokens")
    print(f"Validation prompt: {count_tokens(validation_text):,} tokens")
    
    # Find patterns in combined text
    combined_patterns = find_compressible_patterns(combined_text, min_freq=5)
    single_tokens = get_single_token_chars()
    
    # Maximum compression
    max_replacements = min(len(combined_patterns), len(single_tokens), 300)
    combined_results = calculate_compression(combined_text, combined_patterns, single_tokens[:max_replacements])
    
    print(f"\nMaximum compression ({max_replacements} replacements):")
    print(f"  Net tokens saved: {combined_results['net_tokens_saved']:,}")
    print(f"  Net compression: {combined_results['net_compression_ratio']:.1f}%")
    print(f"  Final token count: {combined_tokens - combined_results['net_tokens_saved']:,}")
    
    # Create sample dictionary
    print("\nGenerating compression dictionary...")
    dictionary = create_compression_dictionary(combined_patterns[:50], single_tokens[:50])
    
    with open("compression_dictionary.txt", "w") as f:
        f.write(dictionary)
    
    print("Compression dictionary saved to compression_dictionary.txt")