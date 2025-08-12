#!/usr/bin/env python3
"""
Dynamic Form Generator
Generates forms based on field configurations from the database
"""

import json
from typing import Dict, List, Optional
from models import db_manager

class DynamicFormGenerator:
    """Generates dynamic forms based on database field configurations"""
    
    def __init__(self):
        self.db_manager = db_manager
    
    def get_field_configurations(self, form_flag: str = 'A') -> List[Dict]:
        """Get field configurations for a specific form"""
        try:
            import sqlite3
            
            conn = sqlite3.connect('ai_consultant.db')
            cursor = conn.cursor()
            
            query = '''
                SELECT fc.field_name, fc.field_label, fc.field_type, fc.section_name, fc.is_required, fc.is_visible, fc.form_flag, fc.step_number, fc.sort_order, sc.step_number as section_step, sc.section_title
                FROM field_configurations fc
                LEFT JOIN section_configurations sc ON fc.section_name = sc.section_name AND fc.form_flag = sc.form_flag
                WHERE fc.form_flag = ?
                ORDER BY sc.step_number, fc.step_number, fc.sort_order, fc.field_name
            '''
            
            cursor.execute(query, (form_flag,))
            rows = cursor.fetchall()
            conn.close()
            
            configurations = []
            for row in rows:
                configurations.append({
                    'field_name': row[0],
                    'field_label': row[1],
                    'field_type': row[2],
                    'section_name': row[3],
                    'is_required': bool(row[4]),
                    'is_visible': bool(row[5]),
                    'form_flag': row[6],
                    'step_number': row[7] if row[7] is not None else 1,
                    'sort_order': row[8] if row[8] is not None else 0,
                    'section_step': row[9] if row[9] is not None else 1,
                    'section_title': row[10] if row[10] is not None else 'Unassigned'
                })
            
            # Group fields by section
            sections = {}
            for field in configurations:
                section_name = field.get('section_title', 'Unknown')
                if section_name not in sections:
                    sections[section_name] = []
                sections[section_name].append(field)
            
            return sections
        except Exception as e:
            print(f"Error getting field configurations: {e}")
            return {}
    
    def generate_form_html(self, form_flag: str = 'A') -> str:
        """Generate HTML form based on field configurations"""
        try:
            sections = self.get_field_configurations(form_flag)
            
            if not sections:
                return "<p>No form configuration found.</p>"
            
            html = []
            step_number = 1
            
            # Sort sections by section_step
            sorted_section_names = sorted(sections.keys(), key=lambda k: sections[k][0].get('section_step', 0))
            
            for section_name in sorted_section_names:
                fields = sorted(sections[section_name], key=lambda f: (f.get('step_number', 0), f.get('sort_order', 0)))
                
                # Only include visible fields in the step
                visible_fields = [f for f in fields if f.get('is_visible', True)]
                if not visible_fields:
                    continue # Skip section if no visible fields
                
                html.append(f'<div class="step" id="step{step_number}">')
                html.append(f'<div class="form-card">')
                html.append(f'<div class="card-header">')
                html.append(f'<h3>{section_name}</h3>')
                html.append(f'</div>')
                html.append(f'<div class="card-body">')
                
                # Generate fields based on section type
                if section_name == "Contact & Company Information":
                    html.extend(self._generate_contact_section(visible_fields))
                else:
                    html.extend(self._generate_generic_section(visible_fields))
                
                html.append(f'</div>')  # Close card-body
                html.append(f'</div>')  # Close form-card
                html.append('</div>')   # Close step
                step_number += 1
            
            # Add step navigation
            html.append('''
            <div class="step-navigation">
                <button type="button" class="btn-secondary" id="prevBtn" onclick="changeStep(-1)" style="display: none;">Previous</button>
                <button type="button" class="cta-button" id="nextBtn" onclick="changeStep(1)">Next</button>
            </div>
            ''')
            
            return '\n'.join(html)
            
        except Exception as e:
            print(f"Error generating form HTML: {e}")
            return f"<p>Error generating form: {e}</p>"
    
    def _generate_contact_section(self, fields: List[Dict]) -> List[str]:
        """Generate contact information section with specific layout"""
        html = []
        
        # First row: First Name, Last Name
        name_fields = [f for f in fields if f['field_name'] in ['first_name', 'last_name']]
        if name_fields:
            html.append('<div class="form-row">')
            for field in name_fields:
                html.append('<div class="form-col">')
                html.extend(self._generate_field_html(field))
                html.append('</div>')
            html.append('</div>')
        
        # Second row: Email, Phone, Website
        contact_fields = [f for f in fields if f['field_name'] in ['email', 'phone', 'website']]
        if contact_fields:
            html.append('<div class="form-row">')
            for field in contact_fields:
                html.append('<div class="form-col">')
                html.extend(self._generate_field_html(field))
                html.append('</div>')
            html.append('</div>')
        
        # Third row: Company Name, Role
        company_fields = [f for f in fields if f['field_name'] in ['company_name', 'role']]
        if company_fields:
            html.append('<div class="form-row">')
            for field in company_fields:
                html.append('<div class="form-col">')
                html.extend(self._generate_field_html(field))
                html.append('</div>')
            html.append('</div>')
        
        # Fourth row: Industry, Company Size
        business_fields = [f for f in fields if f['field_name'] in ['industry', 'company_size']]
        if business_fields:
            html.append('<div class="form-row">')
            for field in business_fields:
                html.append('<div class="form-col">')
                html.extend(self._generate_field_html(field))
                html.append('</div>')
            html.append('</div>')
        
        return html
    
    def _generate_generic_section(self, fields: List[Dict]) -> List[str]:
        """Generate generic section with single-row layout"""
        html = []
        
        # Each field gets its own row for better organization
        for field in fields:
            html.append('<div class="form-row">')
            html.append('<div class="form-col-full">')
            html.extend(self._generate_field_html(field))
            html.append('</div>')
            html.append('</div>')
        
        return html
    
    def _generate_field_html(self, field: Dict) -> List[str]:
        """Generate HTML for a single field"""
        html = []
        
        field_name = field['field_name']
        field_label = field['field_label']
        field_type = field['field_type']
        is_required = field.get('is_required', False)
        is_visible = field.get('is_visible', True)
        
        # Skip if field is not visible
        if not is_visible:
            return []
        
        # Don't add required asterisk or required attribute - all fields are optional for testing
        label_text = field_label
        
        html.append('<div class="form-group">')
        html.append(f'<label class="field-label">{label_text}</label>')
        
        if field_type == 'text':
            html.append(f'<input type="text" name="{field_name}" class="form-control" placeholder="Enter {field_label.lower()}">')
        
        elif field_type == 'email':
            html.append(f'<input type="email" name="{field_name}" class="form-control" placeholder="Enter your email">')
        
        elif field_type == 'tel':
            html.append(f'<input type="tel" name="{field_name}" class="form-control" placeholder="Enter phone number">')
        
        elif field_type == 'url':
            html.append(f'<input type="url" name="{field_name}" class="form-control" placeholder="https://example.com">')
        
        elif field_type == 'select':
            html.append(f'<select name="{field_name}" class="form-control">')
            html.append('<option value="">Select an option</option>')
            
            # Get dropdown options for this field
            options = self._get_dropdown_options(field_name)
            for option in options:
                html.append(f'<option value="{option["option_value"]}">{option["option_label"]}</option>')
            
            html.append('</select>')
        
        elif field_type == 'checkbox':
            # Get dropdown options for checkbox group
            options = self._get_dropdown_options(field_name)
            html.append('<div class="checkbox-group">')
            for option in options:
                html.append(f'<label class="checkbox-option">')
                html.append(f'<input type="checkbox" name="{field_name}" value="{option["option_value"]}" class="checkbox-input">')
                html.append(f'<span class="checkbox-label">{option["option_label"]}</span>')
                html.append('</label>')
            # Add "Other" text input at bottom
            html.append('<div class="other-input-section">')
            html.append(f'<input type="text" name="{field_name}_other" class="form-control other-input" placeholder="Enter other {field_label.lower()}">')
            html.append('</div>')
            html.append('</div>')
        
        elif field_type == 'textarea':
            html.append(f'<textarea name="{field_name}" rows="4" class="form-control" placeholder="Enter {field_label.lower()}"></textarea>')
        
        else:
            # Default to text input
            html.append(f'<input type="text" name="{field_name}" class="form-control" placeholder="Enter {field_label.lower()}">')
        
        html.append('</div>')
        
        return html
    
    def _get_dropdown_options(self, field_name: str) -> List[Dict]:
        """Get dropdown options for a field"""
        try:
            import sqlite3
            
            conn = sqlite3.connect('ai_consultant.db')
            cursor = conn.cursor()
            
            query = '''
                SELECT id, field_name, option_value, option_label, sort_order, form_flag
                FROM dropdown_options
                WHERE field_name = ?
                ORDER BY sort_order
            '''
            
            cursor.execute(query, (field_name,))
            rows = cursor.fetchall()
            conn.close()
            
            options = []
            for row in rows:
                options.append({
                    'id': row[0],
                    'field_name': row[1],
                    'option_value': row[2],
                    'option_label': row[3],
                    'sort_order': row[4],
                    'form_flag': row[5]
                })
            
            return options
        except Exception as e:
            print(f"Error getting dropdown options for {field_name}: {e}")
            return []
    
    def get_form_validation_rules(self, form_flag: str = 'A') -> Dict:
        """Get validation rules for the form"""
        try:
            import sqlite3
            
            conn = sqlite3.connect('ai_consultant.db')
            cursor = conn.cursor()
            
            query = '''
                SELECT fc.field_name, fc.field_type, fc.is_required, fc.is_visible
                FROM field_configurations fc
                WHERE fc.form_flag = ?
                ORDER BY fc.field_name
            '''
            
            cursor.execute(query, (form_flag,))
            rows = cursor.fetchall()
            conn.close()
            
            validation_rules = {
                'required_fields': [],
                'field_types': {},
                'checkbox_groups': []
            }
            
            for row in rows:
                field_name = row[0]
                field_type = row[1]
                is_required = bool(row[2])
                is_visible = bool(row[3])
                
                # Skip invisible fields
                if not is_visible:
                    continue
                
                # Don't add any fields as required - all fields are optional for testing
                # if is_required:
                #     validation_rules['required_fields'].append(field_name)
                
                # Store field type for validation
                validation_rules['field_types'][field_name] = field_type
                
                # Add checkbox groups for validation
                if field_type == 'checkbox':
                    validation_rules['checkbox_groups'].append(field_name)
            
            return validation_rules
            
        except Exception as e:
            print(f"Error getting validation rules: {e}")
            return {'required_fields': [], 'field_types': {}, 'checkbox_groups': []}

def main():
    """Test the dynamic form generator"""
    print("🔧 Dynamic Form Generator Test")
    print("=" * 50)
    
    generator = DynamicFormGenerator()
    
    # Test assessment form generation
    print("\n📋 Assessment Form Configuration:")
    assessment_html = generator.generate_form_html('A')
    print(f"Generated {len(assessment_html)} characters of HTML")
    
    # Test validation rules
    print("\n✅ Validation Rules:")
    validation_rules = generator.get_form_validation_rules('A')
    print(f"Required fields: {validation_rules['required_fields']}")
    print(f"Field types: {len(validation_rules['field_types'])} fields")
    print(f"Checkbox groups: {validation_rules['checkbox_groups']}")
    
    print("\n✅ Dynamic form generator test complete!")

if __name__ == "__main__":
    main()
