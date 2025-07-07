"""
Test script for IronWall Quarantine Management System
Demonstrates the full functionality of the quarantine system
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.quarantine import QuarantineManager

def create_test_file(content, filename):
    """Create a test file with given content"""
    file_path = os.path.join(tempfile.gettempdir(), filename)
    with open(file_path, 'w') as f:
        f.write(content)
    return file_path

def test_quarantine_system():
    """Test the quarantine management system"""
    print("🧪 Testing IronWall Quarantine Management System")
    print("=" * 60)
    
    # Initialize quarantine manager
    quarantine_manager = QuarantineManager()
    
    # Create some test files
    print("\n📁 Creating test threat files...")
    test_files = []
    
    # Test file 1: Malicious script
    malicious_script = create_test_file(
        "echo 'This is a malicious script'\n"
        "del /f /q C:\\Windows\\System32\\*.*\n"
        "format C: /q /y",
        "malicious_script.bat"
    )
    test_files.append(malicious_script)
    
    # Test file 2: Suspicious JavaScript
    suspicious_js = create_test_file(
        "eval('alert(\"Suspicious code\")');\n"
        "document.location='http://malicious-site.com';",
        "suspicious_script.js"
    )
    test_files.append(suspicious_js)
    
    # Test file 3: Large fake executable
    fake_exe = create_test_file(
        "This is a fake executable file with malicious content.\n" * 1000,
        "fake_malware.exe"
    )
    test_files.append(fake_exe)
    
    print(f"✅ Created {len(test_files)} test files")
    
    # Quarantine the test files
    print("\n🦠 Quarantining test files...")
    for i, file_path in enumerate(test_files):
        threat_types = ["Trojan", "Adware", "Worm"]
        severities = ["Critical", "Moderate", "Low"]
        
        success = quarantine_manager.quarantine_file(
            file_path=file_path,
            threat_type=threat_types[i],
            severity=severities[i],
            signature=f"TEST_SIGNATURE_{i+1}",
            risk_level="High" if severities[i] == "Critical" else "Medium",
            description=f"This is a test {threat_types[i].lower()} file for demonstration purposes",
            origin="Test Scan"
        )
        
        if success:
            print(f"✅ Quarantined: {os.path.basename(file_path)} ({threat_types[i]})")
        else:
            print(f"❌ Failed to quarantine: {os.path.basename(file_path)}")
    
    # Test listing items
    print("\n📋 Listing quarantined items...")
    items = quarantine_manager.list_items()
    print(f"Found {len(items)} quarantined items:")
    
    for item in items:
        print(f"  - {item.get('file_name', 'Unknown')} ({item.get('threat_type', 'Unknown')}) - {item.get('severity', 'Unknown')}")
    
    # Test search functionality
    print("\n🔍 Testing search functionality...")
    search_results = quarantine_manager.list_items(search="script")
    print(f"Search for 'script' found {len(search_results)} items:")
    for item in search_results:
        print(f"  - {item.get('file_name', 'Unknown')}")
    
    # Test storage info
    print("\n💾 Storage information:")
    storage_info = quarantine_manager.get_storage_info()
    print(f"  Total items: {storage_info.get('total_items', 0)}")
    print(f"  Total size: {storage_info.get('total_size', 0)} bytes")
    print(f"  Available space: {storage_info.get('available_space', 0)} bytes")
    
    # Test getting item details
    if items:
        print("\n🔍 Getting details for first item...")
        first_item = items[0]
        item_id = first_item.get('id')
        if item_id:
            details = quarantine_manager.get_item_details(item_id)
            if details:
                print(f"  File: {details.get('file_name', 'Unknown')}")
                print(f"  Threat Type: {details.get('threat_type', 'Unknown')}")
                print(f"  Severity: {details.get('severity', 'Unknown')}")
                print(f"  MD5: {details.get('md5', 'Unknown')[:16]}...")
                print(f"  SHA256: {details.get('sha256', 'Unknown')[:16]}...")
    
    # Test restore functionality (restore the first item)
    if items:
        print("\n🔄 Testing restore functionality...")
        first_item = items[0]
        item_id = first_item.get('id')
        if item_id:
            success, message = quarantine_manager.restore_file(item_id)
            if success:
                print(f"✅ Restored: {first_item.get('file_name', 'Unknown')}")
            else:
                print(f"❌ Failed to restore: {message}")
    
    # Test delete functionality (delete the second item if it exists)
    if len(items) > 1:
        print("\n🗑️ Testing delete functionality...")
        second_item = items[1]
        item_id = second_item.get('id')
        if item_id:
            success, message = quarantine_manager.delete_quarantined_file(item_id)
            if success:
                print(f"✅ Deleted: {second_item.get('file_name', 'Unknown')}")
            else:
                print(f"❌ Failed to delete: {message}")
    
    # Test cleanup rules
    print("\n🧹 Testing cleanup rules...")
    success = quarantine_manager.apply_cleanup_rules(max_days=1, max_size=1024*1024)  # 1 day, 1MB
    if success:
        print("✅ Cleanup rules applied")
    else:
        print("ℹ️ No files were cleaned up")
    
    # Final status
    print("\n📊 Final quarantine status:")
    final_items = quarantine_manager.list_items()
    print(f"Remaining items: {len(final_items)}")
    
    final_storage = quarantine_manager.get_storage_info()
    print(f"Final storage: {final_storage.get('total_size', 0)} bytes")
    
    print("\n🎉 Quarantine system test completed!")
    print("\nTo test the UI:")
    print("1. Run: python main.py")
    print("2. Click on 'Quarantine' in the sidebar")
    print("3. Explore the quarantine management interface")

if __name__ == "__main__":
    test_quarantine_system() 