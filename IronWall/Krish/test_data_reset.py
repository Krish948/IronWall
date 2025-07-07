"""
IronWall Antivirus - Data Reset Test Script
Test the comprehensive data reset functionality
"""

import os
import sys
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.data_reset import DataResetManager

def test_data_reset():
    """Test the data reset functionality"""
    print("🛡️ IronWall Antivirus - Data Reset Test")
    print("=" * 50)
    
    # Create data reset manager
    data_reset_manager = DataResetManager()
    
    print(f"Base directory: {data_reset_manager.base_dir}")
    print(f"Data files to reset: {data_reset_manager.data_files}")
    print(f"Data directories to reset: {data_reset_manager.data_directories}")
    
    # Test backup creation
    print("\n📦 Testing backup creation...")
    backup_success = data_reset_manager.create_backup()
    print(f"Backup creation: {'✅ Success' if backup_success else '❌ Failed'}")
    
    if backup_success:
        print("Backup log:")
        for log_entry in data_reset_manager.get_reset_log():
            print(f"  {log_entry}")
    
    # Test individual reset operations
    print("\n🔄 Testing individual reset operations...")
    
    # Test settings reset
    print("Testing settings reset...")
    settings_success = data_reset_manager.reset_settings()
    print(f"Settings reset: {'✅ Success' if settings_success else '❌ Failed'}")
    
    # Test threat database reset
    print("Testing threat database reset...")
    threat_db_success = data_reset_manager.reset_threat_database()
    print(f"Threat database reset: {'✅ Success' if threat_db_success else '❌ Failed'}")
    
    # Test quarantine reset
    print("Testing quarantine reset...")
    quarantine_success = data_reset_manager.reset_quarantine()
    print(f"Quarantine reset: {'✅ Success' if quarantine_success else '❌ Failed'}")
    
    # Test scan history reset
    print("Testing scan history reset...")
    history_success = data_reset_manager.reset_scan_history()
    print(f"Scan history reset: {'✅ Success' if history_success else '❌ Failed'}")
    
    # Test system logs reset
    print("Testing system logs reset...")
    logs_success = data_reset_manager.reset_system_logs()
    print(f"System logs reset: {'✅ Success' if logs_success else '❌ Failed'}")
    
    # Test scheduled scans reset
    print("Testing scheduled scans reset...")
    scans_success = data_reset_manager.reset_scheduled_scans()
    print(f"Scheduled scans reset: {'✅ Success' if scans_success else '❌ Failed'}")
    
    # Test network rules reset
    print("Testing network rules reset...")
    rules_success = data_reset_manager.reset_network_rules()
    print(f"Network rules reset: {'✅ Success' if rules_success else '❌ Failed'}")
    
    # Test backups reset
    print("Testing backups reset...")
    backups_success = data_reset_manager.reset_backups()
    print(f"Backups reset: {'✅ Success' if backups_success else '❌ Failed'}")
    
    # Test restore points reset
    print("Testing restore points reset...")
    restore_success = data_reset_manager.reset_restore_points()
    print(f"Restore points reset: {'✅ Success' if restore_success else '❌ Failed'}")
    
    # Test diagnostic files clear
    print("Testing diagnostic files clear...")
    diag_success = data_reset_manager.clear_diagnostic_files()
    print(f"Diagnostic files clear: {'✅ Success' if diag_success else '❌ Failed'}")
    
    # Show final reset log
    print("\n📋 Final Reset Log:")
    for log_entry in data_reset_manager.get_reset_log():
        print(f"  {log_entry}")
    
    print("\n✅ Data reset test completed!")

def test_comprehensive_reset():
    """Test the comprehensive reset functionality"""
    print("\n🔄 Testing comprehensive data reset...")
    print("=" * 50)
    
    # Create data reset manager
    data_reset_manager = DataResetManager()
    
    # Perform comprehensive reset
    results = data_reset_manager.reset_all_data(create_backup=True)
    
    # Show results
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    print(f"\n📊 Reset Results: {success_count}/{total_count} operations successful")
    
    for operation, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {operation.replace('_', ' ').title()}")
    
    # Show reset log
    print("\n📋 Comprehensive Reset Log:")
    for log_entry in data_reset_manager.get_reset_log():
        print(f"  {log_entry}")
    
    print("\n✅ Comprehensive reset test completed!")

def main():
    """Main test function"""
    try:
        # Test individual operations
        test_data_reset()
        
        # Test comprehensive reset
        test_comprehensive_reset()
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 