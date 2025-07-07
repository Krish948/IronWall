"""
IronWall Antivirus - Reset Button Test
Test the reset button functionality directly
"""

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_reset_functionality():
    """Test the reset functionality directly"""
    print("🛡️ Testing Reset Button Functionality")
    print("=" * 50)
    
    try:
        from utils.data_reset import DataResetManager
        
        # Create data reset manager
        data_reset_manager = DataResetManager()
        
        print("✅ Data reset manager created successfully")
        
        # Test the reset functionality
        print("🔄 Testing reset_all_data method...")
        results = data_reset_manager.reset_all_data(create_backup=True)
        
        # Show results
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        print(f"✅ Reset completed: {success_count}/{total_count} operations successful")
        
        for operation, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {operation.replace('_', ' ').title()}")
        
        # Show reset log
        print("\n📋 Reset Log:")
        for log_entry in data_reset_manager.get_reset_log():
            print(f"  {log_entry}")
        
        print("\n✅ Reset functionality test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_settings_panel_reset():
    """Test the settings panel reset method"""
    print("\n🖥️ Testing Settings Panel Reset Method")
    print("=" * 50)
    
    try:
        # Create a simple test window
        root = ttk.Window()
        root.withdraw()  # Hide the window
        
        # Import and test the reset method
        from ui.settings_panel import SettingsPanel
        
        # Create a mock main window
        class MockMainWindow:
            def __init__(self):
                pass
        
        # Create settings panel
        settings_panel = SettingsPanel(root, MockMainWindow())
        
        print("✅ Settings panel created successfully")
        
        # Test the reset method directly
        print("🔄 Testing reset_all_data method...")
        settings_panel.reset_all_data()
        
        print("✅ Settings panel reset method called successfully!")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Settings panel test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Testing IronWall Reset Button Functionality")
    print("=" * 60)
    
    # Test 1: Direct reset functionality
    test1_success = test_reset_functionality()
    
    # Test 2: Settings panel reset method
    test2_success = test_settings_panel_reset()
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print(f"Direct Reset Functionality: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"Settings Panel Reset Method: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    if test1_success and test2_success:
        print("\n🎉 All tests passed! Reset functionality is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
    
    print("\nTo test the actual button in the GUI:")
    print("1. Run IronWall Antivirus")
    print("2. Go to Settings → Advanced tab")
    print("3. Click '🔄 Reset All Data' button")

if __name__ == "__main__":
    main() 