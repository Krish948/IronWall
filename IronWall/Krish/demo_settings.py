"""
IronWall Antivirus - Settings Panel Demo
Comprehensive demonstration of all settings features
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ui.settings_panel import SettingsPanel
from utils.settings_manager import get_settings_manager
import json
from datetime import datetime

class SettingsDemo:
    """Demo application for IronWall Settings Panel"""
    
    def __init__(self):
        self.root = ttk.Window(themename="flatly")
        self.root.title("🛡️ IronWall Antivirus - Settings Panel Demo")
        self.root.geometry("1400x900")
        self.root.state('zoomed')
        
        self.settings_manager = get_settings_manager()
        self.create_demo_interface()
        
    def create_demo_interface(self):
        """Create the demo interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(header_frame, text="🛡️ IronWall Antivirus", 
                 font=("Segoe UI", 28, "bold")).pack(side=LEFT)
        ttk.Label(header_frame, text="Settings Panel Demo", 
                 font=("Segoe UI", 16), foreground="gray").pack(side=LEFT, padx=(10, 0))
        
        # Demo controls
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side=RIGHT)
        
        ttk.Button(controls_frame, text="📊 Show Current Settings", 
                  style="info.TButton", command=self.show_current_settings).pack(side=LEFT, padx=5)
        ttk.Button(controls_frame, text="🔄 Reset to Defaults", 
                  style="warning.TButton", command=self.reset_to_defaults).pack(side=LEFT, padx=5)
        ttk.Button(controls_frame, text="💾 Export Settings", 
                  style="success.TButton", command=self.export_demo_settings).pack(side=LEFT, padx=5)
        
        # Create settings panel
        self.settings_panel = SettingsPanel(main_frame, self)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=X, pady=(20, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready - Settings Panel Loaded", 
                                     font=("Segoe UI", 10))
        self.status_label.pack(side=LEFT)
        
        ttk.Label(status_frame, text=f"Demo started at {datetime.now().strftime('%H:%M:%S')}", 
                 font=("Segoe UI", 10), foreground="gray").pack(side=RIGHT)
        
    def show_current_settings(self):
        """Show current settings in a popup"""
        settings = self.settings_manager.get_all_settings()
        
        # Create popup window
        popup = ttk.Toplevel(self.root)
        popup.title("Current Settings")
        popup.geometry("800x600")
        
        # Create scrolled text widget
        text_frame = ttk.Frame(popup)
        text_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Insert formatted settings
        formatted_settings = json.dumps(settings, indent=2, ensure_ascii=False)
        text_widget.insert(tk.END, f"Current IronWall Settings:\n")
        text_widget.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")
        text_widget.insert(tk.END, formatted_settings)
        
        text_widget.config(state=tk.DISABLED)
        
        # Add close button
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)
        
    def reset_to_defaults(self):
        """Reset settings to defaults"""
        if tk.messagebox.askyesno("Reset Settings", 
                                 "This will reset all settings to factory defaults.\nContinue?"):
            self.settings_manager.reset_to_defaults()
            tk.messagebox.showinfo("Success", "Settings reset to defaults!")
            self.status_label.config(text="Settings reset to defaults")
            
    def export_demo_settings(self):
        """Export current settings"""
        from tkinter import filedialog
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Settings"
        )
        
        if filepath:
            if self.settings_manager.export_settings(filepath):
                tk.messagebox.showinfo("Success", f"Settings exported to:\n{filepath}")
                self.status_label.config(text=f"Settings exported to {filepath}")
            else:
                tk.messagebox.showerror("Error", "Failed to export settings")
                
    def run(self):
        """Run the demo"""
        self.root.mainloop()

def main():
    """Main function"""
    print("🛡️ IronWall Antivirus - Settings Panel Demo")
    print("=" * 50)
    print("This demo showcases the comprehensive settings panel with:")
    print("• 10 major configuration categories")
    print("• Real-time protection settings")
    print("• Scan control and exclusions")
    print("• Scheduling and notifications")
    print("• Performance tuning")
    print("• Privacy and security controls")
    print("• Appearance customization")
    print("• Advanced backup features")
    print("=" * 50)
    
    demo = SettingsDemo()
    demo.run()

if __name__ == "__main__":
    main() 