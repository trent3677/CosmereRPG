#!/usr/bin/env python3
"""
OpenAI Usage Tracker - Uses built-in usage data from OpenAI API responses
No external dependencies, no token counting - just collects what OpenAI provides
"""

import time
from datetime import datetime, timedelta
from collections import deque
import threading

class OpenAIUsageTracker:
    """Tracks OpenAI's built-in usage statistics"""
    
    def __init__(self):
        # Cumulative totals
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_tokens = 0
        self.total_requests = 0
        
        # Sliding window for TPM/RPM (last 60 seconds)
        self.usage_history = deque()  # (timestamp, prompt_tokens, completion_tokens, total_tokens)
        
        self.lock = threading.Lock()
    
    def track(self, response):
        """Track usage from OpenAI response - uses built-in data only"""
        try:
            # Only proceed if response has usage data
            if not hasattr(response, 'usage'):
                return
            
            with self.lock:
                now = datetime.now()
                
                # Extract OpenAI's provided usage data
                usage = response.usage
                prompt_tokens = getattr(usage, 'prompt_tokens', 0)
                completion_tokens = getattr(usage, 'completion_tokens', 0)
                total_tokens = getattr(usage, 'total_tokens', 0)
                
                # Update totals
                self.total_prompt_tokens += prompt_tokens
                self.total_completion_tokens += completion_tokens
                self.total_tokens += total_tokens
                self.total_requests += 1
                
                # Add to history
                self.usage_history.append((now, prompt_tokens, completion_tokens, total_tokens))
                
                # Clean old entries (older than 60 seconds)
                cutoff = now - timedelta(seconds=60)
                while self.usage_history and self.usage_history[0][0] < cutoff:
                    self.usage_history.popleft()
                    
        except:
            pass  # Silently ignore any errors
    
    def get_current_stats(self):
        """Get current usage statistics"""
        try:
            with self.lock:
                # Clean old entries first (older than 60 seconds)
                now = datetime.now()
                cutoff = now - timedelta(seconds=60)
                while self.usage_history and self.usage_history[0][0] < cutoff:
                    self.usage_history.popleft()
                
                # Calculate tokens/requests in the last minute
                tpm = sum(entry[3] for entry in self.usage_history)  # Sum of total_tokens
                rpm = len(self.usage_history)  # Number of requests
                
                return {
                    'tpm': tpm,
                    'rpm': rpm,
                    'total_tokens': self.total_tokens,
                    'total_prompt_tokens': self.total_prompt_tokens,
                    'total_completion_tokens': self.total_completion_tokens,
                    'total_requests': self.total_requests
                }
        except:
            return {
                'tpm': 0,
                'rpm': 0,
                'total_tokens': 0,
                'total_prompt_tokens': 0,
                'total_completion_tokens': 0,
                'total_requests': 0
            }

# Global tracker instance
_global_tracker = None

def get_global_tracker():
    """Get or create the global usage tracker"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = OpenAIUsageTracker()
    return _global_tracker

def track_response(response):
    """Track an OpenAI response (safe - never throws)"""
    try:
        tracker = get_global_tracker()
        tracker.track(response)
        return True
    except:
        return False

def get_usage_stats():
    """Get current usage statistics (safe - always returns valid data)"""
    try:
        tracker = get_global_tracker()
        return tracker.get_current_stats()
    except:
        return {
            'tpm': 0,
            'rpm': 0,
            'total_tokens': 0,
            'total_prompt_tokens': 0,
            'total_completion_tokens': 0,
            'total_requests': 0
        }