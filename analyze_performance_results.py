#!/usr/bin/env python3
"""Analyze model performance results with tokens per second calculations"""

import json

# Load results
with open('model_performance_results.json', 'r') as f:
    results = json.load(f)

print("="*70)
print("MODEL PERFORMANCE ANALYSIS - TOKENS PER SECOND")
print("="*70)
print()

# Calculate tokens per second for each model
analysis = {}

for model, data in results.items():
    if data.get('tokens'):
        # Calculate various metrics
        avg_time = data['avg_time']
        input_tokens = data['tokens']['prompt']
        output_tokens = data['tokens']['completion']
        total_tokens = data['tokens']['total']
        
        # Tokens per second calculations
        input_tps = input_tokens / avg_time if avg_time > 0 else 0
        output_tps = output_tokens / avg_time if avg_time > 0 else 0
        total_tps = total_tokens / avg_time if avg_time > 0 else 0
        
        # Time to first token estimate (rough approximation)
        # Assuming most of the time is generation, not processing
        time_per_output_token = avg_time / output_tokens if output_tokens > 0 else 0
        
        analysis[model] = {
            'avg_time': avg_time,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': total_tokens,
            'input_tps': input_tps,
            'output_tps': output_tps,
            'total_tps': total_tps,
            'time_per_output_token': time_per_output_token,
            'output_length': data['avg_output_length']
        }

# Print detailed analysis
for model in ['gpt-4.1-2025-04-14', 'gpt-4.1-mini-2025-04-14', 'gpt-5-2025-08-07', 'gpt-5-mini-2025-08-07']:
    if model in analysis:
        data = analysis[model]
        print(f"{model}:")
        print(f"  Response Time: {data['avg_time']:.2f}s")
        print(f"  Input Tokens: {data['input_tokens']:,}")
        print(f"  Output Tokens: {data['output_tokens']:,}")
        print(f"  Output Characters: {data['output_length']:,}")
        print(f"  ")
        print(f"  Performance Metrics:")
        print(f"    Output Generation: {data['output_tps']:.1f} tokens/sec")
        print(f"    Input Processing: {data['input_tps']:.0f} tokens/sec (theoretical)")
        print(f"    Time per Output Token: {data['time_per_output_token']*1000:.1f}ms")
        print(f"    Characters per Token: {data['output_length']/data['output_tokens']:.1f}")
        print()

# Compare GPT-4.1 vs GPT-5
print("="*70)
print("COMPARISON: GPT-4.1 vs GPT-5")
print("="*70)
print()

# Full models comparison
if 'gpt-4.1-2025-04-14' in analysis and 'gpt-5-2025-08-07' in analysis:
    gpt41 = analysis['gpt-4.1-2025-04-14']
    gpt5 = analysis['gpt-5-2025-08-07']
    
    print("FULL MODELS:")
    print("-" * 40)
    print(f"Response Time:")
    print(f"  GPT-4.1: {gpt41['avg_time']:.2f}s")
    print(f"  GPT-5:   {gpt5['avg_time']:.2f}s ({gpt5['avg_time']/gpt41['avg_time']:.1f}x slower)")
    print()
    print(f"Output Length:")
    print(f"  GPT-4.1: {gpt41['output_tokens']:,} tokens ({gpt41['output_length']:,} chars)")
    print(f"  GPT-5:   {gpt5['output_tokens']:,} tokens ({gpt5['output_length']:,} chars)")
    print(f"  GPT-5 generates {gpt5['output_tokens']/gpt41['output_tokens']:.1f}x more tokens")
    print()
    print(f"Generation Speed:")
    print(f"  GPT-4.1: {gpt41['output_tps']:.1f} tokens/sec")
    print(f"  GPT-5:   {gpt5['output_tps']:.1f} tokens/sec")
    print()
    print(f"Time per Token:")
    print(f"  GPT-4.1: {gpt41['time_per_output_token']*1000:.1f}ms")
    print(f"  GPT-5:   {gpt5['time_per_output_token']*1000:.1f}ms")
    print()

# Mini models comparison
if 'gpt-4.1-mini-2025-04-14' in analysis and 'gpt-5-mini-2025-08-07' in analysis:
    gpt41_mini = analysis['gpt-4.1-mini-2025-04-14']
    gpt5_mini = analysis['gpt-5-mini-2025-08-07']
    
    print("MINI MODELS:")
    print("-" * 40)
    print(f"Response Time:")
    print(f"  GPT-4.1-mini: {gpt41_mini['avg_time']:.2f}s")
    print(f"  GPT-5-mini:   {gpt5_mini['avg_time']:.2f}s ({gpt5_mini['avg_time']/gpt41_mini['avg_time']:.1f}x slower)")
    print()
    print(f"Output Length:")
    print(f"  GPT-4.1-mini: {gpt41_mini['output_tokens']:,} tokens ({gpt41_mini['output_length']:,} chars)")
    print(f"  GPT-5-mini:   {gpt5_mini['output_tokens']:,} tokens ({gpt5_mini['output_length']:,} chars)")
    print(f"  GPT-5-mini generates {gpt5_mini['output_tokens']/gpt41_mini['output_tokens']:.1f}x more tokens")
    print()
    print(f"Generation Speed:")
    print(f"  GPT-4.1-mini: {gpt41_mini['output_tps']:.1f} tokens/sec")
    print(f"  GPT-5-mini:   {gpt5_mini['output_tps']:.1f} tokens/sec")
    print()

print("="*70)
print("KEY INSIGHTS")
print("="*70)
print()

# Calculate why GPT-5 is slower
if 'gpt-4.1-2025-04-14' in analysis and 'gpt-5-2025-08-07' in analysis:
    gpt41 = analysis['gpt-4.1-2025-04-14']
    gpt5 = analysis['gpt-5-2025-08-07']
    
    # Extra time due to more tokens
    extra_tokens = gpt5['output_tokens'] - gpt41['output_tokens']
    extra_time_from_tokens = extra_tokens * gpt41['time_per_output_token']
    expected_time_if_same_length = gpt41['avg_time'] * (gpt5['output_tokens'] / gpt41['output_tokens'])
    
    print(f"1. GPT-5 generates {gpt5['output_tokens']/gpt41['output_tokens']:.1f}x more tokens by default")
    print(f"   - GPT-4.1: {gpt41['output_tokens']} tokens")
    print(f"   - GPT-5: {gpt5['output_tokens']} tokens")
    print()
    print(f"2. Token generation speed comparison:")
    print(f"   - GPT-4.1: {gpt41['output_tps']:.1f} tokens/sec")
    print(f"   - GPT-5: {gpt5['output_tps']:.1f} tokens/sec")
    print(f"   - GPT-5 is {gpt41['output_tps']/gpt5['output_tps']:.1f}x slower per token")
    print()
    print(f"3. If GPT-5 generated the same number of tokens as GPT-4.1:")
    print(f"   - Estimated time: {gpt5['time_per_output_token'] * gpt41['output_tokens']:.2f}s")
    print(f"   - Actual GPT-4.1 time: {gpt41['avg_time']:.2f}s")
    print(f"   - GPT-5 would still be {(gpt5['time_per_output_token'] * gpt41['output_tokens'])/gpt41['avg_time']:.1f}x slower")
    print()
    print(f"4. Why GPT-5 takes {gpt5['avg_time']:.1f}s vs GPT-4.1's {gpt41['avg_time']:.1f}s:")
    print(f"   - {extra_tokens} extra tokens × {gpt5['time_per_output_token']*1000:.1f}ms/token = {extra_tokens * gpt5['time_per_output_token']:.1f}s extra")
    print(f"   - Slower per-token generation adds the rest")
    
print("\nCONCLUSION:")
print("-" * 40)
print("GPT-5 is slower primarily because:")
print("1. It generates 3.8x more tokens by default (no max_tokens limit)")
print("2. Each token takes longer to generate (25.6ms vs 24.8ms)")
print("3. Without token limits, GPT-5 provides much more detailed responses")