#!/usr/bin/env python3
"""
Database Management Script
Handles migrations, backups, and rollbacks for the AI Consultant Platform
"""

import sys
import os
from migrations import DatabaseMigration

def show_help():
    """Show usage information"""
    print("""
Database Management Commands:
============================

1. Create backup:
   python db_management.py backup [name]

2. Restore from backup:
   python db_management.py restore <backup_file>

3. Show migration history:
   python db_management.py history

4. Apply pending migrations:
   python db_management.py migrate

5. Create migration for field ordering fix:
   python db_management.py create-migration

6. Rollback last migration:
   python db_management.py rollback

Examples:
---------
python db_management.py backup before_field_fix
python db_management.py restore migrations/backup_20250812_132500.db
python db_management.py history
python db_management.py migrate
""")

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    migration = DatabaseMigration()
    
    if command == 'backup':
        backup_name = sys.argv[2] if len(sys.argv) > 2 else None
        migration.create_backup(backup_name)
        
    elif command == 'restore':
        if len(sys.argv) < 3:
            print("Error: Please specify backup file path")
            return
        backup_path = sys.argv[2]
        migration.restore_backup(backup_path)
        
    elif command == 'history':
        print("Migration History:")
        print("=" * 50)
        history = migration.get_migration_history()
        if not history:
            print("No migrations applied yet.")
        else:
            for name, applied_at, description in history:
                print(f"- {name}")
                print(f"  Applied: {applied_at}")
                print(f"  Description: {description}")
                print()
        
    elif command == 'migrate':
        print("Applying pending migrations...")
        count = migration.apply_all_pending_migrations()
        if count == 0:
            print("No pending migrations to apply.")
        
    elif command == 'create-migration':
        from migrations import create_field_ordering_migration
        print("Creating migration for field ordering fix...")
        create_field_ordering_migration()
        
    elif command == 'rollback':
        print("Rolling back last migration...")
        migration.rollback_last_migration()
        
    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()
