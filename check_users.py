#!/usr/bin/env python3
"""
Check users in the restored database
"""
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

def check_users():
    """Check what users exist in the database"""
    
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
        
        print("👥 USERS IN RESTORED DATABASE:")
        print("=" * 60)
        
        # Check users table structure first
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        print("📋 Users Table Structure:")
        for col_name, col_type in columns:
            print(f"   - {col_name}: {col_type}")
        print()
        
        # Get all users
        cursor.execute("SELECT * FROM users ORDER BY user_id;")
        users = cursor.fetchall()
        
        print(f"📊 Found {len(users)} users:")
        print("-" * 60)
        
        for user in users:
            if len(user) >= 4:
                print(f"ID: {user[0]}")
                print(f"Username: {user[1] if len(user) > 1 else 'N/A'}")
                print(f"Email: {user[2] if len(user) > 2 else 'N/A'}")
                print(f"Role: {user[4] if len(user) > 4 else 'N/A'}")
                print(f"Password Hash: {user[3][:50] if len(user) > 3 and user[3] else 'N/A'}...")
                print("-" * 30)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking users: {e}")

if __name__ == "__main__":
    check_users()
