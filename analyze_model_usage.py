#!/usr/bin/env python3
"""Analyze OpenAI API token usage by model type and compare costs between GPT-4.1 and GPT-5"""

import json

# Track usage by model
model_usage = {}
total_calls = 0

with open('openai_capture_logs/forwarded_data_20250805_225813.jsonl', 'r') as f:
    for line in f:
        try:
            data = json.loads(line)
            
            # Get model from request
            model = data.get('request', {}).get('body', {}).get('model', 'unknown')
            
            # Get usage from response
            usage = data.get('response', {}).get('body', {}).get('usage', {})
            
            if usage and model != 'unknown':
                prompt_tokens = usage.get('prompt_tokens', 0)
                completion_tokens = usage.get('completion_tokens', 0)
                
                if model not in model_usage:
                    model_usage[model] = {
                        'calls': 0,
                        'input_tokens': 0,
                        'output_tokens': 0
                    }
                
                model_usage[model]['calls'] += 1
                model_usage[model]['input_tokens'] += prompt_tokens
                model_usage[model]['output_tokens'] += completion_tokens
                total_calls += 1
                
        except Exception as e:
            pass

print("="*60)
print("MODEL USAGE ANALYSIS")
print("="*60)
print()

# Analyze each model
for model, stats in sorted(model_usage.items()):
    print(f"Model: {model}")
    print(f"  Calls: {stats['calls']} ({stats['calls']/total_calls*100:.1f}% of total)")
    print(f"  Input tokens: {stats['input_tokens']:,} (avg {stats['input_tokens']//stats['calls']:,} per call)")
    print(f"  Output tokens: {stats['output_tokens']:,} (avg {stats['output_tokens']//stats['calls']:,} per call)")
    print()

print("="*60)
print("COST ANALYSIS BY MODEL TYPE")
print("="*60)
print()

# Define pricing (per 1M tokens)
pricing = {
    'gpt-4.1': {'4.1': {'input': 2.00, 'output': 8.00}, '5': {'input': 1.25, 'output': 10.00}},
    'gpt-4.1-mini': {'4.1': {'input': 0.40, 'output': 1.60}, '5': {'input': 0.25, 'output': 2.00}}
}

# Map actual models to pricing categories  
model_mapping = {
    'gpt-4.1-2025-04-14': 'gpt-4.1',
    'gpt-4.1-mini-2025-04-14': 'gpt-4.1-mini',
    'gpt-4o': 'gpt-4.1',  # fallback mappings
    'gpt-4o-mini': 'gpt-4.1-mini'
}

# Calculate costs
total_cost_41 = 0
total_cost_5 = 0
mini_calls = 0
full_calls = 0
mini_input = 0
mini_output = 0
full_input = 0
full_output = 0

for model, stats in model_usage.items():
    # Determine pricing category
    price_category = None
    for pattern, category in model_mapping.items():
        if pattern in model:
            price_category = category
            break
    
    if not price_category:
        print(f"Warning: Unknown model {model}, skipping cost calculation")
        continue
    
    # Track mini vs full usage
    if 'mini' in price_category:
        mini_calls += stats['calls']
        mini_input += stats['input_tokens']
        mini_output += stats['output_tokens']
    else:
        full_calls += stats['calls']
        full_input += stats['input_tokens']
        full_output += stats['output_tokens']
    
    # Calculate costs for this model
    input_m = stats['input_tokens'] / 1_000_000
    output_m = stats['output_tokens'] / 1_000_000
    
    cost_41 = input_m * pricing[price_category]['4.1']['input'] + output_m * pricing[price_category]['4.1']['output']
    cost_5 = input_m * pricing[price_category]['5']['input'] + output_m * pricing[price_category]['5']['output']
    
    total_cost_41 += cost_41
    total_cost_5 += cost_5
    
    print(f"{model}:")
    print(f"  GPT-4.1 cost: ${cost_41:.4f}")
    print(f"  GPT-5 cost: ${cost_5:.4f}")
    print(f"  Difference: ${cost_5 - cost_41:.4f} ({(cost_5/cost_41 - 1)*100:.1f}%)")
    print()

print("="*60)
print("USAGE PATTERN ANALYSIS")
print("="*60)
print()

if mini_calls > 0:
    print(f"Mini model usage:")
    print(f"  Calls: {mini_calls} ({mini_calls/total_calls*100:.1f}%)")
    print(f"  Input tokens: {mini_input:,} (avg {mini_input//mini_calls if mini_calls else 0:,} per call)")
    print(f"  Output tokens: {mini_output:,} (avg {mini_output//mini_calls if mini_calls else 0:,} per call)")
    print()

if full_calls > 0:
    print(f"Full model usage:")
    print(f"  Calls: {full_calls} ({full_calls/total_calls*100:.1f}%)")
    print(f"  Input tokens: {full_input:,} (avg {full_input//full_calls if full_calls else 0:,} per call)")
    print(f"  Output tokens: {full_output:,} (avg {full_output//full_calls if full_calls else 0:,} per call)")
    print()

print("When each model is used:")
print("-" * 40)
if mini_calls > 0 and mini_input > 0:
    print(f"Mini model: Used for {mini_calls/total_calls*100:.1f}% of calls")
    print(f"  Average context: {mini_input//mini_calls if mini_calls else 0:,} tokens")
    print(f"  Typical use cases: Shorter interactions, simple queries")
    
if full_calls > 0 and full_input > 0:
    print(f"Full model: Used for {full_calls/total_calls*100:.1f}% of calls")
    print(f"  Average context: {full_input//full_calls if full_calls else 0:,} tokens")
    print(f"  Typical use cases: Complex game logic, full context needed")

print()
print("="*60)
print("TOTAL SESSION COSTS")
print("="*60)
print()

print(f"GPT-4.1 family total: ${total_cost_41:.4f}")
print(f"GPT-5 family total: ${total_cost_5:.4f}")
print(f"Savings with GPT-5: ${total_cost_41 - total_cost_5:.4f} ({(1 - total_cost_5/total_cost_41)*100:.1f}%)")
print()

# Project monthly and yearly costs
sessions_per_month = 30
print(f"Projected costs (assuming {sessions_per_month} sessions/month):")
print(f"  GPT-4.1: ${total_cost_41 * sessions_per_month:.2f}/month, ${total_cost_41 * sessions_per_month * 12:.2f}/year")
print(f"  GPT-5: ${total_cost_5 * sessions_per_month:.2f}/month, ${total_cost_5 * sessions_per_month * 12:.2f}/year")
print(f"  Monthly savings: ${(total_cost_41 - total_cost_5) * sessions_per_month:.2f}")
print(f"  Yearly savings: ${(total_cost_41 - total_cost_5) * sessions_per_month * 12:.2f}")