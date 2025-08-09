#!/usr/bin/env python3
"""
Demonstration script showing the difference between base and LLM-generated descriptions
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
# Load environment variables from global PythonUtils directory
load_dotenv("C:/Users/markw/PythonUtils/.env")

# Add current directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_without_llm():
    """Show base descriptions without LLM"""
    print("📋 BASE DESCRIPTIONS (Without LLM)")
    print("=" * 50)
    
    base_descriptions = {
        'customer-service': 'Implement AI-powered chatbots and automated response systems to handle routine customer inquiries and support requests.',
        'document-processing': 'Automate repetitive business processes including data entry, document processing, and workflow management.',
        'data-analysis': 'Implement AI-powered analytics and reporting to extract actionable insights from business data.',
        'process-automation': 'Establish AI-ready infrastructure and processes to enable future automation and intelligence initiatives.'
    }
    
    for opp_type, desc in base_descriptions.items():
        print(f"\n🎯 {opp_type.replace('-', ' ').title()}")
        print(f"   {desc}")

def demo_with_llm():
    """Show personalized descriptions with LLM"""
    try:
        from llm_service import llm_service
        
        if not llm_service.enabled:
            print("\n❌ LLM service is disabled - no API keys found")
            print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY to see personalized descriptions")
            return
        
        print(f"\n🤖 PERSONALIZED DESCRIPTIONS (With {llm_service.default_provider.upper()})")
        print("=" * 50)
        
        # Sample company for demonstration
        company = {
            'company_name': 'Acme Automotive',
            'industry': 'Automotive',
            'company_size': '50-200 employees',
            'role': 'CEO',
            'challenges': ['customer-service', 'manual-processes'],
            'current_tech': 'Basic CRM and accounting software',
            'ai_experience': 'Beginner'
        }
        
        base_descriptions = {
            'customer-service': 'Implement AI-powered chatbots and automated response systems to handle routine customer inquiries and support requests.',
            'document-processing': 'Automate repetitive business processes including data entry, document processing, and workflow management.',
            'data-analysis': 'Implement AI-powered analytics and reporting to extract actionable insights from business data.',
            'process-automation': 'Establish AI-ready infrastructure and processes to enable future automation and intelligence initiatives.'
        }
        
        print(f"\n🏢 Company: {company['company_name']} ({company['industry']})")
        print(f"   Size: {company['company_size']}")
        print(f"   Role: {company['role']}")
        print(f"   Challenges: {', '.join(company['challenges'])}")
        print(f"   Current Tech: {company['current_tech']}")
        print(f"   AI Experience: {company['ai_experience']}")
        
        for opp_type, base_desc in base_descriptions.items():
            print(f"\n🎯 {opp_type.replace('-', ' ').title()}")
            print(f"   Base: {base_desc}")
            
            try:
                personalized = llm_service.generate_personalized_opportunity_description(
                    opp_type,
                    company,
                    base_desc
                )
                
                print(f"   Personalized: {personalized}")
                
                if personalized != base_desc:
                    print("   ✅ Successfully personalized!")
                else:
                    print("   ⚠️  Using base description")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
    except ImportError:
        print("\n❌ Could not import LLM service")

def main():
    """Main demonstration function"""
    print("🚀 AI Consultant Platform - LLM Integration Demo")
    print("=" * 60)
    
    # Show base descriptions
    demo_without_llm()
    
    # Show personalized descriptions
    demo_with_llm()
    
    print("\n" + "=" * 60)
    print("💡 The personalized descriptions are tailored to the specific company context,")
    print("   making the recommendations much more relevant and actionable!")
    print("\n🔧 To enable LLM features, set your API keys in the .env file:")
    print("   OPENAI_API_KEY=your_key_here")
    print("   or")
    print("   ANTHROPIC_API_KEY=your_key_here")

if __name__ == "__main__":
    main()
