#!/usr/bin/env python3
"""
IronWall Antivirus - Comprehensive Test Script
Tests all major functionality and fixes
"""

import sys
import os
import json
import time
import threading
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing imports...")
    
    try:
        from utils.settings_manager import get_settings_manager
        print("✅ Settings manager import successful")
    except Exception as e:
        print(f"❌ Settings manager import failed: {e}")
        return False
    
    try:
        from utils import scan_history
        print("✅ Scan history import successful")
    except Exception as e:
        print(f"❌ Scan history import failed: {e}")
        return False
    
    try:
        from core.scanner import IronWallScanner
        print("✅ Scanner import successful")
    except Exception as e:
        print(f"❌ Scanner import failed: {e}")
        return False
    
    try:
        from utils.threat_database import ThreatDatabase
        print("✅ Threat database import successful")
    except Exception as e:
        print(f"❌ Threat database import failed: {e}")
        return False
    
    return True

def test_settings_manager():
    """Test settings manager functionality"""
    print("\n🔍 Testing settings manager...")
    
    try:
        from utils.settings_manager import get_settings_manager
        
        settings = get_settings_manager()
        
        # Test basic operations
        settings.set_setting("test", "test_key", "test_value")
        value = settings.get_setting("test", "test_key")
        
        if value == "test_value":
            print("✅ Settings manager basic operations work")
        else:
            print(f"❌ Settings manager basic operations failed: expected 'test_value', got '{value}'")
            return False
        
        # Test save all functionality
        settings.save_settings()
        print("✅ Settings save successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Settings manager test failed: {e}")
        return False

def test_scanner():
    """Test scanner functionality"""
    print("\n🔍 Testing scanner...")
    
    try:
        from core.scanner import IronWallScanner
        from utils.threat_database import ThreatDatabase
        
        threat_db = ThreatDatabase()
        scanner = IronWallScanner(threat_db)
        
        # Test scanner initialization
        if hasattr(scanner, 'scan_folder'):
            print("✅ Scanner initialization successful")
        else:
            print("❌ Scanner initialization failed: missing scan_folder method")
            return False
        
        # Test scanner stats
        stats = scanner.get_scan_stats()
        if isinstance(stats, dict):
            print("✅ Scanner stats method works")
        else:
            print(f"❌ Scanner stats method failed: expected dict, got {type(stats)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Scanner test failed: {e}")
        return False

def test_scan_history():
    """Test scan history functionality"""
    print("\n🔍 Testing scan history...")
    
    try:
        from utils import scan_history
        
        # Test loading scan history
        history = scan_history.load_scan_history()
        if isinstance(history, list):
            print("✅ Scan history loading works")
        else:
            print(f"❌ Scan history loading failed: expected list, got {type(history)}")
            return False
        
        # Test adding scan record
        test_record = {
            'timestamp': time.time(),
            'scan_type': 'test',
            'files_scanned': 0,
            'threats_found': 0,
            'duration': 0
        }
        
        scan_history.add_scan_record(test_record)
        print("✅ Scan history adding works")
        
        return True
        
    except Exception as e:
        print(f"❌ Scan history test failed: {e}")
        return False

def test_ui_components():
    """Test UI component imports"""
    print("\n🔍 Testing UI components...")
    
    try:
        from ui.main_window import IronWallMainWindow
        print("✅ Main window import successful")
    except Exception as e:
        print(f"❌ Main window import failed: {e}")
        return False
    
    try:
        from ui.settings_panel import SettingsPanel
        print("✅ Settings panel import successful")
    except Exception as e:
        print(f"❌ Settings panel import failed: {e}")
        return False
    
    try:
        from ui.theme_preview import ThemeSelectorWidget, ColorPickerWidget
        print("✅ Theme preview import successful")
    except Exception as e:
        print(f"❌ Theme preview import failed: {e}")
        return False
    
    return True

def test_configuration_files():
    """Test configuration file integrity"""
    print("\n🔍 Testing configuration files...")
    
    config_files = [
        'ironwall_settings.json',
        'threat_database.json',
        'quarantine/quarantine_db.json'
    ]
    
    for config_file in config_files:
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    data = json.load(f)
                print(f"✅ {config_file} is valid JSON")
            else:
                print(f"⚠️  {config_file} does not exist (will be created on first run)")
        except Exception as e:
            print(f"❌ {config_file} is invalid: {e}")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🛡️ IronWall Antivirus - Comprehensive Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Settings Manager", test_settings_manager),
        ("Scanner", test_scanner),
        ("Scan History", test_scan_history),
        ("UI Components", test_ui_components),
        ("Configuration Files", test_configuration_files)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! IronWall is ready to run.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 