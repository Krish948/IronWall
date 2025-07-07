"""
IronWall Antivirus - Reset Verification
Verify that the reset functionality actually works
"""

import os
import json
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_file_contents(file_path, description):
    """Check the contents of a file"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                size = len(data)
            elif isinstance(data, list):
                size = len(data)
            else:
                size = "unknown"
            
            print(f"  {description}: {size} items")
            return size
        else:
            print(f"  {description}: File does not exist")
            return 0
    except Exception as e:
        print(f"  {description}: Error reading file - {e}")
        return -1

def verify_reset():
    """Verify that the reset functionality works"""
    print("🛡️ IronWall Antivirus - Reset Verification")
    print("=" * 50)
    
    base_dir = Path(__file__).parent
    
    print("📊 Current data status:")
    print("-" * 30)
    
    # Check various data files
    settings_size = check_file_contents(base_dir / "ironwall_settings.json", "Settings")
    threat_db_size = check_file_contents(base_dir / "threat_database.json", "Threat Database")
    scan_history_size = check_file_contents(base_dir / "scan_history.json", "Scan History")
    system_logs_size = check_file_contents(base_dir / "system_logs.json", "System Logs")
    
    # Check quarantine
    quarantine_dir = base_dir / "quarantine"
    if quarantine_dir.exists():
        quarantine_files = len(list(quarantine_dir.glob("*")))
        print(f"  Quarantine: {quarantine_files} files")
    else:
        print(f"  Quarantine: Directory does not exist")
    
    # Check backups
    backup_dir = base_dir / "backups"
    if backup_dir.exists():
        backup_dirs = len(list(backup_dir.iterdir()))
        print(f"  Backups: {backup_dirs} backup directories")
    else:
        print(f"  Backups: Directory does not exist")
    
    print("\n🔄 Performing reset...")
    print("-" * 30)
    
    try:
        from utils.data_reset import DataResetManager
        
        data_reset_manager = DataResetManager()
        results = data_reset_manager.reset_all_data(create_backup=True)
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        print(f"Reset completed: {success_count}/{total_count} operations successful")
        
    except Exception as e:
        print(f"Reset failed: {e}")
        return False
    
    print("\n📊 Data status after reset:")
    print("-" * 30)
    
    # Check files again after reset
    settings_size_after = check_file_contents(base_dir / "ironwall_settings.json", "Settings")
    threat_db_size_after = check_file_contents(base_dir / "threat_database.json", "Threat Database")
    scan_history_size_after = check_file_contents(base_dir / "scan_history.json", "Scan History")
    system_logs_size_after = check_file_contents(base_dir / "system_logs.json", "System Logs")
    
    # Check quarantine after reset
    if quarantine_dir.exists():
        quarantine_files_after = len(list(quarantine_dir.glob("*")))
        print(f"  Quarantine: {quarantine_files_after} files")
    else:
        print(f"  Quarantine: Directory does not exist")
    
    # Check backups after reset
    if backup_dir.exists():
        backup_dirs_after = len(list(backup_dir.iterdir()))
        print(f"  Backups: {backup_dirs_after} backup directories")
    else:
        print(f"  Backups: Directory does not exist")
    
    print("\n📈 Reset Verification Results:")
    print("-" * 30)
    
    # Verify changes - check if data was reset to defaults
    settings_reset = settings_size_after == 10  # Default settings structure
    threat_db_reset = threat_db_size_after == 4  # Default threat database structure
    scan_history_reset = scan_history_size_after == 0  # Should be empty
    system_logs_reset = system_logs_size_after == 0  # Should be empty
    
    print(f"Settings reset to defaults: {'✅' if settings_reset else '❌'}")
    print(f"Threat database reset to defaults: {'✅' if threat_db_reset else '❌'}")
    print(f"Scan history cleared: {'✅' if scan_history_reset else '❌'}")
    print(f"System logs cleared: {'✅' if system_logs_reset else '❌'}")
    
    # Check if backup was created
    backup_created = backup_dirs_after > backup_dirs if 'backup_dirs' in locals() else True
    print(f"Backup created: {'✅' if backup_created else '❌'}")
    
    all_reset = settings_reset and threat_db_reset and scan_history_reset and system_logs_reset and backup_created
    
    print(f"\nOverall reset verification: {'✅ PASS' if all_reset else '❌ FAIL'}")
    
    return all_reset

def main():
    """Main verification function"""
    success = verify_reset()
    
    if success:
        print("\n🎉 Reset verification passed! The reset functionality is working correctly.")
    else:
        print("\n⚠️  Reset verification failed. Some data may not have been reset properly.")
    
    print("\nTo test the reset button in the GUI:")
    print("1. Run IronWall Antivirus")
    print("2. Go to Settings → Advanced tab")
    print("3. Click '🔄 Reset All Data' button")
    print("4. Confirm the reset operation")

if __name__ == "__main__":
    main() 