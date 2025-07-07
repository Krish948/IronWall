#!/usr/bin/env python3
"""
Test script to verify progress calculation fix
"""

def test_progress_calculation():
    """Test the progress calculation logic"""
    total_files = 100
    files_scanned = 0
    
    print("Testing progress calculation:")
    print(f"Total files: {total_files}")
    
    for i in range(0, total_files + 1, 10):
        files_scanned = i
        progress = (files_scanned / total_files) * 100 if total_files > 0 else 0
        print(f"Files scanned: {files_scanned}/{total_files} = {progress:.1f}%")
    
    # Test edge cases
    print("\nTesting edge cases:")
    
    # Zero total files
    total_files = 0
    files_scanned = 0
    progress = (files_scanned / total_files) * 100 if total_files > 0 else 0
    print(f"Zero total files: {files_scanned}/{total_files} = {progress:.1f}%")
    
    # Zero files scanned
    total_files = 100
    files_scanned = 0
    progress = (files_scanned / total_files) * 100 if total_files > 0 else 0
    print(f"Zero files scanned: {files_scanned}/{total_files} = {progress:.1f}%")
    
    # All files scanned
    total_files = 100
    files_scanned = 100
    progress = (files_scanned / total_files) * 100 if total_files > 0 else 0
    print(f"All files scanned: {files_scanned}/{total_files} = {progress:.1f}%")

if __name__ == "__main__":
    test_progress_calculation() 