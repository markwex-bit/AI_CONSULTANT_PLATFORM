import sqlite3
import os
import json
from datetime import datetime

class DatabaseMigration:
    def __init__(self, db_path='ai_consultant.db'):
        self.db_path = db_path
        self.migrations_dir = 'migrations'
        self.migrations_table = 'database_migrations'
        
        # Create migrations directory if it doesn't exist
        if not os.path.exists(self.migrations_dir):
            os.makedirs(self.migrations_dir)
        
        # Initialize migrations table
        self._init_migrations_table()
    
    def _init_migrations_table(self):
        """Create the migrations tracking table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS database_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_name TEXT UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                sql_changes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_migration(self, name, description, sql_changes):
        """Create a new migration file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{name}.sql"
        filepath = os.path.join(self.migrations_dir, filename)
        
        migration_content = f"""-- Migration: {name}
-- Description: {description}
-- Created: {datetime.now().isoformat()}

{sql_changes}

-- Insert migration record
INSERT OR IGNORE INTO database_migrations (migration_name, description, sql_changes) 
VALUES ('{name}', '{description}', '{sql_changes.replace("'", "''")}');
"""
        
        with open(filepath, 'w') as f:
            f.write(migration_content)
        
        print(f"Created migration: {filename}")
        return filepath
    
    def apply_migration(self, migration_file):
        """Apply a specific migration file"""
        if not os.path.exists(migration_file):
            print(f"Migration file not found: {migration_file}")
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            with open(migration_file, 'r') as f:
                sql_content = f.read()
            
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement and not statement.startswith('--'):
                    cursor.execute(statement)
            
            conn.commit()
            print(f"Applied migration: {os.path.basename(migration_file)}")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error applying migration {migration_file}: {e}")
            return False
        finally:
            conn.close()
    
    def apply_all_pending_migrations(self):
        """Apply all pending migrations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get applied migrations
        cursor.execute('SELECT migration_name FROM database_migrations')
        applied_migrations = {row[0] for row in cursor.fetchall()}
        conn.close()
        
        # Get all migration files
        migration_files = []
        if os.path.exists(self.migrations_dir):
            for filename in os.listdir(self.migrations_dir):
                if filename.endswith('.sql'):
                    migration_files.append(filename)
        
        migration_files.sort()
        
        applied_count = 0
        for filename in migration_files:
            migration_name = filename.replace('.sql', '')
            if migration_name not in applied_migrations:
                filepath = os.path.join(self.migrations_dir, filename)
                if self.apply_migration(filepath):
                    applied_count += 1
        
        print(f"Applied {applied_count} pending migrations")
        return applied_count
    
    def get_migration_history(self):
        """Get list of applied migrations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT migration_name, applied_at, description 
            FROM database_migrations 
            ORDER BY applied_at
        ''')
        
        migrations = cursor.fetchall()
        conn.close()
        
        return migrations
    
    def rollback_last_migration(self):
        """Rollback the last applied migration (if possible)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get the last migration
        cursor.execute('''
            SELECT migration_name, sql_changes 
            FROM database_migrations 
            ORDER BY applied_at DESC 
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        if not result:
            print("No migrations to rollback")
            return False
        
        migration_name, sql_changes = result
        
        # For now, we'll just remove the migration record
        # In a full implementation, you'd want to store rollback SQL
        cursor.execute('DELETE FROM database_migrations WHERE migration_name = ?', (migration_name,))
        conn.commit()
        conn.close()
        
        print(f"Rolled back migration: {migration_name}")
        return True
    
    def create_backup(self, backup_name=None):
        """Create a backup of the current database"""
        if not backup_name:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}.db"
        
        backup_path = os.path.join(self.migrations_dir, backup_name)
        
        # Create backup
        conn = sqlite3.connect(self.db_path)
        backup_conn = sqlite3.connect(backup_path)
        
        conn.backup(backup_conn)
        
        conn.close()
        backup_conn.close()
        
        print(f"Created backup: {backup_path}")
        return backup_path
    
    def restore_backup(self, backup_path):
        """Restore database from backup"""
        if not os.path.exists(backup_path):
            print(f"Backup file not found: {backup_path}")
            return False
        
        # Create backup of current database first
        self.create_backup("pre_restore_backup.db")
        
        # Restore from backup
        backup_conn = sqlite3.connect(backup_path)
        conn = sqlite3.connect(self.db_path)
        
        backup_conn.backup(conn)
        
        backup_conn.close()
        conn.close()
        
        print(f"Restored from backup: {backup_path}")
        return True

# Example usage functions
def create_field_ordering_migration():
    """Create a migration for the field ordering fix we just applied"""
    migration = DatabaseMigration()
    
    sql_changes = """
-- Fix field ordering for Contact & Company Information section
UPDATE field_configurations 
SET sort_order = 1 
WHERE field_name = 'first_name' AND section_name = 'contact_company' AND form_flag = 'A';

UPDATE field_configurations 
SET sort_order = 2 
WHERE field_name = 'last_name' AND section_name = 'contact_company' AND form_flag = 'A';

UPDATE field_configurations 
SET sort_order = 3 
WHERE field_name = 'email' AND section_name = 'contact_company' AND form_flag = 'A';

UPDATE field_configurations 
SET sort_order = 4 
WHERE field_name = 'phone' AND section_name = 'contact_company' AND form_flag = 'A';

UPDATE field_configurations 
SET sort_order = 5 
WHERE field_name = 'company_name' AND section_name = 'contact_company' AND form_flag = 'A';

UPDATE field_configurations 
SET sort_order = 6 
WHERE field_name = 'website' AND section_name = 'contact_company' AND form_flag = 'A';

UPDATE field_configurations 
SET sort_order = 7 
WHERE field_name = 'industry' AND section_name = 'contact_company' AND form_flag = 'A';

UPDATE field_configurations 
SET sort_order = 8 
WHERE field_name = 'role' AND section_name = 'contact_company' AND form_flag = 'A';

UPDATE field_configurations 
SET sort_order = 9 
WHERE field_name = 'company_size' AND section_name = 'contact_company' AND form_flag = 'A';
"""
    
    return migration.create_migration(
        'fix_contact_company_field_ordering',
        'Fix field ordering for Contact & Company Information section to display fields in logical order',
        sql_changes
    )

if __name__ == "__main__":
    # Example usage
    migration = DatabaseMigration()
    
    print("Database Migration System")
    print("=" * 40)
    
    # Show migration history
    print("\nApplied Migrations:")
    history = migration.get_migration_history()
    for name, applied_at, description in history:
        print(f"- {name} ({applied_at}): {description}")
    
    # Create backup
    print("\nCreating backup...")
    migration.create_backup()
    
    # Apply pending migrations
    print("\nApplying pending migrations...")
    migration.apply_all_pending_migrations()
