"""
IronWall Antivirus - Main Entry Point
Professional antivirus solution with modular architecture
"""

import sys
from ui.main_window import IronWallMainWindow
from core.scanner import IronWallScanner
from utils.system_monitor import SystemMonitor
from utils.threat_database import ThreatDatabase

def main():
    """Main entry point for IronWall Antivirus"""
    try:
        # Initialize core components
        threat_db = ThreatDatabase()
        scanner = IronWallScanner(threat_db)
        system_monitor = SystemMonitor()
        
        # Launch the main application window
        app = IronWallMainWindow(scanner, system_monitor, threat_db)
        app.run()
        
    except Exception as e:
        print(f"Error starting IronWall Antivirus: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()