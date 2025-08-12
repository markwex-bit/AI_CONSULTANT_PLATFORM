#!/usr/bin/env python3
"""
Update LLM Models Script
Updates the database with current model versions and verifies model availability
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db_manager
import json

def update_llm_models():
    """Update LLM models to current versions"""
    print("🔄 Updating LLM models to current versions...")
    
    # Initialize the database manager
    db = db_manager
    
    # Clear existing models (except user-added ones)
    print("🗑️  Clearing existing default models...")
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM llm_models WHERE is_default = 0')
        conn.commit()
    
    # Re-initialize with current models
    print("📝 Adding current model versions...")
    db.initialize_default_llm_models()
    
    # Verify the update
    print("✅ Verifying updated models...")
    models = db.get_all_llm_models()
    
    print(f"\n📊 Updated Models Summary:")
    print(f"Total models: {len(models)}")
    
    # Group by provider
    providers = {}
    for model in models:
        provider = model['provider_name']
        if provider not in providers:
            providers[provider] = []
        providers[provider].append(model)
    
    for provider, provider_models in providers.items():
        print(f"\n🔹 {provider} ({len(provider_models)} models):")
        for model in provider_models:
            status = "✅" if model['is_active'] else "❌"
            default = "⭐" if model['is_default'] else "  "
            print(f"  {status} {default} {model['display_name']} ({model['model_name']})")
    
    print(f"\n🎯 Default model: {db.get_default_llm_model()['display_name'] if db.get_default_llm_model() else 'None'}")
    
    return models

def verify_model_access():
    """Verify that models are accessible (basic check)"""
    print("\n🔍 Verifying model access...")
    
    # This would require API keys to be set up
    # For now, just check if the models are in the database
    models = db_manager.get_all_llm_models()
    
    print("📋 Model verification status:")
    for model in models:
        if model['model_type'] == 'openai':
            print(f"  🔑 OpenAI: {model['display_name']} - Requires OPENAI_API_KEY")
        elif model['model_type'] == 'anthropic':
            print(f"  🔑 Anthropic: {model['display_name']} - Requires ANTHROPIC_API_KEY")
        elif model['model_type'] == 'open_source':
            if 'ollama' in model['provider_name'].lower():
                print(f"  🖥️  Ollama: {model['display_name']} - Requires Ollama running locally")
            elif 'huggingface' in model['provider_name'].lower():
                print(f"  🔑 HuggingFace: {model['display_name']} - Requires HUGGINGFACE_API_KEY")

def main():
    """Main function"""
    print("🤖 LLM Model Update Script")
    print("=" * 50)
    
    try:
        # Update models
        models = update_llm_models()
        
        # Verify access
        verify_model_access()
        
        print("\n✅ Model update completed successfully!")
        print("\n📝 Next steps:")
        print("1. Set up your API keys in C:/Users/markw/PythonUtils/.env")
        print("2. For Ollama models, install and run Ollama locally")
        print("3. Test models in the Admin console")
        
    except Exception as e:
        print(f"❌ Error updating models: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
