"""
IronWall Antivirus - Data Reset Utility
Comprehensive data reset functionality for factory defaults
"""

import os
import shutil
import json
import glob
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
import threading

class DataResetManager:
    """Manages comprehensive data reset operations for IronWall Antivirus"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent
        self.reset_log = []
        
        # Define all data files and directories to reset
        self.data_files = [
            "ironwall_settings.json",
            "threat_database.json", 
            "scan_history.json",
            "system_logs.json",
            "scheduled_scans.json",
            "network_rules.json"
        ]
        
        self.data_directories = [
            "quarantine",
            "backups",
            "restore_points"
        ]
        
        self.diagnostic_files = [
            "ironwall_diagnostic_*.json"
        ]
        
        # Backup directory for reset operations
        self.backup_dir = self.base_dir / "reset_backups"
        
    def create_backup(self) -> bool:
        """Create a backup of current data before reset"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"pre_reset_backup_{timestamp}"
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup data files
            for file_name in self.data_files:
                file_path = self.base_dir / file_name
                if file_path.exists():
                    shutil.copy2(file_path, backup_path / file_name)
                    self.reset_log.append(f"Backed up: {file_name}")
            
            # Backup data directories
            for dir_name in self.data_directories:
                dir_path = self.base_dir / dir_name
                if dir_path.exists():
                    backup_dir = backup_path / dir_name
                    shutil.copytree(dir_path, backup_dir, dirs_exist_ok=True)
                    self.reset_log.append(f"Backed up directory: {dir_name}")
            
            # Backup diagnostic files
            for pattern in self.diagnostic_files:
                for file_path in self.base_dir.glob(pattern):
                    shutil.copy2(file_path, backup_path / file_path.name)
                    self.reset_log.append(f"Backed up diagnostic: {file_path.name}")
            
            self.reset_log.append(f"Backup created at: {backup_path}")
            return True
            
        except Exception as e:
            self.reset_log.append(f"Backup failed: {e}")
            return False
    
    def reset_settings(self) -> bool:
        """Reset settings to factory defaults"""
        try:
            from .settings_manager import SettingsManager
            
            settings_manager = SettingsManager(str(self.base_dir / "ironwall_settings.json"))
            settings_manager.reset_to_defaults()
            
            self.reset_log.append("Settings reset to factory defaults")
            return True
            
        except Exception as e:
            self.reset_log.append(f"Settings reset failed: {e}")
            return False
    
    def reset_threat_database(self) -> bool:
        """Reset threat database to empty state"""
        try:
            from .threat_database import ThreatDatabase
            
            threat_db = ThreatDatabase(str(self.base_dir / "threat_database.json"))
            threat_db.clear_database()
            
            self.reset_log.append("Threat database cleared")
            return True
            
        except Exception as e:
            self.reset_log.append(f"Threat database reset failed: {e}")
            return False
    
    def reset_quarantine(self) -> bool:
        """Reset quarantine database and clear quarantined files"""
        try:
            quarantine_dir = self.base_dir / "quarantine"
            if quarantine_dir.exists():
                # Remove all files except the database file
                for file_path in quarantine_dir.glob("*"):
                    if file_path.is_file() and file_path.name != "quarantine_db.json":
                        file_path.unlink()
                        self.reset_log.append(f"Removed quarantined file: {file_path.name}")
                
                # Clear quarantine database
                db_file = quarantine_dir / "quarantine_db.json"
                if db_file.exists():
                    with open(db_file, 'w') as f:
                        json.dump({}, f)
                    self.reset_log.append("Quarantine database cleared")
            
            return True
            
        except Exception as e:
            self.reset_log.append(f"Quarantine reset failed: {e}")
            return False
    
    def reset_scan_history(self) -> bool:
        """Reset scan history"""
        try:
            history_file = self.base_dir / "scan_history.json"
            if history_file.exists():
                with open(history_file, 'w') as f:
                    json.dump([], f)
                self.reset_log.append("Scan history cleared")
            
            return True
            
        except Exception as e:
            self.reset_log.append(f"Scan history reset failed: {e}")
            return False
    
    def reset_system_logs(self) -> bool:
        """Reset system logs"""
        try:
            logs_file = self.base_dir / "system_logs.json"
            if logs_file.exists():
                with open(logs_file, 'w') as f:
                    json.dump([], f)
                self.reset_log.append("System logs cleared")
            
            return True
            
        except Exception as e:
            self.reset_log.append(f"System logs reset failed: {e}")
            return False
    
    def reset_scheduled_scans(self) -> bool:
        """Reset scheduled scans"""
        try:
            scans_file = self.base_dir / "scheduled_scans.json"
            if scans_file.exists():
                with open(scans_file, 'w') as f:
                    json.dump([], f)
                self.reset_log.append("Scheduled scans cleared")
            
            return True
            
        except Exception as e:
            self.reset_log.append(f"Scheduled scans reset failed: {e}")
            return False
    
    def reset_network_rules(self) -> bool:
        """Reset network rules to defaults"""
        try:
            rules_file = self.base_dir / "network_rules.json"
            default_rules = {
                "rules": [],
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            with open(rules_file, 'w') as f:
                json.dump(default_rules, f, indent=2)
            
            self.reset_log.append("Network rules reset to defaults")
            return True
            
        except Exception as e:
            self.reset_log.append(f"Network rules reset failed: {e}")
            return False
    
    def reset_backups(self) -> bool:
        """Clear backup directories"""
        try:
            backup_dir = self.base_dir / "backups"
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
                backup_dir.mkdir(exist_ok=True)
                self.reset_log.append("Backup directories cleared")
            
            return True
            
        except Exception as e:
            self.reset_log.append(f"Backup reset failed: {e}")
            return False
    
    def reset_restore_points(self) -> bool:
        """Clear restore points"""
        try:
            restore_dir = self.base_dir / "restore_points"
            if restore_dir.exists():
                shutil.rmtree(restore_dir)
                restore_dir.mkdir(exist_ok=True)
                self.reset_log.append("Restore points cleared")
            
            return True
            
        except Exception as e:
            self.reset_log.append(f"Restore points reset failed: {e}")
            return False
    
    def clear_diagnostic_files(self) -> bool:
        """Clear diagnostic report files"""
        try:
            cleared_count = 0
            for pattern in self.diagnostic_files:
                for file_path in self.base_dir.glob(pattern):
                    file_path.unlink()
                    cleared_count += 1
                    self.reset_log.append(f"Removed diagnostic file: {file_path.name}")
            
            if cleared_count > 0:
                self.reset_log.append(f"Cleared {cleared_count} diagnostic files")
            
            return True
            
        except Exception as e:
            self.reset_log.append(f"Diagnostic files clear failed: {e}")
            return False
    
    def reset_all_data(self, create_backup: bool = True) -> Dict[str, bool]:
        """Reset all IronWall data to factory defaults"""
        results = {}
        self.reset_log.clear()
        
        try:
            # Create backup if requested
            if create_backup:
                results['backup'] = self.create_backup()
            
            # Reset all data components
            results['settings'] = self.reset_settings()
            results['threat_database'] = self.reset_threat_database()
            results['quarantine'] = self.reset_quarantine()
            results['scan_history'] = self.reset_scan_history()
            results['system_logs'] = self.reset_system_logs()
            results['scheduled_scans'] = self.reset_scheduled_scans()
            results['network_rules'] = self.reset_network_rules()
            results['backups'] = self.reset_backups()
            results['restore_points'] = self.reset_restore_points()
            results['diagnostic_files'] = self.clear_diagnostic_files()
            
            self.reset_log.append("Data reset completed")
            
        except Exception as e:
            self.reset_log.append(f"Data reset failed: {e}")
            results['overall'] = False
        
        return results
    
    def get_reset_log(self) -> List[str]:
        """Get the reset operation log"""
        return self.reset_log.copy()
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """Restore data from a backup"""
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                raise FileNotFoundError(f"Backup directory not found: {backup_path}")
            
            # Restore data files
            for file_name in self.data_files:
                backup_file = backup_dir / file_name
                if backup_file.exists():
                    target_file = self.base_dir / file_name
                    shutil.copy2(backup_file, target_file)
                    self.reset_log.append(f"Restored: {file_name}")
            
            # Restore data directories
            for dir_name in self.data_directories:
                backup_data_dir = backup_dir / dir_name
                target_dir = self.base_dir / dir_name
                if backup_data_dir.exists():
                    if target_dir.exists():
                        shutil.rmtree(target_dir)
                    shutil.copytree(backup_data_dir, target_dir)
                    self.reset_log.append(f"Restored directory: {dir_name}")
            
            self.reset_log.append(f"Data restored from: {backup_path}")
            return True
            
        except Exception as e:
            self.reset_log.append(f"Restore failed: {e}")
            return False


class DataResetDialog:
    """GUI dialog for data reset operations"""
    
    def __init__(self, parent, data_reset_manager: DataResetManager):
        self.parent = parent
        self.data_reset_manager = data_reset_manager
        self.dialog = None
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready to reset data")
        
    def show_dialog(self):
        """Show the data reset dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("IronWall Data Reset")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔄 IronWall Data Reset", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Warning message
        warning_frame = ttk.LabelFrame(main_frame, text="⚠️ Warning", padding="10")
        warning_frame.pack(fill='x', pady=(0, 20))
        
        warning_text = ("This will reset ALL IronWall data to factory defaults:\n\n"
                       "• All settings will be reset to defaults\n"
                       "• Scan history will be cleared\n"
                       "• Quarantine will be emptied\n"
                       "• Threat database will be cleared\n"
                       "• All logs will be cleared\n"
                       "• Scheduled scans will be removed\n"
                       "• Backup data will be cleared\n\n"
                       "This action cannot be undone!")
        
        warning_label = ttk.Label(warning_frame, text=warning_text, 
                                 foreground="red", justify='left')
        warning_label.pack()
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.pack(fill='x', pady=(0, 20))
        
        self.backup_var = tk.BooleanVar(value=True)
        backup_check = ttk.Checkbutton(options_frame, 
                                      text="Create backup before reset", 
                                      variable=self.backup_var)
        backup_check.pack(anchor='w')
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.pack(fill='x', pady=(0, 20))
        
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.pack(anchor='w', pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.pack(fill='x', pady=(0, 5))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        self.reset_button = ttk.Button(button_frame, text="Reset All Data", 
                                      command=self.start_reset, style="danger.TButton")
        self.reset_button.pack(side='left', padx=(0, 10))
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", 
                                       command=self.dialog.destroy)
        self.cancel_button.pack(side='right')
        
    def start_reset(self):
        """Start the data reset process"""
        if not messagebox.askyesno("Confirm Reset", 
                                  "Are you absolutely sure you want to reset all data?\n\n"
                                  "This action cannot be undone!"):
            return
        
        # Disable buttons
        self.reset_button.config(state='disabled')
        self.cancel_button.config(state='disabled')
        
        # Start reset in background thread
        reset_thread = threading.Thread(target=self.perform_reset)
        reset_thread.daemon = True
        reset_thread.start()
    
    def perform_reset(self):
        """Perform the actual reset operation"""
        try:
            self.status_var.set("Creating backup...")
            self.progress_var.set(10)
            self.dialog.update()
            
            # Perform reset
            results = self.data_reset_manager.reset_all_data(
                create_backup=self.backup_var.get()
            )
            
            self.progress_var.set(100)
            self.status_var.set("Reset completed!")
            
            # Show results
            self.show_results(results)
            
        except Exception as e:
            self.status_var.set(f"Reset failed: {e}")
            messagebox.showerror("Reset Error", f"Data reset failed:\n{e}")
        finally:
            # Re-enable buttons
            self.reset_button.config(state='normal')
            self.cancel_button.config(state='normal')
    
    def show_results(self, results: Dict[str, bool]):
        """Show reset results"""
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        result_text = f"Reset completed!\n\n"
        result_text += f"Successful operations: {success_count}/{total_count}\n\n"
        
        for operation, success in results.items():
            status = "✅" if success else "❌"
            result_text += f"{status} {operation.replace('_', ' ').title()}\n"
        
        if success_count == total_count:
            messagebox.showinfo("Reset Complete", result_text)
            self.dialog.destroy()
        else:
            messagebox.showwarning("Reset Partially Complete", result_text) 