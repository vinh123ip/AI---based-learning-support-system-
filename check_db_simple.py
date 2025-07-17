import sqlite3

def check_database(db_name):
    print(f"=== {db_name} ===")
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            print("Users table columns:")
            for col in columns:
                print(f"  {col[1]} {col[2]} {'DEFAULT ' + str(col[4]) if col[4] else ''}")
            
            # Check specifically for is_2fa_enabled
            has_2fa = any(col[1] == 'is_2fa_enabled' for col in columns)
            print(f"Has is_2fa_enabled column: {has_2fa}")
            
            if has_2fa:
                cursor.execute("SELECT id, username, is_2fa_enabled FROM users LIMIT 3")
                users = cursor.fetchall()
                print("Sample users 2FA status:")
                for user in users:
                    print(f"  ID:{user[0]} {user[1]} -> 2FA:{user[2]}")
        else:
            print("No users table found")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
    print()

# Check both databases
check_database("cs466_database.db")
check_database("learning_system.db") 