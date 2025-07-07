#!/usr/bin/env python3
"""
Helper script to run consolidated tests and optionally clean up individual test files
"""

import sys
import os
import glob
import shutil

def run_consolidated_tests():
    """Run the consolidated test suite"""
    print("🛡️ Running IronWall Consolidated Test Suite")
    print("=" * 50)
    
    try:
        from consolidated_tests import IronWallTestSuite
        
        test_suite = IronWallTestSuite()
        success = test_suite.run_all_tests()
        
        if success:
            print("\n✅ All tests passed!")
            return True
        else:
            print("\n❌ Some tests failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error running consolidated tests: {e}")
        return False

def list_individual_test_files():
    """List all individual test files"""
    test_files = glob.glob("test_*.py")
    return test_files

def backup_individual_test_files():
    """Create a backup of individual test files"""
    backup_dir = "test_files_backup"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    test_files = list_individual_test_files()
    
    print(f"📦 Creating backup of {len(test_files)} test files...")
    
    for test_file in test_files:
        if os.path.exists(test_file):
            shutil.copy2(test_file, os.path.join(backup_dir, test_file))
            print(f"✅ Backed up: {test_file}")
    
    print(f"✅ Backup created in: {backup_dir}/")
    return backup_dir

def remove_individual_test_files():
    """Remove individual test files (after backup)"""
    test_files = list_individual_test_files()
    
    print(f"🗑️ Removing {len(test_files)} individual test files...")
    
    for test_file in test_files:
        try:
            os.remove(test_file)
            print(f"✅ Removed: {test_file}")
        except Exception as e:
            print(f"❌ Failed to remove {test_file}: {e}")
    
    print("✅ Individual test files removed!")

def main():
    """Main function"""
    print("IronWall Test Consolidation Helper")
    print("=" * 40)
    
    # Check if consolidated test file exists
    if not os.path.exists("consolidated_tests.py"):
        print("❌ consolidated_tests.py not found!")
        print("Please ensure the consolidated test file exists.")
        return 1
    
    # Run consolidated tests
    print("\n1. Running consolidated tests...")
    test_success = run_consolidated_tests()
    
    if not test_success:
        print("\n⚠️ Tests failed. Individual test files will not be removed.")
        return 1
    
    # List individual test files
    print("\n2. Individual test files found:")
    test_files = list_individual_test_files()
    
    if not test_files:
        print("✅ No individual test files found - already consolidated!")
        return 0
    
    for test_file in test_files:
        print(f"   - {test_file}")
    
    # Ask user what to do
    print(f"\n3. Options:")
    print("   a) Keep individual test files (recommended for development)")
    print("   b) Create backup and remove individual test files")
    print("   c) Just create backup")
    print("   d) Exit")
    
    while True:
        choice = input("\nEnter your choice (a/b/c/d): ").lower().strip()
        
        if choice == 'a':
            print("✅ Individual test files kept for development use.")
            break
        elif choice == 'b':
            print("\n4. Creating backup and removing individual test files...")
            backup_dir = backup_individual_test_files()
            remove_individual_test_files()
            print(f"\n✅ Done! Backup saved in: {backup_dir}/")
            print("✅ Individual test files removed.")
            print("✅ Use consolidated_tests.py for all testing.")
            break
        elif choice == 'c':
            print("\n4. Creating backup only...")
            backup_dir = backup_individual_test_files()
            print(f"\n✅ Backup created in: {backup_dir}/")
            print("✅ Individual test files kept.")
            break
        elif choice == 'd':
            print("✅ Exiting without changes.")
            break
        else:
            print("❌ Invalid choice. Please enter a, b, c, or d.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 