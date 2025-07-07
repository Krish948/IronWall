#!/usr/bin/env python3
"""
IronWall Antivirus Launcher
Simple launcher script with error handling and status messages
"""

import sys
import os
import traceback
from pathlib import Path

def main():
    """Launch IronWall Antivirus with proper error handling"""
    print("🛡️  IronWall Antivirus - Starting...")
    print("=" * 50)
    
    try:
        # Add current directory to Python path
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        # Import and run main application
        from main import main as run_ironwall
        run_ironwall()
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        return 1
        
    except Exception as e:
        print(f"❌ Error starting IronWall: {e}")
        print("\nFull error details:")
        traceback.print_exc()
        return 1
    
    print("\n✅ IronWall Antivirus has been closed.")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 