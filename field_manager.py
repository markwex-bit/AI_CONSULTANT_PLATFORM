#!/usr/bin/env python3
"""
Field Manager - Command Line Interface
Provides easy-to-use commands for field organization
"""

import sys
import argparse
from field_organizer import FieldOrganizer

def main():
    parser = argparse.ArgumentParser(description='Field Organization Management System')
    parser.add_argument('command', choices=[
        'analyze', 'reorder', 'insert', 'remove', 'move', 
        'template', 'export', 'auto-fix'
    ], help='Command to execute')
    
    parser.add_argument('--section', '-s', required=True, 
                       help='Section name (e.g., contact_company)')
    parser.add_argument('--form', '-f', default='A', 
                       help='Form flag (A=Assessment, S=Strategy)')
    parser.add_argument('--field', help='Field name for insert/remove/move operations')
    parser.add_argument('--position', '-p', type=int, 
                       help='Position for insert/move operations')
    parser.add_argument('--output', '-o', 
                       help='Output filename for export')
    
    args = parser.parse_args()
    
    organizer = FieldOrganizer()
    
    if args.command == 'analyze':
        print("🔍 Analyzing field layout...")
        organizer.analyze_field_layout(args.section, args.form)
        
    elif args.command == 'reorder':
        print("🔄 Reordering fields...")
        organizer.auto_reorder_fields(args.section, args.form)
        
    elif args.command == 'insert':
        if not args.field or not args.position:
            print("❌ Error: --field and --position are required for insert command")
            return
        print(f"➕ Inserting field '{args.field}' at position {args.position}...")
        organizer.insert_field_at_position(args.field, args.section, args.position, args.form)
        
    elif args.command == 'remove':
        if not args.field:
            print("❌ Error: --field is required for remove command")
            return
        print(f"➖ Removing field '{args.field}'...")
        organizer.remove_field_and_reorder(args.field, args.section, args.form)
        
    elif args.command == 'move':
        if not args.field or not args.position:
            print("❌ Error: --field and --position are required for move command")
            return
        print(f"🔄 Moving field '{args.field}' to position {args.position}...")
        organizer.move_field(args.field, args.section, args.position, args.form)
        
    elif args.command == 'template':
        print("📋 Creating field template...")
        organizer.create_field_template(args.section, args.form)
        
    elif args.command == 'export':
        print("📤 Exporting field layout...")
        organizer.export_field_layout(args.section, args.form, args.output)
        
    elif args.command == 'auto-fix':
        print("🔧 Auto-fixing field layout issues...")
        fields, issues = organizer.analyze_field_layout(args.section, args.form)
        if issues:
            print("\n🔄 Issues detected, attempting to fix...")
            organizer.auto_reorder_fields(args.section, args.form)
            print("\n✅ Re-analyzing after fix...")
            organizer.analyze_field_layout(args.section, args.form)
        else:
            print("✅ No issues to fix!")

def show_examples():
    """Show usage examples"""
    print("""
Field Manager - Usage Examples
==============================

1. Analyze current field layout:
   python field_manager.py analyze --section contact_company

2. Auto-reorder fields to fix gaps/duplicates:
   python field_manager.py reorder --section contact_company

3. Insert a new field at position 3:
   python field_manager.py insert --section contact_company --field new_field --position 3

4. Remove a field and reorder:
   python field_manager.py remove --section contact_company --field old_field

5. Move a field to a new position:
   python field_manager.py move --section contact_company --field email --position 1

6. Create a field template:
   python field_manager.py template --section contact_company

7. Export field layout to JSON:
   python field_manager.py export --section contact_company --output layout.json

8. Auto-fix all issues:
   python field_manager.py auto-fix --section contact_company

Form Flags:
- A = Assessment form
- S = Strategic Blueprint form

Examples:
---------
python field_manager.py analyze -s contact_company -f A
python field_manager.py insert -s contact_company -f A --field middle_name --position 2
python field_manager.py move -s contact_company -f A --field phone --position 4
""")

if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help', 'help']:
        show_examples()
    else:
        main()
