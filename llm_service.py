# llm_service.py - LLM integration for dynamic content generation
import os
import json
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from global PythonUtils directory
load_dotenv("C:/Users/markw/PythonUtils/.env")

logger = logging.getLogger(__name__)

class LLMService:
    """Service for generating dynamic content using LLMs"""
    
    def __init__(self):
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        self.anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.huggingface_api_key = os.environ.get('HUGGINGFACE_API_KEY')
        self.default_provider = os.environ.get('LLM_PROVIDER', 'openai')
        
        # Import database manager
        from models import db_manager
        self.db_manager = db_manager
        
        # Initialize default models if not exists
        self.db_manager.initialize_default_llm_models()
        
        if not self.openai_api_key and not self.anthropic_api_key and not self.huggingface_api_key:
            logger.warning("No LLM API keys found. Dynamic content will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
    
    def generate_personalized_opportunity_description(
        self, 
        opportunity_type: str, 
        company_data: Dict,
        base_description: str
    ) -> str:
        """
        Generate a personalized opportunity description based on company context
        
        Args:
            opportunity_type: Type of opportunity (e.g., 'customer-service', 'document-processing')
            company_data: Dictionary containing company information
            base_description: Base description to personalize
            
        Returns:
            Personalized description string
        """
        if not self.enabled:
            return base_description
        
        try:
            # Build company context
            company_context = self._build_company_context(company_data)
            
            # Create prompt for personalized description
            prompt = self._create_opportunity_prompt(opportunity_type, company_context, base_description)
            
            # Generate response using LLM
            response = self._call_llm(prompt)
            
            if response and len(response.strip()) > 50:  # Ensure we got a meaningful response
                return response.strip()
            else:
                logger.warning(f"LLM returned empty or too short response, using base description")
                return base_description
                
        except Exception as e:
            logger.error(f"Error generating personalized description: {e}")
            return base_description
    
    def _build_company_context(self, company_data: Dict) -> str:
        """Build a context string from company data"""
        context_parts = []
        
        if company_data.get('company_name'):
            context_parts.append(f"Company: {company_data['company_name']}")
        
        if company_data.get('industry'):
            context_parts.append(f"Industry: {company_data['industry']}")
        
        if company_data.get('company_size'):
            context_parts.append(f"Size: {company_data['company_size']}")
        
        if company_data.get('role'):
            context_parts.append(f"Contact Role: {company_data['role']}")
        
        if company_data.get('challenges'):
            challenges = company_data['challenges']
            if isinstance(challenges, list):
                challenges_str = ', '.join(challenges)
            else:
                challenges_str = str(challenges)
            context_parts.append(f"Key Challenges: {challenges_str}")
        
        if company_data.get('current_tech'):
            context_parts.append(f"Current Technology: {company_data['current_tech']}")
        
        # Include client notes if available
        if company_data.get('client_notes'):
            context_parts.append(f"Additional Context: {company_data['client_notes']}")
        
        if company_data.get('ai_experience'):
            context_parts.append(f"AI Experience: {company_data['ai_experience']}")
        
        return " | ".join(context_parts)
    
    def _create_opportunity_prompt(self, opportunity_type: str, company_context: str, base_description: str) -> str:
        """Create a prompt for generating personalized opportunity descriptions"""
        
        opportunity_templates = {
            'customer-service': {
                'title': 'Customer Service Automation',
                'focus': 'customer service, support, and communication'
            },
            'document-processing': {
                'title': 'Document Processing Automation', 
                'focus': 'document handling, data entry, and workflow automation'
            },
            'data-analysis': {
                'title': 'AI-Enhanced Business Intelligence',
                'focus': 'data analysis, reporting, and business insights'
            },
            'process-automation': {
                'title': 'Process Automation',
                'focus': 'business process optimization and automation'
            }
        }
        
        template = opportunity_templates.get(opportunity_type, {
            'title': 'AI Opportunity',
            'focus': 'business optimization'
        })
        
        prompt = f"""
You are an AI consultant helping to personalize opportunity descriptions for a business assessment report.

Company Context: {company_context}

Opportunity Type: {template['title']}
Focus Area: {template['focus']}

Base Description: {base_description}

Please create a personalized, 2-3 sentence description of this AI opportunity that:
1. References the company's specific industry and context
2. Explains how this AI solution addresses their specific challenges
3. Uses concrete, business-relevant language
4. Maintains a professional, consultative tone
5. Focuses on practical benefits and outcomes

Write only the personalized description, nothing else:
"""
        
        return prompt.strip()
    
    def _call_llm(self, prompt: str) -> Optional[str]:
        """Call the configured LLM provider"""
        # Get the current default model from database
        default_model = self.db_manager.get_default_llm_model()
        if not default_model:
            logger.error("No default LLM model configured")
            return None
        
        model_type = default_model['model_type']
        
        if model_type == 'openai' and self.openai_api_key:
            return self._call_openai(prompt, default_model)
        elif model_type == 'anthropic' and self.anthropic_api_key:
            return self._call_anthropic(prompt, default_model)
        elif model_type == 'open_source':
            return self._call_open_source(prompt, default_model)
        else:
            logger.error(f"No available LLM provider configured for model type: {model_type}")
            return None

    def call_specific_model(self, model_id: int, prompt: str) -> Optional[str]:
        """Call a specific model by ID"""
        # Get the specific model from database
        models = self.db_manager.get_all_llm_models()
        target_model = None
        for model in models:
            if model['id'] == model_id:
                target_model = model
                break
        
        if not target_model:
            logger.error(f"Model with ID {model_id} not found")
            return None
        
        model_type = target_model['model_type']
        
        if model_type == 'openai' and self.openai_api_key:
            return self._call_openai(prompt, target_model)
        elif model_type == 'anthropic' and self.anthropic_api_key:
            return self._call_anthropic(prompt, target_model)
        elif model_type == 'open_source':
            return self._call_open_source(prompt, target_model)
        else:
            logger.error(f"No available LLM provider configured for model type: {model_type}")
            return None
    
    def _call_openai(self, prompt: str, model_config: dict) -> Optional[str]:
        """Call OpenAI API"""
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model=model_config['model_name'],
                messages=[
                    {"role": "system", "content": "You are a professional AI consultant helping businesses understand AI opportunities."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=model_config.get('max_tokens', 200),
                temperature=model_config.get('temperature', 0.7)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    def _call_anthropic(self, prompt: str, model_config: dict) -> Optional[str]:
        """Call Anthropic API"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            
            response = client.messages.create(
                model=model_config['model_name'],
                max_tokens=model_config.get('max_tokens', 200),
                temperature=model_config.get('temperature', 0.7),
                system="You are a professional AI consultant helping businesses understand AI opportunities.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return None

    def _call_open_source(self, prompt: str, model_config: dict) -> Optional[str]:
        """Call Open Source API (Ollama, HuggingFace, etc.)"""
        try:
            import requests
            
            api_endpoint = model_config.get('api_endpoint')
            if not api_endpoint:
                logger.error("No API endpoint configured for open source model")
                return None
            
            # Handle different open source providers
            if 'ollama' in model_config['provider_name'].lower():
                return self._call_ollama(prompt, model_config)
            elif 'huggingface' in model_config['provider_name'].lower():
                return self._call_huggingface(prompt, model_config)
            else:
                # Generic REST API call
                return self._call_generic_api(prompt, model_config)
                
        except Exception as e:
            logger.error(f"Open Source API error: {e}")
            return None

    def _call_ollama(self, prompt: str, model_config: dict) -> Optional[str]:
        """Call Ollama API"""
        try:
            import requests
            
            payload = {
                "model": model_config['model_name'],
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": model_config.get('temperature', 0.7),
                    "num_predict": model_config.get('max_tokens', 200)
                }
            }
            
            response = requests.post(
                model_config['api_endpoint'],
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return None

    def _call_huggingface(self, prompt: str, model_config: dict) -> Optional[str]:
        """Call HuggingFace API"""
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.huggingface_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": model_config.get('max_tokens', 200),
                    "temperature": model_config.get('temperature', 0.7),
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                model_config['api_endpoint'],
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '')
                return str(result)
            else:
                logger.error(f"HuggingFace API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"HuggingFace API error: {e}")
            return None

    def _call_generic_api(self, prompt: str, model_config: dict) -> Optional[str]:
        """Call generic REST API"""
        try:
            import requests
            
            payload = {
                "prompt": prompt,
                "max_tokens": model_config.get('max_tokens', 200),
                "temperature": model_config.get('temperature', 0.7)
            }
            
            response = requests.post(
                model_config['api_endpoint'],
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', result.get('text', str(result)))
            else:
                logger.error(f"Generic API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Generic API error: {e}")
            return None

    def select_relevant_tools(
        self,
        opportunity_type: str,
        company_data: Dict,
        available_tools: List[Dict],
        max_tools: int = 2
    ) -> List[Dict]:
        """
        Select the most relevant tools for a company based on their profile
        
        Args:
            opportunity_type: Type of opportunity (e.g., 'customer-service', 'document-processing')
            company_data: Dictionary containing company information
            available_tools: List of available tools for this opportunity type
            max_tools: Maximum number of tools to recommend (default: 2)
            
        Returns:
            List of selected tools (up to max_tools)
        """
        if not self.enabled or not available_tools:
            return available_tools[:max_tools]
        
        try:
            # Build company context
            company_context = self._build_company_context(company_data)
            
            # Create tool selection prompt
            prompt = self._create_tool_selection_prompt(opportunity_type, company_context, available_tools, max_tools)
            
            # Generate response using LLM
            response = self._call_llm(prompt)
            
            if response:
                # Parse the response to get selected tools (including external ones)
                selected_tools = self._parse_tool_selection_response(response, available_tools)
                
                # Ensure we don't exceed max_tools
                return selected_tools[:max_tools]
            else:
                logger.warning("LLM returned empty response for tool selection, using default selection")
                return available_tools[:max_tools]
                
        except Exception as e:
            logger.error(f"Error selecting relevant tools: {e}")
            return available_tools[:max_tools]

    def _create_tool_selection_prompt(
        self,
        opportunity_type: str,
        company_context: str,
        available_tools: List[Dict],
        max_tools: int
    ) -> str:
        """Create a prompt for selecting relevant tools"""
        
        # Format available tools for the prompt
        tools_info = []
        for tool in available_tools:
            tool_info = f"- {tool['name']}: {tool['description']} (Cost: {tool['cost']}, Best for: {tool['best_for']})"
            tools_info.append(tool_info)
        
        tools_text = "\n".join(tools_info)
        
        opportunity_templates = {
            'customer-service': {
                'title': 'Customer Service Automation',
                'focus': 'customer service, support, and communication tools'
            },
            'document-processing': {
                'title': 'Document Processing Automation', 
                'focus': 'document handling, data entry, and workflow automation tools'
            },
            'data-analysis': {
                'title': 'AI-Enhanced Business Intelligence',
                'focus': 'data analysis, reporting, and business intelligence tools'
            },
            'process-automation': {
                'title': 'Process Automation',
                'focus': 'business process optimization and automation tools'
            }
        }
        
        template = opportunity_templates.get(opportunity_type, {
            'title': 'AI Opportunity',
            'focus': 'business optimization tools'
        })
        
        prompt = f"""
You are an AI consultant helping to select the most relevant tools for a business.

Company Context: {company_context}

Opportunity Type: {template['title']}
Focus Area: {template['focus']}

Available Approved Tools:
{tools_text}

Please select the {max_tools} most relevant tools for this company based on:
1. Company size and budget considerations
2. Industry-specific needs
3. Current technology stack
4. AI experience level
5. Specific challenges mentioned

INSTRUCTIONS:
- FIRST, try to find suitable tools from the approved list above
- If the approved tools don't fully meet the company's needs, you may suggest additional external tools
- For external tools, provide: Tool Name, Estimated Cost, Brief Description, and why it's relevant
- Always prioritize approved tools when they are suitable

Respond with tool names, one per line, in order of relevance. For external tools, format as: "Tool Name (External) - $Cost - Description"
"""
        
        return prompt.strip()

    def _parse_tool_selection_response(self, response: str, available_tools: List[Dict]) -> List[Dict]:
        """Parse LLM response to extract tool names and handle external tools"""
        try:
            # Split response into lines and clean up
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            
            selected_tools = []
            available_tool_names = [tool['name'] for tool in available_tools]
            
            for line in lines:
                # Remove common prefixes
                clean_line = line.lstrip('0123456789.-* ').strip()
                if not clean_line:
                    continue
                
                # Check if this is an external tool (contains "(External)")
                if "(External)" in clean_line:
                    # Parse external tool format: "Tool Name (External) - $Cost - Description"
                    parts = clean_line.split(" - ", 2)
                    if len(parts) >= 2:
                        tool_name = parts[0].replace("(External)", "").strip()
                        cost = parts[1].strip() if len(parts) > 1 else "Contact for pricing"
                        description = parts[2].strip() if len(parts) > 2 else "External tool recommendation"
                        
                        external_tool = {
                            'name': tool_name,
                            'type': 'External',
                            'cost': cost,
                            'description': description,
                            'rating': 'N/A',
                            'features': ['External recommendation'],
                            'best_for': 'Specific use case',
                            'implementation': 'TBD',
                            'roi_range': 'TBD',
                            'use_cases': ['Custom implementation']
                        }
                        selected_tools.append(external_tool)
                else:
                    # Check if this tool name matches any available tool
                    for available_name in available_tool_names:
                        if clean_line.lower() in available_name.lower() or available_name.lower() in clean_line.lower():
                            # Find the full tool object
                            for tool in available_tools:
                                if tool['name'] == available_name:
                                    if tool not in selected_tools:
                                        selected_tools.append(tool)
                                    break
                            break
            
            return selected_tools
            
        except Exception as e:
            logger.error(f"Error parsing tool selection response: {e}")
            return []

# Global instance
llm_service = LLMService()
