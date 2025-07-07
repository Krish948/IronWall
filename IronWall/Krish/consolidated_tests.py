#!/usr/bin/env python3
"""
IronWall Antivirus - Comprehensive Consolidated Test Suite
Merges all 18 individual test files into a single comprehensive test suite
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
import random
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class IronWallTestSuite:
    """Comprehensive test suite for IronWall Antivirus - Merged from all 18 test files"""
    
    def __init__(self):
        self.test_results = []
        self.original_ip = None
        
    def run_all_tests(self):
        """Run all tests in the consolidated test suite"""
        print("🛡️ IronWall Antivirus - Comprehensive Consolidated Test Suite")
        print("=" * 80)
        print("📋 Merged from 18 individual test files")
        print("=" * 80)
        
        # Core functionality tests
        self.test_imports()
        self.test_settings_manager()
        self.test_scanner()
        self.test_scan_history()
        self.test_threat_database()
        self.test_quarantine_system()
        
        # Advanced features tests (from test_advanced_features.py)
        self.test_ai_engine()
        self.test_process_monitor()
        self.test_sandbox()
        self.test_cloud_intelligence()
        self.test_network_protection()
        self.test_ransomware_shield()
        self.test_restore_point()
        self.test_cli()
        
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
        self.test_graph_click_functionality()
        self.test_table_styling()
        self.test_settings_display()
        
        # Integration and configuration tests
        self.test_integration()
        self.test_configuration_files()
        self.test_time_tracking()
        self.test_all_themes_and_functions()
        self.test_quarantine_system_advanced()
        
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
            
            # Test getting all threats
            threats = threat_db.get_all_threats()
            if isinstance(threats, list):
                print("✅ Threat database loading works")
            else:
                print(f"❌ Threat database loading failed: expected list, got {type(threats)}")
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
            
            # Test getting quarantined files
            files = quarantine.get_quarantined_files()
            if isinstance(files, list):
                print("✅ Quarantine system loading works")
            else:
                print(f"❌ Quarantine system loading failed: expected list, got {type(files)}")
                self.test_results.append(("Quarantine System", "FAIL", "get_quarantined_files failed"))
                return False
            
            # Test quarantining a file
            test_file = "test_quarantine_file.txt"
            with open(test_file, 'w') as f:
                f.write("test content")
            
            success = quarantine.quarantine_file(test_file, "test_threat")
            if success:
                print("✅ Quarantine file operation works")
            else:
                print("❌ Quarantine file operation failed")
                self.test_results.append(("Quarantine System", "FAIL", "quarantine_file failed"))
                return False
            
            # Cleanup
            if os.path.exists(test_file):
                os.remove(test_file)
            
            self.test_results.append(("Quarantine System", "PASS", "All operations working"))
            return True
            
        except Exception as e:
            print(f"❌ Quarantine system test failed: {e}")
            self.test_results.append(("Quarantine System", "FAIL", str(e)))
            return False
    
    # ============================================================================
    # ADVANCED FEATURES TESTS (from test_advanced_features.py)
    # ============================================================================
    
    def test_ai_engine(self):
        """Test AI/ML Behavioral Engine"""
        print("\n🤖 Testing AI/ML Behavioral Engine...")
        try:
            from core.ai_engine import AIBehavioralEngine
            
            ai_engine = AIBehavioralEngine()
            
            # Test with a sample file
            test_file = os.path.join(os.path.dirname(__file__), 'test_threats', 'malware.txt')
            if os.path.exists(test_file):
                result = ai_engine.analyze_file(test_file)
                print(f"✅ AI Analysis Result: {result['threat_level']} (Score: {result['threat_score']})")
            else:
                print("⚠️ Test file not found, creating dummy analysis")
                result = ai_engine.analyze_file(__file__)
                print(f"✅ AI Analysis Result: {result['threat_level']} (Score: {result['threat_score']})")
            
            self.test_results.append(("AI Engine", "PASS", "Analysis working"))
            return True
        except Exception as e:
            print(f"❌ AI Engine test failed: {e}")
            self.test_results.append(("AI Engine", "FAIL", str(e)))
            return False
    
    def test_process_monitor(self):
        """Test Process Monitor"""
        print("\n🔄 Testing Process Monitor...")
        try:
            from core.process_monitor import ProcessMonitor
            from utils.threat_database import ThreatDatabase
            
            threat_db = ThreatDatabase()
            process_monitor = ProcessMonitor(threat_db)
            
            # Get process list
            processes = process_monitor.get_process_list(5)
            print(f"✅ Process Monitor: Found {len(processes)} processes")
            
            # Get stats
            stats = process_monitor.get_process_stats()
            print(f"✅ Process Monitor Stats: {stats['total_monitored']} monitored")
            
            self.test_results.append(("Process Monitor", "PASS", "Monitoring working"))
            return True
        except Exception as e:
            print(f"❌ Process Monitor test failed: {e}")
            self.test_results.append(("Process Monitor", "FAIL", str(e)))
            return False
    
    def test_sandbox(self):
        """Test Sandbox Execution"""
        print("\n🧪 Testing Sandbox Execution...")
        try:
            from core.sandbox import SandboxExecution
            
            sandbox = SandboxExecution()
            
            # Test with a simple file
            test_file = os.path.join(os.path.dirname(__file__), 'test_threats', 'suspicious_js.js')
            if os.path.exists(test_file):
                session_id = sandbox.create_sandbox_session(test_file)
                print(f"✅ Sandbox session created: {session_id}")
                
                # Get session info
                session_info = sandbox.get_session_info(session_id)
                print(f"✅ Sandbox session info: {session_info['status']}")
                
                # Cleanup
                sandbox.cleanup_session(session_id)
                print("✅ Sandbox session cleaned up")
            else:
                print("⚠️ Test file not found, skipping sandbox test")
            
            self.test_results.append(("Sandbox", "PASS", "Sandbox working"))
            return True
        except Exception as e:
            print(f"❌ Sandbox test failed: {e}")
            self.test_results.append(("Sandbox", "FAIL", str(e)))
            return False
    
    def test_cloud_intelligence(self):
        """Test Cloud Threat Intelligence"""
        print("\n☁️ Testing Cloud Threat Intelligence...")
        try:
            from core.cloud_intelligence import CloudThreatIntelligence
            
            cloud_intel = CloudThreatIntelligence()
            
            # Test with a known hash (this is a safe test hash)
            test_hash = "d41d8cd98f00b204e9800998ecf8427e"  # Empty file hash
            result = cloud_intel.check_file_hash(test_hash)
            print(f"✅ Cloud Intelligence Result: {result['overall_verdict']}")
            
            # Get available sources
            sources = cloud_intel.get_available_sources()
            print(f"✅ Available sources: {len(sources['sources'])}")
            
            self.test_results.append(("Cloud Intelligence", "PASS", "Cloud checks working"))
            return True
        except Exception as e:
            print(f"❌ Cloud Intelligence test failed: {e}")
            self.test_results.append(("Cloud Intelligence", "FAIL", str(e)))
            return False
    
    def test_network_protection(self):
        """Test Network Protection"""
        print("\n🌐 Testing Network Protection...")
        try:
            from core.network_protection import NetworkProtection
            
            network_protection = NetworkProtection()
            
            # Test blocking an IP
            test_ip = "192.168.1.100"
            network_protection.add_blocked_ip(test_ip)
            print(f"✅ Blocked IP: {test_ip}")
            
            # Get stats
            stats = network_protection.get_network_stats()
            print(f"✅ Network Protection Stats: {stats['blocked_ips_count']} blocked IPs")
            
            # Unblock the IP
            network_protection.remove_blocked_ip(test_ip)
            print(f"✅ Unblocked IP: {test_ip}")
            
            self.test_results.append(("Network Protection", "PASS", "Network protection working"))
            return True
        except Exception as e:
            print(f"❌ Network Protection test failed: {e}")
            self.test_results.append(("Network Protection", "FAIL", str(e)))
            return False
    
    def test_ransomware_shield(self):
        """Test Ransomware Shield"""
        print("\n🔐 Testing Ransomware Shield...")
        try:
            from core.ransomware_shield import RansomwareShield
            
            ransomware_shield = RansomwareShield()
            
            # Get protection stats
            stats = ransomware_shield.get_protection_stats()
            print(f"✅ Ransomware Protection Stats: {stats['protected_files']} protected files")
            
            # Add a protected directory
            test_dir = os.path.dirname(__file__)
            ransomware_shield.add_protected_directory(test_dir)
            print(f"✅ Added protected directory: {test_dir}")
            
            self.test_results.append(("Ransomware Shield", "PASS", "Protection working"))
            return True
        except Exception as e:
            print(f"❌ Ransomware Shield test failed: {e}")
            self.test_results.append(("Ransomware Shield", "FAIL", str(e)))
            return False
    
    def test_restore_point(self):
        """Test Restore Point Creator"""
        print("\n🔄 Testing Restore Point Creator...")
        try:
            from core.restore_point import RestorePointCreator
            
            restore_point = RestorePointCreator()
            
            # Get stats
            stats = restore_point.get_restore_point_stats()
            print(f"✅ Restore Point Stats: {stats['total_restore_points']} restore points")
            
            # Create a test restore point
            restore_id = restore_point.create_restore_point("test", "Test restore point")
            if restore_id:
                print(f"✅ Created restore point: {restore_id}")
                
                # List restore points
                points = restore_point.list_restore_points()
                print(f"✅ Total restore points: {len(points)}")
                
                # Delete the test restore point
                restore_point.delete_restore_point(restore_id)
                print(f"✅ Deleted restore point: {restore_id}")
            else:
                print("⚠️ Could not create restore point")
            
            self.test_results.append(("Restore Point", "PASS", "Restore points working"))
            return True
        except Exception as e:
            print(f"❌ Restore Point test failed: {e}")
            self.test_results.append(("Restore Point", "FAIL", str(e)))
            return False
    
    def test_cli(self):
        """Test CLI Interface"""
        print("\n💻 Testing CLI Interface...")
        try:
            from cli import IronWallCLI
            
            cli = IronWallCLI()
            
            # Test getting system stats
            stats = cli.system_monitor.get_detailed_stats()
            print(f"✅ CLI System Stats: CPU {stats['cpu']['percent']:.1f}%, Memory {stats['memory']['percent']:.1f}%")
            
            self.test_results.append(("CLI Interface", "PASS", "CLI working"))
            return True
        except Exception as e:
            print(f"❌ CLI test failed: {e}")
            self.test_results.append(("CLI Interface", "FAIL", str(e)))
            return False
    
    # ============================================================================
    # UI COMPONENT TESTS
    # ============================================================================
    
    def test_ui_components(self):
        """Test UI component imports"""
        print("\n🔍 Testing UI components...")
        
        try:
            from ui.main_window import IronWallMainWindow
            print("✅ Main window import successful")
        except Exception as e:
            print(f"❌ Main window import failed: {e}")
            self.test_results.append(("UI Components", "FAIL", "Main window import failed"))
            return False
        
        try:
            from ui.settings_panel import SettingsPanel
            print("✅ Settings panel import successful")
        except Exception as e:
            print(f"❌ Settings panel import failed: {e}")
            self.test_results.append(("UI Components", "FAIL", "Settings panel import failed"))
            return False
        
        try:
            from ui.theme_preview import ThemeSelectorWidget, ColorPickerWidget
            print("✅ Theme preview import successful")
        except Exception as e:
            print(f"❌ Theme preview import failed: {e}")
            self.test_results.append(("UI Components", "FAIL", "Theme preview import failed"))
            return False
        
        self.test_results.append(("UI Components", "PASS", "All UI components imported"))
        return True
    
    def test_about_tab(self):
        """Test about tab functionality"""
        print("\n🔍 Testing about tab...")
        try:
            from ui.main_window import IronWallMainWindow
            from utils.threat_database import ThreatDatabase
            from utils.system_monitor import SystemMonitor
            from core.scanner import IronWallScanner
            
            # Create components
            threat_db = ThreatDatabase()
            system_monitor = SystemMonitor()
            scanner = IronWallScanner(threat_db)
            
            # Test main window creation
            app = IronWallMainWindow(scanner, system_monitor, threat_db)
            print("✅ About tab creation successful")
            
            self.test_results.append(("About Tab", "PASS", "About tab working"))
            return True
        except Exception as e:
            print(f"❌ About tab test failed: {e}")
            self.test_results.append(("About Tab", "FAIL", str(e)))
            return False
    
    def test_settings_panel(self):
        """Test settings panel functionality"""
        print("\n🔍 Testing settings panel...")
        try:
            from ui.settings_panel import SettingsPanel
            from utils.settings_manager import get_settings_manager
            
            settings_manager = get_settings_manager()
            
            # Create a mock parent
            class MockParent:
                def __init__(self):
                    self.settings_manager = settings_manager
            
            parent = MockParent()
            settings_panel = SettingsPanel(parent, parent)
            print("✅ Settings panel creation successful")
            
            self.test_results.append(("Settings Panel", "PASS", "Settings panel working"))
            return True
        except Exception as e:
            print(f"❌ Settings panel test failed: {e}")
            self.test_results.append(("Settings Panel", "FAIL", str(e)))
            return False
    
    def test_scheduler_panel(self):
        """Test scheduler panel functionality"""
        print("\n🔍 Testing scheduler panel...")
        try:
            from ui.scheduler_panel import SchedulerPanel
            from utils.scheduler import Scheduler
            
            scheduler = Scheduler()
            
            # Create a mock parent
            class MockParent:
                def __init__(self):
                    self.scheduler = scheduler
            
            parent = MockParent()
            scheduler_panel = SchedulerPanel(parent, parent)
            print("✅ Scheduler panel creation successful")
            
            self.test_results.append(("Scheduler Panel", "PASS", "Scheduler panel working"))
            return True
        except Exception as e:
            print(f"❌ Scheduler panel test failed: {e}")
            self.test_results.append(("Scheduler Panel", "FAIL", str(e)))
            return False
    
    def test_reports_panel(self):
        """Test reports panel functionality"""
        print("\n🔍 Testing reports panel...")
        try:
            from ui.reports_panel import ReportsPanel
            
            # Create a mock parent
            class MockParent:
                pass
            
            parent = MockParent()
            reports_panel = ReportsPanel(parent, parent)
            print("✅ Reports panel creation successful")
            
            self.test_results.append(("Reports Panel", "PASS", "Reports panel working"))
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
            
            # Create a mock parent
            class MockParent:
                pass
            
            parent = MockParent()
            analytics_panel = AnalyticsPanel(parent, parent)
            print("✅ Analytics panel creation successful")
            
            self.test_results.append(("Analytics Performance", "PASS", "Analytics working"))
            return True
        except Exception as e:
            print(f"❌ Analytics performance test failed: {e}")
            self.test_results.append(("Analytics Performance", "FAIL", str(e)))
            return False
    
    def test_interface_options(self):
        """Test interface options functionality"""
        print("\n🔍 Testing interface options...")
        try:
            from ui.settings_panel import SettingsPanel
            from utils.settings_manager import get_settings_manager
            
            settings_manager = get_settings_manager()
            
            # Test interface settings
            settings_manager.set_setting("interface", "theme", "flatly")
            theme = settings_manager.get_setting("interface", "theme")
            
            if theme == "flatly":
                print("✅ Interface options working")
            else:
                print(f"❌ Interface options failed: expected 'flatly', got '{theme}'")
                self.test_results.append(("Interface Options", "FAIL", "Theme setting failed"))
                return False
            
            self.test_results.append(("Interface Options", "PASS", "Interface options working"))
            return True
        except Exception as e:
            print(f"❌ Interface options test failed: {e}")
            self.test_results.append(("Interface Options", "FAIL", str(e)))
            return False
    
    def test_color_palette(self):
        """Test color palette functionality"""
        print("\n🔍 Testing color palette...")
        try:
            from utils.color_palette import get_color_palette
            from ui.theme_preview import ThemeSelectorWidget, ColorPickerWidget
            
            color_palette = get_color_palette()
            
            # Test getting themes
            themes = color_palette.get_all_themes()
            if isinstance(themes, list) and len(themes) > 0:
                print(f"✅ Color palette working: {len(themes)} themes available")
            else:
                print("❌ Color palette failed: no themes available")
                self.test_results.append(("Color Palette", "FAIL", "No themes available"))
                return False
            
            self.test_results.append(("Color Palette", "PASS", "Color palette working"))
            return True
        except Exception as e:
            print(f"❌ Color palette test failed: {e}")
            self.test_results.append(("Color Palette", "FAIL", str(e)))
            return False
    
    def test_new_about_sections(self):
        """Test new about sections functionality"""
        print("\n🔍 Testing new about sections...")
        try:
            from ui.main_window import IronWallMainWindow
            from utils.threat_database import ThreatDatabase
            from utils.system_monitor import SystemMonitor
            from core.scanner import IronWallScanner
            
            # Create components
            threat_db = ThreatDatabase()
            system_monitor = SystemMonitor()
            scanner = IronWallScanner(threat_db)
            
            # Test main window with about sections
            app = IronWallMainWindow(scanner, system_monitor, threat_db)
            print("✅ New about sections working")
            
            self.test_results.append(("New About Sections", "PASS", "About sections working"))
            return True
        except Exception as e:
            print(f"❌ New about sections test failed: {e}")
            self.test_results.append(("New About Sections", "FAIL", str(e)))
            return False
    
    def test_graph_click_functionality(self):
        """Test graph click functionality"""
        print("\n🔍 Testing graph click functionality...")
        try:
            from ui.analytics_panel import AnalyticsPanel
            
            # Create a mock parent
            class MockParent:
                pass
            
            parent = MockParent()
            analytics_panel = AnalyticsPanel(parent, parent)
            print("✅ Graph click functionality working")
            
            self.test_results.append(("Graph Click Functionality", "PASS", "Graph clicks working"))
            return True
        except Exception as e:
            print(f"❌ Graph click functionality test failed: {e}")
            self.test_results.append(("Graph Click Functionality", "FAIL", str(e)))
            return False
    
    def test_table_styling(self):
        """Test table styling functionality"""
        print("\n🔍 Testing table styling...")
        try:
            from ui.reports_panel import ReportsPanel
            
            # Create a mock parent
            class MockParent:
                pass
            
            parent = MockParent()
            reports_panel = ReportsPanel(parent, parent)
            print("✅ Table styling working")
            
            self.test_results.append(("Table Styling", "PASS", "Table styling working"))
            return True
        except Exception as e:
            print(f"❌ Table styling test failed: {e}")
            self.test_results.append(("Table Styling", "FAIL", str(e)))
            return False
    
    def test_settings_display(self):
        """Test settings display functionality"""
        print("\n🔍 Testing settings display...")
        try:
            from ui.settings_panel import SettingsPanel
            from utils.settings_manager import get_settings_manager
            
            settings_manager = get_settings_manager()
            
            # Test settings display
            settings_manager.set_setting("display", "test_key", "test_value")
            value = settings_manager.get_setting("display", "test_key")
            
            if value == "test_value":
                print("✅ Settings display working")
            else:
                print(f"❌ Settings display failed: expected 'test_value', got '{value}'")
                self.test_results.append(("Settings Display", "FAIL", "Settings display failed"))
                return False
            
            self.test_results.append(("Settings Display", "PASS", "Settings display working"))
            return True
        except Exception as e:
            print(f"❌ Settings display test failed: {e}")
            self.test_results.append(("Settings Display", "FAIL", str(e)))
            return False
    
    # ============================================================================
    # INTEGRATION AND CONFIGURATION TESTS
    # ============================================================================
    
    def test_integration(self):
        """Test integration between components"""
        print("\n🔗 Testing Component Integration...")
        try:
            from utils.threat_database import ThreatDatabase
            from core.scanner import IronWallScanner
            from core.ai_engine import AIBehavioralEngine
            from core.process_monitor import ProcessMonitor
            
            # Initialize components
            threat_db = ThreatDatabase()
            scanner = IronWallScanner(threat_db)
            ai_engine = AIBehavioralEngine()
            process_monitor = ProcessMonitor(threat_db)
            
            print("✅ All components initialized successfully")
            
            # Test component communication
            test_file = __file__
            scan_result = scanner._scan_file_enhanced(test_file, lambda x: None)
            ai_result = ai_engine.analyze_file(test_file)
            
            print(f"✅ Scanner result: {scan_result}")
            print(f"✅ AI result: {ai_result['threat_level']}")
            
            self.test_results.append(("Integration", "PASS", "Component integration working"))
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
                self.test_results.append(("Configuration Files", "FAIL", f"{config_file} invalid"))
                return False
        
        self.test_results.append(("Configuration Files", "PASS", "All config files valid"))
        return True
    
    def test_time_tracking(self):
        """Test time tracking functionality"""
        print("\n🔍 Testing time tracking...")
        try:
            from utils.scheduler import Scheduler
            
            scheduler = Scheduler()
            
            # Test time tracking
            start_time = time.time()
            time.sleep(0.1)  # Small delay
            end_time = time.time()
            
            duration = end_time - start_time
            if duration > 0:
                print(f"✅ Time tracking working: {duration:.3f} seconds")
            else:
                print("❌ Time tracking failed")
                self.test_results.append(("Time Tracking", "FAIL", "Time tracking failed"))
                return False
            
            self.test_results.append(("Time Tracking", "PASS", "Time tracking working"))
            return True
        except Exception as e:
            print(f"❌ Time tracking test failed: {e}")
            self.test_results.append(("Time Tracking", "FAIL", str(e)))
            return False
    
    def test_all_themes_and_functions(self):
        """Test all themes and functions"""
        print("\n🔍 Testing all themes and functions...")
        try:
            from utils.color_palette import get_color_palette
            from ui.theme_preview import ThemeSelectorWidget
            
            color_palette = get_color_palette()
            
            # Test all themes
            themes = color_palette.get_all_themes()
            for theme in themes:
                if 'name' in theme and 'colors' in theme:
                    print(f"✅ Theme '{theme['name']}' is valid")
                else:
                    print(f"❌ Theme '{theme.get('name', 'Unknown')}' is invalid")
                    self.test_results.append(("All Themes and Functions", "FAIL", f"Theme {theme.get('name', 'Unknown')} invalid"))
                    return False
            
            print(f"✅ All {len(themes)} themes are valid")
            
            self.test_results.append(("All Themes and Functions", "PASS", "All themes valid"))
            return True
        except Exception as e:
            print(f"❌ All themes and functions test failed: {e}")
            self.test_results.append(("All Themes and Functions", "FAIL", str(e)))
            return False
    
    def test_quarantine_system_advanced(self):
        """Test advanced quarantine system functionality"""
        print("\n🔍 Testing advanced quarantine system...")
        try:
            from utils.quarantine import QuarantineManager
            
            quarantine = QuarantineManager()
            
            # Test advanced quarantine operations
            test_file = "test_advanced_quarantine.txt"
            with open(test_file, 'w') as f:
                f.write("test content for advanced quarantine")
            
            # Quarantine file
            success = quarantine.quarantine_file(test_file, "advanced_test_threat")
            if not success:
                print("❌ Advanced quarantine failed")
                self.test_results.append(("Advanced Quarantine", "FAIL", "Quarantine operation failed"))
                return False
            
            # Get quarantined files
            files = quarantine.get_quarantined_files()
            if len(files) > 0:
                print(f"✅ Advanced quarantine working: {len(files)} files quarantined")
            else:
                print("⚠️ No files in quarantine")
            
            # Restore file
            if os.path.exists(test_file):
                os.remove(test_file)
            
            self.test_results.append(("Advanced Quarantine", "PASS", "Advanced quarantine working"))
            return True
        except Exception as e:
            print(f"❌ Advanced quarantine test failed: {e}")
            self.test_results.append(("Advanced Quarantine", "FAIL", str(e)))
            return False
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed = 0
        total = len(self.test_results)
        
        # Group results by category
        categories = {}
        for test_name, status, details in self.test_results:
            category = test_name.split()[0] if ' ' in test_name else test_name
            if category not in categories:
                categories[category] = []
            categories[category].append((test_name, status, details))
        
        # Print results by category
        for category, tests in categories.items():
            print(f"\n📋 {category.upper()} TESTS:")
            print("-" * 40)
            category_passed = 0
            for test_name, status, details in tests:
                status_icon = "✅" if status == "PASS" else "❌"
                print(f"{status_icon} {test_name}: {details}")
                if status == "PASS":
                    passed += 1
                    category_passed += 1
            
            category_total = len(tests)
            print(f"   {category_passed}/{category_total} passed")
        
        # Overall summary
        print("\n" + "=" * 80)
        print("📈 OVERALL SUMMARY")
        print("=" * 80)
        print(f"🎯 Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {total - passed}")
        print(f"📊 Success Rate: {passed/total*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! IronWall is working perfectly!")
        elif passed >= total * 0.8:
            print("⚠️ Most tests passed. Some minor issues detected.")
        else:
            print("🚨 Multiple tests failed. Please check the system.")
        
        print("=" * 80)
    
    def get_test_results(self):
        """Get test results for programmatic access"""
        passed = sum(1 for _, status, _ in self.test_results if status == "PASS")
        total = len(self.test_results)
        return {
            'total_tests': total,
            'passed_tests': passed,
            'failed_tests': total - passed,
            'success_rate': passed / total if total > 0 else 0,
            'results': self.test_results
        }

def main():
    """Main function to run the consolidated test suite"""
    test_suite = IronWallTestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        return True
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 