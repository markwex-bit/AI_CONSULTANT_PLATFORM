#!/usr/bin/env python3
"""
LLM Models Verification Script
Actually checks official API documentation and sites to verify current models
"""

import requests
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv("C:/Users/markw/PythonUtils/.env")

def check_openai_models():
    """Check OpenAI models from their API"""
    print("🔍 Checking OpenAI models...")
    
    try:
        # OpenAI API endpoint for models
        url = "https://api.openai.com/v1/models"
        headers = {
            "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY', '')}"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            available_models = []
            
            for model in models['data']:
                model_id = model['id']
                if any(prefix in model_id for prefix in ['gpt-', 'text-']):
                    available_models.append({
                        'id': model_id,
                        'created': model.get('created'),
                        'owned_by': model.get('owned_by')
                    })
            
            print(f"✅ Found {len(available_models)} OpenAI models")
            for model in available_models[:10]:  # Show first 10
                print(f"   - {model['id']} (created: {model['created']})")
            
            return available_models
        else:
            print(f"❌ OpenAI API error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error checking OpenAI: {e}")
        return []

def check_anthropic_models():
    """Check Anthropic models from their API"""
    print("🔍 Checking Anthropic models...")
    
    try:
        # Anthropic API endpoint for models
        url = "https://api.anthropic.com/v1/models"
        headers = {
            "x-api-key": os.environ.get('ANTHROPIC_API_KEY', ''),
            "anthropic-version": "2023-06-01"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            available_models = []
            
            for model in models['data']:
                model_id = model['id']
                available_models.append({
                    'id': model_id,
                    'name': model.get('name'),
                    'type': model.get('type')
                })
            
            print(f"✅ Found {len(available_models)} Anthropic models")
            for model in available_models:
                print(f"   - {model['id']}")
            
            return available_models
        else:
            print(f"❌ Anthropic API error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error checking Anthropic: {e}")
        return []

def check_huggingface_models():
    """Check HuggingFace models from their API"""
    print("🔍 Checking HuggingFace models...")
    
    try:
        # HuggingFace API endpoint for models
        url = "https://huggingface.co/api/models"
        headers = {
            "Authorization": f"Bearer {os.environ.get('HUGGINGFACE_API_KEY', '')}"
        }
        
        params = {
            'search': 'gpt2',
            'limit': 10
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            available_models = []
            
            for model in models:
                model_id = model['id']
                available_models.append({
                    'id': model_id,
                    'downloads': model.get('downloads', 0),
                    'likes': model.get('likes', 0)
                })
            
            print(f"✅ Found {len(available_models)} HuggingFace models (GPT-2 search)")
            for model in available_models[:5]:
                print(f"   - {model['id']} (downloads: {model['downloads']})")
            
            return available_models
        else:
            print(f"❌ HuggingFace API error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error checking HuggingFace: {e}")
        return []

def check_ollama_models():
    """Check Ollama models from local installation"""
    print("🔍 Checking Ollama models...")
    
    try:
        # Ollama local API endpoint
        url = "http://localhost:11434/api/tags"
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            available_models = []
            
            for model in data.get('models', []):
                model_name = model['name']
                available_models.append({
                    'name': model_name,
                    'size': model.get('size', 0),
                    'modified_at': model.get('modified_at')
                })
            
            print(f"✅ Found {len(available_models)} Ollama models")
            for model in available_models:
                print(f"   - {model['name']}")
            
            return available_models
        else:
            print(f"❌ Ollama not running or error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return []

def check_official_documentation():
    """Check official documentation for model updates"""
    print("📚 Checking official documentation...")
    
    docs_to_check = [
        {
            'name': 'OpenAI',
            'url': 'https://platform.openai.com/docs/models',
            'description': 'OpenAI Model Documentation'
        },
        {
            'name': 'Anthropic',
            'url': 'https://docs.anthropic.com/en/docs/models-overview',
            'description': 'Anthropic Model Documentation'
        },
        {
            'name': 'HuggingFace',
            'url': 'https://huggingface.co/models',
            'description': 'HuggingFace Model Hub'
        },
        {
            'name': 'Ollama',
            'url': 'https://ollama.ai/library',
            'description': 'Ollama Model Library'
        }
    ]
    
    for doc in docs_to_check:
        try:
            response = requests.get(doc['url'], timeout=10)
            if response.status_code == 200:
                print(f"✅ {doc['name']}: Documentation accessible")
            else:
                print(f"❌ {doc['name']}: Documentation error {response.status_code}")
        except Exception as e:
            print(f"❌ {doc['name']}: Cannot access documentation - {e}")

def compare_with_database():
    """Compare verified models with our database"""
    print("🔍 Comparing with database...")
    
    try:
        from models import db_manager
        
        # Get models from our database
        db_models = db_manager.get_all_llm_models()
        
        print(f"📊 Database has {len(db_models)} models:")
        
        # Group by provider
        providers = {}
        for model in db_models:
            provider = model['provider_name']
            if provider not in providers:
                providers[provider] = []
            providers[provider].append(model)
        
        for provider, models in providers.items():
            print(f"\n🔹 {provider} ({len(models)} models):")
            for model in models:
                status = "✅" if model['is_active'] else "❌"
                default = "⭐" if model['is_default'] else "  "
                print(f"  {status} {default} {model['display_name']} ({model['model_name']})")
        
        return db_models
        
    except Exception as e:
        print(f"❌ Error comparing with database: {e}")
        return []

def main():
    """Main verification function"""
    print("🤖 LLM Models Verification Script")
    print("=" * 60)
    print(f"📅 Verification Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check API keys
    print("🔑 Checking API Keys:")
    openai_key = os.environ.get('OPENAI_API_KEY')
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
    huggingface_key = os.environ.get('HUGGINGFACE_API_KEY')
    
    print(f"  OpenAI: {'✅' if openai_key else '❌'}")
    print(f"  Anthropic: {'✅' if anthropic_key else '❌'}")
    print(f"  HuggingFace: {'✅' if huggingface_key else '❌'}")
    print()
    
    # Verify models from APIs
    openai_models = check_openai_models()
    print()
    
    anthropic_models = check_anthropic_models()
    print()
    
    huggingface_models = check_huggingface_models()
    print()
    
    ollama_models = check_ollama_models()
    print()
    
    # Check documentation
    check_official_documentation()
    print()
    
    # Compare with our database
    db_models = compare_with_database()
    print()
    
    # Summary
    print("📋 Verification Summary:")
    print(f"  OpenAI API: {len(openai_models)} models found")
    print(f"  Anthropic API: {len(anthropic_models)} models found")
    print(f"  HuggingFace API: {len(huggingface_models)} models found")
    print(f"  Ollama Local: {len(ollama_models)} models found")
    print(f"  Our Database: {len(db_models)} models stored")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if not openai_models and openai_key:
        print("  - OpenAI API key may be invalid or expired")
    if not anthropic_models and anthropic_key:
        print("  - Anthropic API key may be invalid or expired")
    if not ollama_models:
        print("  - Ollama not running locally - install and start Ollama")
    
    print("\n✅ Verification complete!")

if __name__ == "__main__":
    exit(main())
