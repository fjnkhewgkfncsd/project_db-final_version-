#!/usr/bin/env python3
"""
Add Default Admin User Without Clearing Data
"""

import os
import psycopg2
import bcrypt
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def create_admin_user():
    # Connection parameters
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'ecommerce_db'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'hengmengly123')
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Check if admin exists
        cursor.execute("SELECT user_id FROM users WHERE email = %s", ('admin@example.com',))
        existing = cursor.fetchone()
        
        if existing:
            print("✅ Admin user already exists!")
            return
        
        # Create admin user
        admin_id = str(uuid.uuid4())
        password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute("""
            INSERT INTO users (user_id, username, email, password_hash, first_name, last_name, 
                             phone, date_of_birth, created_at, role, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            admin_id,
            'admin',
            'admin@example.com',
            password_hash,
            'Admin',
            'User',
            '+1234567890',
            '1990-01-01',
            datetime.now(),
            'admin',
            True
        ))
        
        # Create staff user
        staff_id = str(uuid.uuid4())
        staff_password_hash = bcrypt.hashpw('staff123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute("""
            INSERT INTO users (user_id, username, email, password_hash, first_name, last_name, 
                             phone, date_of_birth, created_at, role, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            staff_id,
            'staff',
            'staff@example.com',
            staff_password_hash,
            'Staff',
            'User',
            '+1234567891',
            '1990-01-01',
            datetime.now(),
            'staff',
            True
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Admin and Staff users created successfully!")
        print("   🔒 Admin: admin@example.com / admin123")
        print("   👤 Staff: staff@example.com / staff123")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

if __name__ == "__main__":
    create_admin_user()
