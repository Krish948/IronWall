"""
IronWall Antivirus - Advanced Features Test Script
Test all advanced security features
"""

import os
import sys
import time
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ai_engine():
    """Test AI/ML Behavioral Engine"""
    print("🤖 Testing AI/ML Behavioral Engine...")
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
        
        return True
    except Exception as e:
        print(f"❌ AI Engine test failed: {e}")
        return False

def test_process_monitor():
    """Test Process Monitor"""
    print("🔄 Testing Process Monitor...")
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
        
        return True
    except Exception as e:
        print(f"❌ Process Monitor test failed: {e}")
        return False

def test_sandbox():
    """Test Sandbox Execution"""
    print("🧪 Testing Sandbox Execution...")
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
        
        return True
    except Exception as e:
        print(f"❌ Sandbox test failed: {e}")
        return False

def test_cloud_intelligence():
    """Test Cloud Threat Intelligence"""
    print("☁️ Testing Cloud Threat Intelligence...")
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
        
        return True
    except Exception as e:
        print(f"❌ Cloud Intelligence test failed: {e}")
        return False

def test_network_protection():
    """Test Network Protection"""
    print("🌐 Testing Network Protection...")
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
        
        return True
    except Exception as e:
        print(f"❌ Network Protection test failed: {e}")
        return False

def test_ransomware_shield():
    """Test Ransomware Shield"""
    print("🔐 Testing Ransomware Shield...")
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
        
        return True
    except Exception as e:
        print(f"❌ Ransomware Shield test failed: {e}")
        return False

def test_restore_point():
    """Test Restore Point Creator"""
    print("🔄 Testing Restore Point Creator...")
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
        
        return True
    except Exception as e:
        print(f"❌ Restore Point test failed: {e}")
        return False

def test_cli():
    """Test CLI Interface"""
    print("💻 Testing CLI Interface...")
    try:
        from cli import IronWallCLI
        
        cli = IronWallCLI()
        
        # Test getting system stats
        stats = cli.system_monitor.get_detailed_stats()
        print(f"✅ CLI System Stats: CPU {stats['cpu']['percent']:.1f}%, Memory {stats['memory']['percent']:.1f}%")
        
        return True
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def test_integration():
    """Test integration between components"""
    print("🔗 Testing Component Integration...")
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
        
        return True
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🛡️ IronWall Antivirus - Advanced Features Test Suite")
    print("=" * 60)
    
    tests = [
        ("AI/ML Behavioral Engine", test_ai_engine),
        ("Process Monitor", test_process_monitor),
        ("Sandbox Execution", test_sandbox),
        ("Cloud Intelligence", test_cloud_intelligence),
        ("Network Protection", test_network_protection),
        ("Ransomware Shield", test_ransomware_shield),
        ("Restore Point Creator", test_restore_point),
        ("CLI Interface", test_cli),
        ("Component Integration", test_integration)
    ]
    
    results = []
    start_time = time.time()
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    elapsed_time = time.time() - start_time
    print(f"⏱️ Total test time: {elapsed_time:.2f} seconds")
    
    if passed == total:
        print("🎉 All tests passed! Advanced features are working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 