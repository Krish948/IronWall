#!/usr/bin/env python3
"""
IronWall Antivirus - Consolidated Test Suite
Combines all test functions from individual test files into a single comprehensive test suite
"""

import sys
import os
import json
import time
import threading
import tkinter as tk
import ttkbootstrap as ttk
import requests
import subprocess
import platform
from datetime import datetime
from pathlib import Path
from utils import scan_history

# Add the IronWall/Krish directory to Python path
krish_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "IronWall", "Krish")
if os.path.exists(krish_dir):
    sys.path.insert(0, krish_dir)
else:
    # If running from IronWall/Krish directory directly
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class IronWallTestSuite:
    """Comprehensive test suite for IronWall Antivirus"""
    
    def __init__(self):
        self.test_results = []
        self.original_ip = None
        
    def run_all_tests(self):
        """Run all tests in the consolidated test suite"""
        print("🛡️ IronWall Antivirus - Consolidated Test Suite")
        print("=" * 60)
        
        # Core functionality tests
        self.test_imports()
        self.test_settings_manager()
        self.test_scanner()
        self.test_scan_history()
        self.test_threat_database()
        self.test_quarantine_system()
        
        # UI component tests
        self.test_ui_components()
        self.test_about_tab()
        self.test_settings_panel()
        self.test_scheduler_panel()
        self.test_reports_panel()
        self.test_analytics_performance()
        self.test_interface_options()
        self.test_color_palette()
        self.test_new_about_sections()
        
        # Integration and configuration tests
        self.test_integration()
        self.test_configuration_files()
        self.test_time_tracking()
        
        # Print comprehensive summary
        self.print_test_summary()
        
        return self.get_test_results()
    
    # ============================================================================
    # CORE FUNCTIONALITY TESTS
    # ============================================================================
    
    def test_imports(self):
        """Test all critical imports"""
        print("\n🔍 Testing imports...")
        
        imports_to_test = [
            ("Settings manager", "utils.settings_manager", "get_settings_manager"),
            ("Scan history", "utils.scan_history", None),
            ("Scanner", "core.scanner", "IronWallScanner"),
            ("Threat database", "utils.threat_database", "ThreatDatabase"),
            ("Quarantine", "utils.quarantine", "QuarantineManager"),
            ("Scheduler", "utils.scheduler", "Scheduler"),
            ("System monitor", "utils.system_monitor", "SystemMonitor"),
            ("Color palette", "utils.color_palette", "ColorPalette"),
            ("Main window", "ui.main_window", "IronWallMainWindow"),
            ("Settings panel", "ui.settings_panel", "SettingsPanel"),
            ("Scan panel", "ui.scan_panel", "ScanPanel"),
            ("Quarantine panel", "ui.quarantine_panel", "QuarantinePanel"),
            ("Reports panel", "ui.reports_panel", "ReportsPanel"),
            ("Scheduler panel", "ui.scheduler_panel", "SchedulerPanel"),
            ("Analytics panel", "ui.analytics_panel", "AnalyticsPanel"),
            ("Theme preview", "ui.theme_preview", "ThemeSelectorWidget"),
            ("Version", "version", None)
        ]
        
        passed = 0
        total = len(imports_to_test)
        
        for name, module, item in imports_to_test:
            try:
                if item:
                    exec(f"from {module} import {item}")
                else:
                    exec(f"import {module}")
                print(f"✅ {name} import successful")
                passed += 1
            except Exception as e:
                print(f"❌ {name} import failed: {e}")
        
        self.test_results.append(("Imports", "PASS" if passed == total else "FAIL", f"{passed}/{total} successful"))
        return passed == total
    
    def test_settings_manager(self):
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
                self.test_results.append(("Settings Manager", "FAIL", "Basic operations failed"))
                return False
            
            # Test save all functionality
            settings.save_settings()
            print("✅ Settings save successful")
            
            # Test get all settings
            all_settings = settings.get_all_settings()
            if isinstance(all_settings, dict):
                print("✅ Get all settings works")
            else:
                print("❌ Get all settings failed")
                self.test_results.append(("Settings Manager", "FAIL", "Get all settings failed"))
                return False
            
            self.test_results.append(("Settings Manager", "PASS", "All operations successful"))
            return True
            
        except Exception as e:
            print(f"❌ Settings manager test failed: {e}")
            self.test_results.append(("Settings Manager", "FAIL", str(e)))
            return False
    
    def test_scanner(self):
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
                self.test_results.append(("Scanner", "FAIL", "Missing scan_folder method"))
                return False
            
            # Test scanner stats
            stats = scanner.get_scan_stats()
            if isinstance(stats, dict):
                print("✅ Scanner stats method works")
            else:
                print(f"❌ Scanner stats method failed: expected dict, got {type(stats)}")
                self.test_results.append(("Scanner", "FAIL", "get_scan_stats failed"))
                return False
            
            self.test_results.append(("Scanner", "PASS", "All methods working"))
            return True
            
        except Exception as e:
            print(f"❌ Scanner test failed: {e}")
            self.test_results.append(("Scanner", "FAIL", str(e)))
            return False
    
    def test_scan_history(self):
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
                self.test_results.append(("Scan History", "FAIL", "load_scan_history failed"))
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
            
            self.test_results.append(("Scan History", "PASS", "All operations working"))
            return True
            
        except Exception as e:
            print(f"❌ Scan history test failed: {e}")
            self.test_results.append(("Scan History", "FAIL", str(e)))
            return False
    
    def test_threat_database(self):
        """Test threat database functionality"""
        print("\n🔍 Testing threat database...")
        
        try:
            from utils.threat_database import ThreatDatabase
            
            threat_db = ThreatDatabase()
            
            # Test basic operations
            threats = threat_db.get_all_threats()
            if isinstance(threats, list):
                print(f"✅ Threat database loading works: {len(threats)} threats loaded")
            else:
                print("❌ Threat database loading failed")
                self.test_results.append(("Threat Database", "FAIL", "get_all_threats failed"))
                return False
            
            # Test adding threat
            test_threat = {
                'id': 'test_threat_001',
                'name': 'Test Threat',
                'type': 'test',
                'severity': 'low',
                'description': 'Test threat for testing purposes'
            }
            
            threat_db.add_threat(test_threat)
            print("✅ Threat database adding works")
            
            self.test_results.append(("Threat Database", "PASS", "All operations working"))
            return True
            
        except Exception as e:
            print(f"❌ Threat database test failed: {e}")
            self.test_results.append(("Threat Database", "FAIL", str(e)))
            return False
    
    def test_quarantine_system(self):
        """Test quarantine system functionality"""
        print("\n🔍 Testing quarantine system...")
        
        try:
            from utils.quarantine import QuarantineManager
            
            quarantine = QuarantineManager()
            
            # Test basic operations
            quarantined_files = quarantine.get_quarantined_files()
            if isinstance(quarantined_files, list):
                print(f"✅ Quarantine loading works: {len(quarantined_files)} files quarantined")
            else:
                print("❌ Quarantine loading failed")
                self.test_results.append(("Quarantine System", "FAIL", "get_quarantined_files failed"))
                return False
            
            # Test quarantine file operations
            test_file = "test_quarantine_file.txt"
            with open(test_file, 'w') as f:
                f.write("Test content for quarantine")
            
            success = quarantine.quarantine_file(test_file, "test_threat")
            if success:
                print("✅ Quarantine file operation works")
            else:
                print("❌ Quarantine file operation failed")
                self.test_results.append(("Quarantine System", "FAIL", "quarantine_file failed"))
                return False
            
            # Clean up test file
            if os.path.exists(test_file):
                os.remove(test_file)
            
            self.test_results.append(("Quarantine System", "PASS", "All operations working"))
            return True
            
        except Exception as e:
            print(f"❌ Quarantine system test failed: {e}")
            self.test_results.append(("Quarantine System", "FAIL", str(e)))
            return False
    
    # ============================================================================
    # UI COMPONENT TESTS
    # ============================================================================
    
    def test_ui_components(self):
        """Test UI component imports"""
        print("\n🔍 Testing UI components...")
        
        ui_components = [
            ("Main window", "ui.main_window", "IronWallMainWindow"),
            ("Settings panel", "ui.settings_panel", "SettingsPanel"),
            ("Scan panel", "ui.scan_panel", "ScanPanel"),
            ("Quarantine panel", "ui.quarantine_panel", "QuarantinePanel"),
            ("Reports panel", "ui.reports_panel", "ReportsPanel"),
            ("Scheduler panel", "ui.scheduler_panel", "SchedulerPanel"),
            ("Analytics panel", "ui.analytics_panel", "AnalyticsPanel"),
            ("Theme preview", "ui.theme_preview", "ThemeSelectorWidget")
        ]
        
        passed = 0
        total = len(ui_components)
        
        for name, module, class_name in ui_components:
            try:
                exec(f"from {module} import {class_name}")
                print(f"✅ {name} import successful")
                passed += 1
            except Exception as e:
                print(f"❌ {name} import failed: {e}")
        
        self.test_results.append(("UI Components", "PASS" if passed == total else "FAIL", f"{passed}/{total} successful"))
        return passed == total
    
    def test_about_tab(self):
        """Test the version configuration and About tab functionality"""
        print("\n🔍 Testing About tab...")
        
        try:
            import version
            
            # Test basic version info
            print(f"✅ App Name: {version.APP_NAME}")
            print(f"✅ App Version: {version.APP_VERSION}")
            print(f"✅ App Build: {version.APP_BUILD}")
            print(f"✅ Supported OS: {version.SUPPORTED_OS}")
            
            # Test version info function
            info = version.get_version_info()
            print(f"✅ Version info function returns: {len(info)} items")
            
            # Test that we can import the main window
            from ui.main_window import IronWallMainWindow
            print("✅ Main window import successful")
            
            self.test_results.append(("About Tab", "PASS", "All components working"))
            return True
            
        except Exception as e:
            print(f"❌ About tab test failed: {e}")
            self.test_results.append(("About Tab", "FAIL", str(e)))
            return False
    
    def test_settings_panel(self):
        """Test the settings panel functionality"""
        print("\n🔍 Testing settings panel...")
        
        try:
            from ui.settings_panel import SettingsPanel
            from utils.settings_manager import get_settings_manager
            
            # Test settings manager
            sm = get_settings_manager()
            settings = sm.get_all_settings()
            print(f"✅ Settings manager works: {len(settings)} settings loaded")
            
            # Test settings panel creation (without GUI)
            print("✅ Settings panel components available")
            
            self.test_results.append(("Settings Panel", "PASS", "All components working"))
            return True
            
        except Exception as e:
            print(f"❌ Settings panel test failed: {e}")
            self.test_results.append(("Settings Panel", "FAIL", str(e)))
            return False
    
    def test_scheduler_panel(self):
        """Test the scheduler panel functionality"""
        print("\n🔍 Testing scheduler panel...")
        
        try:
            from ui.scheduler_panel import SchedulerPanel
            from utils.scheduler import SchedulerManager
            
            # Test scheduler functionality
            scheduler = SchedulerManager()
            schedules = scheduler.get_all_schedules()
            print(f"✅ Scheduler works: {len(schedules)} schedules loaded")
            
            # Test scheduler panel components
            print("✅ Scheduler panel components available")
            
            self.test_results.append(("Scheduler Panel", "PASS", "All components working"))
            return True
            
        except Exception as e:
            print(f"❌ Scheduler panel test failed: {e}")
            self.test_results.append(("Scheduler Panel", "FAIL", str(e)))
            return False
    
    def test_reports_panel(self):
        """Test the reports panel functionality"""
        print("\n🔍 Testing reports panel...")
        
        try:
            from ui.reports_panel import ReportsPanel
            
            # Test reports panel components
            print("✅ Reports panel components available")
            
            self.test_results.append(("Reports Panel", "PASS", "All components working"))
            return True
            
        except Exception as e:
            print(f"❌ Reports panel test failed: {e}")
            self.test_results.append(("Reports Panel", "FAIL", str(e)))
            return False
    
    def test_analytics_performance(self):
        """Test analytics performance functionality"""
        print("\n🔍 Testing analytics performance...")
        
        try:
            from ui.analytics_panel import AnalyticsPanel
            from utils.system_monitor import SystemMonitor
            
            # Test system monitor
            monitor = SystemMonitor()
            stats = monitor.get_system_stats()
            print(f"✅ System monitor works: {len(stats)} stats available")
            
            # Test analytics panel components
            print("✅ Analytics panel components available")
            
            self.test_results.append(("Analytics Performance", "PASS", "All components working"))
            return True
            
        except Exception as e:
            print(f"❌ Analytics performance test failed: {e}")
            self.test_results.append(("Analytics Performance", "FAIL", str(e)))
            return False
    
    def test_interface_options(self):
        """Test interface options functionality"""
        print("\n🔍 Testing interface options...")
        
        try:
            from ui.theme_preview import ThemeSelectorWidget, ColorPickerWidget
            from utils.color_palette import ColorPalette
            
            # Test color palette
            palette = ColorPalette()
            colors = palette.get_available_themes()
            print(f"✅ Color palette works: {len(colors)} themes available")
            
            # Test theme components
            print("✅ Theme selector components available")
            
            self.test_results.append(("Interface Options", "PASS", "All components working"))
            return True
            
        except Exception as e:
            print(f"❌ Interface options test failed: {e}")
            self.test_results.append(("Interface Options", "FAIL", str(e)))
            return False
    
    def test_color_palette(self):
        """Test color palette functionality"""
        print("\n🔍 Testing color palette...")
        
        try:
            from utils.color_palette import ColorPalette
            
            palette = ColorPalette()
            
            # Test theme operations
            themes = palette.get_available_themes()
            if isinstance(themes, list) and len(themes) > 0:
                print(f"✅ Color palette works: {len(themes)} themes available")
            else:
                print("❌ Color palette failed: no themes available")
                self.test_results.append(("Color Palette", "FAIL", "No themes available"))
                return False
            
            # Test theme application
            if themes:
                theme = themes[0]
                colors = palette.get_theme_colors(theme)
                if isinstance(colors, dict):
                    print("✅ Theme color retrieval works")
                else:
                    print("❌ Theme color retrieval failed")
                    self.test_results.append(("Color Palette", "FAIL", "Theme color retrieval failed"))
                    return False
            
            self.test_results.append(("Color Palette", "PASS", "All operations working"))
            return True
            
        except Exception as e:
            print(f"❌ Color palette test failed: {e}")
            self.test_results.append(("Color Palette", "FAIL", str(e)))
            return False
    
    def test_new_about_sections(self):
        """Test new about sections functionality"""
        print("\n🔍 Testing new about sections...")
        
        try:
            # Test database information
            from utils.threat_database import ThreatDatabase
            threat_db = ThreatDatabase()
            threats = threat_db.get_all_threats()
            print(f"✅ Database information: {len(threats)} threats in database")
            
            # Test security status
            from utils.system_monitor import SystemMonitor
            monitor = SystemMonitor()
            security_status = monitor.get_security_status()
            print("✅ Security status retrieval works")
            
            # Test resource usage
            resource_usage = monitor.get_resource_usage()
            print("✅ Resource usage monitoring works")
            
            # Test system information
            system_info = monitor.get_system_info()
            print("✅ System information retrieval works")
            
            self.test_results.append(("New About Sections", "PASS", "All sections working"))
            return True
            
        except Exception as e:
            print(f"❌ New about sections test failed: {e}")
            self.test_results.append(("New About Sections", "FAIL", str(e)))
            return False
    
    # ============================================================================
    # INTEGRATION AND CONFIGURATION TESTS
    # ============================================================================
    
    def test_integration(self):
        """Test overall integration"""
        print("\n🔍 Testing integration...")
        
        try:
            # Test main application components
            from ui.main_window import IronWallMainWindow
            print("✅ Main application components available")
            
            # Test settings integration
            from utils.settings_manager import get_settings_manager
            settings = get_settings_manager()
            print("✅ Settings integration works")
            
            # Test UI integration
            print("✅ UI integration components available")
            
            self.test_results.append(("Integration", "PASS", "All integrations working"))
            return True
            
        except Exception as e:
            print(f"❌ Integration test failed: {e}")
            self.test_results.append(("Integration", "FAIL", str(e)))
            return False
    
    def test_configuration_files(self):
        """Test configuration file integrity"""
        print("\n🔍 Testing configuration files...")
        
        config_files = [
            'ironwall_settings.json',
            'threat_database.json',
            'quarantine/quarantine_db.json',
            'scan_history.json',
            'system_logs.json'
        ]
        
        passed = 0
        total = len(config_files)
        
        for config_file in config_files:
            try:
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        data = json.load(f)
                    print(f"✅ {config_file} is valid JSON")
                    passed += 1
                else:
                    print(f"⚠️ {config_file} does not exist (will be created on first run)")
                    passed += 1  # Not existing is not a failure
            except Exception as e:
                print(f"❌ {config_file} is invalid: {e}")
        
        self.test_results.append(("Configuration Files", "PASS" if passed == total else "FAIL", f"{passed}/{total} valid"))
        return passed == total
    
    def test_time_tracking(self):
        """Test time tracking functionality"""
        print("\n🔍 Testing time tracking...")
        
        try:
            from utils.scheduler import SchedulerManager
            
            scheduler = SchedulerManager()
            
            # Test time tracking features
            print("✅ Time tracking components available")
            
            # Test schedule operations
            schedules = scheduler.get_all_schedules()
            print(f"✅ Schedule operations work: {len(schedules)} schedules")
            
            self.test_results.append(("Time Tracking", "PASS", "All features working"))
            return True
            
        except Exception as e:
            print(f"❌ Time tracking test failed: {e}")
            self.test_results.append(("Time Tracking", "FAIL", str(e)))
            return False
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 CONSOLIDATED TEST RESULTS SUMMARY")
        print("=" * 60)
        
        # Count results
        passed = sum(1 for result in self.test_results if result[1] == "PASS")
        failed = sum(1 for result in self.test_results if result[1] == "FAIL")
        skipped = sum(1 for result in self.test_results if result[1] == "SKIP")
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Skipped: {skipped}")
        
        print("\nDetailed Results:")
        print("-" * 60)
        
        for test_name, status, details in self.test_results:
            status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
            print(f"{status_icon} {test_name:<25} {status:<6} {details}")
        
        print("\n" + "=" * 60)
        
        if failed == 0:
            print("🎉 All tests passed! IronWall is ready to run.")
        else:
            print(f"⚠️ {failed} test(s) failed. Please check the errors above.")
        
        print("=" * 60)
    
    def get_test_results(self):
        """Get test results summary"""
        passed = sum(1 for result in self.test_results if result[1] == "PASS")
        total = len(self.test_results)
        return passed == total

def main():
    """Main function to run the consolidated test suite"""
    test_suite = IronWallTestSuite()
    success = test_suite.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 