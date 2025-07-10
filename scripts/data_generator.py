#!/usr/bin/env python3
"""
E-Commerce Database Data Generator
Generates approximately 1 million records per table using Faker library
"""

import os
import sys
import time
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import execute_batch
from faker import Faker
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseDataGenerator:
    def __init__(self):
        self.fake = Faker()
        self.conn = None
        self.cursor = None
        
        # Configuration
        self.BATCH_SIZE = 1000
        self.TARGET_RECORDS_PER_TABLE = 1_000_000
        
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
            total_batches = len(data) // self.BATCH_SIZE + (1 if len(data) % self.BATCH_SIZE else 0)
            
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

    def generate_users(self, count: int = 1_000_000):
        """Generate user records"""
        print(f"\n🧑‍💼 Generating {count:,} users...")
        
        users_data = []
        roles = ['customer'] * 950000 + ['staff'] * 45000 + ['admin'] * 5000  # 95% customers, 4.5% staff, 0.5% admin
        random.shuffle(roles)
        
        for i in range(count):
            user_id = str(uuid.uuid4())
            self.generated_data['user_ids'].append(user_id)
            
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            username = f"{first_name.lower()}.{last_name.lower()}.{i}"
            email = f"{username}@{self.fake.domain_name()}"
            
            users_data.append((
                user_id,
                username,
                email,
                '$2b$10$rKjw.6QxEQsxZ5GvKjQxHOqXcXPKXP8Zd8WcE7Y3qYzRxZqK9WqDC',  # hashed 'password123'
                first_name,
                last_name,
                self.fake.phone_number(),
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

    def generate_categories(self, count: int = 1000):
        """Generate category records"""
        print(f"\n📂 Generating {count:,} categories...")
        
        # Base categories
        base_categories = [
            "Electronics", "Clothing", "Books", "Home & Garden", "Sports", "Beauty",
            "Automotive", "Toys", "Health", "Food", "Jewelry", "Music", "Pet Supplies",
            "Office", "Industrial", "Travel", "Baby", "Outdoor", "Art", "Collectibles"
        ]
        
        categories_data = []
        parent_category_ids = []
        
        # Generate root categories
        for name in base_categories:
            category_id = str(uuid.uuid4())
            self.generated_data['category_ids'].append(category_id)
            parent_category_ids.append(category_id)
            
            categories_data.append((
                category_id,
                name,
                self.fake.text(max_nb_chars=200),
                None,  # parent_category_id
                self.fake.image_url(),
                True,
                self.fake.date_time_between(start_date='-1y', end_date='now')
            ))
        
        # Generate subcategories
        for i in range(count - len(base_categories)):
            category_id = str(uuid.uuid4())
            self.generated_data['category_ids'].append(category_id)
            
            categories_data.append((
                category_id,
                self.fake.bs().title(),
                self.fake.text(max_nb_chars=200),
                random.choice(parent_category_ids) if random.random() < 0.7 else None,
                self.fake.image_url(),
                random.choice([True, True, True, False]),  # 75% active
                self.fake.date_time_between(start_date='-1y', end_date='now')
            ))
        
        query = """
            INSERT INTO categories (category_id, name, description, parent_category_id, 
                                  image_url, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        self.execute_batch_insert(query, categories_data, "Inserting categories")
        print(f"✅ Generated {count:,} categories")

    def generate_products(self, count: int = 1_000_000):
        """Generate product records"""
        print(f"\n🛍️ Generating {count:,} products...")
        
        brands = [
            "Apple", "Samsung", "Nike", "Adidas", "Sony", "Dell", "HP", "Canon",
            "Microsoft", "Google", "Amazon", "Tesla", "BMW", "Mercedes", "Toyota"
        ] + [self.fake.company() for _ in range(50)]
        
        materials = ["Cotton", "Polyester", "Plastic", "Metal", "Wood", "Glass", "Leather", "Silk"]
        colors = ["Red", "Blue", "Green", "Black", "White", "Gray", "Brown", "Yellow", "Pink", "Purple"]
        
        products_data = []
        
        for i in range(count):
            product_id = str(uuid.uuid4())
            self.generated_data['product_ids'].append(product_id)
            
            products_data.append((
                product_id,
                self.fake.catch_phrase(),
                self.fake.text(max_nb_chars=500),
                random.choice(self.generated_data['category_ids']),
                random.choice(brands),
                f"SKU-{i:08d}",
                round(random.uniform(9.99, 999.99), 2),
                round(random.uniform(0, 50), 2),  # discount
                random.randint(0, 1000),  # stock
                round(random.uniform(0.1, 50.0), 2),  # weight
                f"{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(5, 50)}cm",
                random.choice(colors),
                random.choice(materials),
                [self.fake.image_url() for _ in range(random.randint(1, 5))],  # image array
                random.choice([True, True, True, False]),  # 75% active
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

    def generate_product_sizes(self, count: int = 3_000_000):
        """Generate product size records"""
        print(f"\n📏 Generating {count:,} product sizes...")
        
        sizes = ["XS", "S", "M", "L", "XL", "XXL", "6", "7", "8", "9", "10", "11", "12"]
        
        sizes_data = []
        products_sample = random.sample(self.generated_data['product_ids'], 
                                      min(count // 3, len(self.generated_data['product_ids'])))
        
        for product_id in products_sample:
            num_sizes = random.randint(1, 5)
            product_sizes = random.sample(sizes, min(num_sizes, len(sizes)))
            
            for size in product_sizes:
                if len(sizes_data) >= count:
                    break
                    
                size_id = str(uuid.uuid4())
                self.generated_data['size_ids'].append(size_id)
                
                sizes_data.append((
                    size_id,
                    product_id,
                    size,
                    size,
                    round(random.uniform(0, 20), 2),  # additional price
                    random.randint(0, 100),  # stock
                    self.fake.date_time_between(start_date='-1y', end_date='now')
                ))
        
        query = """
            INSERT INTO product_sizes (size_id, product_id, size_name, size_value, 
                                     additional_price, stock_quantity, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        self.execute_batch_insert(query, sizes_data, "Inserting product sizes")
        print(f"✅ Generated {len(sizes_data):,} product sizes")

    def generate_carts(self, count: int = 800_000):
        """Generate shopping cart records"""
        print(f"\n🛒 Generating {count:,} shopping carts...")
        
        carts_data = []
        users_sample = random.sample(self.generated_data['user_ids'], 
                                   min(count, len(self.generated_data['user_ids'])))
        
        for user_id in users_sample:
            cart_id = str(uuid.uuid4())
            self.generated_data['cart_ids'].append(cart_id)
            
            carts_data.append((
                cart_id,
                user_id,
                self.fake.date_time_between(start_date='-6m', end_date='now')
            ))
        
        query = """
            INSERT INTO cart (cart_id, user_id, created_at)
            VALUES (%s, %s, %s)
        """
        
        self.execute_batch_insert(query, carts_data, "Inserting shopping carts")
        print(f"✅ Generated {len(carts_data):,} shopping carts")

    def generate_orders(self, count: int = 2_000_000):
        """Generate order records"""
        print(f"\n📦 Generating {count:,} orders...")
        
        statuses = ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"]
        payment_methods = ["credit_card", "debit_card", "paypal", "stripe", "cash_on_delivery"]
        
        orders_data = []
        
        for i in range(count):
            order_id = str(uuid.uuid4())
            self.generated_data['order_ids'].append(order_id)
            
            total_amount = round(random.uniform(25.00, 2000.00), 2)
            discount_amount = round(total_amount * random.uniform(0, 0.3), 2)
            tax_amount = round(total_amount * 0.08, 2)  # 8% tax
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
                {
                    "street": self.fake.street_address(),
                    "city": self.fake.city(),
                    "state": self.fake.state(),
                    "zip": self.fake.zipcode(),
                    "country": self.fake.country()
                },
                {
                    "street": self.fake.street_address(),
                    "city": self.fake.city(),
                    "state": self.fake.state(),
                    "zip": self.fake.zipcode(),
                    "country": self.fake.country()
                },
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

    def generate_performance_test_data(self):
        """Generate specific data for performance testing"""
        print("\n🚀 Generating performance test data...")
        
        # Generate data for complex queries
        self.generate_notifications(500_000)
        self.generate_favorites(1_000_000)
        self.generate_payments(2_000_000)
        
    def generate_notifications(self, count: int):
        """Generate notification records"""
        print(f"\n📢 Generating {count:,} notifications...")
        
        notification_types = ["order_update", "promotion", "newsletter", "security", "system"]
        priorities = ["low", "normal", "high", "urgent"]
        
        notifications_data = []
        
        for i in range(count):
            notifications_data.append((
                str(uuid.uuid4()),
                random.choice(self.generated_data['user_ids']),
                self.fake.sentence(nb_words=6),
                self.fake.text(max_nb_chars=200),
                random.choice(notification_types),
                random.choice([True, False]),  # is_read
                random.choice(priorities),
                self.fake.url() if random.random() < 0.3 else None,
                {"campaign_id": i} if random.random() < 0.2 else None,
                self.fake.date_time_between(start_date='-6m', end_date='now')
            ))
        
        query = """
            INSERT INTO notifications (notification_id, user_id, title, message, notification_type,
                                     is_read, priority, action_url, metadata, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        self.execute_batch_insert(query, notifications_data, "Inserting notifications")
        print(f"✅ Generated {count:,} notifications")

    def generate_favorites(self, count: int):
        """Generate user favorites records"""
        print(f"\n❤️ Generating {count:,} favorites...")
        
        favorites_data = []
        user_product_pairs = set()
        
        while len(favorites_data) < count:
            user_id = random.choice(self.generated_data['user_ids'])
            product_id = random.choice(self.generated_data['product_ids'])
            
            if (user_id, product_id) not in user_product_pairs:
                user_product_pairs.add((user_id, product_id))
                favorites_data.append((
                    str(uuid.uuid4()),
                    user_id,
                    product_id,
                    self.fake.date_time_between(start_date='-1y', end_date='now')
                ))
        
        query = """
            INSERT INTO favorites (favorite_id, user_id, product_id, added_at)
            VALUES (%s, %s, %s, %s)
        """
        
        self.execute_batch_insert(query, favorites_data, "Inserting favorites")
        print(f"✅ Generated {count:,} favorites")

    def generate_payments(self, count: int):
        """Generate payment records"""
        print(f"\n💳 Generating {count:,} payments...")
        
        payment_methods = ["credit_card", "debit_card", "paypal", "stripe", "apple_pay", "google_pay"]
        statuses = ["pending", "completed", "failed", "refunded", "cancelled"]
        
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
                {"gateway": "stripe", "fee": round(random.uniform(1.0, 10.0), 2)},
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
        
        print("🚀 Starting E-Commerce Database Data Generation")
        print(f"📊 Target: ~{self.TARGET_RECORDS_PER_TABLE:,} records per table")
        print(f"🔧 Batch size: {self.BATCH_SIZE:,}")
        
        try:
            self.connect_database()
            
            # Generate data in dependency order
            self.generate_users(1_000_000)
            self.generate_categories(1_000)
            self.generate_products(1_000_000)
            self.generate_product_sizes(3_000_000)
            self.generate_carts(800_000)
            self.generate_orders(2_000_000)
            self.generate_performance_test_data()
            
            # Generate statistics
            self.print_statistics()
            
        except Exception as e:
            print(f"❌ Error during generation: {e}")
            raise
        finally:
            self.close_connection()
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"\n✅ Data generation completed in {duration:.2f} seconds")
        print(f"📈 Generated approximately {sum([1_000_000, 1_000, 1_000_000, 3_000_000, 800_000, 2_000_000, 2_000_000]):,} total records")

    def print_statistics(self):
        """Print generation statistics"""
        print("\n📊 Generation Statistics:")
        
        try:
            # Get table record counts
            tables = [
                'users', 'categories', 'products', 'product_sizes', 
                'cart', 'orders', 'notifications', 'favorites', 'payments'
            ]
            
            for table in tables:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                print(f"   {table:20}: {count:>10,} records")
                
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")

if __name__ == "__main__":
    generator = DatabaseDataGenerator()
    generator.run_generation()
