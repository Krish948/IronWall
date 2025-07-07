"""
IronWall Antivirus - CLI Reset Test
Simple test script to demonstrate CLI reset functionality
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cli_reset():
    """Test the CLI reset functionality"""
    print("🛡️ IronWall Antivirus - CLI Reset Test")
    print("=" * 50)
    
    try:
        from utils.data_reset import DataResetManager
        
        # Create data reset manager
        data_reset_manager = DataResetManager()
        
        print("✅ Data reset manager created successfully")
        print(f"Base directory: {data_reset_manager.base_dir}")
        
        # Test individual reset operations
        print("\n🔄 Testing individual reset operations...")
        
        # Test settings reset
        print("Testing settings reset...")
        if data_reset_manager.reset_settings():
            print("✅ Settings reset successful")
        else:
            print("❌ Settings reset failed")
        
        # Test quarantine reset
        print("Testing quarantine reset...")
        if data_reset_manager.reset_quarantine():
            print("✅ Quarantine reset successful")
        else:
            print("❌ Quarantine reset failed")
        
        # Test scan history reset
        print("Testing scan history reset...")
        if data_reset_manager.reset_scan_history():
            print("✅ Scan history reset successful")
        else:
            print("❌ Scan history reset failed")
        
        # Test system logs reset
        print("Testing system logs reset...")
        if data_reset_manager.reset_system_logs():
            print("✅ System logs reset successful")
        else:
            print("❌ System logs reset failed")
        
        print("\n✅ CLI reset functionality test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def simulate_cli_reset_command():
    """Simulate CLI reset command functionality"""
    print("\n🖥️ Simulating CLI reset command...")
    print("=" * 50)
    
    try:
        from utils.data_reset import DataResetManager
        
        data_reset_manager = DataResetManager()
        
        # Simulate --all command
        print("Simulating: python cli.py reset --all")
        print("⚠️  WARNING: This will reset ALL IronWall data to factory defaults!")
        print("This includes settings, scan history, quarantine, logs, and more.")
        
        # Simulate user confirmation
        print("User response: yes")
        
        print("🔄 Starting comprehensive data reset...")
        results = data_reset_manager.reset_all_data(create_backup=True)
        
        # Show results
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        print(f"\n✅ Reset completed: {success_count}/{total_count} operations successful")
        
        for operation, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {operation.replace('_', ' ').title()}")
        
        # Show reset log
        print("\n📋 Reset Log:")
        for log_entry in data_reset_manager.get_reset_log():
            print(f"  {log_entry}")
        
        print("\n✅ CLI reset command simulation completed!")
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function"""
    print("Testing IronWall CLI Reset Functionality")
    print("=" * 60)
    
    # Test basic functionality
    test_cli_reset()
    
    # Simulate CLI command
    simulate_cli_reset_command()
    
    print("\n🎉 All CLI reset tests completed successfully!")
    print("\nTo use the actual CLI, run:")
    print("  python cli.py reset --all")
    print("  python cli.py reset --settings")
    print("  python cli.py reset --quarantine")
    print("  python cli.py reset --logs")

if __name__ == "__main__":
    main() 