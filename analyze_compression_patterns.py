#!/usr/bin/env python3
"""
Analyze conversation history to identify patterns for compression.
Finds common multi-word phrases that could be replaced with single characters.
"""

import json
import re
from collections import Counter
from typing import Dict, List, Tuple
import math

def load_conversation_history(file_path: str) -> List[Dict]:
    """Load conversation history from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading file: {e}")
        return []

def extract_text_content(conversation: List[Dict]) -> str:
    """Extract all text content from conversation history."""
    text_parts = []
    for message in conversation:
        if 'content' in message:
            text_parts.append(message['content'])
    return '\n'.join(text_parts)

def find_ngrams(text: str, n: int) -> Counter:
    """Find all n-grams (word sequences of length n) in the text."""
    # Clean and tokenize
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Create n-grams
    ngrams = []
    for i in range(len(words) - n + 1):
        ngram = ' '.join(words[i:i+n])
        ngrams.append(ngram)
    
    return Counter(ngrams)

def calculate_compression_savings(text: str, patterns: List[Tuple[str, int]], max_replacements: int = 200) -> Dict:
    """Calculate potential compression savings."""
    original_length = len(text)
    compressed_text = text.lower()
    
    # Track replacements
    total_chars_saved = 0
    replacements_made = 0
    
    # Use ASCII characters starting from extended set (avoiding common ones)
    replacement_chars = [chr(i) for i in range(128, 128 + max_replacements) if chr(i).isprintable()]
    
    replacement_map = {}
    
    for i, (pattern, count) in enumerate(patterns[:len(replacement_chars)]):
        if count < 5:  # Skip rare patterns
            continue
            
        pattern_length = len(pattern)
        replacement_char = replacement_chars[i]
        
        # Calculate savings (pattern length - 1 char) * occurrences
        chars_saved = (pattern_length - 1) * count
        total_chars_saved += chars_saved
        
        replacement_map[pattern] = {
            'char': replacement_char,
            'count': count,
            'saved': chars_saved,
            'pattern_length': pattern_length
        }
        
        replacements_made += 1
        
        # Apply replacement to track actual compression
        compressed_text = compressed_text.replace(pattern, replacement_char)
    
    compressed_length = len(compressed_text)
    compression_ratio = (original_length - compressed_length) / original_length * 100
    
    return {
        'original_length': original_length,
        'compressed_length': compressed_length,
        'chars_saved': total_chars_saved,
        'compression_ratio': compression_ratio,
        'replacements_made': replacements_made,
        'replacement_map': replacement_map
    }

def analyze_conversation_patterns(file_path: str):
    """Main analysis function."""
    print(f"Analyzing conversation history: {file_path}")
    print("=" * 60)
    
    # Load conversation
    conversation = load_conversation_history(file_path)
    if not conversation:
        return
    
    print(f"Loaded {len(conversation)} messages")
    
    # Extract text
    text = extract_text_content(conversation)
    print(f"Total text length: {len(text):,} characters")
    print(f"Estimated tokens (rough): {len(text) // 4:,}")
    print()
    
    # Find patterns of different lengths
    all_patterns = []
    
    for n in range(2, 8):  # 2-word to 7-word phrases
        print(f"Finding {n}-word patterns...")
        ngrams = find_ngrams(text, n)
        # Only keep patterns that appear multiple times
        frequent_ngrams = [(ngram, count) for ngram, count in ngrams.items() if count >= 5]
        all_patterns.extend(frequent_ngrams)
    
    # Sort by total characters saved (length * frequency)
    all_patterns.sort(key=lambda x: len(x[0]) * x[1], reverse=True)
    
    print(f"\nFound {len(all_patterns)} frequent patterns")
    print("\nTop 20 patterns by compression potential:")
    print("-" * 60)
    
    for i, (pattern, count) in enumerate(all_patterns[:20]):
        savings = (len(pattern) - 1) * count
        print(f"{i+1:3}. '{pattern}' (len={len(pattern)}, count={count}, saves={savings} chars)")
    
    # Calculate compression potential
    print("\n" + "=" * 60)
    print("COMPRESSION ANALYSIS")
    print("=" * 60)
    
    # Different replacement strategies
    strategies = [
        ("Top 50 patterns", 50),
        ("Top 100 patterns", 100),
        ("Top 200 patterns", 200),
        ("All frequent patterns", len(all_patterns))
    ]
    
    for strategy_name, num_patterns in strategies:
        if num_patterns > len(all_patterns):
            num_patterns = len(all_patterns)
            
        results = calculate_compression_savings(text, all_patterns, num_patterns)
        
        print(f"\n{strategy_name} ({num_patterns} replacements):")
        print(f"  Original size: {results['original_length']:,} chars")
        print(f"  Compressed size: {results['compressed_length']:,} chars")
        print(f"  Characters saved: {results['chars_saved']:,}")
        print(f"  Compression ratio: {results['compression_ratio']:.1f}%")
        print(f"  Token reduction (estimate): {results['chars_saved'] // 4:,} tokens")
    
    # Pattern categories
    print("\n" + "=" * 60)
    print("PATTERN CATEGORIES")
    print("=" * 60)
    
    categories = {
        'game_mechanics': ['you have', 'you are', 'you can', 'hit points', 'saving throw', 'spell slots'],
        'narrative': ['you see', 'you hear', 'you feel', 'in the', 'of the', 'to the'],
        'combat': ['attack', 'damage', 'initiative', 'armor class', 'weapon', 'shield'],
        'dialogue': ['says', 'replies', 'asks', 'tells you', 'speaking', 'conversation'],
        'movement': ['you move', 'you walk', 'you enter', 'you leave', 'north', 'south', 'east', 'west']
    }
    
    for category, keywords in categories.items():
        category_patterns = [p for p, c in all_patterns if any(kw in p for kw in keywords)]
        total_occurrences = sum(c for p, c in all_patterns if any(kw in p for kw in keywords))
        print(f"\n{category.upper()}: {len(category_patterns)} patterns, {total_occurrences} total occurrences")
        
        # Show top 5 for this category
        category_sorted = [(p, c) for p, c in all_patterns if any(kw in p for kw in keywords)][:5]
        for pattern, count in category_sorted:
            print(f"  - '{pattern}' ({count}x)")
    
    # Summary recommendations
    print("\n" + "=" * 60)
    print("COMPRESSION RECOMMENDATIONS")
    print("=" * 60)
    print(f"1. Using 200 single-character replacements could save ~{results['compression_ratio']:.1f}% of text")
    print(f"2. This translates to approximately {results['chars_saved'] // 4:,} fewer tokens per conversation")
    print(f"3. Most common patterns are game mechanics and narrative phrases")
    print(f"4. Combat and movement commands are highly repetitive and good compression targets")
    print(f"5. A custom tokenizer trained on these patterns could significantly reduce API costs")

if __name__ == "__main__":
    # Analyze the main conversation history
    analyze_conversation_patterns("modules/conversation_history/conversation_history.json")
    
    print("\n\nWould you like to analyze other conversation files? (combat, level_up, etc.)")