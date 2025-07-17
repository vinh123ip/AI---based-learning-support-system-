import sqlite3

# Đường dẫn tới file database
db_path = 'cs466_database.db'

# Kết nối đến database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== CHECKING USERS TABLE STRUCTURE ===")

# Check current structure
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
print("Current columns:")
for col in columns:
    print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else ''} {'DEFAULT ' + str(col[4]) if col[4] else ''}")

# Check if is_2fa_enabled column exists
column_names = [col[1] for col in columns]
has_2fa_column = 'is_2fa_enabled' in column_names

print(f"\nhas is_2fa_enabled column: {has_2fa_column}")

if not has_2fa_column:
    print("\n=== ADDING is_2fa_enabled COLUMN ===")
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_2fa_enabled BOOLEAN DEFAULT 1")
        print("✅ Successfully added is_2fa_enabled column")
        
        # Update existing users to have 2FA enabled by default
        cursor.execute("UPDATE users SET is_2fa_enabled = 1 WHERE is_2fa_enabled IS NULL")
        rows_updated = cursor.rowcount
        print(f"✅ Updated {rows_updated} existing users with default 2FA=True")
        
        conn.commit()
    except Exception as e:
        print(f"❌ Error adding column: {e}")
else:
    print("✅ is_2fa_enabled column already exists")

# Verify final structure
print("\n=== FINAL TABLE STRUCTURE ===")
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else ''} {'DEFAULT ' + str(col[4]) if col[4] else ''}")

# Show some sample data
print("\n=== SAMPLE USER DATA ===")
cursor.execute("SELECT id, username, email, is_2fa_enabled FROM users LIMIT 3")
users = cursor.fetchall()
for user in users:
    print(f"  ID:{user[0]} {user[1]} ({user[2]}) 2FA:{user[3]}")

# Đóng kết nối
conn.close()
print("\n✅ Database operations completed!")
