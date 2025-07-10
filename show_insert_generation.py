#!/usr/bin/env python3
"""
Demonstrate how user data becomes INSERT statements in backups
"""

import psycopg2
import os
from datetime import datetime

# Database connection
conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    database=os.getenv('DB_NAME', 'ecommerce_db'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', 'hengmengly123'),
    port=os.getenv('DB_PORT', 5432)
)

cursor = conn.cursor()

print("🔍 Showing how web form data becomes INSERT statements in backups\n")

# 1. Show current users (these came from web forms/API calls, not manual SQL)
print("📊 Current users in database (from web forms/API):")
cursor.execute("SELECT id, username, email, created_at FROM users LIMIT 5")
users = cursor.fetchall()

for user in users:
    print(f"   ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")

print(f"\n💾 Total users in database: ", end="")
cursor.execute("SELECT COUNT(*) FROM users")
total_users = cursor.fetchone()[0]
print(f"{total_users}")

# 2. Show what INSERT statements would look like for these users
print(f"\n🔧 What pg_dump generates as INSERT statements for these users:")
print("   (This is what appears in backup files)")

cursor.execute("SELECT id, username, email, password_hash, full_name, role, created_at FROM users LIMIT 3")
sample_users = cursor.fetchall()

for user in sample_users:
    insert_sql = f"""INSERT INTO users (id, username, email, password_hash, full_name, role, created_at) VALUES ({user[0]}, '{user[1]}', '{user[2]}', '{user[3]}', '{user[4]}', '{user[5]}', '{user[6]}');"""
    print(f"   {insert_sql}")

# 3. Show data flow
print(f"\n🔄 Data Flow:")
print("   1. User fills registration form on website")
print("   2. Frontend sends data to backend API")
print("   3. Backend executes: INSERT INTO users (...) VALUES (...)")
print("   4. Data is stored in database")
print("   5. pg_dump reads database and generates INSERT statements")
print("   6. Backup file contains INSERT statements")
print("   7. During restore, these INSERT statements recreate the data")

# 4. Show recent activity
print(f"\n📈 Recent user registrations (from web forms):")
cursor.execute("""
    SELECT username, email, created_at 
    FROM users 
    WHERE created_at >= NOW() - INTERVAL '7 days' 
    ORDER BY created_at DESC 
    LIMIT 5
""")
recent_users = cursor.fetchall()

if recent_users:
    for user in recent_users:
        print(f"   {user[0]} ({user[1]}) - {user[2]}")
else:
    print("   No recent registrations in the last 7 days")

cursor.close()
conn.close()

print(f"\n✅ Summary:")
print("   - Users never write INSERT statements manually")
print("   - Web forms → API calls → Automatic INSERT statements")
print("   - pg_dump reads database and generates INSERT statements for backups")
print("   - Backup files contain INSERT statements even though users used forms")
