import sqlite3

def check_admin_accounts():
    """Check current admin accounts in database"""
    conn = sqlite3.connect('cs466_database.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, email, role, full_name FROM users WHERE role = "admin"')
    admin_accounts = cursor.fetchall()
    
    print("=== ADMIN ACCOUNTS ===")
    if admin_accounts:
        for row in admin_accounts:
            print(f"ID: {row[0]}")
            print(f"Username: {row[1]}")
            print(f"Email: {row[2]}")
            print(f"Role: {row[3]}")
            print(f"Full Name: {row[4]}")
            print("-" * 30)
    else:
        print("No admin accounts found!")
    
    conn.close()

if __name__ == "__main__":
    check_admin_accounts() 