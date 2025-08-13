# report_generator.py - Dynamic report content generation using LLM
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from llm_service import llm_service

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Service for generating dynamic report content using LLM"""
    
    def __init__(self):
        self.llm_service = llm_service
    
    def generate_assessment_report_data(self, assessment_data: Dict) -> Dict[str, Any]:
        """Generate dynamic content for Assessment Report"""
        try:
            # Extract company information
            company_name = assessment_data.get('company_name', 'Your Company')
            industry = assessment_data.get('industry', 'technology')
            company_size = assessment_data.get('company_size', '11-50')
            role = assessment_data.get('role', 'ceo')
            challenges = assessment_data.get('challenges', [])
            
            # Extract new comprehensive data
            current_tools = assessment_data.get('current_tools', [])
            tool_preferences = assessment_data.get('tool_preferences', [])
            implementation_priority = assessment_data.get('implementation_priority', [])
            team_availability = assessment_data.get('team_availability', '')
            change_management_experience = assessment_data.get('change_management_experience', '')
            data_governance = assessment_data.get('data_governance', '')
            security_requirements = assessment_data.get('security_requirements', [])
            compliance_needs = assessment_data.get('compliance_needs', [])
            integration_requirements = assessment_data.get('integration_requirements', [])
            success_metrics = assessment_data.get('success_metrics', [])
            expected_roi = assessment_data.get('expected_roi', '')
            payback_period = assessment_data.get('payback_period', '')
            risk_factors = assessment_data.get('risk_factors', [])
            mitigation_strategies = assessment_data.get('mitigation_strategies', [])
            implementation_phases = assessment_data.get('implementation_phases', [])
            resource_requirements = assessment_data.get('resource_requirements', [])
            training_needs = assessment_data.get('training_needs', [])
            vendor_criteria = assessment_data.get('vendor_criteria', [])
            pilot_project = assessment_data.get('pilot_project', '')
            scalability_requirements = assessment_data.get('scalability_requirements', '')
            maintenance_plan = assessment_data.get('maintenance_plan', '')
            client_notes = assessment_data.get('client_notes', '')
            
            # Generate personalized content using LLM with enhanced data
            personalized_content = self._generate_personalized_assessment_content(
                company_name, industry, company_size, role, challenges, current_tools, 
                tool_preferences, implementation_priority, team_availability, 
                change_management_experience, data_governance, security_requirements,
                compliance_needs, integration_requirements, success_metrics, 
                expected_roi, payback_period, risk_factors, mitigation_strategies,
                client_notes
            )
            
            # Calculate comprehensive scores based on enhanced assessment data
            scores = self._calculate_enhanced_assessment_scores(assessment_data)
            
            # Generate specific opportunities with detailed recommendations
            opportunities = self._generate_detailed_opportunities(assessment_data)
            
            # Generate curated tool recommendations with pricing
            tool_recommendations = self._generate_tool_recommendations(
                assessment_data, current_tools, tool_preferences, vendor_criteria,
                security_requirements, compliance_needs, integration_requirements
            )
            
            # Generate detailed 6-month implementation roadmap
            implementation_roadmap = self._generate_implementation_roadmap(
                assessment_data, implementation_phases, resource_requirements,
                training_needs, pilot_project, team_availability
            )
            
            # Generate detailed ROI projections and payback periods
            roi_projections = self._generate_roi_projections(
                assessment_data, expected_roi, payback_period, opportunities
            )
            
            # Generate comprehensive risk assessment and mitigation strategies
            risk_assessment = self._generate_comprehensive_risk_assessment(
                assessment_data, risk_factors, mitigation_strategies, 
                change_management_experience, data_governance
            )
            
            # Build comprehensive report data
            report_data = {
                'client_company': company_name,
                'primary_contact': f"{assessment_data.get('first_name', '')} {assessment_data.get('last_name', '')}",
                'report_date': datetime.now().strftime('%B %d, %Y'),
                
                # Include all assessment data for context display
                'industry': assessment_data.get('industry', 'technology'),
                'company_size': assessment_data.get('company_size', '11-50'),
                'first_name': assessment_data.get('first_name', ''),
                'last_name': assessment_data.get('last_name', ''),
                'email': assessment_data.get('email', ''),
                'website': assessment_data.get('website', ''),
                'current_tech': assessment_data.get('current_tech', 'basic'),
                'ai_experience': assessment_data.get('ai_experience', 'exploring'),
                'current_tools': assessment_data.get('current_tools', []),
                'timeline': assessment_data.get('timeline', '6-months'),
                'budget': assessment_data.get('budget', 'under-25k'),
                'team_availability': assessment_data.get('team_availability', 'limited'),
                'change_management_experience': assessment_data.get('change_management_experience', 'none'),
                'data_governance': assessment_data.get('data_governance', 'none'),
                'security_requirements': assessment_data.get('security_requirements', []),
                'compliance_needs': assessment_data.get('compliance_needs', []),
                'challenges': assessment_data.get('challenges', []),
                'implementation_priority': assessment_data.get('implementation_priority', []),
                
                'ai_score': scores['overall'],
                'readiness_level': scores['readiness_level'],
                'opportunity_count': len(opportunities),
                'total_roi_min': roi_projections['total_roi_min'],
                'total_roi_max': roi_projections['total_roi_max'],
                'payback_period': roi_projections['payback_period'],
                
                # Enhanced Assessment breakdown
                'tech_score': scores['tech'],
                'data_score': scores['data'],
                'team_score': scores['team'],
                'process_score': scores['process'],
                'change_score': scores['change'],
                'security_score': scores['security'],
                'tech_status': scores['tech_status'],
                'data_status': scores['data_status'],
                'team_status': scores['team_status'],
                'process_status': scores['process_status'],
                'change_status': scores['change_status'],
                'security_status': scores['security_status'],
                
                # Detailed explanations for each dimension
                'tech_explanation': scores.get('tech_explanation', 'Technology infrastructure analysis based on current systems and tools.'),
                'data_explanation': scores.get('data_explanation', 'Data readiness assessment considering governance, security, and compliance requirements.'),
                'team_explanation': scores.get('team_explanation', 'Team preparedness evaluation including availability, experience, and change management capabilities.'),
                'process_explanation': scores.get('process_explanation', 'Process maturity analysis based on timeline, budget, and change management experience.'),
                
                # Strengths and weaknesses
                'tech_strengths': personalized_content['tech_strengths'],
                'data_strengths': personalized_content['data_strengths'],
                'team_strengths': personalized_content['team_strengths'],
                'process_strengths': personalized_content['process_strengths'],
                'tech_weaknesses': personalized_content['tech_weaknesses'],
                'data_weaknesses': personalized_content['data_weaknesses'],
                'team_weaknesses': personalized_content['team_weaknesses'],
                'process_weaknesses': personalized_content['process_weaknesses'],
                
                # Detailed opportunities with specific recommendations
                'opportunities': opportunities,
                
                # Curated tool recommendations with pricing
                'tool_recommendations': tool_recommendations,
                
                # 6-month implementation roadmap
                'implementation_roadmap': implementation_roadmap,
                
                # ROI projections and payback periods
                'roi_projections': roi_projections,
                'roi_explanation': roi_projections.get('roi_explanation', ''),
                'roi_risk_factors': roi_projections.get('risk_factors', []),
                'roi_assumptions': roi_projections.get('assumptions', []),
                
                # Risk assessment and mitigation strategies
                'risk_assessment': risk_assessment,
                
                # Additional insights
                'current_tools_analysis': personalized_content['current_tools_analysis'],
                'team_readiness': personalized_content['team_readiness'],
                'change_management_plan': personalized_content['change_management_plan'],
                'success_metrics': personalized_content['success_metrics']
            }
            
            return report_data
            
        except Exception as e:
            logger.error(f"Error generating assessment report data: {e}")
            return self._get_fallback_assessment_data(assessment_data)
    
    def generate_strategy_blueprint_data(self, assessment_data: Dict) -> Dict[str, Any]:
        """Generate dynamic content for Strategy Blueprint"""
        try:
            # Extract company information
            company_name = assessment_data.get('company_name', 'Your Company')
            industry = assessment_data.get('industry', 'technology')
            company_size = assessment_data.get('company_size', '11-50')
            
            # Generate personalized strategic content using LLM
            strategic_content = self._generate_personalized_strategic_content(
                company_name, industry, company_size
            )
            
            # Calculate ROI and budget
            total_roi = 1500000  # Base ROI for strategy blueprint
            budget_breakdown = self._calculate_budget_breakdown(company_size)
            
            # Build report data
            report_data = {
                'client_company': company_name,
                'primary_contact': f"{assessment_data.get('first_name', '')} {assessment_data.get('last_name', '')}",
                'report_date': datetime.now().strftime('%B %d, %Y'),
                'strategic_position': strategic_content['strategic_position'],
                'total_roi_min': total_roi,
                
                # Include all assessment data for context display
                'industry': assessment_data.get('industry', 'technology'),
                'company_size': assessment_data.get('company_size', '11-50'),
                'first_name': assessment_data.get('first_name', ''),
                'last_name': assessment_data.get('last_name', ''),
                'email': assessment_data.get('email', ''),
                'website': assessment_data.get('website', ''),
                'current_tech': assessment_data.get('current_tech', 'basic'),
                'ai_experience': assessment_data.get('ai_experience', 'exploring'),
                'current_tools': assessment_data.get('current_tools', []),
                'timeline': assessment_data.get('timeline', '6-months'),
                'budget': assessment_data.get('budget', 'under-25k'),
                'team_availability': assessment_data.get('team_availability', 'limited'),
                'change_management_experience': assessment_data.get('change_management_experience', 'none'),
                'data_governance': assessment_data.get('data_governance', 'none'),
                'security_requirements': assessment_data.get('security_requirements', []),
                'compliance_needs': assessment_data.get('compliance_needs', []),
                'challenges': assessment_data.get('challenges', []),
                'implementation_priority': assessment_data.get('implementation_priority', []),
                
                # Competitive analysis
                'competitor_1_name': strategic_content['competitors'][0]['name'],
                'competitor_1_position': strategic_content['competitors'][0]['position'],
                'competitor_1_analysis': strategic_content['competitors'][0]['analysis'],
                'competitor_2_name': strategic_content['competitors'][1]['name'],
                'competitor_2_position': strategic_content['competitors'][1]['position'],
                'competitor_2_analysis': strategic_content['competitors'][1]['analysis'],
                'competitor_3_name': strategic_content['competitors'][2]['name'],
                'competitor_3_position': strategic_content['competitors'][2]['position'],
                'competitor_3_analysis': strategic_content['competitors'][2]['analysis'],
                'strategic_recommendations': strategic_content['strategic_recommendations'],
                
                # Vendor matrix
                'vendor_matrix': strategic_content['vendor_matrix'],
                
                # Risk assessment
                'risk_assessment': strategic_content['risk_assessment'],
                
                # Budget planning
                'q1_budget': budget_breakdown['q1'],
                'q2_budget': budget_breakdown['q2'],
                'q3_budget': budget_breakdown['q3'],
                'q4_budget': budget_breakdown['q4'],
                'total_budget': budget_breakdown['total'],
                'roi_percentage': 300,
                
                # KPI dashboard
                'kpi_dashboard': strategic_content['kpi_dashboard']
            }
            
            return report_data
            
        except Exception as e:
            logger.error(f"Error generating strategy blueprint data: {e}")
            return self._get_fallback_strategy_data(assessment_data)
    
    def _generate_personalized_assessment_content(self, company_name: str, industry: str, 
                                               company_size: str, role: str, challenges: List[str],
                                               current_tools: List[str], tool_preferences: List[str],
                                               implementation_priority: List[str], team_availability: str,
                                               change_management_experience: str, data_governance: str,
                                               security_requirements: List[str], compliance_needs: List[str],
                                               integration_requirements: List[str], success_metrics: List[str],
                                               expected_roi: str, payback_period: str, risk_factors: List[str],
                                               mitigation_strategies: List[str], client_notes: str = '') -> Dict:
        """Generate personalized assessment content using LLM"""
        if not self.llm_service.enabled:
            return self._get_default_assessment_content()
        
        try:
            # Create context for LLM
            context = f"Company: {company_name}, Industry: {industry}, Size: {company_size}, Role: {role}, Challenges: {', '.join(challenges)}"
            if client_notes:
                context += f", Additional Context: {client_notes}"
            
            # Generate strengths for each area
            tech_strengths = self._generate_strengths_prompt(context, "technology infrastructure")
            data_strengths = self._generate_strengths_prompt(context, "data assets and readiness")
            team_strengths = self._generate_strengths_prompt(context, "team capabilities and preparedness")
            process_strengths = self._generate_strengths_prompt(context, "process maturity and optimization")
            
            # Generate weaknesses for each area
            tech_weaknesses = self._generate_weaknesses_prompt(context, "technology infrastructure")
            data_weaknesses = self._generate_weaknesses_prompt(context, "data assets and readiness")
            team_weaknesses = self._generate_weaknesses_prompt(context, "team capabilities and preparedness")
            process_weaknesses = self._generate_weaknesses_prompt(context, "process maturity and optimization")
            
            # Generate additional insights
            current_tools_analysis = self._generate_tools_analysis_prompt(context, current_tools)
            team_readiness = self._generate_team_readiness_prompt(context, team_availability, change_management_experience)
            change_management_plan = self._generate_change_management_prompt(context, change_management_experience)
            success_metrics = self._generate_success_metrics_prompt(context, success_metrics)
            
            return {
                'tech_strengths': tech_strengths,
                'data_strengths': data_strengths,
                'team_strengths': team_strengths,
                'process_strengths': process_strengths,
                'tech_weaknesses': tech_weaknesses,
                'data_weaknesses': data_weaknesses,
                'team_weaknesses': team_weaknesses,
                'process_weaknesses': process_weaknesses,
                'current_tools_analysis': current_tools_analysis,
                'team_readiness': team_readiness,
                'change_management_plan': change_management_plan,
                'success_metrics': success_metrics
            }
            
        except Exception as e:
            logger.error(f"Error generating personalized assessment content: {e}")
            return self._get_default_assessment_content()
    
    def _generate_personalized_strategic_content(self, company_name: str, industry: str, 
                                               company_size: str) -> Dict:
        """Generate personalized strategic content using LLM"""
        if not self.llm_service.enabled:
            return self._get_default_strategic_content()
        
        try:
            # Create context for LLM
            context = f"Company: {company_name}, Industry: {industry}, Size: {company_size}"
            
            # Generate competitive analysis
            competitors = self._generate_competitive_analysis(context, industry)
            
            # Generate strategic recommendations
            strategic_recommendations = self._generate_strategic_recommendations(context, industry)
            
            # Generate vendor matrix
            vendor_matrix = self._generate_vendor_matrix(industry, company_size)
            
            # Generate risk assessment
            risk_assessment = self._generate_risk_assessment(context, industry)
            
            # Generate KPI dashboard
            kpi_dashboard = self._generate_kpi_dashboard(industry, company_size)
            
            return {
                'strategic_position': self._determine_strategic_position(company_size, industry),
                'competitors': competitors,
                'strategic_recommendations': strategic_recommendations,
                'vendor_matrix': vendor_matrix,
                'risk_assessment': risk_assessment,
                'kpi_dashboard': kpi_dashboard
            }
            
        except Exception as e:
            logger.error(f"Error generating personalized strategic content: {e}")
            return self._get_default_strategic_content()
    
    def _generate_strengths_prompt(self, context: str, area: str) -> str:
        """Generate strengths for a specific area using LLM"""
        prompt = f"""
Based on this company context: {context}

Generate 2-3 specific strengths for their {area}. Focus on:
- Current capabilities that support AI implementation
- Existing resources that can be leveraged
- Organizational advantages in this area

Write 1-2 sentences describing their key strengths in {area}:
"""
        
        response = self.llm_service._call_llm(prompt)
        return response if response else f"Strong foundation in {area} with room for AI enhancement."
    
    def _generate_weaknesses_prompt(self, context: str, area: str) -> str:
        """Generate weaknesses for a specific area using LLM"""
        prompt = f"""
Based on this company context: {context}

Generate 2-3 specific areas for improvement in their {area}. Focus on:
- Current limitations that could hinder AI implementation
- Gaps that need to be addressed
- Areas requiring investment or development

Write 1-2 sentences describing key improvement areas in {area}:
"""
        
        response = self.llm_service._call_llm(prompt)
        return response if response else f"Opportunities for enhancement in {area} to support AI initiatives."
    
    def _generate_tools_analysis_prompt(self, context: str, current_tools: List[str]) -> str:
        """Generate analysis of current tools using LLM"""
        tools_str = ', '.join(current_tools) if current_tools else 'limited tools'
        prompt = f"""
Based on this company context: {context}

Analyze their current tools: {tools_str}

Provide insights on:
- How existing tools can support AI implementation
- Integration opportunities
- Potential gaps or limitations

Write 2-3 sentences analyzing their current tool landscape:
"""
        
        response = self.llm_service._call_llm(prompt)
        return response if response else f"Current tools provide a foundation for AI integration with opportunities for enhancement."
    
    def _generate_team_readiness_prompt(self, context: str, team_availability: str, change_management_experience: str) -> str:
        """Generate team readiness analysis using LLM"""
        prompt = f"""
Based on this company context: {context}

Team availability: {team_availability}
Change management experience: {change_management_experience}

Assess team readiness for AI implementation:
- Current capabilities and gaps
- Training needs
- Change management considerations

Write 2-3 sentences on team readiness:
"""
        
        response = self.llm_service._call_llm(prompt)
        return response if response else f"Team shows potential for AI adoption with appropriate training and change management support."
    
    def _generate_change_management_prompt(self, context: str, change_management_experience: str) -> str:
        """Generate change management plan using LLM"""
        prompt = f"""
Based on this company context: {context}

Change management experience: {change_management_experience}

Develop a change management approach for AI implementation:
- Key strategies for adoption
- Communication plan
- Training and support needs

Write 2-3 sentences on change management approach:
"""
        
        response = self.llm_service._call_llm(prompt)
        return response if response else f"Structured change management approach needed to ensure successful AI adoption and user acceptance."
    
    def _generate_success_metrics_prompt(self, context: str, success_metrics: List[str]) -> str:
        """Generate success metrics analysis using LLM"""
        metrics_str = ', '.join(success_metrics) if success_metrics else 'general business metrics'
        prompt = f"""
Based on this company context: {context}

Current success metrics focus: {metrics_str}

Recommend AI-specific success metrics:
- KPIs for measuring AI implementation success
- Business impact indicators
- ROI measurement approaches

Write 2-3 sentences on success metrics for AI initiatives:
"""
        
        response = self.llm_service._call_llm(prompt)
        return response if response else f"AI-specific metrics should focus on efficiency gains, cost savings, and business process improvements."
    
    def _generate_competitive_analysis(self, context: str, industry: str) -> List[Dict]:
        """Generate competitive analysis using LLM"""
        prompt = f"""
Based on this company context: {context}

Generate competitive analysis for 3 key competitors in the {industry} industry. For each competitor, provide:
1. Company name (real or realistic)
2. Market position (Leader, Challenger, Niche, etc.)
3. Brief analysis of their AI adoption and competitive advantages

Format as JSON with fields: name, position, analysis
"""
        
        try:
            response = self.llm_service._call_llm(prompt)
            if response and '{' in response:
                # Try to extract JSON from response
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                competitors = json.loads(json_str)
                return competitors if isinstance(competitors, list) else [competitors]
        except:
            pass
        
        # Fallback competitors
        return [
            {
                'name': 'Industry Leader Inc',
                'position': 'Market Leader',
                'analysis': 'Advanced AI implementation with strong market position and significant resources.'
            },
            {
                'name': 'Innovation Tech Corp',
                'position': 'Challenger',
                'analysis': 'Rapidly growing competitor with aggressive AI adoption strategy.'
            },
            {
                'name': 'Niche Solutions Ltd',
                'position': 'Niche Player',
                'analysis': 'Specialized AI solutions in specific market segments.'
            }
        ]
    
    def _generate_strategic_recommendations(self, context: str, industry: str) -> str:
        """Generate strategic recommendations using LLM"""
        prompt = f"""
Based on this company context: {context}

Provide 2-3 strategic recommendations for AI implementation in the {industry} industry. Focus on:
- Competitive positioning opportunities
- Strategic advantages to pursue
- Market timing considerations

Write 2-3 sentences of strategic recommendations:
"""
        
        response = self.llm_service._call_llm(prompt)
        return response if response else f"Focus on rapid implementation of customer-facing AI solutions to gain competitive advantage in the {industry} market."
    
    def _generate_vendor_matrix(self, industry: str, company_size: str) -> List[Dict]:
        """Generate vendor evaluation matrix"""
        # Base vendors for different categories
        vendors = [
            {
                'name': 'Intercom',
                'category': 'Customer Service',
                'cost_rating': 'good',
                'features_rating': 'excellent',
                'support_rating': 'excellent',
                'integration_rating': 'good',
                'overall_score': 9
            },
            {
                'name': 'Zapier',
                'category': 'Automation',
                'cost_rating': 'excellent',
                'features_rating': 'good',
                'support_rating': 'good',
                'integration_rating': 'excellent',
                'overall_score': 8
            },
            {
                'name': 'Tableau',
                'category': 'Analytics',
                'cost_rating': 'fair',
                'features_rating': 'excellent',
                'support_rating': 'excellent',
                'integration_rating': 'good',
                'overall_score': 8
            },
            {
                'name': 'Microsoft Power Platform',
                'category': 'Enterprise',
                'cost_rating': 'good',
                'features_rating': 'excellent',
                'support_rating': 'excellent',
                'integration_rating': 'excellent',
                'overall_score': 9
            },
            {
                'name': 'Salesforce Einstein',
                'category': 'CRM',
                'cost_rating': 'fair',
                'features_rating': 'excellent',
                'support_rating': 'excellent',
                'integration_rating': 'good',
                'overall_score': 8
            }
        ]
        
        return vendors
    
    def _generate_risk_assessment(self, context: str, industry: str) -> List[Dict]:
        """Generate risk assessment using LLM"""
        prompt = f"""
Based on this company context: {context}

Identify 3-4 key risks for AI implementation in the {industry} industry. For each risk, provide:
1. Risk title
2. Risk level (High, Medium, Low)
3. Potential impact
4. Mitigation strategy

Format as JSON with fields: title, level, impact, mitigation
"""
        
        try:
            response = self.llm_service._call_llm(prompt)
            if response and '{' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                risks = json.loads(json_str)
                return risks if isinstance(risks, list) else [risks]
        except:
            pass
        
        # Fallback risks
        return [
            {
                'title': 'Data Security & Privacy',
                'level': 'High',
                'impact': 'Regulatory compliance and customer trust',
                'mitigation': 'Implement robust encryption, access controls, and compliance frameworks'
            },
            {
                'title': 'Employee Resistance',
                'level': 'Medium',
                'impact': 'Slower adoption and reduced effectiveness',
                'mitigation': 'Comprehensive training program and change management strategy'
            },
            {
                'title': 'Integration Complexity',
                'level': 'Medium',
                'impact': 'Implementation delays and cost overruns',
                'mitigation': 'Phased implementation approach with thorough testing'
            }
        ]
    
    def _generate_kpi_dashboard(self, industry: str, company_size: str) -> List[Dict]:
        """Generate KPI dashboard"""
        return [
            {
                'metric': 'Customer Satisfaction',
                'current_value': '85%',
                'target_value': '90%'
            },
            {
                'metric': 'Response Time',
                'current_value': '4 hours',
                'target_value': '2 hours'
            },
            {
                'metric': 'Operational Efficiency',
                'current_value': '70%',
                'target_value': '85%'
            },
            {
                'metric': 'Cost Savings',
                'current_value': '$0',
                'target_value': '$50K/month'
            }
        ]
    
    def _calculate_assessment_scores(self, assessment_data: Dict) -> Dict:
        """Calculate assessment scores based on data"""
        # Base scores
        tech_score = 75
        data_score = 70
        team_score = 80
        process_score = 65
        
        # Adjust based on current technology level
        current_tech = assessment_data.get('current_tech', 'basic')
        if current_tech == 'advanced':
            tech_score += 15
        elif current_tech == 'intermediate':
            tech_score += 8
        
        # Adjust based on AI experience
        ai_experience = assessment_data.get('ai_experience', 'none')
        if ai_experience == 'implementing':
            team_score += 15
        elif ai_experience == 'exploring':
            team_score += 8
        
        # Calculate overall score
        overall = (tech_score + data_score + team_score + process_score) // 4
        
        # Determine readiness level
        if overall >= 85:
            readiness_level = "High"
        elif overall >= 70:
            readiness_level = "Medium"
        else:
            readiness_level = "Low"
        
        # Determine status for each area
        def get_status(score):
            if score >= 85:
                return "Excellent"
            elif score >= 70:
                return "Good"
            elif score >= 55:
                return "Fair"
            else:
                return "Needs Improvement"
        
        return {
            'overall': overall,
            'readiness_level': readiness_level,
            'tech': tech_score,
            'data': data_score,
            'team': team_score,
            'process': process_score,
            'tech_status': get_status(tech_score),
            'data_status': get_status(data_score),
            'team_status': get_status(team_score),
            'process_status': get_status(process_score)
        }
    
    def _generate_opportunities(self, assessment_data: Dict) -> List[Dict]:
        """Generate AI opportunities based on assessment data"""
        challenges = assessment_data.get('challenges', [])
        industry = assessment_data.get('industry', 'technology')
        
        opportunities = []
        
        # Map challenges to opportunities
        opportunity_mapping = {
            'customer-service': {
                'title': 'Customer Service Automation',
                'roi': 120000,
                'description': 'Implement AI-powered chatbots and support systems to improve customer experience and reduce response times.'
            },
            'manual-processes': {
                'title': 'Process Automation',
                'roi': 180000,
                'description': 'Automate repetitive tasks and workflows to increase efficiency and reduce operational costs.'
            },
            'data-analysis': {
                'title': 'AI-Enhanced Business Intelligence',
                'roi': 200000,
                'description': 'Leverage AI for advanced data analysis and insights to drive better decision-making.'
            },
            'document-processing': {
                'title': 'Document Processing Automation',
                'roi': 150000,
                'description': 'Automate document handling and data extraction to streamline operations.'
            }
        }
        
        # Add opportunities based on challenges
        for challenge in challenges:
            if challenge in opportunity_mapping:
                opportunities.append(opportunity_mapping[challenge])
        
        # Add default opportunities if none found
        if not opportunities:
            opportunities = [
                {
                    'title': 'Customer Service Automation',
                    'roi': 120000,
                    'description': 'Implement AI-powered chatbots and support systems.'
                },
                {
                    'title': 'Process Automation',
                    'roi': 180000,
                    'description': 'Automate repetitive tasks and workflows.'
                }
            ]
        
        return opportunities
    
    def _calculate_budget_breakdown(self, company_size: str) -> Dict:
        """Calculate budget breakdown based on company size"""
        # Base budget for strategy blueprint
        if '500+' in company_size:
            total_budget = 200000
        elif '251-500' in company_size:
            total_budget = 150000
        elif '101-250' in company_size:
            total_budget = 120000
        elif '51-100' in company_size:
            total_budget = 100000
        elif '11-50' in company_size:
            total_budget = 80000
        else:
            total_budget = 60000
        
        # Quarterly breakdown
        q1 = int(total_budget * 0.35)  # Foundation
        q2 = int(total_budget * 0.30)  # Implementation
        q3 = int(total_budget * 0.20)  # Scaling
        q4 = int(total_budget * 0.15)  # Optimization
        
        return {
            'q1': q1,
            'q2': q2,
            'q3': q3,
            'q4': q4,
            'total': total_budget
        }
    
    def _determine_strategic_position(self, company_size: str, industry: str) -> str:
        """Determine strategic position based on company size and industry"""
        if '500+' in company_size:
            return "Market Leader"
        elif '251-500' in company_size:
            return "Established Player"
        elif '101-250' in company_size:
            return "Growing Challenger"
        elif '51-100' in company_size:
            return "Emerging Competitor"
        else:
            return "Innovative Startup"
    
    def _get_default_assessment_content(self) -> Dict:
        """Get default assessment content when LLM is not available"""
        return {
            'tech_strengths': 'Solid technology foundation with potential for AI enhancement.',
            'data_strengths': 'Existing data assets that can be leveraged for AI implementation.',
            'team_strengths': 'Capable team with willingness to adopt new technologies.',
            'process_strengths': 'Established processes that can be optimized with AI.'
        }
    
    def _calculate_enhanced_assessment_scores(self, assessment_data: Dict) -> Dict:
        """Calculate comprehensive assessment scores based on enhanced data"""
        scores = {}
        
        # Technology score (enhanced with current tools and preferences)
        tech_score = 50
        current_tech = assessment_data.get('current_tech', 'basic')
        current_tools = assessment_data.get('current_tools', [])
        tool_preferences = assessment_data.get('tool_preferences', [])
        
        if current_tech == 'advanced':
            tech_score += 30
        elif current_tech == 'intermediate':
            tech_score += 20
        
        tech_score += len(current_tools) * 3
        tech_score += len(tool_preferences) * 2
        
        scores['tech'] = min(tech_score, 95)
        scores['tech_status'] = self._get_status(scores['tech'])
        
        # Data score (enhanced with governance and security)
        data_score = 50
        data_governance = assessment_data.get('data_governance', 'none')
        security_requirements = assessment_data.get('security_requirements', [])
        compliance_needs = assessment_data.get('compliance_needs', [])
        
        if data_governance == 'advanced':
            data_score += 30
        elif data_governance == 'intermediate':
            data_score += 20
        elif data_governance == 'basic':
            data_score += 10
        
        data_score += len(security_requirements) * 3
        data_score += len(compliance_needs) * 2
        
        scores['data'] = min(data_score, 95)
        scores['data_status'] = self._get_status(scores['data'])
        
        # Team score (enhanced with availability and training needs)
        team_score = 50
        team_availability = assessment_data.get('team_availability', 'limited')
        training_needs = assessment_data.get('training_needs', [])
        resource_requirements = assessment_data.get('resource_requirements', [])
        
        if team_availability == 'dedicated':
            team_score += 25
        elif team_availability == 'part-time':
            team_score += 15
        elif team_availability == 'consultant':
            team_score += 10
        
        team_score += len(training_needs) * 2
        team_score += len(resource_requirements) * 2
        
        scores['team'] = min(team_score, 95)
        scores['team_status'] = self._get_status(scores['team'])
        
        # Process score (enhanced with implementation phases)
        process_score = 50
        implementation_phases = assessment_data.get('implementation_phases', [])
        implementation_priority = assessment_data.get('implementation_priority', [])
        
        process_score += len(implementation_phases) * 5
        process_score += len(implementation_priority) * 3
        
        scores['process'] = min(process_score, 95)
        scores['process_status'] = self._get_status(scores['process'])
        
        # Change management score (new)
        change_score = 50
        change_management_experience = assessment_data.get('change_management_experience', 'none')
        mitigation_strategies = assessment_data.get('mitigation_strategies', [])
        
        if change_management_experience == 'expert':
            change_score += 30
        elif change_management_experience == 'experienced':
            change_score += 20
        elif change_management_experience == 'some':
            change_score += 10
        
        change_score += len(mitigation_strategies) * 3
        
        scores['change'] = min(change_score, 95)
        scores['change_status'] = self._get_status(scores['change'])
        
        # Security score (new)
        security_score = 50
        security_requirements = assessment_data.get('security_requirements', [])
        compliance_needs = assessment_data.get('compliance_needs', [])
        
        security_score += len(security_requirements) * 4
        security_score += len(compliance_needs) * 3
        
        scores['security'] = min(security_score, 95)
        scores['security_status'] = self._get_status(scores['security'])
        
        # Overall score
        scores['overall'] = int((scores['tech'] + scores['data'] + scores['team'] + 
                               scores['process'] + scores['change'] + scores['security']) / 6)
        
        # Readiness level
        if scores['overall'] >= 85:
            scores['readiness_level'] = 'Excellent'
        elif scores['overall'] >= 70:
            scores['readiness_level'] = 'Good'
        elif scores['overall'] >= 55:
            scores['readiness_level'] = 'Fair'
        else:
            scores['readiness_level'] = 'Needs Improvement'
        
        # Generate detailed explanations for each dimension
        scores['tech_explanation'] = self._generate_tech_explanation(
            current_tech, assessment_data.get('ai_experience', 'exploring'), 
            current_tools, scores['tech']
        )
        scores['data_explanation'] = self._generate_data_explanation(
            data_governance, security_requirements, compliance_needs, scores['data']
        )
        scores['team_explanation'] = self._generate_team_explanation(
            team_availability, change_management_experience, 
            assessment_data.get('ai_experience', 'exploring'), scores['team']
        )
        scores['process_explanation'] = self._generate_process_explanation(
            assessment_data.get('timeline', '6-months'), 
            assessment_data.get('budget', 'under-25k'), 
            change_management_experience, scores['process']
        )
        
        # Generate strengths and improvement recommendations
        strengths = self._generate_strengths_analysis(assessment_data, scores['tech'], scores['data'], scores['team'], scores['process'])
        improvements = self._generate_improvement_recommendations(assessment_data, scores['tech'], scores['data'], scores['team'], scores['process'])
        
        scores.update(strengths)
        scores.update(improvements)
        
        return scores
    
    def _get_status(self, score: int) -> str:
        """Get status based on score"""
        if score >= 85:
            return 'Excellent'
        elif score >= 70:
            return 'Good'
        elif score >= 55:
            return 'Fair'
        else:
            return 'Needs Improvement'
    
    def _generate_tech_explanation(self, current_tech: str, ai_experience: str, current_tools: List[str], tech_score: int) -> str:
        """Generate detailed explanation for technology infrastructure score"""
        explanations = {
            'basic': "Your organization currently operates with basic technology infrastructure, which is common for companies in early stages of digital transformation.",
            'intermediate': "Your organization has established intermediate technology infrastructure with some modern tools and systems in place.",
            'advanced': "Your organization demonstrates advanced technology infrastructure with sophisticated systems and tools already implemented."
        }
        
        experience_explanations = {
            'exploring': "You're in the early exploration phase of AI adoption, which is a natural starting point for many organizations.",
            'piloting': "You have some AI pilot projects underway, showing proactive interest in AI implementation.",
            'implementing': "You're actively implementing AI solutions, demonstrating strong commitment to AI adoption.",
            'scaling': "You're scaling AI across your organization, indicating mature AI capabilities."
        }
        
        base_explanation = explanations.get(current_tech, explanations['basic'])
        experience_explanation = experience_explanations.get(ai_experience, experience_explanations['exploring'])
        
        tools_analysis = ""
        if current_tools:
            tools_analysis = f" Your current tool stack includes {', '.join(current_tools)}, which provides a solid foundation for AI integration."
        else:
            tools_analysis = " You currently have limited tools in place, which presents opportunities for strategic AI tool selection."
        
        score_analysis = ""
        if tech_score >= 85:
            score_analysis = " This excellent score reflects your strong technological foundation and readiness for advanced AI implementations."
        elif tech_score >= 70:
            score_analysis = " This good score indicates you have a solid foundation for AI adoption with room for strategic enhancements."
        elif tech_score >= 55:
            score_analysis = " This fair score suggests you have basic infrastructure that can support AI initiatives with targeted improvements."
        else:
            score_analysis = " This score indicates that technology infrastructure improvements should be prioritized before major AI implementations."
        
        return f"{base_explanation} {experience_explanation}{tools_analysis}{score_analysis}"
    
    def _generate_data_explanation(self, data_governance: str, security_requirements: List[str], compliance_needs: List[str], data_score: int) -> str:
        """Generate detailed explanation for data readiness score"""
        governance_explanations = {
            'none': "Your organization currently lacks formal data governance structures, which is common in early-stage companies.",
            'basic': "You have basic data governance practices in place, providing a foundation for data-driven initiatives.",
            'intermediate': "Your organization has established intermediate data governance with structured policies and procedures.",
            'advanced': "You demonstrate advanced data governance with comprehensive policies, procedures, and oversight mechanisms."
        }
        
        base_explanation = governance_explanations.get(data_governance, governance_explanations['none'])
        
        security_analysis = ""
        if security_requirements:
            security_analysis = f" Your security requirements include {', '.join(security_requirements)}, indicating strong security awareness."
        else:
            security_analysis = " You have minimal security requirements defined, which should be addressed before AI implementation."
        
        compliance_analysis = ""
        if compliance_needs:
            compliance_analysis = f" Your compliance needs include {', '.join(compliance_needs)}, which will influence AI solution selection."
        else:
            compliance_analysis = " You have limited compliance requirements, providing flexibility in AI solution choices."
        
        score_analysis = ""
        if data_score >= 85:
            score_analysis = " This excellent score reflects your mature data governance and strong security/compliance posture."
        elif data_score >= 70:
            score_analysis = " This good score indicates solid data foundations with room for strategic enhancements."
        elif data_score >= 55:
            score_analysis = " This fair score suggests basic data readiness that can support AI with targeted improvements."
        else:
            score_analysis = " This score indicates that data governance and security improvements should be prioritized."
        
        return f"{base_explanation}{security_analysis}{compliance_analysis}{score_analysis}"
    
    def _generate_team_explanation(self, team_availability: str, change_management_experience: str, ai_experience: str, team_score: int) -> str:
        """Generate detailed explanation for team preparedness score"""
        availability_explanations = {
            'limited': "Your team has limited availability for AI initiatives, which is common in resource-constrained organizations.",
            'part-time': "You have part-time team availability for AI projects, allowing for gradual implementation.",
            'dedicated': "You have dedicated team resources for AI initiatives, indicating strong organizational commitment.",
            'consultant': "You're relying on consultant support for AI initiatives, which can provide expertise but may limit internal capability building."
        }
        
        change_explanations = {
            'none': "Your organization has limited change management experience, which is typical for companies new to digital transformation.",
            'some': "You have some change management experience, providing a foundation for AI adoption.",
            'experienced': "Your organization has experienced change management capabilities, which will be valuable for AI implementation.",
            'expert': "You have expert-level change management experience, positioning you well for complex AI transformations."
        }
        
        base_explanation = availability_explanations.get(team_availability, availability_explanations['limited'])
        change_explanation = change_explanations.get(change_management_experience, change_explanations['none'])
        
        ai_experience_analysis = ""
        if ai_experience in ['implementing', 'scaling']:
            ai_experience_analysis = " Your team has practical AI experience, which significantly strengthens your implementation capabilities."
        elif ai_experience == 'piloting':
            ai_experience_analysis = " Your team is gaining AI experience through pilot projects, building valuable knowledge."
        else:
            ai_experience_analysis = " Your team is new to AI, which will require focused training and support during implementation."
        
        score_analysis = ""
        if team_score >= 85:
            score_analysis = " This excellent score reflects your strong team capabilities and readiness for AI implementation."
        elif team_score >= 70:
            score_analysis = " This good score indicates solid team foundations with room for targeted skill development."
        elif team_score >= 55:
            score_analysis = " This fair score suggests basic team readiness that can support AI with focused training and support."
        else:
            score_analysis = " This score indicates that team development and change management should be prioritized."
        
        return f"{base_explanation} {change_explanation}{ai_experience_analysis}{score_analysis}"
    
    def _generate_process_explanation(self, timeline: str, budget: str, change_management_experience: str, process_score: int) -> str:
        """Generate detailed explanation for process maturity score"""
        timeline_explanations = {
            'immediate': "Your organization is ready for immediate AI implementation, indicating strong urgency and readiness.",
            '3-months': "You have a 3-month timeline for AI implementation, suggesting focused, rapid deployment.",
            '6-months': "You have a 6-month timeline, allowing for thorough planning and implementation.",
            '12-months': "You have a 12-month timeline, enabling comprehensive transformation planning."
        }
        
        budget_explanations = {
            'under-25k': "Your budget is under $25,000, which is suitable for pilot projects and initial AI exploration.",
            '25k-50k': "Your budget of $25,000-$50,000 allows for meaningful AI implementations and tool investments.",
            '50k-100k': "Your budget of $50,000-$100,000 enables comprehensive AI initiatives with multiple solutions.",
            'over-100k': "Your budget over $100,000 supports enterprise-level AI transformations and advanced solutions."
        }
        
        base_explanation = timeline_explanations.get(timeline, timeline_explanations['6-months'])
        budget_explanation = budget_explanations.get(budget, budget_explanations['under-25k'])
        
        change_analysis = ""
        if change_management_experience in ['experienced', 'expert']:
            change_analysis = " Your strong change management experience will be valuable for process transformation."
        elif change_management_experience == 'some':
            change_analysis = " Your some change management experience provides a foundation for process improvements."
        else:
            change_analysis = " You may need to focus on change management as part of your process transformation."
        
        score_analysis = ""
        if process_score >= 85:
            score_analysis = " This excellent score reflects your mature processes and strong readiness for AI transformation."
        elif process_score >= 70:
            score_analysis = " This good score indicates solid process foundations with room for optimization."
        elif process_score >= 55:
            score_analysis = " This fair score suggests basic process maturity that can support AI with targeted improvements."
        else:
            score_analysis = " This score indicates that process optimization should be prioritized before AI implementation."
        
        return f"{base_explanation} {budget_explanation}{change_analysis}{score_analysis}"
    
    def _generate_strengths_analysis(self, assessment_data: Dict, tech_score: int, data_score: int, team_score: int, process_score: int) -> Dict:
        """Generate strengths analysis for each dimension"""
        strengths = {}
        
        # Technology strengths
        tech_strengths = []
        current_tech = assessment_data.get('current_tech', 'basic')
        current_tools = assessment_data.get('current_tools', [])
        
        if current_tech in ['intermediate', 'advanced']:
            tech_strengths.append(f"Strong {current_tech} technology infrastructure")
        if current_tools:
            tech_strengths.append(f"Existing tool stack with {len(current_tools)} tools")
        if tech_score >= 70:
            tech_strengths.append("Solid foundation for AI integration")
        
        strengths['tech_strengths'] = '; '.join(tech_strengths) if tech_strengths else "Basic technology infrastructure with room for growth"
        
        # Data strengths
        data_strengths = []
        data_governance = assessment_data.get('data_governance', 'none')
        security_requirements = assessment_data.get('security_requirements', [])
        
        if data_governance in ['intermediate', 'advanced']:
            data_strengths.append(f"{data_governance.capitalize()} data governance practices")
        if security_requirements:
            data_strengths.append(f"Strong security awareness with {len(security_requirements)} requirements")
        if data_score >= 70:
            data_strengths.append("Good data foundation for AI initiatives")
        
        strengths['data_strengths'] = '; '.join(data_strengths) if data_strengths else "Basic data practices with opportunities for improvement"
        
        # Team strengths
        team_strengths = []
        team_availability = assessment_data.get('team_availability', 'limited')
        change_management_experience = assessment_data.get('change_management_experience', 'none')
        
        if team_availability in ['part-time', 'dedicated']:
            team_strengths.append(f"{team_availability.capitalize()} team availability")
        if change_management_experience in ['experienced', 'expert']:
            team_strengths.append(f"{change_management_experience.capitalize()} change management capabilities")
        if team_score >= 70:
            team_strengths.append("Strong team foundation for AI adoption")
        
        strengths['team_strengths'] = '; '.join(team_strengths) if team_strengths else "Basic team capabilities with growth potential"
        
        # Process strengths
        process_strengths = []
        timeline = assessment_data.get('timeline', '6-months')
        budget = assessment_data.get('budget', 'under-25k')
        
        if timeline in ['immediate', '3-months']:
            process_strengths.append("Agile implementation timeline")
        if budget in ['50k-100k', 'over-100k']:
            process_strengths.append("Strong budget allocation for AI initiatives")
        if process_score >= 70:
            process_strengths.append("Mature process foundation")
        
        strengths['process_strengths'] = '; '.join(process_strengths) if process_strengths else "Basic process maturity with optimization opportunities"
        
        return strengths
    
    def _generate_improvement_recommendations(self, assessment_data: Dict, tech_score: int, data_score: int, team_score: int, process_score: int) -> Dict:
        """Generate improvement recommendations for each dimension"""
        recommendations = {}
        
        # Technology recommendations
        tech_recommendations = []
        if tech_score < 70:
            tech_recommendations.extend([
                "Upgrade core technology infrastructure",
                "Implement modern collaboration tools",
                "Establish cloud-based systems"
            ])
        if tech_score < 85:
            tech_recommendations.extend([
                "Enhance integration capabilities",
                "Implement advanced analytics tools",
                "Strengthen cybersecurity measures"
            ])
        
        recommendations['tech_recommendations'] = tech_recommendations if tech_recommendations else ["Maintain current technology excellence"]
        
        # Data recommendations
        data_recommendations = []
        if data_score < 70:
            data_recommendations.extend([
                "Establish data governance framework",
                "Implement data quality standards",
                "Create data security policies"
            ])
        if data_score < 85:
            data_recommendations.extend([
                "Enhance data analytics capabilities",
                "Implement advanced data management",
                "Strengthen compliance monitoring"
            ])
        
        recommendations['data_recommendations'] = data_recommendations if data_recommendations else ["Maintain current data excellence"]
        
        # Team recommendations
        team_recommendations = []
        if team_score < 70:
            team_recommendations.extend([
                "Provide AI training and education",
                "Establish change management processes",
                "Develop internal AI champions"
            ])
        if team_score < 85:
            team_recommendations.extend([
                "Enhance cross-functional collaboration",
                "Implement advanced training programs",
                "Strengthen leadership support"
            ])
        
        recommendations['team_recommendations'] = team_recommendations if team_recommendations else ["Maintain current team excellence"]
        
        # Process recommendations
        process_recommendations = []
        if process_score < 70:
            process_recommendations.extend([
                "Optimize core business processes",
                "Implement process automation",
                "Establish performance metrics"
            ])
        if process_score < 85:
            process_recommendations.extend([
                "Enhance process integration",
                "Implement advanced workflow management",
                "Strengthen continuous improvement"
            ])
        
        recommendations['process_recommendations'] = process_recommendations if process_recommendations else ["Maintain current process excellence"]
        
        return recommendations
    
    def _generate_detailed_opportunities(self, assessment_data: Dict) -> List[Dict]:
        """Generate detailed opportunities with specific recommendations and comprehensive explanations"""
        opportunities = []
        challenges = assessment_data.get('challenges', [])
        implementation_priority = assessment_data.get('implementation_priority', [])
        company_size = assessment_data.get('company_size', '11-50')
        industry = assessment_data.get('industry', 'technology')
        current_tech = assessment_data.get('current_tech', 'basic')
        
        # Map challenges to opportunities with detailed explanations
        opportunity_map = {
            'customer-service': {
                'title': 'Customer Service Automation',
                'description': 'Implement AI-powered chatbots and automated customer support systems',
                'detailed_explanation': f'Based on your {industry} industry focus and {company_size} company size, customer service automation represents a high-impact opportunity. This solution addresses common pain points in {industry} businesses including response time delays, repetitive inquiry handling, and customer satisfaction challenges. Your {current_tech} technology infrastructure provides a solid foundation for integrating AI-powered customer service tools.',
                'roi': 150000 if company_size in ['1-10', '11-50'] else 300000,
                'timeline': '3-6 months',
                'priority': 'High' if 'customer-service' in implementation_priority else 'Medium',
                'tools': ['Intercom', 'Zendesk', 'Freshdesk'],
                'benefits': ['24/7 customer support', 'Reduced response time', 'Improved customer satisfaction'],
                'implementation_steps': [
                    'Conduct customer service workflow analysis',
                    'Select appropriate AI chatbot platform',
                    'Train AI models on common customer inquiries',
                    'Integrate with existing CRM systems',
                    'Implement monitoring and feedback loops'
                ],
                'success_metrics': [
                    'Response time reduction by 60-80%',
                    'Customer satisfaction score improvement',
                    'Support ticket volume reduction',
                    'Agent productivity increase'
                ]
            },
            'manual-processes': {
                'title': 'Process Automation',
                'description': 'Automate repetitive manual tasks and workflows',
                'detailed_explanation': f'Process automation is particularly valuable for {industry} companies of your size, where manual processes often create bottlenecks and inefficiencies. This opportunity leverages your existing {current_tech} technology infrastructure to streamline operations, reduce human error, and free up valuable team resources for higher-value activities. The {company_size} company size indicates you have sufficient process complexity to benefit from automation while maintaining manageable implementation scope.',
                'roi': 100000 if company_size in ['1-10', '11-50'] else 250000,
                'timeline': '4-8 months',
                'priority': 'High' if 'process-automation' in implementation_priority else 'Medium',
                'tools': ['Zapier', 'n8n', 'Microsoft Power Automate'],
                'benefits': ['Time savings', 'Reduced errors', 'Increased efficiency'],
                'implementation_steps': [
                    'Identify high-impact manual processes',
                    'Map current workflow and pain points',
                    'Design automated workflow solutions',
                    'Select appropriate automation platform',
                    'Implement pilot automation projects',
                    'Scale successful automations across organization'
                ],
                'success_metrics': [
                    'Process completion time reduction by 40-70%',
                    'Error rate reduction by 50-80%',
                    'Employee productivity increase',
                    'Cost savings from reduced manual work'
                ]
            },
            'data-analysis': {
                'title': 'Advanced Data Analytics',
                'description': 'Implement comprehensive data analytics and business intelligence',
                'detailed_explanation': f'Advanced data analytics represents a strategic opportunity for {industry} companies like yours, where data-driven insights can provide significant competitive advantages. Your {company_size} company size indicates you have sufficient data volume to generate meaningful insights while maintaining manageable complexity. This opportunity builds upon your {current_tech} technology infrastructure to create a comprehensive analytics ecosystem that supports strategic decision-making across all business functions.',
                'roi': 200000 if company_size in ['1-10', '11-50'] else 400000,
                'timeline': '6-9 months',
                'priority': 'High' if 'data-analytics' in implementation_priority else 'Medium',
                'tools': ['Tableau', 'Power BI', 'Looker'],
                'benefits': ['Data-driven decisions', 'Improved insights', 'Better forecasting'],
                'implementation_steps': [
                    'Conduct comprehensive data audit and assessment',
                    'Design data architecture and governance framework',
                    'Select appropriate analytics and BI platforms',
                    'Develop key performance indicators and dashboards',
                    'Implement data integration and ETL processes',
                    'Train teams on analytics tools and data interpretation'
                ],
                'success_metrics': [
                    'Improved decision-making speed and accuracy',
                    'Increased revenue through data-driven insights',
                    'Enhanced operational efficiency',
                    'Better customer understanding and targeting'
                ]
            },
            'document-processing': {
                'title': 'Document Processing Automation',
                'description': 'Automate document processing, classification, and data extraction',
                'roi': 80000 if company_size in ['1-10', '11-50'] else 180000,
                'timeline': '3-5 months',
                'priority': 'Medium',
                'tools': ['UiPath', 'Automation Anywhere', 'Microsoft Power Automate'],
                'benefits': ['Faster processing', 'Reduced manual work', 'Improved accuracy']
            }
        }
        
        # Generate opportunities based on challenges
        for challenge in challenges:
            if challenge in opportunity_map:
                opportunities.append(opportunity_map[challenge])
        
        # Add opportunities based on implementation priorities
        for priority in implementation_priority:
            if priority not in [opp.get('title', '').lower().replace(' ', '-') for opp in opportunities]:
                if priority == 'marketing':
                    opportunities.append({
                        'title': 'Marketing Automation',
                        'description': 'Implement AI-powered marketing automation and lead generation',
                        'roi': 120000 if company_size in ['1-10', '11-50'] else 250000,
                        'timeline': '4-7 months',
                        'priority': 'High',
                        'tools': ['HubSpot', 'Marketo', 'Pardot'],
                        'benefits': ['Improved lead quality', 'Automated campaigns', 'Better ROI tracking']
                    })
                elif priority == 'operations':
                    opportunities.append({
                        'title': 'Operations Optimization',
                        'description': 'Optimize operational processes with AI and automation',
                        'roi': 180000 if company_size in ['1-10', '11-50'] else 350000,
                        'timeline': '6-10 months',
                        'priority': 'High',
                        'tools': ['ServiceNow', 'Jira', 'Asana'],
                        'benefits': ['Streamlined operations', 'Better resource allocation', 'Improved productivity']
                    })
        
        return opportunities[:5]  # Limit to top 5 opportunities
    
    def _generate_tool_recommendations(self, assessment_data: Dict, current_tools: List[str],
                                     tool_preferences: List[str], vendor_criteria: List[str],
                                     security_requirements: List[str], compliance_needs: List[str],
                                     integration_requirements: List[str]) -> List[Dict]:
        """Generate curated tool recommendations with pricing using preferred vendors"""
        try:
            # Load preferred vendors from saas_tools_database.json
            with open('saas_tools_database.json', 'r') as f:
                preferred_vendors = json.load(f)
        except FileNotFoundError:
            # Fallback to hardcoded preferred vendors if file not found
            preferred_vendors = {
                "customer_service": [
                    {
                        "name": "Zendesk Answer Bot",
                        "type": "SaaS",
                        "cost": "$50-150/month",
                        "description": "Automated customer support with ML-powered answer suggestions",
                        "rating": "4.5",
                        "features": ["Auto-suggest responses", "Ticket deflection", "Knowledge base integration", "Performance analytics"],
                        "best_for": "Established support teams",
                        "implementation": "1-2 weeks",
                        "roi_range": "2,000% - 8,000%",
                        "use_cases": ["Support ticket automation", "Knowledge base optimization", "Response time reduction"]
                    }
                ],
                "workflow_automation": [
                    {
                        "name": "Zapier",
                        "type": "SaaS",
                        "cost": "$20-599/month",
                        "description": "AI orchestration platform connecting 8,000+ apps with automated workflows",
                        "rating": "4.5",
                        "features": ["8,000+ app integrations", "AI workflows and chatbots", "No-code automation", "Enterprise governance"],
                        "best_for": "All business sizes",
                        "implementation": "1-4 weeks",
                        "roi_range": "2,360% - 2,400%",
                        "use_cases": ["Lead processing automation", "Sales pipeline management", "Marketing campaign attribution"]
                    }
                ],
                "business_intelligence": [
                    {
                        "name": "Power BI",
                        "type": "SaaS",
                        "cost": "$10-20/user/month",
                        "description": "Microsoft's business analytics service with AI insights and natural language queries",
                        "rating": "4.2",
                        "features": ["Natural language queries", "AI-powered insights", "Excel integration", "Real-time dashboards"],
                        "best_for": "Microsoft ecosystem users",
                        "implementation": "1-4 weeks",
                        "roi_range": "1,200% - 3,500%",
                        "use_cases": ["Financial reporting", "Sales analytics", "Operational monitoring"]
                    }
                ]
            }
        
        recommendations = []
        
        # Map assessment needs to vendor categories
        category_mapping = {
            'customer-service': 'customer_service',
            'analytics': 'business_intelligence',
            'automation': 'workflow_automation',
            'sales-marketing': 'sales_marketing',
            'development': 'development',
            'research-analysis': 'research_analysis',
            'knowledge-management': 'knowledge_management',
            'presentations': 'presentations'
        }
        
        # Generate recommendations based on assessment data
        for assessment_category, vendor_category in category_mapping.items():
            if vendor_category in preferred_vendors:
                tools = preferred_vendors[vendor_category]
                
                # Add preferred vendor flag
                for tool in tools:
                    tool['is_preferred'] = True
                
                # Add external vendor alternatives if needed
                external_alternatives = self._get_external_alternatives(assessment_category)
                for tool in external_alternatives:
                    tool['is_preferred'] = False
                
                recommendations.append({
                    'category': assessment_category.replace('-', ' ').title(),
                    'preferred_tools': tools[:2],  # Top 2 preferred tools
                    'external_tools': external_alternatives[:1],  # 1 external alternative
                    'rationale': f'Based on your {assessment_category} needs and preferences'
                })
        
        return recommendations
    
    def _get_external_alternatives(self, category: str) -> List[Dict]:
        """Get external vendor alternatives when preferred vendors don't meet requirements"""
        external_vendors = {
            'customer-service': [
                {
                    'name': 'Freshdesk',
                    'type': 'SaaS',
                    'cost': '$15-79/month',
                    'description': 'Cloud-based customer support platform with AI automation',
                    'rating': '4.3',
                    'features': ['AI-powered automation', 'Multi-channel support', 'Advanced reporting', 'Integrations'],
                    'best_for': 'Growing support teams',
                    'implementation': '2-3 weeks',
                    'roi_range': '1,500% - 4,000%',
                    'use_cases': ['Customer support automation', 'Ticket management', 'Knowledge base']
                }
            ],
            'analytics': [
                {
                    'name': 'Tableau',
                    'type': 'SaaS',
                    'cost': '$70/user/month',
                    'description': 'Leading data visualization and business intelligence platform',
                    'rating': '4.3',
                    'features': ['Interactive dashboards', 'AI-powered insights', 'Real-time data connections', 'Advanced analytics'],
                    'best_for': 'Data-driven organizations',
                    'implementation': '2-6 weeks',
                    'roi_range': '1,500% - 4,000%',
                    'use_cases': ['Executive dashboards', 'Sales performance tracking', 'Operational analytics']
                }
            ],
            'automation': [
                {
                    'name': 'Microsoft Power Automate',
                    'type': 'SaaS',
                    'cost': '$15/user/month',
                    'description': 'Microsoft\'s workflow automation platform with AI capabilities',
                    'rating': '4.1',
                    'features': ['Microsoft 365 integration', 'AI Builder', 'RPA capabilities', 'Low-code automation'],
                    'best_for': 'Microsoft ecosystem companies',
                    'implementation': '2-4 weeks',
                    'roi_range': '1,200% - 3,000%',
                    'use_cases': ['Office automation', 'Document processing', 'Approval workflows']
                }
            ]
        }
        
        return external_vendors.get(category, [])
    
    def _generate_implementation_roadmap(self, assessment_data: Dict, implementation_phases: List[str],
                                       resource_requirements: List[str], training_needs: List[str],
                                       pilot_project: str, team_availability: str) -> List[Dict]:
        """Generate detailed 6-month implementation roadmap"""
        roadmap = []
        
        # Month 1-2: Assessment & Planning
        roadmap.append({
            'phase': 'Month 1-2',
            'title': 'Assessment & Planning',
            'activities': [
                'Comprehensive data audit and quality assessment',
                'Stakeholder alignment and goal setting',
                'Pilot project selection and scoping',
                'Resource allocation and team formation',
                'Security and compliance review'
            ],
            'deliverables': [
                'Detailed implementation plan',
                'Resource allocation matrix',
                'Success metrics and KPIs',
                'Risk assessment and mitigation plan',
                'Pilot project charter'
            ],
            'resources': ['Project manager', 'Technical lead', 'Data analyst'],
            'timeline': '8 weeks'
        })
        
        # Month 3-4: Pilot Implementation
        pilot_activities = []
        if pilot_project == 'customer-service':
            pilot_activities = ['Customer service automation pilot', 'Chatbot training and testing']
        elif pilot_project == 'data-analytics':
            pilot_activities = ['Data analytics dashboard development', 'Initial data integration']
        elif pilot_project == 'process-automation':
            pilot_activities = ['Process automation pilot', 'Workflow testing and optimization']
        else:
            pilot_activities = ['Selected pilot project implementation', 'System testing and validation']
        
        roadmap.append({
            'phase': 'Month 3-4',
            'title': 'Pilot Implementation',
            'activities': pilot_activities + [
                'Team training and skill development',
                'Initial metrics collection and analysis',
                'User feedback collection and iteration'
            ],
            'deliverables': [
                'Working pilot system',
                'Training materials and documentation',
                'Baseline performance metrics',
                'User feedback report',
                'Lessons learned document'
            ],
            'resources': ['Technical team', 'End users', 'Change manager'],
            'timeline': '8 weeks'
        })
        
        # Month 5-6: Scale & Optimize
        roadmap.append({
            'phase': 'Month 5-6',
            'title': 'Scale & Optimize',
            'activities': [
                'Full system deployment and integration',
                'Process optimization and workflow refinement',
                'Performance monitoring and optimization',
                'Advanced feature implementation',
                'Team training completion'
            ],
            'deliverables': [
                'Full system deployment',
                'Optimized workflows and processes',
                'Performance dashboard and monitoring',
                'Comprehensive training program',
                'Maintenance and support plan'
            ],
            'resources': ['Full implementation team', 'End users', 'Support team'],
            'timeline': '8 weeks'
        })
        
        return roadmap
    
    def _generate_roi_projections(self, assessment_data: Dict, expected_roi: str, 
                                payback_period: str, opportunities: List[Dict]) -> Dict:
        """Generate realistic ROI projections and payback periods based on budget constraints"""
        # Get budget information for realistic calculations
        budget = assessment_data.get('budget', '25k-50k')
        company_size = assessment_data.get('company_size', '11-50')
        industry = assessment_data.get('industry', 'technology')
        
        # Calculate realistic ROI based on budget and company size
        if '25k-50k' in budget:
            base_roi = 75000  # Conservative base ROI for small budget
            max_roi = 150000  # Maximum realistic ROI
        elif '50k-100k' in budget:
            base_roi = 150000
            max_roi = 300000
        elif '100k-250k' in budget:
            base_roi = 300000
            max_roi = 600000
        else:  # 250k+
            base_roi = 600000
            max_roi = 1200000
        
        # Adjust based on company size
        if '1-10' in company_size:
            base_roi = int(base_roi * 0.5)
            max_roi = int(max_roi * 0.5)
        elif '11-50' in company_size:
            base_roi = int(base_roi * 0.8)
            max_roi = int(max_roi * 0.8)
        elif '51-100' in company_size:
            base_roi = int(base_roi * 1.0)  # Base calculation
            max_roi = int(max_roi * 1.0)
        elif '101-250' in company_size:
            base_roi = int(base_roi * 1.2)
            max_roi = int(max_roi * 1.2)
        else:  # 250+
            base_roi = int(base_roi * 1.5)
            max_roi = int(max_roi * 1.5)
        
        # Calculate payback period based on budget and implementation complexity
        if '3-months' in assessment_data.get('timeline', ''):
            payback_months = 6
        elif '6-months' in assessment_data.get('timeline', ''):
            payback_months = 9
        elif '12-months' in assessment_data.get('timeline', ''):
            payback_months = 15
        else:
            payback_months = 12  # Default 12 months
        
        # Generate realistic ROI explanation
        roi_explanation = f"Based on your {industry} industry focus, {company_size} company size, and {budget} budget range, our analysis projects a realistic annual ROI of ${base_roi:,}-${max_roi:,} with upside potential of ${int(max_roi * 1.3):,}. This projection considers your budget constraints, team readiness, and implementation complexity. The analysis incorporates industry benchmarks for {industry} companies of your size and accounts for the phased implementation approach."
        
        # Generate ROI breakdown with realistic explanations
        roi_breakdown = {
            'year_1': int(base_roi * 0.4),  # 40% in first year
            'year_2': int(base_roi * 0.4),  # 40% in second year
            'year_3': int(base_roi * 0.2),  # 20% in third year
            'explanation': f'Year 1 focuses on initial implementation and pilot projects (40% of total ROI). Year 2 represents full deployment and optimization (40% of total ROI). Year 3 reflects mature operations and advanced features (20% of total ROI).'
        }
        
        # Generate realistic risk factors and assumptions
        risk_factors = [
            f'Implementation timeline delays could extend payback period by 2-4 months',
            f'Team adoption challenges may reduce initial ROI by 10-15%',
            f'Technology integration complexity could increase implementation costs by 15-20%',
            f'Market conditions in {industry} sector may impact revenue growth projections',
            f'Budget constraints may limit full implementation scope'
        ]
        
        assumptions = [
            f'Full team adoption and training completion within projected timeline',
            f'Successful integration with existing {industry} business processes',
            f'Maintenance of current market conditions and competitive landscape',
            f'Adequate budget allocation for ongoing support and optimization',
            f'Phased implementation approach to manage risk and costs'
        ]
        
        return {
            'total_roi_min': base_roi,
            'total_roi_max': max_roi,
            'payback_period': f'{payback_months} months',
            'annual_savings': int(base_roi / 2),  # Assuming 2-year ROI
            'efficiency_gains': '25%',
            'cost_reduction': '20%',
            'roi_explanation': roi_explanation,
            'roi_breakdown': roi_breakdown,
            'risk_factors': risk_factors,
            'assumptions': assumptions
        }
    
    def _generate_comprehensive_risk_assessment(self, assessment_data: Dict, risk_factors: List[str],
                                              mitigation_strategies: List[str], change_management_experience: str,
                                              data_governance: str) -> List[Dict]:
        """Generate comprehensive risk assessment and mitigation strategies"""
        risks = []
        
        # Map risk factors to detailed assessments
        risk_mapping = {
            'budget-constraints': {
                'risk': 'Budget Constraints',
                'probability': 'Medium',
                'impact': 'High',
                'description': 'Limited budget may restrict implementation scope and timeline',
                'mitigation': 'Phased implementation approach, prioritize high-ROI projects, secure additional funding'
            },
            'time-constraints': {
                'risk': 'Time Constraints',
                'probability': 'High',
                'impact': 'Medium',
                'description': 'Aggressive timelines may lead to rushed implementation and quality issues',
                'mitigation': 'Realistic timeline planning, phased approach, dedicated project management'
            },
            'skill-gaps': {
                'risk': 'Skill Gaps',
                'probability': 'High',
                'impact': 'High',
                'description': 'Team lacks necessary skills for AI implementation and maintenance',
                'mitigation': 'Comprehensive training program, external consultant support, gradual skill building'
            },
            'resistance': {
                'risk': 'Employee Resistance',
                'probability': 'Medium',
                'impact': 'High',
                'description': 'Employees may resist new technologies and processes',
                'mitigation': 'Change management program, clear communication, training, incentives'
            },
            'data-quality': {
                'risk': 'Data Quality Issues',
                'probability': 'High',
                'impact': 'Medium',
                'description': 'Poor data quality may affect AI system performance and accuracy',
                'mitigation': 'Data audit and cleanup, quality improvement initiatives, ongoing monitoring'
            },
            'integration': {
                'risk': 'Integration Challenges',
                'probability': 'Medium',
                'impact': 'Medium',
                'description': 'Complex integration with existing systems may cause delays',
                'mitigation': 'Thorough integration planning, API-first approach, phased integration'
            },
            'vendor-lockin': {
                'risk': 'Vendor Lock-in',
                'probability': 'Low',
                'impact': 'Medium',
                'description': 'Dependency on specific vendors may limit flexibility',
                'mitigation': 'Multi-vendor strategy, open standards, exit planning'
            },
            'security': {
                'risk': 'Security Concerns',
                'probability': 'Medium',
                'impact': 'High',
                'description': 'AI systems may introduce new security vulnerabilities',
                'mitigation': 'Security review, compliance audit, ongoing security monitoring'
            }
        }
        
        # Generate risk assessments based on identified factors
        for risk_factor in risk_factors:
            if risk_factor in risk_mapping:
                risks.append(risk_mapping[risk_factor])
        
        # Add risks based on change management experience
        if change_management_experience == 'none':
            risks.append({
                'risk': 'Change Management Inexperience',
                'probability': 'High',
                'impact': 'High',
                'description': 'Lack of change management experience may lead to implementation failure',
                'mitigation': 'External change management consultant, structured change program, stakeholder engagement'
            })
        
        # Add risks based on data governance
        if data_governance == 'none':
            risks.append({
                'risk': 'Data Governance Gaps',
                'probability': 'High',
                'impact': 'Medium',
                'description': 'Lack of data governance may affect data quality and compliance',
                'mitigation': 'Data governance framework, policies and procedures, data stewardship program'
            })
        
        return risks
    
    def _get_default_strategic_content(self) -> Dict:
        """Get default strategic content when LLM is not available"""
        return {
            'strategic_position': 'Competitive Challenger',
            'competitors': [
                {
                    'name': 'Industry Leader Inc',
                    'position': 'Market Leader',
                    'analysis': 'Advanced AI implementation with strong market position.'
                },
                {
                    'name': 'Innovation Tech Corp',
                    'position': 'Challenger',
                    'analysis': 'Rapidly growing competitor with aggressive AI adoption.'
                },
                {
                    'name': 'Niche Solutions Ltd',
                    'position': 'Niche Player',
                    'analysis': 'Specialized AI solutions in specific segments.'
                }
            ],
            'strategic_recommendations': 'Focus on rapid implementation of customer-facing AI solutions to gain competitive advantage.',
            'vendor_matrix': [],
            'risk_assessment': [],
            'kpi_dashboard': []
        }
    
    def _get_fallback_assessment_data(self, assessment_data: Dict) -> Dict:
        """Get fallback assessment data when generation fails"""
        return {
            'client_company': assessment_data.get('company_name', 'Your Company'),
            'primary_contact': f"{assessment_data.get('first_name', '')} {assessment_data.get('last_name', '')}",
            'report_date': datetime.now().strftime('%B %d, %Y'),
            'ai_score': 75,
            'readiness_level': 'Good',
            'opportunity_count': 3,
            'total_roi_min': 450000,
            'total_roi_max': 675000,
            'payback_period': '9 months',
            
            # Enhanced Assessment breakdown
            'tech_score': 80,
            'data_score': 70,
            'team_score': 75,
            'process_score': 70,
            'change_score': 65,
            'security_score': 85,
            'tech_status': 'Good',
            'data_status': 'Fair',
            'team_status': 'Good',
            'process_status': 'Fair',
            'change_status': 'Fair',
            'security_status': 'Excellent',
            
            # Strengths and weaknesses
            'tech_strengths': ['Solid technology foundation', 'Cloud-ready environment'],
            'data_strengths': ['Existing data assets', 'Basic analytics in place'],
            'team_strengths': ['Willing to learn', 'Some technical skills'],
            'process_strengths': ['Clear business processes', 'Documented workflows'],
            'tech_weaknesses': ['Limited automation', 'Manual processes'],
            'data_weaknesses': ['Data quality issues', 'Limited data governance'],
            'team_weaknesses': ['Limited AI experience', 'Need training'],
            'process_weaknesses': ['Manual workflows', 'Inefficient processes'],
            
            # Detailed opportunities with specific recommendations
            'opportunities': [
                {
                    'title': 'Customer Service Automation',
                    'description': 'Implement AI-powered chatbots and automated customer support systems',
                    'roi': 150000,
                    'timeline': '3-6 months',
                    'priority': 'High',
                    'tools': ['Intercom', 'Zendesk', 'Freshdesk'],
                    'benefits': ['24/7 customer support', 'Reduced response time', 'Improved customer satisfaction']
                },
                {
                    'title': 'Process Automation',
                    'description': 'Automate repetitive manual tasks and workflows',
                    'roi': 100000,
                    'timeline': '4-8 months',
                    'priority': 'High',
                    'tools': ['Zapier', 'n8n', 'Microsoft Power Automate'],
                    'benefits': ['Time savings', 'Reduced errors', 'Increased efficiency']
                },
                {
                    'title': 'Advanced Data Analytics',
                    'description': 'Implement comprehensive data analytics and business intelligence',
                    'roi': 200000,
                    'timeline': '6-9 months',
                    'priority': 'Medium',
                    'tools': ['Tableau', 'Power BI', 'Looker'],
                    'benefits': ['Data-driven decisions', 'Improved insights', 'Better forecasting']
                }
            ],
            
            # Curated tool recommendations with pricing
            'tool_recommendations': [
                {
                    'category': 'Customer Service',
                    'tools': [
                        {'name': 'Intercom', 'price': '$99/month', 'features': ['AI chatbot', 'Live chat', 'Analytics']},
                        {'name': 'Zendesk', 'price': '$49/month', 'features': ['Ticket management', 'Knowledge base', 'Automation']}
                    ],
                    'rationale': 'Based on your customer service needs and preferences'
                },
                {
                    'category': 'Analytics',
                    'tools': [
                        {'name': 'Tableau', 'price': '$70/month', 'features': ['Data visualization', 'Business intelligence', 'Real-time dashboards']},
                        {'name': 'Power BI', 'price': '$9.99/month', 'features': ['Microsoft integration', 'Self-service BI', 'Advanced analytics']}
                    ],
                    'rationale': 'Based on your analytics needs and preferences'
                }
            ],
            
            # 6-month implementation roadmap
            'implementation_roadmap': [
                {
                    'phase': 'Month 1-2',
                    'title': 'Assessment & Planning',
                    'activities': ['Data audit', 'Stakeholder alignment', 'Pilot project selection'],
                    'deliverables': ['Detailed implementation plan', 'Resource allocation', 'Success metrics'],
                    'resources': ['Project manager', 'Technical lead', 'Data analyst'],
                    'timeline': '8 weeks'
                },
                {
                    'phase': 'Month 3-4',
                    'title': 'Pilot Implementation',
                    'activities': ['Customer service automation pilot', 'Team training', 'Initial metrics'],
                    'deliverables': ['Working pilot system', 'Training materials', 'Baseline metrics'],
                    'resources': ['Technical team', 'End users', 'Change manager'],
                    'timeline': '8 weeks'
                },
                {
                    'phase': 'Month 5-6',
                    'title': 'Scale & Optimize',
                    'activities': ['Full implementation', 'Process optimization', 'Performance monitoring'],
                    'deliverables': ['Full system deployment', 'Optimized workflows', 'Performance dashboard'],
                    'resources': ['Full implementation team', 'End users', 'Support team'],
                    'timeline': '8 weeks'
                }
            ],
            
            # ROI projections and payback periods
            'roi_projections': {
                'total_roi_min': 450000,
                'total_roi_max': 675000,
                'payback_period': '9 months',
                'annual_savings': 150000,
                'efficiency_gains': '35%',
                'cost_reduction': '25%',
                'roi_breakdown': {
                    'year_1': 135000,
                    'year_2': 180000,
                    'year_3': 135000
                }
            },
            
            # Risk assessment and mitigation strategies
            'risk_assessment': [
                {
                    'risk': 'Employee Resistance',
                    'probability': 'Medium',
                    'impact': 'High',
                    'description': 'Employees may resist new technologies and processes',
                    'mitigation': 'Change management program, clear communication, training, incentives'
                },
                {
                    'risk': 'Data Quality Issues',
                    'probability': 'High',
                    'impact': 'Medium',
                    'description': 'Poor data quality may affect AI system performance and accuracy',
                    'mitigation': 'Data audit and cleanup, quality improvement initiatives, ongoing monitoring'
                },
                {
                    'risk': 'Integration Challenges',
                    'probability': 'Medium',
                    'impact': 'Medium',
                    'description': 'Complex integration with existing systems may cause delays',
                    'mitigation': 'Thorough integration planning, API-first approach, phased integration'
                }
            ],
            
            # Additional insights
            'current_tools_analysis': 'Basic tools in place, good foundation for AI implementation',
            'team_readiness': 'Team shows willingness to learn, training recommended',
            'change_management_plan': 'Structured change management program needed',
            'success_metrics': ['Cost reduction', 'Efficiency improvement', 'Customer satisfaction']
        }
    
    def _get_fallback_strategy_data(self, assessment_data: Dict) -> Dict:
        """Get fallback strategy data when generation fails"""
        return {
            'client_company': assessment_data.get('company_name', 'Your Company'),
            'primary_contact': f"{assessment_data.get('first_name', '')} {assessment_data.get('last_name', '')}",
            'report_date': datetime.now().strftime('%B %d, %Y'),
            'strategic_position': 'Competitive Challenger',
            'total_roi_min': 1500000,
            'competitor_1_name': 'Industry Leader Inc',
            'competitor_1_position': 'Market Leader',
            'competitor_1_analysis': 'Advanced AI implementation with strong market position.',
            'competitor_2_name': 'Innovation Tech Corp',
            'competitor_2_position': 'Challenger',
            'competitor_2_analysis': 'Rapidly growing competitor with aggressive AI adoption.',
            'competitor_3_name': 'Niche Solutions Ltd',
            'competitor_3_position': 'Niche Player',
            'competitor_3_analysis': 'Specialized AI solutions in specific segments.',
            'strategic_recommendations': 'Focus on rapid implementation of customer-facing AI solutions to gain competitive advantage.',
            'vendor_matrix': [],
            'risk_assessment': [],
            'q1_budget': 35000,
            'q2_budget': 30000,
            'q3_budget': 20000,
            'q4_budget': 15000,
            'total_budget': 100000,
            'roi_percentage': 300,
            'kpi_dashboard': []
        }

# Global instance
report_generator = ReportGenerator()
