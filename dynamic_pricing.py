#!/usr/bin/env python3
"""
Dynamic Pricing System for LLM Models
Fetches current pricing from provider APIs and documentation
"""

import requests
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv("C:/Users/markw/PythonUtils/.env")

class DynamicPricing:
    """Dynamic pricing system for LLM models"""
    
    def __init__(self):
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        self.anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
        
        # Known pricing URLs and patterns
        self.pricing_sources = {
            'openai': {
                'url': 'https://openai.com/api/pricing',
                'docs_url': 'https://platform.openai.com/docs/models',
                'api_url': 'https://api.openai.com/v1/models'
            },
            'anthropic': {
                'url': 'https://www.anthropic.com/pricing',
                'docs_url': 'https://docs.anthropic.com/en/docs/models-overview',
                'api_url': 'https://api.anthropic.com/v1/models'
            }
        }
        
        # Current pricing (updated manually when providers change pricing)
        # This is the most reliable approach since most providers don't expose pricing via API
        self.current_pricing = {
            'OpenAI': {
                'gpt-5': 0.01,
                'gpt-5-nano': 0.002,
                'gpt-5-mini': 0.005,
                'gpt-4o': 0.005,
                'gpt-4o-mini': 0.00015,
                'gpt-4-turbo': 0.01,
                'gpt-3.5-turbo': 0.002
            },
            'Anthropic': {
                'claude-opus-4-1-20250805': 0.015,
                'claude-opus-4-20250514': 0.015,
                'claude-sonnet-4-20250514': 0.003,
                'claude-3-7-sonnet-20250219': 0.003,
                'claude-3-5-sonnet-20241022': 0.003,
                'claude-3-5-haiku-20241022': 0.00025,
                'claude-3-sonnet-20240229': 0.003,
                'claude-3-haiku-20240307': 0.00025,
                'claude-3-opus-20240229': 0.015
            },
            'HuggingFace': {
                'gpt2': 0.0,
                'distilgpt2': 0.0,
                'microsoft/DialoGPT-medium': 0.0
            },
            'Ollama': {
                'llama3.1:8b': 0.0,
                'llama3.1:70b': 0.0,
                'mistral:7b': 0.0,
                'codellama:7b': 0.0
            }
        }

    def get_current_pricing(self, provider: str) -> Dict[str, float]:
        """Get current pricing for a provider"""
        print(f"🔍 Getting current pricing for {provider}...")
        
        if provider in self.current_pricing:
            pricing = self.current_pricing[provider]
            print(f"✅ Found {len(pricing)} {provider} models with pricing")
            return pricing
        else:
            print(f"❌ No pricing data for {provider}")
            return {}

    def _parse_openai_pricing_page(self, content: str) -> Optional[Dict[str, float]]:
        """Parse OpenAI pricing from webpage content"""
        try:
            # Look for pricing patterns in the content
            pricing = {}
            
            # Common patterns for OpenAI pricing
            patterns = [
                r'gpt-5[^$]*\$([0-9.]+)',
                r'gpt-4[^$]*\$([0-9.]+)',
                r'gpt-3\.5[^$]*\$([0-9.]+)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    try:
                        price = float(match)
                        # Extract model name from context
                        # This is a simplified parser - would need more sophisticated logic
                        if 'gpt-5' in pattern:
                            pricing['gpt-5'] = price
                        elif 'gpt-4' in pattern:
                            pricing['gpt-4o'] = price
                        elif 'gpt-3.5' in pattern:
                            pricing['gpt-3.5-turbo'] = price
                    except ValueError:
                        continue
            
            return pricing if pricing else None
            
        except Exception as e:
            print(f"❌ Error parsing OpenAI pricing: {e}")
            return None

    def _parse_anthropic_pricing_page(self, content: str) -> Optional[Dict[str, float]]:
        """Parse Anthropic pricing from webpage content"""
        try:
            # Look for pricing patterns in the content
            pricing = {}
            
            # Common patterns for Anthropic pricing
            patterns = [
                r'claude[^$]*\$([0-9.]+)',
                r'opus[^$]*\$([0-9.]+)',
                r'sonnet[^$]*\$([0-9.]+)',
                r'haiku[^$]*\$([0-9.]+)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    try:
                        price = float(match)
                        # Extract model name from context
                        # This is a simplified parser - would need more sophisticated logic
                        if 'opus' in pattern:
                            pricing['claude-opus-4-1-20250805'] = price
                        elif 'sonnet' in pattern:
                            pricing['claude-sonnet-4-20250514'] = price
                        elif 'haiku' in pattern:
                            pricing['claude-3-5-haiku-20241022'] = price
                    except ValueError:
                        continue
            
            return pricing if pricing else None
            
        except Exception as e:
            print(f"❌ Error parsing Anthropic pricing: {e}")
            return None

    def update_database_pricing(self):
        """Update pricing in the database with current rates"""
        print("🔄 Updating database pricing...")
        
        try:
            from models import db_manager
            
            # Get current pricing for all providers
            all_pricing = {}
            for provider in ['OpenAI', 'Anthropic', 'HuggingFace', 'Ollama']:
                all_pricing[provider] = self.get_current_pricing(provider)
            
            # Get all models from database
            models = db_manager.get_all_llm_models()
            
            updated_count = 0
            
            for model in models:
                model_name = model['model_name']
                provider = model['provider_name']
                new_price = None
                
                # Find matching pricing
                if provider in all_pricing and model_name in all_pricing[provider]:
                    new_price = all_pricing[provider][model_name]
                else:
                    new_price = None
                    if provider not in all_pricing:
                        print(f"    ❌ Provider '{provider}' not found in pricing data")
                    elif model_name not in all_pricing[provider]:
                        print(f"    ❌ Model '{model_name}' not found in {provider} pricing")
                
                # Debug logging
                print(f"  Checking {model_name} ({provider}): current=${model['cost_per_1k_tokens']}, new=${new_price}")
                
                # Update if price changed
                if new_price is not None and new_price != model['cost_per_1k_tokens']:
                    success = db_manager.update_llm_model(model['id'], {
                        'cost_per_1k_tokens': new_price
                    })
                    if success:
                        updated_count += 1
                        print(f"  ✅ Updated {model_name}: ${model['cost_per_1k_tokens']} → ${new_price}")
            
            print(f"✅ Updated pricing for {updated_count} models")
            return updated_count
            
        except Exception as e:
            print(f"❌ Error updating database pricing: {e}")
            return 0

    def get_current_pricing_summary(self) -> Dict:
        """Get a summary of current pricing"""
        print("📊 Generating pricing summary...")
        
        try:
            from models import db_manager
            
            models = db_manager.get_all_llm_models()
            
            summary = {
                'total_models': len(models),
                'providers': {},
                'last_updated': datetime.now().isoformat(),
                'pricing_source': 'database'
            }
            
            for model in models:
                provider = model['provider_name']
                if provider not in summary['providers']:
                    summary['providers'][provider] = {
                        'models': [],
                        'total_cost_range': {'min': float('inf'), 'max': 0}
                    }
                
                cost = model['cost_per_1k_tokens']
                summary['providers'][provider]['models'].append({
                    'name': model['display_name'],
                    'model_id': model['model_name'],
                    'cost_per_1k': cost,
                    'is_default': model['is_default']
                })
                
                # Update cost range
                if cost < summary['providers'][provider]['total_cost_range']['min']:
                    summary['providers'][provider]['total_cost_range']['min'] = cost
                if cost > summary['providers'][provider]['total_cost_range']['max']:
                    summary['providers'][provider]['total_cost_range']['max'] = cost
            
            return summary
            
        except Exception as e:
            print(f"❌ Error generating pricing summary: {e}")
            return {}

def main():
    """Main function for testing dynamic pricing"""
    print("💰 Dynamic Pricing System")
    print("=" * 50)
    
    pricing = DynamicPricing()
    
    # Update database pricing
    updated_count = pricing.update_database_pricing()
    
    # Get pricing summary
    summary = pricing.get_current_pricing_summary()
    
    print(f"\n📋 Pricing Summary:")
    print(f"Total models: {summary.get('total_models', 0)}")
    print(f"Last updated: {summary.get('last_updated', 'Unknown')}")
    
    for provider, data in summary.get('providers', {}).items():
        print(f"\n🔹 {provider}:")
        print(f"  Models: {len(data['models'])}")
        print(f"  Cost range: ${data['total_cost_range']['min']:.4f} - ${data['total_cost_range']['max']:.4f}")
        
        # Show default model
        for model in data['models']:
            if model['is_default']:
                print(f"  Default: {model['name']} (${model['cost_per_1k']:.4f}/1K tokens)")
                break
    
    print(f"\n✅ Dynamic pricing update complete!")

if __name__ == "__main__":
    main()
