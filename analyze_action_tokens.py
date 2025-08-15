#!/usr/bin/env python3
"""
Analyze token count of actions in conversation history using OpenAI's tiktoken.
"""

import json
import tiktoken
from typing import Dict, List

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens using OpenAI's tiktoken for specific model."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def analyze_conversation_actions(file_path: str):
    """Analyze the token usage of actions vs narration in conversation history."""
    
    # Load conversation history
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            conversation = json.load(f)
    except Exception as e:
        print(f"Error loading file: {e}")
        return
    
    print(f"Analyzing: {file_path}")
    print("=" * 80)
    
    # Track statistics
    total_messages = 0
    messages_with_json = 0
    total_tokens = 0
    narration_tokens = 0
    action_tokens = 0
    full_json_tokens = 0
    
    # Track action patterns
    action_types = {}
    
    for message in conversation:
        if message.get('role') == 'assistant' and message.get('content'):
            total_messages += 1
            content = message['content']
            
            # Count total tokens for the message
            message_tokens = count_tokens(content)
            total_tokens += message_tokens
            
            # Try to parse as JSON to find actions
            try:
                parsed = json.loads(content)
                messages_with_json += 1
                
                # Count full JSON tokens
                full_json_tokens += message_tokens
                
                # Extract and count narration
                if 'narration' in parsed:
                    narration_text = parsed['narration']
                    narration_token_count = count_tokens(narration_text)
                    narration_tokens += narration_token_count
                
                # Extract and count actions
                if 'actions' in parsed and isinstance(parsed['actions'], list):
                    # Convert just the actions array to JSON string
                    actions_json = json.dumps(parsed['actions'], indent=2)
                    actions_token_count = count_tokens(actions_json)
                    action_tokens += actions_token_count
                    
                    # Track action types
                    for action in parsed['actions']:
                        action_type = action.get('action', 'unknown')
                        if action_type not in action_types:
                            action_types[action_type] = {
                                'count': 0,
                                'total_tokens': 0,
                                'examples': []
                            }
                        
                        # Count tokens for this specific action
                        single_action_json = json.dumps(action, indent=2)
                        single_action_tokens = count_tokens(single_action_json)
                        
                        action_types[action_type]['count'] += 1
                        action_types[action_type]['total_tokens'] += single_action_tokens
                        
                        # Store first few examples
                        if len(action_types[action_type]['examples']) < 3:
                            action_types[action_type]['examples'].append({
                                'action': action,
                                'tokens': single_action_tokens
                            })
                
            except json.JSONDecodeError:
                # Not JSON, skip
                pass
    
    # Calculate percentages
    action_percentage = (action_tokens / total_tokens * 100) if total_tokens > 0 else 0
    narration_percentage = (narration_tokens / total_tokens * 100) if total_tokens > 0 else 0
    json_overhead = full_json_tokens - (narration_tokens + action_tokens)
    json_overhead_percentage = (json_overhead / total_tokens * 100) if total_tokens > 0 else 0
    
    # Analyze system prompt (first message)
    system_prompt_tokens = 0
    total_conversation_tokens = count_tokens(json.dumps(conversation))
    
    if conversation and conversation[0].get('role') == 'system':
        system_prompt = conversation[0].get('content', '')
        system_prompt_tokens = count_tokens(system_prompt)
        system_prompt_percentage = (system_prompt_tokens / total_conversation_tokens * 100)
    
    # Print results
    print(f"SYSTEM PROMPT ANALYSIS:")
    print(f"System prompt tokens: {system_prompt_tokens:,}")
    print(f"Total conversation tokens (all messages): {total_conversation_tokens:,}")
    print(f"System prompt percentage of total conversation: {system_prompt_percentage:.1f}%")
    print()
    print(f"Total assistant messages: {total_messages}")
    print(f"Messages with JSON structure: {messages_with_json}")
    print(f"\nTOKEN ANALYSIS:")
    print(f"Total tokens in all assistant messages: {total_tokens:,}")
    print(f"Narration tokens: {narration_tokens:,} ({narration_percentage:.1f}%)")
    print(f"Action tokens: {action_tokens:,} ({action_percentage:.1f}%)")
    print(f"JSON structure overhead: {json_overhead:,} ({json_overhead_percentage:.1f}%)")
    
    print(f"\nACTION TYPE BREAKDOWN:")
    print("-" * 80)
    
    # Sort action types by frequency
    sorted_actions = sorted(action_types.items(), key=lambda x: x[1]['count'], reverse=True)
    
    for action_name, data in sorted_actions:
        avg_tokens = data['total_tokens'] / data['count'] if data['count'] > 0 else 0
        print(f"\n{action_name}:")
        print(f"  Count: {data['count']}")
        print(f"  Total tokens: {data['total_tokens']:,}")
        print(f"  Average tokens per action: {avg_tokens:.1f}")
        
        if data['examples']:
            print(f"  Examples:")
            for i, example in enumerate(data['examples'], 1):
                print(f"    {i}. {json.dumps(example['action'])} ({example['tokens']} tokens)")
    
    # Calculate potential savings
    print(f"\nCOMPRESSION POTENTIAL:")
    print("-" * 80)
    print(f"If all actions were removed after processing:")
    print(f"  - Would save {action_tokens:,} tokens ({action_percentage:.1f}% of total)")
    print(f"  - Conversation would be {total_tokens - action_tokens:,} tokens")
    
    print(f"\nIf only keeping narration (removing all JSON structure):")
    print(f"  - Would save {total_tokens - narration_tokens:,} tokens")
    print(f"  - Conversation would be {narration_tokens:,} tokens ({narration_percentage:.1f}% of original)")
    
    # Estimate cost savings
    # GPT-4 pricing (approximate)
    input_cost_per_1k = 0.01  # $0.01 per 1K tokens
    saved_cost = (action_tokens / 1000) * input_cost_per_1k
    
    print(f"\nCOST ANALYSIS (GPT-4 input pricing):")
    print(f"  - Current conversation cost: ${(total_tokens / 1000) * input_cost_per_1k:.2f}")
    print(f"  - Cost without actions: ${((total_tokens - action_tokens) / 1000) * input_cost_per_1k:.2f}")
    print(f"  - Potential savings: ${saved_cost:.2f}")

if __name__ == "__main__":
    # First install tiktoken if needed
    try:
        import tiktoken
    except ImportError:
        print("Installing tiktoken...")
        import subprocess
        subprocess.check_call(["pip", "install", "tiktoken"])
        import tiktoken
    
    # Analyze the main conversation history
    analyze_conversation_actions("modules/conversation_history/conversation_history.json")