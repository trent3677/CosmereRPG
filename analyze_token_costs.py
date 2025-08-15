#!/usr/bin/env python3
"""Analyze OpenAI API token usage and compare costs between GPT-4.1 and GPT-5"""

import json

total_input = 0
total_output = 0
count = 0

with open('openai_capture_logs/forwarded_data_20250805_225813.jsonl', 'r') as f:
    for line in f:
        try:
            data = json.loads(line)
            usage = data.get('response', {}).get('body', {}).get('usage', {})
            if usage:
                prompt = usage.get('prompt_tokens', 0)
                completion = usage.get('completion_tokens', 0)
                total_input += prompt
                total_output += completion
                count += 1
        except:
            pass

print(f'Total API calls: {count}')
print(f'Total input tokens: {total_input:,}')
print(f'Total output tokens: {total_output:,}')
print(f'Average input per call: {total_input//count if count else 0:,}')
print(f'Average output per call: {total_output//count if count else 0:,}')
print()
print('Cost Analysis (per session):')
print('='*50)

# Calculate costs for GPT-4.1
gpt41_input_cost = (total_input / 1_000_000) * 2.00
gpt41_output_cost = (total_output / 1_000_000) * 8.00
gpt41_total = gpt41_input_cost + gpt41_output_cost

# Calculate costs for GPT-5
gpt5_input_cost = (total_input / 1_000_000) * 1.25
gpt5_output_cost = (total_output / 1_000_000) * 10.00
gpt5_total = gpt5_input_cost + gpt5_output_cost

# Calculate costs for mini versions
gpt41_mini_input = (total_input / 1_000_000) * 0.40
gpt41_mini_output = (total_output / 1_000_000) * 1.60
gpt41_mini_total = gpt41_mini_input + gpt41_mini_output

gpt5_mini_input = (total_input / 1_000_000) * 0.25
gpt5_mini_output = (total_output / 1_000_000) * 2.00
gpt5_mini_total = gpt5_mini_input + gpt5_mini_output

print(f'GPT-4.1 costs:')
print(f'  Input:  ${gpt41_input_cost:.4f}')
print(f'  Output: ${gpt41_output_cost:.4f}')
print(f'  Total:  ${gpt41_total:.4f}')
print()
print(f'GPT-5 costs:')
print(f'  Input:  ${gpt5_input_cost:.4f}')
print(f'  Output: ${gpt5_output_cost:.4f}')
print(f'  Total:  ${gpt5_total:.4f}')
print()
print(f'GPT-4.1-mini costs:')
print(f'  Input:  ${gpt41_mini_input:.4f}')
print(f'  Output: ${gpt41_mini_output:.4f}')
print(f'  Total:  ${gpt41_mini_total:.4f}')
print()
print(f'GPT-5-mini costs:')
print(f'  Input:  ${gpt5_mini_input:.4f}')
print(f'  Output: ${gpt5_mini_output:.4f}')
print(f'  Total:  ${gpt5_mini_total:.4f}')
print()
print('Comparisons:')
print(f'GPT-5 vs GPT-4.1: ${gpt5_total - gpt41_total:.4f} ({((gpt5_total/gpt41_total - 1) * 100):.1f}%)')
print(f'GPT-5-mini vs GPT-4.1-mini: ${gpt5_mini_total - gpt41_mini_total:.4f} ({((gpt5_mini_total/gpt41_mini_total - 1) * 100):.1f}%)')

# Calculate with caching (assuming 50% of input tokens could be cached)
cached_ratio = 0.5
cached_input = total_input * cached_ratio
uncached_input = total_input * (1 - cached_ratio)

gpt41_cached = (uncached_input / 1_000_000) * 2.00 + (cached_input / 1_000_000) * 0.50 + (total_output / 1_000_000) * 8.00
gpt5_cached = (uncached_input / 1_000_000) * 1.25 + (cached_input / 1_000_000) * 0.125 + (total_output / 1_000_000) * 10.00

print()
print('With 50% input caching:')
print(f'GPT-4.1 with cache: ${gpt41_cached:.4f}')
print(f'GPT-5 with cache: ${gpt5_cached:.4f}')
print(f'Savings with GPT-5: ${gpt41_cached - gpt5_cached:.4f} ({((1 - gpt5_cached/gpt41_cached) * 100):.1f}%)')