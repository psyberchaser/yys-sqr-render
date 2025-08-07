#!/usr/bin/env python3
"""
Database migration to add IPFS fields to TradingCard table
Run this script to add ipfs_cid and watermarked_ipfs_cid columns
"""

import os
import sys
from sqlalchemy import create_engine, text

def run_migration():
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        print("🔄 Adding IPFS fields to trading_cards table...")
        
        # Add the new columns
        with engine.connect() as conn:
            # Add ipfs_cid column
            try:
                conn.execute(text("ALTER TABLE trading_cards ADD COLUMN ipfs_cid VARCHAR(100)"))
                print("✅ Added ipfs_cid column")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("ℹ️ ipfs_cid column already exists")
                else:
                    raise e
            
            # Add watermarked_ipfs_cid column
            try:
                conn.execute(text("ALTER TABLE trading_cards ADD COLUMN watermarked_ipfs_cid VARCHAR(100)"))
                print("✅ Added watermarked_ipfs_cid column")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("ℹ️ watermarked_ipfs_cid column already exists")
                else:
                    raise e
            
            # Commit the changes
            conn.commit()
        
        print("🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)