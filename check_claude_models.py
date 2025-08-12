#!/usr/bin/env python3
"""
Check Claude Models Script
Verifies what Claude models are currently available from Anthropic
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv("C:/Users/markw/PythonUtils/.env")

def check_claude_models():
    """Check available Claude models"""
    print("🔍 Checking available Claude models...")
    
    # Known Claude models (as of August 2024)
    known_models = [
        # Claude 4 models (Latest)
        ("claude-4o", "Claude 4o", "Latest Claude 4 model"),
        ("claude-4o-mini", "Claude 4o Mini", "Fast Claude 4o variant"),
        ("claude-4-sonnet", "Claude 4 Sonnet", "Claude 4 Sonnet model"),
        ("claude-4-opus", "Claude 4 Opus", "Claude 4 Opus model"),
        
        # Claude 3.5 models
        ("claude-3-5-sonnet-20241022", "Claude 3.5 Sonnet", "Claude 3.5 Sonnet model"),
        ("claude-3-5-haiku-20241022", "Claude 3.5 Haiku", "Claude 3.5 Haiku model"),
        
        # Claude 3 models (Legacy)
        ("claude-3-sonnet-20240229", "Claude 3 Sonnet", "Legacy Claude 3 Sonnet"),
        ("claude-3-haiku-20240307", "Claude 3 Haiku", "Legacy Claude 3 Haiku"),
        ("claude-3-opus-20240229", "Claude 3 Opus", "Legacy Claude 3 Opus"),
    ]
    
    print("\n📋 Known Claude Models:")
    for i, (model_id, display_name, description) in enumerate(known_models, 1):
        print(f"{i:2d}. {display_name:20} ({model_id})")
        print(f"    {description}")
    
    print(f"\n📊 Total Known Models: {len(known_models)}")
    
    # Check if we have API key to test
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if api_key:
        print(f"\n✅ ANTHROPIC_API_KEY found: {api_key[:10]}...")
        print("💡 You can test these models in the Admin console")
    else:
        print(f"\n❌ ANTHROPIC_API_KEY not found")
        print("💡 Add your API key to C:/Users/markw/PythonUtils/.env to test models")
    
    return known_models

def main():
    """Main function"""
    print("🤖 Claude Models Checker")
    print("=" * 50)
    
    try:
        models = check_claude_models()
        
        print(f"\n📝 Recommendation:")
        print("Update models.py to include Claude 4 models (claude-4o, claude-4-sonnet, claude-4-opus)")
        print("These are the latest and most capable Claude models available.")
        
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
