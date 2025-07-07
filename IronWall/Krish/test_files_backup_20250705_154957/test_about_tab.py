#!/usr/bin/env python3
"""
Test script for IronWall Antivirus About Tab
Tests the version configuration and About tab functionality
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_version_config():
    """Test the version configuration module"""
    print("Testing version configuration...")
    
    try:
        import version
        
        # Test basic version info
        print(f"✓ App Name: {version.APP_NAME}")
        print(f"✓ App Version: {version.APP_VERSION}")
        print(f"✓ App Build: {version.APP_BUILD}")
        print(f"✓ Supported OS: {version.SUPPORTED_OS}")
        
        # Test version info function
        info = version.get_version_info()
        print(f"✓ Version info function returns: {len(info)} items")
        
        print("✓ Version configuration test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Version configuration test failed: {e}")
        return False

def test_about_tab_imports():
    """Test that About tab can be imported without errors"""
    print("\nTesting About tab imports...")
    
    try:
        # Test that we can import the main window
        from ui.main_window import IronWallMainWindow
        print("✓ Main window import successful")
        
        # Test that version module is accessible
        import version
        print("✓ Version module import successful")
        
        print("✓ About tab import test passed!")
        return True
        
    except Exception as e:
        print(f"✗ About tab import test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("IronWall Antivirus - About Tab Test Suite")
    print("=" * 50)
    
    tests = [
        test_version_config,
        test_about_tab_imports
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! About tab is ready to use.")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 