#!/usr/bin/env python3
"""
Complete LLM Integration Demo
Shows both Dynamic Opportunity Descriptions and Tool Selection Intelligence
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables from global PythonUtils directory
load_dotenv("C:/Users/markw/PythonUtils/.env")

# Add current directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_without_llm():
    """Show base descriptions and all tools without LLM"""
    print("📋 BASE ASSESSMENT REPORT (Without LLM)")
    print("=" * 60)
    
    base_descriptions = {
        'customer-service': 'Implement AI-powered chatbots and automated response systems to handle routine customer inquiries and support requests.',
        'document-processing': 'Automate repetitive business processes including data entry, document processing, and workflow management.',
        'data-analysis': 'Implement AI-powered analytics and reporting to extract actionable insights from business data.',
        'process-automation': 'Establish AI-ready infrastructure and processes to enable future automation and intelligence initiatives.'
    }
    
    for opp_type, desc in base_descriptions.items():
        print(f"\n🎯 {opp_type.replace('-', ' ').title()}")
        print(f"   Description: {desc}")
        print(f"   Tools: All tools in category shown (not personalized)")

def demo_with_llm():
    """Show personalized descriptions and intelligent tool selection with LLM"""
    try:
        from llm_service import llm_service
        
        if not llm_service.enabled:
            print("\n❌ LLM service is disabled - no API keys found")
            print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY to see personalized content")
            return
        
        print(f"\n🤖 ENHANCED ASSESSMENT REPORT (With {llm_service.default_provider.upper()})")
        print("=" * 60)
        
        # Load available tools
        try:
            with open('saas_tools_database.json', 'r') as file:
                saas_solutions = json.load(file)
        except FileNotFoundError:
            print("❌ Could not find saas_tools_database.json")
            return
        
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
        
        print(f"\n🏢 Company: {company['company_name']} ({company['industry']})")
        print(f"   Size: {company['company_size']}")
        print(f"   Role: {company['role']}")
        print(f"   Challenges: {', '.join(company['challenges'])}")
        print(f"   Current Tech: {company['current_tech']}")
        print(f"   AI Experience: {company['ai_experience']}")
        
        base_descriptions = {
            'customer-service': 'Implement AI-powered chatbots and automated response systems to handle routine customer inquiries and support requests.',
            'document-processing': 'Automate repetitive business processes including data entry, document processing, and workflow management.',
            'data-analysis': 'Implement AI-powered analytics and reporting to extract actionable insights from business data.',
            'process-automation': 'Establish AI-ready infrastructure and processes to enable future automation and intelligence initiatives.'
        }
        
        opportunity_types = [
            ('customer-service', 'customer_service'),
            ('document-processing', 'workflow_automation'),
            ('data-analysis', 'business_intelligence'),
            ('process-automation', 'workflow_automation')
        ]
        
        for opp_type, tool_category in opportunity_types:
            print(f"\n🎯 {opp_type.replace('-', ' ').title()}")
            print(f"   Base Description: {base_descriptions[opp_type]}")
            
            try:
                # Generate personalized description
                personalized = llm_service.generate_personalized_opportunity_description(
                    opp_type,
                    company,
                    base_descriptions[opp_type]
                )
                print(f"   Personalized Description: {personalized}")
                
                # Select relevant tools
                available_tools = saas_solutions.get(tool_category, [])
                selected_tools = llm_service.select_relevant_tools(
                    opp_type,
                    company,
                    available_tools,
                    max_tools=2
                )
                
                print(f"   Recommended Tools ({len(selected_tools)} of {len(available_tools)} available):")
                for tool in selected_tools:
                    print(f"     ✅ {tool['name']} - {tool['cost']}")
                    print(f"        Best for: {tool['best_for']}")
                
                if personalized != base_descriptions[opp_type]:
                    print("   ✅ Successfully personalized description!")
                if len(selected_tools) > 0:
                    print("   ✅ Successfully selected relevant tools!")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
    except ImportError:
        print("\n❌ Could not import LLM service")

def main():
    """Main demonstration function"""
    print("🚀 AI Consultant Platform - Complete LLM Integration Demo")
    print("=" * 80)
    
    # Show base assessment report
    demo_without_llm()
    
    # Show enhanced assessment report
    demo_with_llm()
    
    print("\n" + "=" * 80)
    print("💡 The enhanced report provides:")
    print("   • Personalized opportunity descriptions tailored to the company")
    print("   • Intelligent tool selection based on company profile")
    print("   • More relevant and actionable recommendations")
    print("\n🔧 To enable LLM features, set your API keys in the .env file:")
    print("   OPENAI_API_KEY=your_key_here")
    print("   or")
    print("   ANTHROPIC_API_KEY=your_key_here")

if __name__ == "__main__":
    main()
