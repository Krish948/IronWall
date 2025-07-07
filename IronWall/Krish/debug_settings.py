"""
Debug script to identify settings panel issues
"""

import sys
import traceback

def debug_settings_panel():
    """Debug the settings panel step by step"""
    try:
        print("Step 1: Importing ttkbootstrap...")
        import ttkbootstrap as ttk
        print("✓ ttkbootstrap imported successfully")
        
        print("Step 2: Creating root window...")
        root = ttk.Window(themename='flatly')
        root.title("Debug Settings Panel")
        root.geometry("1000x700")
        print("✓ Root window created")
        
        print("Step 3: Importing settings manager...")
        from utils.settings_manager import get_settings_manager
        settings_manager = get_settings_manager()
        print("✓ Settings manager created")
        
        print("Step 4: Importing settings panel...")
        from ui.settings_panel import SettingsPanel
        print("✓ Settings panel imported")
        
        print("Step 5: Creating settings panel...")
        settings_panel = SettingsPanel(root, None)
        print("✓ Settings panel created")
        
        print("Step 6: Adding close button...")
        close_btn = ttk.Button(root, text="Close", command=root.destroy, style="danger.TButton")
        close_btn.pack(pady=10)
        print("✓ Close button added")
        
        print("Step 7: Starting mainloop...")
        print("If you can see the settings panel with tabs, it's working!")
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_settings_panel() 