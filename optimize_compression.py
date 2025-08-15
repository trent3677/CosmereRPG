#!/usr/bin/env python3
"""
Optimize compression strategy by testing all combinations to find minimum token count.
Apply compression to conversation histories and validate accuracy.
"""

import json
import re
import tiktoken
from collections import Counter
from typing import Dict, List, Tuple, Set
import itertools
import hashlib
from difflib import SequenceMatcher

class CompressionOptimizer:
    def __init__(self, model="gpt-4"):
        self.encoding = tiktoken.encoding_for_model(model)
        self.compression_map = {}
        self.decompression_map = {}
        
    def count_tokens(self, text: str) -> int:
        """Count tokens for given text."""
        return len(self.encoding.encode(text))
    
    def get_replacement_chars(self, count: int = 300) -> List[str]:
        """Get single-token replacement characters."""
        chars = []
        
        # Unicode ranges that are single tokens
        ranges = [
            (0x2500, 0x257F),  # Box Drawing
            (0x2580, 0x259F),  # Block Elements
            (0x25A0, 0x25FF),  # Geometric Shapes
            (0x2600, 0x26FF),  # Miscellaneous Symbols
            (0x2190, 0x21FF),  # Arrows
            (0x2200, 0x22FF),  # Mathematical Operators
            (0x2300, 0x23FF),  # Miscellaneous Technical
            (0xA0, 0xFF),      # Latin-1 Supplement
            (0x100, 0x17F),     # Latin Extended-A
            (0x180, 0x24F),     # Latin Extended-B
        ]
        
        for start, end in ranges:
            for code in range(start, min(end + 1, start + 50)):
                try:
                    char = chr(code)
                    # Verify it's a single token
                    if len(self.encoding.encode(char)) == 1:
                        chars.append(char)
                        if len(chars) >= count:
                            return chars
                except:
                    pass
        
        return chars
    
    def extract_patterns(self, messages: List[Dict], min_freq: int = 2) -> List[Tuple[str, int, int]]:
        """Extract patterns from conversation messages (excluding system prompt)."""
        patterns = Counter()
        
        # Skip system messages, only process user and assistant messages
        for msg in messages:
            role = msg.get('role', '')
            if role in ['user', 'assistant']:
                content = msg.get('content', '')
                
                # Extract all possible substrings
                content_lower = content.lower()
                
                # Word-level patterns
                words = re.findall(r'\b[\w\-\']+\b', content_lower)
                for word in words:
                    token_count = len(self.encoding.encode(word))
                    if token_count > 1:
                        patterns[(word, token_count)] += 1
                
                # Multi-word phrases (2-7 words)
                for n in range(2, 8):
                    for i in range(len(words) - n + 1):
                        phrase = ' '.join(words[i:i+n])
                        token_count = len(self.encoding.encode(phrase))
                        if token_count > 1:
                            patterns[(phrase, token_count)] += 1
                
                # JSON structure patterns
                json_patterns = [
                    '{"action":', '{"narration":', '"parameters":{',
                    '"actions":[', '"}', '"},', '"}]', ':[{',
                    '","', '":"', '":{"', '"},"'
                ]
                for pattern in json_patterns:
                    if pattern in content:
                        count = content.count(pattern)
                        token_count = len(self.encoding.encode(pattern))
                        patterns[(pattern, token_count)] += count
        
        # Convert to list with savings calculation
        result = []
        for (pattern, token_count), freq in patterns.items():
            if freq >= min_freq:
                savings = (token_count - 1) * freq
                result.append((pattern, freq, token_count, savings))
        
        # Sort by savings potential
        result.sort(key=lambda x: x[3], reverse=True)
        return result
    
    def find_optimal_compression(self, messages: List[Dict], max_replacements: int = 200):
        """Find the optimal set of replacements to minimize token count."""
        print("Extracting patterns...")
        patterns = self.extract_patterns(messages)
        print(f"Found {len(patterns)} candidate patterns")
        
        # Get replacement characters
        replacement_chars = self.get_replacement_chars(max_replacements)
        print(f"Available replacement characters: {len(replacement_chars)}")
        
        # Calculate original token count (excluding system messages)
        original_text = ""
        for msg in messages:
            if msg.get('role') in ['user', 'assistant']:
                original_text += msg.get('content', '') + "\n"
        
        original_tokens = self.count_tokens(original_text)
        print(f"Original tokens (user + assistant only): {original_tokens:,}")
        
        # Try different numbers of replacements to find optimal
        best_config = None
        best_net_savings = 0
        
        test_counts = [25, 50, 75, 100, 125, 150, 175, 200, 250, 300]
        
        for num_replacements in test_counts:
            if num_replacements > len(patterns) or num_replacements > len(replacement_chars):
                continue
            
            # Select top patterns
            selected_patterns = patterns[:num_replacements]
            
            # Calculate gross savings
            gross_savings = sum(p[3] for p in selected_patterns)
            
            # Calculate dictionary overhead
            # Each entry needs: pattern + separator + replacement char
            dictionary_overhead = sum(self.count_tokens(p[0]) + 2 for p in selected_patterns)
            
            # Net savings
            net_savings = gross_savings - dictionary_overhead
            
            if net_savings > best_net_savings:
                best_net_savings = net_savings
                best_config = {
                    'num_replacements': num_replacements,
                    'patterns': selected_patterns,
                    'gross_savings': gross_savings,
                    'dictionary_overhead': dictionary_overhead,
                    'net_savings': net_savings,
                    'compression_ratio': (net_savings / original_tokens) * 100
                }
        
        print(f"\nOptimal configuration:")
        print(f"  Replacements: {best_config['num_replacements']}")
        print(f"  Gross savings: {best_config['gross_savings']:,} tokens")
        print(f"  Dictionary overhead: {best_config['dictionary_overhead']:,} tokens")
        print(f"  Net savings: {best_config['net_savings']:,} tokens")
        print(f"  Compression ratio: {best_config['compression_ratio']:.1f}%")
        
        # Create compression/decompression maps
        self.compression_map = {}
        self.decompression_map = {}
        
        for i, (pattern, freq, tokens, savings) in enumerate(best_config['patterns']):
            char = replacement_chars[i]
            self.compression_map[pattern] = char
            self.decompression_map[char] = pattern
        
        return best_config
    
    def compress_text(self, text: str) -> str:
        """Apply compression to text."""
        compressed = text.lower()  # Normalize to lowercase
        
        # Sort patterns by length (longest first) to avoid partial replacements
        sorted_patterns = sorted(self.compression_map.items(), key=lambda x: len(x[0]), reverse=True)
        
        # Use word boundaries to avoid partial replacements
        for pattern, replacement in sorted_patterns:
            # For word patterns, use word boundary replacement
            if pattern.replace(' ', '').replace('-', '').replace("'", '').isalnum():
                # Use regex for whole word replacement
                compressed = re.sub(r'\b' + re.escape(pattern) + r'\b', replacement, compressed)
            else:
                # For non-word patterns (like JSON structures), use direct replacement
                compressed = compressed.replace(pattern, replacement)
        
        return compressed
    
    def decompress_text(self, text: str) -> str:
        """Decompress text back to original."""
        decompressed = text
        
        # Sort by replacement char length (shouldn't matter but just in case)
        sorted_replacements = sorted(self.decompression_map.items(), key=lambda x: len(x[0]), reverse=True)
        
        for char, pattern in sorted_replacements:
            decompressed = decompressed.replace(char, pattern)
        
        return decompressed
    
    def compress_conversation(self, messages: List[Dict]) -> List[Dict]:
        """Compress a conversation history."""
        compressed_messages = []
        
        for msg in messages:
            compressed_msg = msg.copy()
            
            # Only compress user and assistant messages
            if msg.get('role') in ['user', 'assistant']:
                compressed_msg['content'] = self.compress_text(msg.get('content', ''))
                compressed_msg['_original_tokens'] = self.count_tokens(msg.get('content', ''))
                compressed_msg['_compressed_tokens'] = self.count_tokens(compressed_msg['content'])
            
            compressed_messages.append(compressed_msg)
        
        return compressed_messages
    
    def decompress_conversation(self, messages: List[Dict]) -> List[Dict]:
        """Decompress a conversation history."""
        decompressed_messages = []
        
        for msg in messages:
            decompressed_msg = msg.copy()
            
            # Only decompress user and assistant messages
            if msg.get('role') in ['user', 'assistant']:
                decompressed_msg['content'] = self.decompress_text(msg.get('content', ''))
                # Remove metadata
                decompressed_msg.pop('_original_tokens', None)
                decompressed_msg.pop('_compressed_tokens', None)
            
            decompressed_messages.append(decompressed_msg)
        
        return decompressed_messages
    
    def validate_compression(self, original: List[Dict], decompressed: List[Dict]) -> Dict:
        """Validate that decompression accurately recreates the original."""
        validation_results = {
            'message_count_match': len(original) == len(decompressed),
            'content_matches': 0,
            'content_mismatches': 0,
            'mismatch_details': [],
            'similarity_scores': []
        }
        
        for i, (orig_msg, decomp_msg) in enumerate(zip(original, decompressed)):
            # Check role matches
            if orig_msg.get('role') != decomp_msg.get('role'):
                validation_results['mismatch_details'].append(
                    f"Message {i}: Role mismatch"
                )
                continue
            
            # For user and assistant messages, check content
            if orig_msg.get('role') in ['user', 'assistant']:
                orig_content = orig_msg.get('content', '').lower()
                decomp_content = decomp_msg.get('content', '')
                
                if orig_content == decomp_content:
                    validation_results['content_matches'] += 1
                else:
                    validation_results['content_mismatches'] += 1
                    
                    # Calculate similarity
                    similarity = SequenceMatcher(None, orig_content, decomp_content).ratio()
                    validation_results['similarity_scores'].append(similarity)
                    
                    if similarity < 0.99:  # Flag significant mismatches
                        validation_results['mismatch_details'].append(
                            f"Message {i}: Content mismatch (similarity: {similarity:.2%})"
                        )
                        
                        # Show first difference
                        for j, (c1, c2) in enumerate(zip(orig_content, decomp_content)):
                            if c1 != c2:
                                context_start = max(0, j-20)
                                context_end = min(len(orig_content), j+20)
                                validation_results['mismatch_details'].append(
                                    f"  First diff at pos {j}: '{orig_content[context_start:context_end]}' vs '{decomp_content[context_start:context_end]}'"
                                )
                                break
        
        validation_results['is_valid'] = (
            validation_results['content_mismatches'] == 0 and
            validation_results['message_count_match']
        )
        
        if validation_results['similarity_scores']:
            validation_results['avg_similarity'] = sum(validation_results['similarity_scores']) / len(validation_results['similarity_scores'])
        
        return validation_results
    
    def save_compression_dictionary(self, filepath: str):
        """Save the compression dictionary."""
        dictionary = {
            'compression_map': self.compression_map,
            'decompression_map': self.decompression_map,
            'metadata': {
                'num_replacements': len(self.compression_map),
                'timestamp': str(json.dumps(None, default=str))
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dictionary, f, indent=2, ensure_ascii=False)
        
        print(f"Saved compression dictionary to {filepath}")

def analyze_file(filepath: str, name: str, optimizer: CompressionOptimizer):
    """Analyze and compress a single conversation file."""
    print(f"\n{'='*80}")
    print(f"ANALYZING: {name}")
    print(f"File: {filepath}")
    print(f"{'='*80}")
    
    # Load conversation
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            messages = json.load(f)
    except Exception as e:
        print(f"Error loading file: {e}")
        return None
    
    print(f"Loaded {len(messages)} messages")
    
    # Count original tokens
    total_original_tokens = 0
    user_assistant_tokens = 0
    
    for msg in messages:
        tokens = optimizer.count_tokens(msg.get('content', ''))
        total_original_tokens += tokens
        if msg.get('role') in ['user', 'assistant']:
            user_assistant_tokens += tokens
    
    print(f"Total tokens (all messages): {total_original_tokens:,}")
    print(f"User + Assistant tokens: {user_assistant_tokens:,}")
    
    # Find optimal compression
    config = optimizer.find_optimal_compression(messages)
    
    # Apply compression
    print("\nApplying compression...")
    compressed_messages = optimizer.compress_conversation(messages)
    
    # Count compressed tokens
    total_compressed_tokens = 0
    compressed_user_assistant = 0
    
    for msg in compressed_messages:
        tokens = optimizer.count_tokens(msg.get('content', ''))
        total_compressed_tokens += tokens
        if msg.get('role') in ['user', 'assistant']:
            compressed_user_assistant += tokens
    
    print(f"Compressed tokens (user + assistant): {compressed_user_assistant:,}")
    print(f"Actual compression: {((user_assistant_tokens - compressed_user_assistant) / user_assistant_tokens * 100):.1f}%")
    
    # Save compressed version
    output_file = filepath.replace('.json', '_compressed.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(compressed_messages, f, indent=2, ensure_ascii=False)
    print(f"Saved compressed to: {output_file}")
    
    # Test decompression
    print("\nTesting decompression...")
    decompressed_messages = optimizer.decompress_conversation(compressed_messages)
    
    # Validate
    validation = optimizer.validate_compression(messages, decompressed_messages)
    
    print(f"Validation results:")
    print(f"  Messages match: {validation['message_count_match']}")
    print(f"  Content matches: {validation['content_matches']}")
    print(f"  Content mismatches: {validation['content_mismatches']}")
    print(f"  Valid: {validation['is_valid']}")
    
    if validation['mismatch_details']:
        print(f"  Mismatch details:")
        for detail in validation['mismatch_details'][:5]:  # Show first 5
            print(f"    {detail}")
    
    # Save decompressed for comparison
    decomp_file = filepath.replace('.json', '_decompressed.json')
    with open(decomp_file, 'w', encoding='utf-8') as f:
        json.dump(decompressed_messages, f, indent=2, ensure_ascii=False)
    print(f"Saved decompressed to: {decomp_file}")
    
    return {
        'original_tokens': user_assistant_tokens,
        'compressed_tokens': compressed_user_assistant,
        'compression_ratio': (user_assistant_tokens - compressed_user_assistant) / user_assistant_tokens * 100,
        'validation': validation
    }

def main():
    print("COMPRESSION OPTIMIZATION AND VALIDATION")
    print("="*80)
    
    # Initialize optimizer
    optimizer = CompressionOptimizer()
    
    # Analyze main conversation history
    results1 = analyze_file(
        "modules/conversation_history/conversation_history.json",
        "Main Conversation History",
        optimizer
    )
    
    # Save dictionary after first optimization
    optimizer.save_compression_dictionary("compression_dictionary_main.json")
    
    # Create new optimizer for combat history
    combat_optimizer = CompressionOptimizer()
    
    # Analyze combat conversation history
    results2 = analyze_file(
        "modules/conversation_history/combat_conversation_history.json",
        "Combat Conversation History",
        combat_optimizer
    )
    
    # Save combat dictionary
    combat_optimizer.save_compression_dictionary("compression_dictionary_combat.json")
    
    # Summary
    print("\n" + "="*80)
    print("COMPRESSION SUMMARY")
    print("="*80)
    
    if results1:
        print(f"\nMain Conversation:")
        print(f"  Original: {results1['original_tokens']:,} tokens")
        print(f"  Compressed: {results1['compressed_tokens']:,} tokens")
        print(f"  Reduction: {results1['compression_ratio']:.1f}%")
        print(f"  Validation: {'PASSED' if results1['validation']['is_valid'] else 'FAILED'}")
    
    if results2:
        print(f"\nCombat Conversation:")
        print(f"  Original: {results2['original_tokens']:,} tokens")
        print(f"  Compressed: {results2['compressed_tokens']:,} tokens")
        print(f"  Reduction: {results2['compression_ratio']:.1f}%")
        print(f"  Validation: {'PASSED' if results2['validation']['is_valid'] else 'FAILED'}")
    
    if results1 and results2:
        total_original = results1['original_tokens'] + results2['original_tokens']
        total_compressed = results1['compressed_tokens'] + results2['compressed_tokens']
        total_reduction = (total_original - total_compressed) / total_original * 100
        
        print(f"\nCombined:")
        print(f"  Total original: {total_original:,} tokens")
        print(f"  Total compressed: {total_compressed:,} tokens")
        print(f"  Total reduction: {total_reduction:.1f}%")
    
    print("\nOutput files created:")
    print("  - conversation_history_compressed.json")
    print("  - conversation_history_decompressed.json")
    print("  - combat_conversation_history_compressed.json")
    print("  - combat_conversation_history_decompressed.json")
    print("  - compression_dictionary_main.json")
    print("  - compression_dictionary_combat.json")
    
    print("\nValidation: Compare _decompressed.json files with originals to verify accuracy")

if __name__ == "__main__":
    main()