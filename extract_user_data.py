#!/usr/bin/env python3
"""
Extract user data from backup file and convert to INSERT statements
"""

def extract_user_data(backup_file, output_file=None):
    """Extract user data from backup and convert to INSERT statements"""
    
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        user_data = []
        in_users_section = False
        
        print(f"📁 Processing backup file: {backup_file}")
        
        for line in lines:
            # Start of users data section
            if 'COPY public.users' in line:
                in_users_section = True
                print("👥 Found users data section")
                continue
            
            # End of users data section
            if in_users_section and line.strip() == '\\.':
                in_users_section = False
                break
            
            # Process user data lines
            if in_users_section and line.strip() and not line.startswith('--'):
                user_data.append(line.strip())
        
        print(f"📊 Found {len(user_data)} users in backup")
        
        # Display the users found
        print("\n👥 Users found:")
        for i, user_line in enumerate(user_data, 1):
            parts = user_line.split('\t')
            if len(parts) >= 13:
                user_id = parts[0]
                username = parts[1]
                email = parts[2]
                role = parts[12]
                print(f"  {i}. {username} ({email}) - {role}")
        
        # Convert to INSERT statements
        if user_data:
            print(f"\n🔄 Converting to INSERT statements...")
            
            insert_statements = []
            insert_statements.append("-- User data extracted from backup")
            insert_statements.append("-- Generated automatically")
            insert_statements.append("")
            
            for user_line in user_data:
                parts = user_line.split('\t')
                if len(parts) >= 13:
                    # Convert \\N to NULL for SQL
                    sql_parts = []
                    for part in parts:
                        if part == '\\N':
                            sql_parts.append('NULL')
                        else:
                            sql_parts.append(f"'{part}'")
                    
                    insert_sql = f"""INSERT INTO users (user_id, username, email, password_hash, first_name, last_name, phone, date_of_birth, created_at, updated_at, last_login, is_active, role) 
VALUES ({', '.join(sql_parts)});"""
                    insert_statements.append(insert_sql)
                    insert_statements.append("")
            
            # Save to file if requested
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(insert_statements))
                print(f"💾 INSERT statements saved to: {output_file}")
            
            # Display first few INSERT statements
            print("\n📝 Sample INSERT statements:")
            for stmt in insert_statements[:10]:  # Show first few
                if stmt.startswith('INSERT'):
                    print(f"  {stmt[:100]}...")
                    break
        
        return user_data, insert_statements if user_data else ([], [])
        
    except Exception as e:
        print(f"❌ Error processing backup file: {e}")
        return [], []

if __name__ == "__main__":
    backup_file = "backups/ecommerce_backup_2025-06-27_01-28-23.sql"
    output_file = "extracted_users.sql"
    
    users, inserts = extract_user_data(backup_file, output_file)
    
    if users:
        print(f"\n✅ Successfully extracted {len(users)} users!")
        print(f"📄 You can now use '{output_file}' to restore just the user data")
        print("\n💡 To restore these users to your database:")
        print("   1. Use the generated INSERT statements")
        print("   2. Or run: psql -d ecommerce_db -f extracted_users.sql")
        print("   3. Or copy-paste the statements into your Query Console")
    else:
        print("❌ No user data found in backup file")
