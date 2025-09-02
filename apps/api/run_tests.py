#!/usr/bin/env python3
import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.test_db import test_db_connects
from tests.test_models import test_user_crud

def run_tests():
    print("Running database tests...")

    # Test database connection
    try:
        test_db_connects()
        print("✅ Database connection test passed")
    except Exception as e:
        print(f"❌ Database connection test failed: {str(e)}")
        return False

    # Test user CRUD
    try:
        test_user_crud()
        print("✅ User CRUD test passed")
    except Exception as e:
        print(f"❌ User CRUD test failed: {str(e)}")
        return False

    print("✅ All tests passed!")
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
