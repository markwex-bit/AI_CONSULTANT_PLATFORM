#!/usr/bin/env python3
"""
Field Organization System
Provides intelligent field positioning and automatic reordering
"""

import sqlite3
import json
from datetime import datetime

class FieldOrganizer:
    def __init__(self, db_path='ai_consultant.db'):
        self.db_path = db_path
        
    def get_field_layout(self, section_name, form_flag='A'):
        """Get the current field layout for a section"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                fc.field_name,
                fc.field_label,
                fc.step_number as field_step,
                fc.sort_order as field_order,
                sc.step_number as card_step,
                sc.section_title
            FROM field_configurations fc
            LEFT JOIN section_configurations sc ON fc.section_name = sc.section_name AND fc.form_flag = sc.form_flag
            WHERE fc.section_name = ? AND fc.form_flag = ?
            ORDER BY sc.step_number, fc.step_number, fc.sort_order, fc.field_name
        ''', (section_name, form_flag))
        
        fields = cursor.fetchall()
        conn.close()
        
        return fields
    
    def analyze_field_layout(self, section_name, form_flag='A'):
        """Analyze the current field layout and identify issues"""
        fields = self.get_field_layout(section_name, form_flag)
        
        print(f"Field Layout Analysis for: {section_name}")
        print("=" * 60)
        
        issues = []
        
        # Check for duplicate sort orders
        sort_orders = [field[3] for field in fields]
        duplicates = [x for x in set(sort_orders) if sort_orders.count(x) > 1]
        if duplicates:
            issues.append(f"Duplicate sort orders found: {duplicates}")
        
        # Check for gaps in sort order
        if sort_orders:
            expected_range = list(range(1, len(sort_orders) + 1))
            gaps = [x for x in expected_range if x not in sort_orders]
            if gaps:
                issues.append(f"Gaps in sort order: {gaps}")
        
        # Check for zero sort orders
        zero_orders = [field[0] for field in fields if field[3] == 0]
        if zero_orders:
            issues.append(f"Fields with zero sort order: {zero_orders}")
        
        # Display current layout
        print("\nCurrent Field Layout:")
        print("-" * 60)
        for i, field in enumerate(fields, 1):
            field_name, field_label, field_step, field_order, card_step, section_title = field
            print(f"{i:2d}. {field_label:<20} (DB: {field_name:<15}) | Step: {field_step} | Order: {field_order}")
        
        # Display issues
        if issues:
            print("\nIssues Found:")
            print("-" * 60)
            for issue in issues:
                print(f"⚠️  {issue}")
        else:
            print("\n✅ No issues found in field layout")
        
        return fields, issues
    
    def auto_reorder_fields(self, section_name, form_flag='A', preserve_relative_order=True):
        """Automatically reorder fields to fix gaps and duplicates"""
        fields = self.get_field_layout(section_name, form_flag)
        
        if not fields:
            print(f"No fields found for section: {section_name}")
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Create a mapping of current positions to new positions
            if preserve_relative_order:
                # Preserve relative order by sorting by current sort_order
                sorted_fields = sorted(fields, key=lambda x: x[3] if x[3] > 0 else 999)
            else:
                # Use alphabetical order as fallback
                sorted_fields = sorted(fields, key=lambda x: x[1])  # Sort by field_label
            
            # Update sort orders sequentially
            for i, field in enumerate(sorted_fields, 1):
                field_name = field[0]
                cursor.execute('''
                    UPDATE field_configurations 
                    SET sort_order = ? 
                    WHERE field_name = ? AND section_name = ? AND form_flag = ?
                ''', (i, field_name, section_name, form_flag))
            
            conn.commit()
            print(f"✅ Auto-reordered {len(sorted_fields)} fields in section '{section_name}'")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error reordering fields: {e}")
            return False
        finally:
            conn.close()
    
    def insert_field_at_position(self, field_name, section_name, position, form_flag='A'):
        """Insert a field at a specific position and shift others"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get current fields in this section
            cursor.execute('''
                SELECT field_name, sort_order 
                FROM field_configurations 
                WHERE section_name = ? AND form_flag = ?
                ORDER BY sort_order
            ''', (section_name, form_flag))
            
            current_fields = cursor.fetchall()
            
            # Shift fields to make room for insertion
            for field_name_existing, sort_order in current_fields:
                if sort_order >= position:
                    cursor.execute('''
                        UPDATE field_configurations 
                        SET sort_order = ? 
                        WHERE field_name = ? AND section_name = ? AND form_flag = ?
                    ''', (sort_order + 1, field_name_existing, section_name, form_flag))
            
            # Set the new field's position
            cursor.execute('''
                UPDATE field_configurations 
                SET sort_order = ? 
                WHERE field_name = ? AND section_name = ? AND form_flag = ?
            ''', (position, field_name, section_name, form_flag))
            
            conn.commit()
            print(f"✅ Inserted field '{field_name}' at position {position}")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error inserting field: {e}")
            return False
        finally:
            conn.close()
    
    def remove_field_and_reorder(self, field_name, section_name, form_flag='A'):
        """Remove a field and reorder remaining fields"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get the position of the field to remove
            cursor.execute('''
                SELECT sort_order 
                FROM field_configurations 
                WHERE field_name = ? AND section_name = ? AND form_flag = ?
            ''', (field_name, section_name, form_flag))
            
            result = cursor.fetchone()
            if not result:
                print(f"❌ Field '{field_name}' not found in section '{section_name}'")
                return False
            
            removed_position = result[0]
            
            # Shift fields after the removed position
            cursor.execute('''
                UPDATE field_configurations 
                SET sort_order = sort_order - 1 
                WHERE section_name = ? AND form_flag = ? AND sort_order > ?
            ''', (section_name, form_flag, removed_position))
            
            # Set the removed field's sort_order to NULL (or 0)
            cursor.execute('''
                UPDATE field_configurations 
                SET sort_order = 0 
                WHERE field_name = ? AND section_name = ? AND form_flag = ?
            ''', (field_name, section_name, form_flag))
            
            conn.commit()
            print(f"✅ Removed field '{field_name}' from position {removed_position} and reordered remaining fields")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error removing field: {e}")
            return False
        finally:
            conn.close()
    
    def move_field(self, field_name, section_name, new_position, form_flag='A'):
        """Move a field to a new position"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get current position
            cursor.execute('''
                SELECT sort_order 
                FROM field_configurations 
                WHERE field_name = ? AND section_name = ? AND form_flag = ?
            ''', (field_name, section_name, form_flag))
            
            result = cursor.fetchone()
            if not result:
                print(f"❌ Field '{field_name}' not found")
                return False
            
            current_position = result[0]
            
            if current_position == new_position:
                print(f"✅ Field '{field_name}' is already at position {new_position}")
                return True
            
            # Get total number of fields
            cursor.execute('''
                SELECT COUNT(*) 
                FROM field_configurations 
                WHERE section_name = ? AND form_flag = ?
            ''', (section_name, form_flag))
            
            total_fields = cursor.fetchone()[0]
            
            # Validate new position
            if new_position < 1 or new_position > total_fields:
                print(f"❌ Invalid position {new_position}. Must be between 1 and {total_fields}")
                return False
            
            # Move the field
            if current_position < new_position:
                # Moving forward: shift fields between current and new position backward
                cursor.execute('''
                    UPDATE field_configurations 
                    SET sort_order = sort_order - 1 
                    WHERE section_name = ? AND form_flag = ? AND sort_order > ? AND sort_order <= ?
                ''', (section_name, form_flag, current_position, new_position))
            else:
                # Moving backward: shift fields between new and current position forward
                cursor.execute('''
                    UPDATE field_configurations 
                    SET sort_order = sort_order + 1 
                    WHERE section_name = ? AND form_flag = ? AND sort_order >= ? AND sort_order < ?
                ''', (section_name, form_flag, new_position, current_position))
            
            # Set the field's new position
            cursor.execute('''
                UPDATE field_configurations 
                SET sort_order = ? 
                WHERE field_name = ? AND section_name = ? AND form_flag = ?
            ''', (new_position, field_name, section_name, form_flag))
            
            conn.commit()
            print(f"✅ Moved field '{field_name}' from position {current_position} to {new_position}")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error moving field: {e}")
            return False
        finally:
            conn.close()
    
    def create_field_template(self, section_name, form_flag='A'):
        """Create a template showing the ideal field layout for a section"""
        fields = self.get_field_layout(section_name, form_flag)
        
        if not fields:
            print(f"No fields found for section: {section_name}")
            return
        
        print(f"Field Template for: {section_name}")
        print("=" * 60)
        print("Ideal field layout based on form flow:")
        print()
        
        # Group fields by logical sections
        contact_fields = ['first_name', 'last_name', 'email', 'phone']
        company_fields = ['company_name', 'website', 'industry', 'role', 'company_size']
        
        print("📋 Contact Information:")
        for field_name, field_label, field_step, field_order, card_step, section_title in fields:
            if field_name in contact_fields:
                print(f"  • {field_label} (DB: {field_name})")
        
        print("\n🏢 Company Information:")
        for field_name, field_label, field_step, field_order, card_step, section_title in fields:
            if field_name in company_fields:
                print(f"  • {field_label} (DB: {field_name})")
        
        print("\n📊 Other Fields:")
        for field_name, field_label, field_step, field_order, card_step, section_title in fields:
            if field_name not in contact_fields and field_name not in company_fields:
                print(f"  • {field_label} (DB: {field_name})")
    
    def export_field_layout(self, section_name, form_flag='A', filename=None):
        """Export field layout to JSON for backup or sharing"""
        fields = self.get_field_layout(section_name, form_flag)
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"field_layout_{section_name}_{timestamp}.json"
        
        layout_data = {
            'section_name': section_name,
            'form_flag': form_flag,
            'exported_at': datetime.now().isoformat(),
            'fields': []
        }
        
        for field_name, field_label, field_step, field_order, card_step, section_title in fields:
            layout_data['fields'].append({
                'field_name': field_name,
                'field_label': field_label,
                'field_step': field_step,
                'field_order': field_order,
                'card_step': card_step,
                'section_title': section_title
            })
        
        with open(filename, 'w') as f:
            json.dump(layout_data, f, indent=2)
        
        print(f"✅ Exported field layout to: {filename}")
        return filename

# Example usage and testing
if __name__ == "__main__":
    organizer = FieldOrganizer()
    
    # Analyze current layout
    print("=== FIELD LAYOUT ANALYSIS ===")
    organizer.analyze_field_layout('contact_company', 'A')
    
    print("\n" + "="*80 + "\n")
    
    # Create field template
    print("=== FIELD TEMPLATE ===")
    organizer.create_field_template('contact_company', 'A')
    
    print("\n" + "="*80 + "\n")
    
    # Export layout
    print("=== EXPORT LAYOUT ===")
    organizer.export_field_layout('contact_company', 'A')
