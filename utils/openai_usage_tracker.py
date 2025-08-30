#!/usr/bin/env python3
"""
OpenAI Usage Tracker - Uses built-in usage data from OpenAI API responses
Enhanced with telemetry logging and spike detection for migration analysis
"""

import json
import time
from datetime import datetime, timedelta
from collections import deque
import threading
from pathlib import Path
import traceback

class OpenAIUsageTracker:
    """Tracks OpenAI's built-in usage statistics with enhanced telemetry"""
    
    def __init__(self, telemetry_log="telemetry_log.jsonl"):
        # Cumulative totals
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_tokens = 0
        self.total_requests = 0
        
        # Sliding window for TPM/RPM (last 60 seconds)
        self.usage_history = deque()  # (timestamp, prompt_tokens, completion_tokens, total_tokens, context)
        
        # Spike tracking
        self.max_single_call_tokens = 0
        self.max_single_call_context = None
        self.max_single_call_timestamp = None
        
        self.max_tpm_observed = 0
        self.max_tpm_timestamp = None
        
        self.max_rpm_observed = 0
        self.max_rpm_timestamp = None
        
        # Per-endpoint tracking
        self.endpoint_stats = {}  # endpoint -> {'count': N, 'total_tokens': N, 'max_tokens': N}
        
        # Session start time
        self.session_start = datetime.now()
        
        # Telemetry log file
        self.telemetry_log = Path(telemetry_log)
        
        self.lock = threading.Lock()
    
    def track(self, response, context=None):
        """Track usage from OpenAI response with enhanced telemetry"""
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
                
                # Extract model from response if available
                model = "unknown"
                if hasattr(response, 'model'):
                    model = response.model
                elif context and isinstance(context, dict) and 'model' in context:
                    model = context['model']
                
                # Update totals
                self.total_prompt_tokens += prompt_tokens
                self.total_completion_tokens += completion_tokens
                self.total_tokens += total_tokens
                self.total_requests += 1
                
                # Track spike - individual call
                if total_tokens > self.max_single_call_tokens:
                    self.max_single_call_tokens = total_tokens
                    self.max_single_call_context = {
                        'timestamp': now.isoformat(),
                        'tokens': total_tokens,
                        'model': model,
                        'context': context or {}
                    }
                    self.max_single_call_timestamp = now
                    
                    # Log spike to file
                    self._log_spike(total_tokens, model, context)
                
                # Add to history with context
                self.usage_history.append((now, prompt_tokens, completion_tokens, total_tokens, context))
                
                # Clean old entries (older than 60 seconds)
                cutoff = now - timedelta(seconds=60)
                while self.usage_history and self.usage_history[0][0] < cutoff:
                    self.usage_history.popleft()
                
                # Calculate current TPM/RPM
                tpm = sum(entry[3] for entry in self.usage_history)
                rpm = len(self.usage_history)
                
                # Track TPM/RPM spikes
                if tpm > self.max_tpm_observed:
                    self.max_tpm_observed = tpm
                    self.max_tpm_timestamp = now
                    
                if rpm > self.max_rpm_observed:
                    self.max_rpm_observed = rpm
                    self.max_rpm_timestamp = now
                
                # Track per-endpoint stats
                endpoint = 'unknown'
                if context:
                    if isinstance(context, str):
                        endpoint = context
                    elif isinstance(context, dict):
                        endpoint = context.get('endpoint', 'unknown')
                
                if endpoint not in self.endpoint_stats:
                    self.endpoint_stats[endpoint] = {
                        'count': 0,
                        'total_tokens': 0,
                        'max_tokens': 0,
                        'models_used': set()
                    }
                
                self.endpoint_stats[endpoint]['count'] += 1
                self.endpoint_stats[endpoint]['total_tokens'] += total_tokens
                self.endpoint_stats[endpoint]['max_tokens'] = max(
                    self.endpoint_stats[endpoint]['max_tokens'], 
                    total_tokens
                )
                self.endpoint_stats[endpoint]['models_used'].add(model)
                
                # Log telemetry entry
                self._log_telemetry(now, prompt_tokens, completion_tokens, total_tokens, model, context)
                    
        except Exception as e:
            print(f"DEBUG: [TELEMETRY] Error tracking: {e}")
            traceback.print_exc()
    
    def _log_telemetry(self, timestamp, prompt_tokens, completion_tokens, total_tokens, model, context):
        """Log telemetry entry to file"""
        try:
            entry = {
                'timestamp': timestamp.isoformat(),
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens,
                'model': model,
                'context': context or {},
                'session_elapsed': str(timestamp - self.session_start)
            }
            with open(self.telemetry_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            print(f"DEBUG: [TELEMETRY] Error logging: {e}")
    
    def _log_spike(self, tokens, model, context):
        """Log spike detection to file"""
        try:
            spike_entry = {
                'type': 'spike_detected',
                'timestamp': datetime.now().isoformat(),
                'tokens': tokens,
                'model': model,
                'context': context or {},
                'previous_max': self.max_single_call_tokens
            }
            with open(self.telemetry_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(spike_entry) + '\n')
        except Exception as e:
            print(f"DEBUG: [TELEMETRY] Error logging spike: {e}")
    
    def get_current_stats(self):
        """Get enhanced usage statistics with telemetry data"""
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
                
                # Prepare endpoint summary
                endpoint_summary = {}
                for endpoint, stats in self.endpoint_stats.items():
                    endpoint_summary[endpoint] = {
                        'count': stats['count'],
                        'total_tokens': stats['total_tokens'],
                        'avg_tokens': stats['total_tokens'] // stats['count'] if stats['count'] > 0 else 0,
                        'max_tokens': stats['max_tokens'],
                        'models': list(stats['models_used'])
                    }
                
                return {
                    # Current rates
                    'tpm': tpm,
                    'rpm': rpm,
                    
                    # Session totals
                    'total_tokens': self.total_tokens,
                    'total_prompt_tokens': self.total_prompt_tokens,
                    'total_completion_tokens': self.total_completion_tokens,
                    'total_requests': self.total_requests,
                    
                    # Spike tracking
                    'max_single_call': {
                        'tokens': self.max_single_call_tokens,
                        'timestamp': self.max_single_call_timestamp.isoformat() if self.max_single_call_timestamp else None,
                        'context': self.max_single_call_context
                    },
                    'max_tpm': {
                        'value': self.max_tpm_observed,
                        'timestamp': self.max_tpm_timestamp.isoformat() if self.max_tpm_timestamp else None
                    },
                    'max_rpm': {
                        'value': self.max_rpm_observed,
                        'timestamp': self.max_rpm_timestamp.isoformat() if self.max_rpm_timestamp else None
                    },
                    
                    # Per-endpoint breakdown
                    'endpoints': endpoint_summary,
                    
                    # Session info
                    'session_duration': str(datetime.now() - self.session_start),
                    'avg_tokens_per_request': self.total_tokens // self.total_requests if self.total_requests > 0 else 0
                }
        except Exception as e:
            print(f"DEBUG: [TELEMETRY] Error getting stats: {e}")
            return {
                'tpm': 0,
                'rpm': 0,
                'total_tokens': 0,
                'total_prompt_tokens': 0,
                'total_completion_tokens': 0,
                'total_requests': 0,
                'error': str(e)
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