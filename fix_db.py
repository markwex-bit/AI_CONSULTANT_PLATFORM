import sqlite3

# Add missing report_type column
conn = sqlite3.connect('ai_consultant.db')
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE assessments ADD COLUMN report_type TEXT DEFAULT "assessment"')
    conn.commit()
    print("✅ Added report_type column successfully")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("✅ report_type column already exists")
    else:
        print(f"❌ Error adding report_type column: {e}")

conn.close()






