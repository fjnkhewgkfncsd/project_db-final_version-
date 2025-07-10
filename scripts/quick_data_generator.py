#!/usr/bin/env python3
"""
E-Commerce Database Data Generator - Quick Test Version
Generates manageable dataset for testing (10k records per table)
"""

import os
import sys
import time
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import psycopg2
from psycopg2.extras import execute_batch
from faker import Faker
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class QuickDataGenerator:
    def __init__(self):
        self.fake = Faker()
        self.conn = None
        self.cursor = None
        
        # Configuration for quick testing
        self.BATCH_SIZE = 1000
        self.TARGET_RECORDS_PER_TABLE = 10_000  # Much smaller for testing
        
        # Connection parameters
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'ecommerce_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
        
        # Data storage for foreign key relationships
        self.generated_data = {
            'user_ids': [],
            'category_ids': [],
            'product_ids': [],
            'size_ids': [],
            'cart_ids': [],
            'order_ids': []
        }

    def connect_database(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            print("✅ Connected to PostgreSQL database")
            
            # Test connection
            self.cursor.execute("SELECT version();")
            version = self.cursor.fetchone()
            print(f"📋 PostgreSQL version: {version[0]}")
            
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            sys.exit(1)

    def close_connection(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔌 Database connection closed")

    def execute_batch_insert(self, query: str, data: List[tuple], description: str):
        """Execute batch insert with progress tracking"""
        try:
            with tqdm(total=len(data), desc=description, unit='records') as pbar:
                for i in range(0, len(data), self.BATCH_SIZE):
                    batch = data[i:i + self.BATCH_SIZE]
                    execute_batch(self.cursor, query, batch, page_size=self.BATCH_SIZE)
                    self.conn.commit()
                    pbar.update(len(batch))
                    
        except Exception as e:
            print(f"❌ Error in batch insert for {description}: {e}")
            self.conn.rollback()
            raise

    def generate_users(self, count: int = 10_000):
        """Generate user records"""
        print(f"\n🧑‍💼 Generating {count:,} users...")
        
        users_data = []
        roles = ['customer'] * 9500 + ['staff'] * 450 + ['admin'] * 50  # 95% customers, 4.5% staff, 0.5% admin
        random.shuffle(roles)
        
        for i in range(count):
            user_id = str(uuid.uuid4())
            self.generated_data['user_ids'].append(user_id)
            
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            username = f"{first_name.lower()}.{last_name.lower()}.{i}"[:49]  # Limit to 49 chars
            email = f"{username}@example.com"[:99]  # Limit to 99 chars
            phone = self.fake.phone_number()[:19]  # Limit to 19 chars
            
            users_data.append((
                user_id,
                username,
                email,
                '$2b$10$rKjw.6QxEQsxZ5GvKjQxHOqXcXPKXP8Zd8WcE7Y3qYzRxZqK9WqDC',  # hashed 'password123'
                first_name[:49],  # Limit first name
                last_name[:49],   # Limit last name
                phone,
                self.fake.date_of_birth(minimum_age=18, maximum_age=80),
                self.fake.date_time_between(start_date='-2y', end_date='now'),
                roles[i % len(roles)]
            ))
        
        query = """
            INSERT INTO users (user_id, username, email, password_hash, first_name, last_name, 
                             phone, date_of_birth, created_at, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        self.execute_batch_insert(query, users_data, "Inserting users")
        print(f"✅ Generated {count:,} users")

    def generate_categories(self, count: int = 500):
        """Generate category records"""
        print(f"\n📂 Generating {count:,} categories...")
        
        base_categories = [
            "Electronics", "Clothing", "Books", "Home & Garden", "Sports", "Beauty",
            "Automotive", "Toys", "Health", "Food", "Jewelry", "Music", "Pet Supplies",
            "Office", "Industrial", "Travel", "Baby", "Outdoor", "Art", "Collectibles"
        ]
        
        categories_data = []
        parent_category_ids = []
        
        for name in base_categories:
            category_id = str(uuid.uuid4())
            self.generated_data['category_ids'].append(category_id)
            parent_category_ids.append(category_id)
            
            categories_data.append((
                category_id,
                name,
                self.fake.text(max_nb_chars=200),
                None,
                self.fake.image_url(),
                True,
                self.fake.date_time_between(start_date='-1y', end_date='now')
            ))
        
        for i in range(count - len(base_categories)):
            category_id = str(uuid.uuid4())
            self.generated_data['category_ids'].append(category_id)
            
            categories_data.append((
                category_id,
                self.fake.bs().title()[:99],  # Limit category name
                self.fake.text(max_nb_chars=200),
                random.choice(parent_category_ids) if random.random() < 0.7 else None,
                self.fake.image_url()[:254],  # Limit URL
                random.choice([True, True, True, False]),
                self.fake.date_time_between(start_date='-1y', end_date='now')
            ))
        
        query = """
            INSERT INTO categories (category_id, name, description, parent_category_id, 
                                  image_url, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        self.execute_batch_insert(query, categories_data, "Inserting categories")
        print(f"✅ Generated {count:,} categories")

    def generate_products(self, count: int = 10_000):
        """Generate product records"""
        print(f"\n🛍️ Generating {count:,} products...")
        
        brands = ["Apple", "Samsung", "Nike", "Adidas", "Sony"] + [self.fake.company() for _ in range(20)]
        materials = ["Cotton", "Polyester", "Plastic", "Metal", "Wood", "Glass"]
        colors = ["Red", "Blue", "Green", "Black", "White", "Gray"]
        
        products_data = []
        
        for i in range(count):
            product_id = str(uuid.uuid4())
            self.generated_data['product_ids'].append(product_id)
            
            products_data.append((
                product_id,
                self.fake.catch_phrase()[:199],  # Limit product name
                self.fake.text(max_nb_chars=500),
                random.choice(self.generated_data['category_ids']),
                random.choice(brands)[:99],  # Limit brand name
                f"SKU-{i:08d}",
                round(random.uniform(9.99, 999.99), 2),
                round(random.uniform(0, 50), 2),
                random.randint(0, 1000),
                round(random.uniform(0.1, 50.0), 2),
                f"{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(5, 50)}cm"[:49],  # Limit dimensions
                random.choice(colors),
                random.choice(materials),
                [self.fake.image_url() for _ in range(random.randint(1, 3))],
                random.choice([True, True, True, False]),
                self.fake.date_time_between(start_date='-1y', end_date='now')
            ))
        
        query = """
            INSERT INTO products (product_id, name, description, category_id, brand, sku, 
                                base_price, discount_percentage, stock_quantity, weight, 
                                dimensions, color, material, image_urls, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        self.execute_batch_insert(query, products_data, "Inserting products")
        print(f"✅ Generated {count:,} products")

    def generate_orders(self, count: int = 10_000):
        """Generate order records"""
        print(f"\n📦 Generating {count:,} orders...")
        
        statuses = ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"]
        payment_methods = ["credit_card", "debit_card", "paypal", "stripe"]
        
        orders_data = []
        
        for i in range(count):
            order_id = str(uuid.uuid4())
            self.generated_data['order_ids'].append(order_id)
            
            total_amount = round(random.uniform(25.00, 2000.00), 2)
            discount_amount = round(total_amount * random.uniform(0, 0.3), 2)
            tax_amount = round(total_amount * 0.08, 2)
            shipping_cost = round(random.uniform(5.99, 29.99), 2)
            final_amount = round(total_amount - discount_amount + tax_amount + shipping_cost, 2)
            
            orders_data.append((
                order_id,
                random.choice(self.generated_data['user_ids']),
                f"ORD-{i:08d}",
                random.choice(statuses),
                total_amount,
                discount_amount,
                tax_amount,
                shipping_cost,
                final_amount,
                "USD",
                random.choice(payment_methods),
                json.dumps({
                    "street": self.fake.street_address(),
                    "city": self.fake.city(),
                    "state": self.fake.state(),
                    "zip": self.fake.zipcode(),
                    "country": self.fake.country()
                }),
                json.dumps({
                    "street": self.fake.street_address(),
                    "city": self.fake.city(),
                    "state": self.fake.state(),
                    "zip": self.fake.zipcode(),
                    "country": self.fake.country()
                }),
                self.fake.text(max_nb_chars=100) if random.random() < 0.3 else None,
                self.fake.date_time_between(start_date='-1y', end_date='now')
            ))
        
        query = """
            INSERT INTO orders (order_id, user_id, order_number, order_status, total_amount,
                              discount_amount, tax_amount, shipping_cost, final_amount, currency,
                              payment_method, shipping_address, billing_address, notes, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        self.execute_batch_insert(query, orders_data, "Inserting orders")
        print(f"✅ Generated {count:,} orders")

    def generate_payments(self, count: int = 10_000):
        """Generate payment records"""
        print(f"\n💳 Generating {count:,} payments...")
        
        payment_methods = ["credit_card", "debit_card", "paypal", "stripe"]
        statuses = ["completed", "pending", "failed", "refunded"]
        
        payments_data = []
        orders_sample = random.sample(self.generated_data['order_ids'], 
                                    min(count, len(self.generated_data['order_ids'])))
        
        for order_id in orders_sample:
            payments_data.append((
                str(uuid.uuid4()),
                order_id,
                random.choice(payment_methods),
                random.choice(statuses),
                round(random.uniform(25.00, 2000.00), 2),
                "USD",
                f"TXN-{random.randint(10000000, 99999999)}",
                json.dumps({"gateway": "stripe", "fee": round(random.uniform(1.0, 10.0), 2)}),
                self.fake.date_time_between(start_date='-1y', end_date='now'),
                self.fake.date_time_between(start_date='-1y', end_date='now')
            ))
        
        query = """
            INSERT INTO payments (payment_id, order_id, payment_method, payment_status, amount,
                                currency, transaction_id, gateway_response, processed_at, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        self.execute_batch_insert(query, payments_data, "Inserting payments")
        print(f"✅ Generated {count:,} payments")

    def run_generation(self):
        """Run the complete data generation process"""
        start_time = time.time()
        
        print("🚀 Starting Quick Data Generation (10K records per table)")
        print(f"🔧 Batch size: {self.BATCH_SIZE:,}")
        
        try:
            self.connect_database()
            
            # Clear existing data
            print("\n🧹 Clearing existing data...")
            tables = ['payments', 'orders', 'cart_items', 'cart', 'product_sizes', 
                     'favorites', 'notifications', 'products', 'categories', 'users']
            
            for table in tables:
                try:
                    self.cursor.execute(f"DELETE FROM {table};")
                    self.conn.commit()
                    print(f"   ✅ Cleared {table}")
                except Exception as e:
                    print(f"   ⚠️ Could not clear {table}: {e}")
            
            # Generate data
            self.generate_users(10_000)
            self.generate_categories(500)
            self.generate_products(10_000)
            self.generate_orders(10_000)
            self.generate_payments(10_000)
            
            # Print statistics
            self.print_statistics()
            
        except Exception as e:
            print(f"❌ Error during generation: {e}")
            raise
        finally:
            self.close_connection()
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"\n✅ Data generation completed in {duration:.2f} seconds")
        print(f"📈 Generated approximately {50_000:,} total records")

    def print_statistics(self):
        """Print generation statistics"""
        print("\n📊 Generation Statistics:")
        
        try:
            tables = ['users', 'categories', 'products', 'orders', 'payments']
            
            for table in tables:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                print(f"   {table:20}: {count:>10,} records")
                
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")

if __name__ == "__main__":
    generator = QuickDataGenerator()
    generator.run_generation()
