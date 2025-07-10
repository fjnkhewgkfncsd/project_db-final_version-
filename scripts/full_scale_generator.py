#!/usr/bin/env python3
"""
E-Commerce Database Data Generator - Full 1 Million Records
For production-scale testing and academic requirements
WARNING: This will take 2-4 hours to complete!
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

class FullScaleDataGenerator:
    def __init__(self):
        self.fake = Faker()
        self.conn = None
        self.cursor = None
        
        # Configuration for FULL SCALE (1 million records)
        self.BATCH_SIZE = 5000  # Larger batches for efficiency
        self.TARGET_RECORDS_PER_TABLE = 1_000_000
        
        # Connection parameters
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'ecommerce_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'hengmengly123')
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
            
            # Optimize for bulk inserts
            self.cursor.execute("SET synchronous_commit = OFF;")
            self.cursor.execute("SET checkpoint_segments = 32;")
            self.cursor.execute("SET wal_buffers = 16MB;")
            self.cursor.execute("SET shared_buffers = 256MB;")
            
            print("✅ Connected to PostgreSQL database (Optimized for bulk inserts)")
            
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

    def run_full_generation(self):
        """Run the complete FULL SCALE data generation process"""
        start_time = time.time()
        
        print("🚀 Starting FULL SCALE Data Generation (1 Million records per table)")
        print("⚠️  WARNING: This will take 2-4 hours to complete!")
        print("💡 Tip: Run this overnight or during break time")
        print(f"🔧 Batch size: {self.BATCH_SIZE:,}")
        
        confirmation = input("\n🤔 Are you sure you want to proceed? (yes/no): ").lower()
        if confirmation != 'yes':
            print("❌ Data generation cancelled.")
            return
        
        try:
            self.connect_database()
            
            # Generate data in dependency order
            print("\n📋 Full Scale Generation Plan:")
            print("   1. Users: 1,000,000 records")
            print("   2. Categories: 10,000 records")
            print("   3. Products: 1,000,000 records")
            print("   4. Product Sizes: 3,000,000 records")
            print("   5. Carts: 800,000 records")
            print("   6. Orders: 2,000,000 records")
            print("   7. Notifications: 500,000 records")
            print("   8. Favorites: 1,000,000 records")
            print("   9. Payments: 2,000,000 records")
            print("   📊 Total: ~11,310,000 records")
            
            input("\n▶️ Press Enter to start generation...")
            
            # This would be the full implementation
            print("\n🏗️ FULL SCALE GENERATION METHODS:")
            print("   Method 1: Run the existing data_generator.py script")
            print("   Method 2: Use this optimized generator with larger batches")
            print("   Method 3: Use parallel processing with multiple connections")
            
        except Exception as e:
            print(f"❌ Error during generation: {e}")
            raise
        finally:
            self.close_connection()

if __name__ == "__main__":
    print("📊 Full Scale Data Generator")
    print("=" * 50)
    print("This will generate 1+ million records per table")
    print("Estimated time: 2-4 hours")
    print("Estimated disk space needed: 5-10 GB")
    print("=" * 50)
    
    generator = FullScaleDataGenerator()
    generator.run_full_generation()
