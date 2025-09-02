#!/usr/bin/env python3
import os
import sys
from sqlalchemy import create_engine, text

def test_db_connection():
    # Get database URL from environment or use default
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///test.db')

    print(f"Testing connection to: {db_url}")

    try:
        # Create engine
        engine = create_engine(db_url)

        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            value = result.scalar()

            if value == 1:
                print("✅ Database connection successful!")
                return True
            else:
                print("❌ Database query returned unexpected result")
                return False

    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_db_connection()
    sys.exit(0 if success else 1)
