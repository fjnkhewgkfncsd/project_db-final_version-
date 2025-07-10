#!/usr/bin/env python3
"""
Reset admin password for main system access
"""
import psycopg2
import os
import bcrypt
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

def reset_admin_password():
    """Reset the admin password to admin123"""
    
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'hengmengly123')
    DB_NAME = os.getenv('DB_NAME', 'ecommerce_db')
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        print("🔑 RESETTING ADMIN PASSWORD")
        print("=" * 40)
        
        # Hash the new password
        new_password = "admin123"
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
        
        print(f"New password: {new_password}")
        print(f"Generated hash: {password_hash[:50]}...")
        
        # Update admin password
        cursor.execute("""
            UPDATE users 
            SET password_hash = %s, updated_at = CURRENT_TIMESTAMP
            WHERE email = 'admin@example.com' AND role ILIKE 'admin';
        """, (password_hash,))
        
        rows_affected = cursor.rowcount
        conn.commit()
        
        if rows_affected > 0:
            print(f"✅ Successfully updated {rows_affected} admin account(s)")
            print()
            print("📋 UPDATED ADMIN CREDENTIALS:")
            print("   Email: admin@example.com")
            print("   Password: admin123")
            print("   Role: Admin")
            print()
            print("🎯 You can now login to the main system at http://localhost:3000")
        else:
            print("❌ No admin accounts found to update")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error resetting password: {e}")

if __name__ == "__main__":
    reset_admin_password()
