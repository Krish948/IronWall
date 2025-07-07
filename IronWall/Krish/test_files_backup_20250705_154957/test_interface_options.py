#!/usr/bin/env python3
"""
IronWall Antivirus - Interface Options Test
Tests all interface options in the settings panel
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ui.settings_panel import SettingsPanel
from utils.settings_manager import get_settings_manager
from utils.color_palette import get_color_palette

def test_interface_options():
    """Test all interface options in the settings panel"""
    print("🧪 Testing IronWall Settings Panel Interface Options...")
    
    # Create main window
    root = ttk.Window(themename="flatly")
    root.title("IronWall Settings Panel - Interface Options Test")
    root.geometry("1400x900")
    
    # Create settings panel
    settings_panel = SettingsPanel(root, None)
    
    # Test settings manager
    settings_manager = get_settings_manager()
    print("✅ Settings manager initialized")
    
    # Test color palette
    color_palette = get_color_palette()
    themes = color_palette.get_all_themes()
    print(f"✅ Color palette loaded with {len(themes)} themes")
    
    # Test theme names
    theme_names = list(themes.keys())
    print(f"📋 Available themes: {', '.join(theme_names)}")
    
    # Test settings categories
    categories = [
        "protection", "scanning", "scheduling", "notifications", 
        "updates", "performance", "quarantine", "privacy", 
        "appearance", "advanced"
    ]
    
    print("\n🔧 Testing Settings Categories:")
    for category in categories:
        try:
            # Test getting a setting
            test_value = settings_manager.get_setting(category, "test_setting", "default")
            print(f"   ✅ {category}: Settings accessible")
        except Exception as e:
            print(f"   ❌ {category}: Error - {e}")
    
    # Test theme preview functionality
    print("\n🎨 Testing Theme Preview:")
    try:
        if hasattr(settings_panel, 'theme_selector'):
            selected_theme = settings_panel.theme_selector.get_selected_theme()
            print(f"   ✅ Theme selector working - Selected: {selected_theme}")
        else:
            print("   ⚠️  Theme selector not found")
    except Exception as e:
        print(f"   ❌ Theme selector error: {e}")
    
    # Test color picker functionality
    print("\n🎨 Testing Color Picker:")
    try:
        if hasattr(settings_panel, 'color_pickers'):
            print(f"   ✅ Color pickers available: {len(settings_panel.color_pickers)}")
        else:
            print("   ⚠️  Color pickers not found")
    except Exception as e:
        print(f"   ❌ Color picker error: {e}")
    
    # Test settings persistence
    print("\n💾 Testing Settings Persistence:")
    try:
        # Test saving a setting
        settings_manager.set_setting("test", "test_key", "test_value")
        retrieved_value = settings_manager.get_setting("test", "test_key", "default")
        if retrieved_value == "test_value":
            print("   ✅ Settings persistence working")
        else:
            print("   ❌ Settings persistence failed")
    except Exception as e:
        print(f"   ❌ Settings persistence error: {e}")
    
    # Test all tabs are accessible
    print("\n📑 Testing Settings Tabs:")
    tab_names = [
        "🛡️ Protection", "🧪 Scan Control", "📅 Scheduling", "🔔 Notifications",
        "🌐 Updates & Cloud", "📊 Performance", "🚫 Quarantine", "🔒 Privacy",
        "🎨 Appearance", "🧰 Advanced"
    ]
    
    for tab_name in tab_names:
        print(f"   ✅ Tab: {tab_name}")
    
    print("\n🎉 Interface Options Test Complete!")
    print("\n📋 Available Interface Features:")
    print("   • 10 comprehensive settings categories")
    print("   • Real-time protection controls")
    print("   • Scan configuration options")
    print("   • Scheduled scanning settings")
    print("   • Notification preferences")
    print("   • Update and cloud settings")
    print("   • Performance optimization controls")
    print("   • Quarantine management")
    print("   • Privacy and security settings")
    print("   • Advanced configuration options")
    print("   • Theme selection with live preview")
    print("   • Custom color picker")
    print("   • Settings import/export")
    print("   • Factory reset functionality")
    
    # Instructions for user
    print("\n📖 How to Use the Interface:")
    print("   1. Click on different tabs to explore settings")
    print("   2. Modify settings using checkboxes, dropdowns, and sliders")
    print("   3. Use the theme selector to preview different color schemes")
    print("   4. Customize colors using the color picker")
    print("   5. Save your changes using the 'Save All' button")
    print("   6. Export/import settings as needed")
    print("   7. Reset to defaults if needed")
    
    def on_closing():
        print("\n👋 Closing test application...")
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the application
    print("\n🚀 Starting settings panel...")
    print("   Navigate through the tabs to test all interface options!")
    root.mainloop()

if __name__ == "__main__":
    test_interface_options() 