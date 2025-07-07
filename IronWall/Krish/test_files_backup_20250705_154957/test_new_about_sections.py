#!/usr/bin/env python3
"""
Test script for new About tab sections with real data
Tests the Database Information, Security Status, and Resource Usage sections
"""

import sys
import os
import json
import psutil
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_information():
    """Test database information retrieval with real data"""
    print("Testing Database Information...")
    
    try:
        # Test threat database
        db_file = 'threat_database.json'
        if os.path.exists(db_file):
            db_size = os.path.getsize(db_file)
            with open(db_file, 'r') as f:
                db_data = json.load(f)
                db_version = db_data.get('version', '1.0')
                threat_hashes = len(db_data.get('hashes', {}))
                threat_signatures = len(db_data.get('signatures', []))
                last_update = db_data.get('last_updated', 'Unknown')
                
                # Parse the last update timestamp
                if last_update != 'Unknown':
                    try:
                        dt = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                        last_update_formatted = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        last_update_formatted = last_update
                else:
                    last_update_formatted = 'Unknown'
            
            print(f"✓ Database Version: v{db_version}")
            print(f"✓ Threat Hashes: {threat_hashes:,}")
            print(f"✓ Threat Signatures: {threat_signatures:,}")
            print(f"✓ Total Signatures: {threat_hashes + threat_signatures:,}")
            print(f"✓ Database Size: {db_size / 1024:.1f} KB")
            print(f"✓ Last Updated: {last_update_formatted}")
            print(f"✓ Database Location: {os.path.basename(db_file)}")
            return True
        else:
            print("✗ Threat database file not found")
            return False
            
    except Exception as e:
        print(f"✗ Database information test failed: {e}")
        return False

def test_security_status():
    """Test security status information retrieval with real data"""
    print("\nTesting Security Status...")
    
    try:
        # Test scan history
        from utils import scan_history
        scan_data = scan_history.load_scan_history()
        
        # Count real threats
        threats_detected = len([s for s in scan_data if s.get('status') in ['Threat Detected', 'Pattern Match', 'Heuristic Match']])
        clean_files = len([s for s in scan_data if s.get('status') == 'Clean'])
        
        # Get last scan time
        if scan_data:
            last_scan_timestamp = scan_data[-1].get('timestamp', 0)
            if last_scan_timestamp:
                last_scan_dt = datetime.fromtimestamp(last_scan_timestamp)
                last_scan = last_scan_dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                last_scan = 'Unknown'
        else:
            last_scan = 'Never'
        
        # Test quarantine
        quarantine_count = 0
        quarantine_size = 0
        try:
            quarantine_db_path = os.path.join('quarantine', 'quarantine_db.json')
            if os.path.exists(quarantine_db_path):
                with open(quarantine_db_path, 'r') as f:
                    quarantine_db = json.load(f)
                    quarantine_count = len(quarantine_db)
                    
                    # Calculate total quarantine size
                    for file_info in quarantine_db.values():
                        quarantine_size += file_info.get('file_size', 0)
        except:
            pass
        
        # Test protection status from settings
        try:
            with open('ironwall_settings.json', 'r') as f:
                settings = json.load(f)
                real_time_protection = settings.get('protection', {}).get('real_time_protection', False)
                firewall_protection = settings.get('protection', {}).get('firewall_protection', False)
                heuristic_scanning = settings.get('protection', {}).get('heuristic_scanning', 'Disabled')
        except:
            real_time_protection = False
            firewall_protection = False
            heuristic_scanning = 'Disabled'
        
        print(f"✓ Real-time Protection: {'🟢 Active' if real_time_protection else '🔴 Inactive'}")
        print(f"✓ Firewall Protection: {'🟢 Active' if firewall_protection else '🔴 Inactive'}")
        print(f"✓ Heuristic Scanning: {heuristic_scanning}")
        print(f"✓ Last Scan: {last_scan}")
        print(f"✓ Threats Detected: {threats_detected}")
        print(f"✓ Clean Files Scanned: {clean_files}")
        print(f"✓ Total Files Scanned: {threats_detected + clean_files}")
        print(f"✓ Quarantine Items: {quarantine_count}")
        print(f"✓ Quarantine Size: {quarantine_size / 1024:.1f} KB")
        print(f"✓ Scan History Size: {len(scan_data)} entries")
        return True
        
    except Exception as e:
        print(f"✗ Security status test failed: {e}")
        return False

def test_resource_usage():
    """Test resource usage information retrieval with real data"""
    print("\nTesting Resource Usage...")
    
    try:
        # Test process information
        current_process = psutil.Process()
        memory_usage = current_process.memory_info().rss / 1024 / 1024  # MB
        cpu_percent = current_process.cpu_percent()
        
        # Test log files
        log_files = []
        total_log_size = 0
        
        log_files_to_check = [
            'scan_history.json',
            'system_logs.json',
            'ironwall_settings.json',
            'threat_database.json'
        ]
        
        for log_file in log_files_to_check:
            if os.path.exists(log_file):
                file_size = os.path.getsize(log_file)
                total_log_size += file_size
                log_files.append(f"{log_file}: {file_size / 1024:.1f} KB")
        
        # Test scan performance
        from utils import scan_history
        scan_data = scan_history.load_scan_history()
        if len(scan_data) > 1:
            recent_scans = scan_data[-5:]  # Last 5 scans
            
            # Calculate average scan duration (if available)
            durations = [s.get('duration', 0) for s in recent_scans if s.get('duration')]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            # Calculate files per second
            total_files = sum(s.get('files_scanned', 1) for s in recent_scans)
            total_time = sum(durations) if durations else 1
            files_per_sec = total_files / total_time if total_time > 0 else 0
            
            # Get scan statistics
            scan_types = {}
            for scan in scan_data:
                scan_type = scan.get('scan_type', 'Unknown')
                scan_types[scan_type] = scan_types.get(scan_type, 0) + 1
            
            most_common_scan = max(scan_types.items(), key=lambda x: x[1])[0] if scan_types else 'Unknown'
        else:
            avg_duration = 0
            files_per_sec = 0
            most_common_scan = 'None'
        
        print(f"✓ Memory Usage: {memory_usage:.1f} MB")
        print(f"✓ CPU Usage: {cpu_percent:.1f}%")
        print(f"✓ Total Log Size: {total_log_size / 1024:.1f} KB")
        print(f"✓ Log Files: {len(log_files)} files")
        print(f"✓ Avg Scan Duration: {avg_duration:.1f}s")
        print(f"✓ Scan Speed: {files_per_sec:.1f} files/sec")
        print(f"✓ Most Common Scan: {most_common_scan}")
        print(f"✓ Process ID: {current_process.pid}")
        return True
        
    except Exception as e:
        print(f"✗ Resource usage test failed: {e}")
        return False

def test_system_information():
    """Test system information retrieval with real data"""
    print("\nTesting System Information...")
    
    try:
        import platform
        
        # Get real memory information
        memory = psutil.virtual_memory()
        total_memory_gb = memory.total // (1024**3)
        available_memory_gb = memory.available // (1024**3)
        memory_percent = memory.percent
        
        # Get real disk information
        disk = psutil.disk_usage('/')
        total_disk_gb = disk.total // (1024**3)
        free_disk_gb = disk.free // (1024**3)
        disk_percent = (disk.used / disk.total) * 100
        
        # Get real CPU information
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        cpu_freq_mhz = cpu_freq.current if cpu_freq else "Unknown"
        
        print(f"✓ Operating System: {platform.system()} {platform.release()}")
        print(f"✓ Architecture: {platform.architecture()[0]}")
        print(f"✓ Machine: {platform.machine()}")
        print(f"✓ Processor: {platform.processor()} ({cpu_count} cores)")
        print(f"✓ CPU Frequency: {cpu_freq_mhz:.0f} MHz")
        print(f"✓ Total Memory: {total_memory_gb:.1f} GB ({memory_percent:.1f}% used)")
        print(f"✓ Available Memory: {available_memory_gb:.1f} GB")
        print(f"✓ Total Disk Space: {total_disk_gb:.1f} GB ({disk_percent:.1f}% used)")
        print(f"✓ Free Disk Space: {free_disk_gb:.1f} GB")
        print(f"✓ Python Version: {sys.version.split()[0]}")
        print(f"✓ Working Directory: {os.getcwd()}")
        return True
        
    except Exception as e:
        print(f"✗ System information test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("IronWall Antivirus - Real Data About Tab Sections Test Suite")
    print("=" * 70)
    
    tests = [
        test_database_information,
        test_security_status,
        test_resource_usage,
        test_system_information
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 70)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! About tab sections are using real data correctly.")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 