"""
IronWall Antivirus - Integration Test
Tests all components working together
"""

import sys
import os

def test_imports():
    """Test all imports"""
    print("🔄 Testing imports...")
    
    try:
        import ttkbootstrap as ttk
        print("✅ ttkbootstrap imported successfully")
    except ImportError as e:
        print(f"❌ ttkbootstrap import failed: {e}")
        return False
    
    try:
        from utils.settings_manager import get_settings_manager
        print("✅ Settings manager imported successfully")
    except ImportError as e:
        print(f"❌ Settings manager import failed: {e}")
        return False
    
    try:
        from ui.settings_panel import SettingsPanel
        print("✅ Settings panel imported successfully")
    except ImportError as e:
        print(f"❌ Settings panel import failed: {e}")
        return False
    
    try:
        from core.scanner import IronWallScanner
        print("✅ Scanner imported successfully")
    except ImportError as e:
        print(f"❌ Scanner import failed: {e}")
        return False
    
    try:
        from utils.system_monitor import SystemMonitor
        print("✅ System monitor imported successfully")
    except ImportError as e:
        print(f"❌ System monitor import failed: {e}")
        return False
    
    try:
        from utils.threat_database import ThreatDatabase
        print("✅ Threat database imported successfully")
    except ImportError as e:
        print(f"❌ Threat database import failed: {e}")
        return False
    
    return True

def test_settings_manager():
    """Test settings manager functionality"""
    print("\n🔄 Testing settings manager...")
    
    try:
        from utils.settings_manager import get_settings_manager
        sm = get_settings_manager()
        
        # Test basic operations
        sm.set_setting("protection", "real_time_protection", True)
        value = sm.get_setting("protection", "real_time_protection")
        assert value == True, "Setting not saved correctly"
        
        # Test category operations
        protection_settings = sm.get_category("protection")
        assert "real_time_protection" in protection_settings, "Category not retrieved correctly"
        
        print("✅ Settings manager working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Settings manager test failed: {e}")
        return False

def test_ui_components():
    """Test UI components"""
    print("\n🔄 Testing UI components...")
    
    try:
        import ttkbootstrap as ttk
        from ui.settings_panel import SettingsPanel
        
        # Create a test window
        root = ttk.Window(themename="flatly")
        root.withdraw()  # Hide the window
        
        # Test settings panel creation
        settings_panel = SettingsPanel(root, None)
        
        print("✅ UI components working correctly")
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ UI components test failed: {e}")
        return False

def test_main_application():
    """Test main application components"""
    print("\n🔄 Testing main application...")
    
    try:
        from core.scanner import IronWallScanner
        from utils.system_monitor import SystemMonitor
        from utils.threat_database import ThreatDatabase
        
        # Initialize components
        threat_db = ThreatDatabase()
        scanner = IronWallScanner(threat_db)
        system_monitor = SystemMonitor()
        
        print("✅ Main application components working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Main application test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🛡️ IronWall Antivirus - Integration Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Settings Manager Test", test_settings_manager),
        ("UI Components Test", test_ui_components),
        ("Main Application Test", test_main_application),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! IronWall is ready to run.")
        print("\n🚀 You can now run:")
        print("   python main.py              # Main application")
        print("   python demo_settings.py     # Settings panel demo")
        print("   python test_settings.py     # Basic settings test")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 