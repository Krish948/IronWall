"""
IronWall Antivirus - Main Entry Point
Professional antivirus solution with modular architecture
"""

import sys
import os
import json
import argparse
from ui.main_window import IronWallMainWindow
from core.scanner import IronWallScanner
from utils.system_monitor import SystemMonitor
from utils.threat_database import ThreatDatabase
import tkinter as tk
from tkinter import messagebox

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'ironwall_settings.json')

def load_settings(settings_path=SETTINGS_PATH):
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {}

def parse_args():
    parser = argparse.ArgumentParser(description="IronWall Antivirus")
    parser.add_argument('--safe-mode', action='store_true', help='Start in safe mode (minimal features)')
    parser.add_argument('--no-gui', action='store_true', help='Run without GUI')
    return parser.parse_args()

def show_error_dialog(message):
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("IronWall Antivirus - Startup Error", message)
        root.destroy()
    except Exception:
        print(message)

def initialize_components(settings, args):
    threat_db = ThreatDatabase()
    scanner = IronWallScanner(threat_db)
    system_monitor = SystemMonitor()
    return scanner, system_monitor, threat_db

def main():
    args = parse_args()
    settings = load_settings()
    try:
        scanner, system_monitor, threat_db = initialize_components(settings, args)
        if args.no_gui:
            print("IronWall Antivirus started in no-GUI mode.")
            sys.exit(0)
        app = IronWallMainWindow(scanner, system_monitor, threat_db)
        app.run()
    except Exception as e:
        show_error_dialog(f"Error starting IronWall Antivirus:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()