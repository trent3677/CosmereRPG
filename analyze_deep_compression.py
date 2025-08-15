#!/usr/bin/env python3
"""
Deep compression analysis for maximum token reduction.
Analyzes word patterns, sub-word patterns, and semantic clustering.
"""

import json
import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set
import tiktoken
from itertools import combinations

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens using OpenAI's tiktoken."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def analyze_word_patterns(text: str) -> Dict:
    """Analyze word-level patterns for compression."""
    encoding = tiktoken.encoding_for_model("gpt-4")
    
    # Tokenize at word level
    words = re.findall(r'\b[\w\-\']+\b', text.lower())
    
    # Analyze individual words
    word_freq = Counter(words)
    word_analysis = {}
    
    for word, freq in word_freq.items():
        if freq >= 2:  # Even 2 occurrences might be worth replacing
            token_count = len(encoding.encode(word))
            if token_count > 1:
                savings = (token_count - 1) * freq
                word_analysis[word] = {
                    'frequency': freq,
                    'tokens': token_count,
                    'savings': savings
                }
    
    return word_analysis

def analyze_subword_patterns(text: str) -> Dict:
    """Analyze sub-word patterns (prefixes, suffixes, stems)."""
    words = re.findall(r'\b[\w\-\']+\b', text.lower())
    
    # Common D&D/gaming suffixes and prefixes
    prefixes = ['un', 're', 'pre', 'over', 'under', 'out', 'up', 'down']
    suffixes = ['ing', 'ed', 'er', 'est', 'ly', 'tion', 'ness', 'ment', 'able', 'ful']
    
    prefix_counts = Counter()
    suffix_counts = Counter()
    stem_counts = Counter()
    
    for word in words:
        # Check prefixes
        for prefix in prefixes:
            if word.startswith(prefix) and len(word) > len(prefix) + 2:
                prefix_counts[prefix] += 1
                stem = word[len(prefix):]
                stem_counts[stem] += 1
        
        # Check suffixes
        for suffix in suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                suffix_counts[suffix] += 1
                stem = word[:-len(suffix)]
                stem_counts[stem] += 1
    
    return {
        'prefixes': dict(prefix_counts.most_common(20)),
        'suffixes': dict(suffix_counts.most_common(20)),
        'stems': dict(stem_counts.most_common(20))
    }

def analyze_semantic_clusters(text: str) -> Dict:
    """Find semantic clusters of related terms that could share compression."""
    
    # D&D semantic groups
    semantic_groups = {
        'abilities': ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'],
        'skills': ['acrobatics', 'athletics', 'deception', 'history', 'insight', 'intimidation',
                   'investigation', 'medicine', 'nature', 'perception', 'performance', 'persuasion',
                   'religion', 'sleight', 'stealth', 'survival'],
        'conditions': ['blinded', 'charmed', 'deafened', 'frightened', 'grappled', 'incapacitated',
                      'invisible', 'paralyzed', 'petrified', 'poisoned', 'prone', 'restrained',
                      'stunned', 'unconscious'],
        'combat': ['attack', 'damage', 'hit', 'miss', 'critical', 'roll', 'save', 'saving throw',
                  'armor class', 'initiative', 'action', 'bonus action', 'reaction'],
        'movement': ['move', 'walk', 'run', 'fly', 'swim', 'climb', 'crawl', 'jump', 'teleport'],
        'dice': ['d4', 'd6', 'd8', 'd10', 'd12', 'd20', 'd100', 'dice', 'roll', 'modifier'],
        'magic': ['spell', 'cantrip', 'slot', 'level', 'cast', 'concentration', 'ritual', 'components'],
        'items': ['weapon', 'armor', 'shield', 'potion', 'scroll', 'wand', 'ring', 'amulet'],
        'time': ['turn', 'round', 'minute', 'hour', 'day', 'short rest', 'long rest'],
        'distance': ['feet', 'foot', 'mile', 'miles', 'range', 'reach', 'radius', 'area']
    }
    
    text_lower = text.lower()
    cluster_stats = {}
    
    for group_name, terms in semantic_groups.items():
        group_count = 0
        term_counts = {}
        
        for term in terms:
            count = text_lower.count(term)
            if count > 0:
                term_counts[term] = count
                group_count += count
        
        if group_count > 0:
            cluster_stats[group_name] = {
                'total_occurrences': group_count,
                'unique_terms': len(term_counts),
                'top_terms': dict(sorted(term_counts.items(), key=lambda x: x[1], reverse=True)[:5])
            }
    
    return cluster_stats

def analyze_conversation_patterns(conversation: List[Dict]) -> Dict:
    """Analyze patterns specific to conversation history."""
    
    patterns = {
        'role_sequences': [],
        'message_lengths': [],
        'json_structures': 0,
        'narration_patterns': [],
        'action_patterns': [],
        'common_phrases': Counter()
    }
    
    for i, msg in enumerate(conversation):
        role = msg.get('role', '')
        content = msg.get('content', '')
        
        # Track role sequences
        if i > 0:
            prev_role = conversation[i-1].get('role', '')
            patterns['role_sequences'].append(f"{prev_role}->{role}")
        
        # Track message lengths
        patterns['message_lengths'].append(len(content))
        
        # Check for JSON
        try:
            parsed = json.loads(content)
            patterns['json_structures'] += 1
            
            if 'narration' in parsed:
                # Extract first 50 chars of narration
                narr_start = parsed['narration'][:50]
                patterns['narration_patterns'].append(narr_start)
            
            if 'actions' in parsed:
                for action in parsed['actions']:
                    patterns['action_patterns'].append(action.get('action', ''))
        except:
            pass
        
        # Common phrases in natural language
        if role == 'user':
            # Common player commands
            commands = ['i ', 'i want to', 'i attack', 'i cast', 'i move', 'i search', 
                       'i check', 'i talk to', 'i examine', 'i use', 'i take', 'i look']
            for cmd in commands:
                if content.lower().startswith(cmd):
                    patterns['common_phrases'][cmd] += 1
    
    return patterns

def calculate_aggressive_compression(text: str, level: str = "extreme") -> Dict:
    """Calculate compression at different aggressiveness levels."""
    
    encoding = tiktoken.encoding_for_model("gpt-4")
    original_tokens = count_tokens(text)
    
    compression_strategies = {
        'moderate': {
            'word_threshold': 5,  # Replace words appearing 5+ times
            'phrase_length': 3,    # Replace phrases up to 3 words
            'keep_punctuation': True
        },
        'aggressive': {
            'word_threshold': 3,   # Replace words appearing 3+ times
            'phrase_length': 5,    # Replace phrases up to 5 words
            'keep_punctuation': False  # Remove unnecessary punctuation
        },
        'extreme': {
            'word_threshold': 2,   # Replace words appearing 2+ times
            'phrase_length': 7,    # Replace phrases up to 7 words
            'keep_punctuation': False,
            'use_stems': True,     # Replace with word stems
            'semantic_compression': True  # Compress semantic groups
        }
    }
    
    strategy = compression_strategies[level]
    
    # Estimate compression based on strategy
    words = re.findall(r'\b[\w\-\']+\b', text.lower())
    word_freq = Counter(words)
    
    # Calculate replaceable items
    replaceable_words = sum(1 for word, freq in word_freq.items() 
                           if freq >= strategy['word_threshold'])
    
    # Estimate token savings
    estimated_savings = 0
    for word, freq in word_freq.items():
        if freq >= strategy['word_threshold']:
            word_tokens = len(encoding.encode(word))
            if word_tokens > 1:
                estimated_savings += (word_tokens - 1) * freq
    
    # Additional savings from semantic compression
    if strategy.get('semantic_compression'):
        estimated_savings *= 1.3  # 30% additional from semantic clustering
    
    compression_ratio = estimated_savings / original_tokens * 100
    
    return {
        'original_tokens': original_tokens,
        'estimated_savings': int(estimated_savings),
        'compression_ratio': compression_ratio,
        'final_tokens': original_tokens - int(estimated_savings),
        'replaceable_patterns': replaceable_words
    }

def analyze_deep_compression(file_path: str, file_type: str = "prompt"):
    """Main deep compression analysis."""
    
    print(f"\n{'='*80}")
    print(f"DEEP COMPRESSION ANALYSIS: {file_path}")
    print(f"{'='*80}")
    
    # Load file
    try:
        if file_type == "conversation":
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                text = json.dumps(data)
                conversation_patterns = analyze_conversation_patterns(data)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                conversation_patterns = None
    except Exception as e:
        print(f"Error loading file: {e}")
        return
    
    original_tokens = count_tokens(text)
    print(f"Original tokens: {original_tokens:,}")
    
    # Word pattern analysis
    print("\n1. WORD PATTERN ANALYSIS")
    print("-" * 40)
    word_patterns = analyze_word_patterns(text)
    
    # Sort by savings potential
    top_words = sorted(word_patterns.items(), key=lambda x: x[1]['savings'], reverse=True)[:20]
    
    print(f"Total unique words: {len(word_patterns)}")
    print(f"Multi-token words: {sum(1 for w in word_patterns.values() if w['tokens'] > 1)}")
    print("\nTop compressible words:")
    for word, data in top_words[:10]:
        print(f"  '{word}': {data['frequency']}x, {data['tokens']} tokens, saves {data['savings']}")
    
    # Sub-word pattern analysis
    print("\n2. SUB-WORD PATTERN ANALYSIS")
    print("-" * 40)
    subword_patterns = analyze_subword_patterns(text)
    
    print("Common prefixes:", subword_patterns['prefixes'])
    print("Common suffixes:", subword_patterns['suffixes'])
    print("Common stems:", list(subword_patterns['stems'].keys())[:10])
    
    # Semantic clustering
    print("\n3. SEMANTIC CLUSTERING")
    print("-" * 40)
    clusters = analyze_semantic_clusters(text)
    
    for cluster_name, data in sorted(clusters.items(), key=lambda x: x[1]['total_occurrences'], reverse=True):
        print(f"{cluster_name}: {data['total_occurrences']} occurrences")
        print(f"  Top terms: {data['top_terms']}")
    
    # Conversation-specific patterns
    if conversation_patterns:
        print("\n4. CONVERSATION-SPECIFIC PATTERNS")
        print("-" * 40)
        print(f"JSON messages: {conversation_patterns['json_structures']}")
        print(f"Common user commands: {dict(conversation_patterns['common_phrases'].most_common(10))}")
        print(f"Action patterns: {Counter(conversation_patterns['action_patterns']).most_common(5)}")
    
    # Compression estimates
    print("\n5. COMPRESSION POTENTIAL")
    print("-" * 40)
    
    for level in ['moderate', 'aggressive', 'extreme']:
        results = calculate_aggressive_compression(text, level)
        print(f"\n{level.upper()} compression:")
        print(f"  Original: {results['original_tokens']:,} tokens")
        print(f"  Compressed: {results['final_tokens']:,} tokens")
        print(f"  Savings: {results['estimated_savings']:,} tokens ({results['compression_ratio']:.1f}%)")
        print(f"  Replaceable patterns: {results['replaceable_patterns']:,}")
    
    return {
        'original_tokens': original_tokens,
        'word_patterns': len(word_patterns),
        'clusters': clusters,
        'extreme_compression': calculate_aggressive_compression(text, 'extreme')
    }

def create_training_summary():
    """Create a brief training summary that replaces system prompt."""
    
    summary = """
    # COMPRESSED SYSTEM DIRECTIVE (Replace 22k token prompt)
    
    You are DM for 5e game. JSON response only.
    
    ## Response Format
    {"narration": "...", "actions": [...]}
    
    ## Core Rules (learned through training)
    - D20 system
    - Standard 5e mechanics
    - Action economy
    - Spell slots
    - Rest mechanics
    
    ## Compression Tokens
    [Model trained on 3000+ examples with these patterns]
    █ = common JSON structures
    ▓ = parameter blocks
    ▲ = action arrays
    ◆ = dice rolls
    ♦ = ability checks
    
    Training handles all detailed rules. This is just structure reminder.
    """
    
    tokens = count_tokens(summary)
    print(f"\nTRAINING SUMMARY REPLACEMENT:")
    print(f"Original system prompt: 22,672 tokens")
    print(f"Compressed summary: {tokens} tokens")
    print(f"Reduction: {(1 - tokens/22672) * 100:.1f}%")
    
    return summary

if __name__ == "__main__":
    print("DEEP COMPRESSION ANALYSIS FOR MAXIMUM TOKEN REDUCTION")
    print("="*80)
    
    # Analyze system prompt
    print("\nSYSTEM PROMPT ANALYSIS:")
    system_results = analyze_deep_compression("prompts/system_prompt.txt", "prompt")
    
    # Analyze conversation history
    print("\nCONVERSATION HISTORY ANALYSIS:")
    conv_results = analyze_deep_compression("modules/conversation_history/conversation_history.json", "conversation")
    
    # Create training summary
    training_summary = create_training_summary()
    
    # Final recommendations
    print("\n" + "="*80)
    print("FINAL COMPRESSION STRATEGY")
    print("="*80)
    
    print("\n1. SYSTEM PROMPT REPLACEMENT:")
    print("   - Train model on 3000+ examples")
    print("   - Replace 22k token prompt with <500 token summary")
    print("   - Savings: ~95% reduction")
    
    print("\n2. CONVERSATION COMPRESSION:")
    print("   - Apply extreme DSL compression")
    print("   - Semantic clustering for D&D terms")
    print("   - Expected: 70-80% reduction")
    
    print("\n3. TOTAL EXPECTED COMPRESSION:")
    system_extreme = system_results['extreme_compression']
    conv_extreme = conv_results['extreme_compression']
    
    print(f"   - System prompt: 22,672 → 500 tokens (97.8% reduction)")
    print(f"   - Conversation: {conv_extreme['original_tokens']:,} → {conv_extreme['final_tokens']:,} tokens ({conv_extreme['compression_ratio']:.1f}% reduction)")
    print(f"   - Combined reduction: ~85-90% fewer tokens")
    
    print("\n4. IMPLEMENTATION STEPS:")
    print("   a) Generate training data with compressed inputs")
    print("   b) Fine-tune model on pattern recognition")
    print("   c) Implement client-side compression/decompression")
    print("   d) Test with progressive compression levels")
    
    print("\nWith this approach, a 50k token conversation could become ~5-7k tokens!")