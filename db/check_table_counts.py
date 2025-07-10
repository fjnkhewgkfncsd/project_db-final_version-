#!/usr/bin/env python3
"""
Quick Database Record Count Check
"""
import os
import subprocess
from dotenv import load_dotenv

def get_table_counts():
    # Load environment variables
    load_dotenv('../backend/.env')
    
    # Database connection details
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'ecommerce_db'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password')
    }
    
    # Tables to check
    tables = [
        'users', 'categories', 'products', 'product_sizes',
        'cart', 'cart_items', 'orders', 'order_items',
        'payments', 'shipments', 'notifications', 'favorites'
    ]
    
    print('=== DATABASE TABLE RECORD COUNTS ===')
    print(f'Database: {db_config["database"]}')
    print(f'Host: {db_config["host"]}:{db_config["port"]}')
    print('=' * 50)
    print(f'{"Table Name":<20} | {"Record Count":>12}')
    print('-' * 50)
    
    # Set password environment variable
    env = os.environ.copy()
    env['PGPASSWORD'] = db_config['password']
    
    total_records = 0
    
    for table in tables:
        query = f'SELECT COUNT(*) FROM {table};'
        cmd = [
            'psql',
            '-h', db_config['host'],
            '-p', db_config['port'],
            '-U', db_config['user'],
            '-d', db_config['database'],
            '-c', query,
            '--no-password',
            '-t',
            '-A'
        ]
        
        try:
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                count = int(result.stdout.strip())
                total_records += count
                print(f'{table:<20} | {count:>12,}')
            else:
                print(f'{table:<20} | {"ERROR":>12}')
                print(f'  Error: {result.stderr.strip()}')
        except subprocess.TimeoutExpired:
            print(f'{table:<20} | {"TIMEOUT":>12}')
        except Exception as e:
            print(f'{table:<20} | {"EXCEPTION":>12}')
            print(f'  Exception: {str(e)}')
    
    print('-' * 50)
    print(f'{"TOTAL RECORDS":<20} | {total_records:>12,}')
    print('=' * 50)

if __name__ == "__main__":
    get_table_counts()
