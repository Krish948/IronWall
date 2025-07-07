"""
IronWall Antivirus - Color Palette Test
Demonstrates the new color palette features
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ui.settings_panel import SettingsPanel
from utils.settings_manager import get_settings_manager
from utils.color_palette import get_color_palette
from ui.theme_preview import ThemeSelectorWidget, ColorPickerWidget, ThemePreviewWidget

class ColorPaletteTest:
    """Test application for the new color palette features"""
    
    def __init__(self):
        self.root = ttk.Window(themename="flatly")
        self.root.title("🎨 IronWall Color Palette Test")
        self.root.geometry("1400x900")
        self.root.state('zoomed')
        
        self.settings_manager = get_settings_manager()
        self.color_palette = get_color_palette()
        
        self.create_test_interface()
        
    def create_test_interface(self):
        """Create the test interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(header_frame, text="🎨 IronWall Color Palette Test", 
                 font=("Segoe UI", 28, "bold")).pack(side=LEFT)
        ttk.Label(header_frame, text="Testing the new color palette features", 
                 font=("Segoe UI", 16), foreground="gray").pack(side=LEFT, padx=(10, 0))
        
        # Test controls
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side=RIGHT)
        
        ttk.Button(controls_frame, text="📊 Show All Themes", 
                  style="info.TButton", command=self.show_all_themes).pack(side=LEFT, padx=5)
        ttk.Button(controls_frame, text="🔄 Reset Settings", 
                  style="warning.TButton", command=self.reset_settings).pack(side=LEFT, padx=5)
        ttk.Button(controls_frame, text="🎨 Open Settings", 
                  style="success.TButton", command=self.open_settings).pack(side=LEFT, padx=5)
        
        # Create notebook for different test sections
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=BOTH, expand=True)
        
        # Test different sections
        self.create_theme_selector_test()
        self.create_color_picker_test()
        self.create_preview_test()
        self.create_settings_test()
        
    def create_theme_selector_test(self):
        """Test the theme selector widget"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🎨 Theme Selector")
        
        # Title
        ttk.Label(frame, text="Theme Selector Widget Test", 
                 font=("Segoe UI", 18, "bold")).pack(pady=10)
        
        # Theme selector
        self.theme_selector = ThemeSelectorWidget(
            frame, 
            self.color_palette.get_all_themes(),
            on_theme_selected=self.on_theme_selected
        )
        self.theme_selector.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Info
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill=X, padx=20, pady=10)
        
        self.selected_theme_label = ttk.Label(info_frame, text="Selected: None", 
                                             font=("Segoe UI", 12))
        self.selected_theme_label.pack(side=LEFT)
        
        ttk.Button(info_frame, text="Get Selected Theme", 
                  command=self.get_selected_theme).pack(side=RIGHT)
    
    def create_color_picker_test(self):
        """Test the color picker widget"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🖌 Color Picker")
        
        # Title
        ttk.Label(frame, text="Color Picker Widget Test", 
                 font=("Segoe UI", 18, "bold")).pack(pady=10)
        
        # Color pickers
        picker_frame = ttk.Frame(frame)
        picker_frame.pack(fill=X, padx=20, pady=20)
        
        self.color_pickers = {}
        color_options = [
            ("primary_accent", "Primary Accent", "#1976D2"),
            ("secondary_accent", "Secondary Accent", "#42A5F5"),
            ("background", "Background", "#F7F9FB"),
            ("surface", "Surface", "#FFFFFF"),
            ("text_primary", "Primary Text", "#222B45"),
            ("text_secondary", "Secondary Text", "#6B778C"),
            ("border", "Border", "#D1D9E6")
        ]
        
        for color_key, color_label, default_color in color_options:
            picker = ColorPickerWidget(
                picker_frame, 
                color_label, 
                default_color,
                on_color_changed=self.on_color_changed
            )
            picker.pack(fill=X, pady=5)
            self.color_pickers[color_key] = picker
        
        # Test buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=X, padx=20, pady=10)
        
        ttk.Button(button_frame, text="💾 Save as Custom Theme", 
                  style="success.TButton",
                  command=self.save_test_theme).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Reset Colors", 
                  style="warning.TButton",
                  command=self.reset_colors).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="🎨 Apply to Preview", 
                  style="info.TButton",
                  command=self.apply_to_preview).pack(side=LEFT, padx=5)
    
    def create_preview_test(self):
        """Test the theme preview widget"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🖥 Preview")
        
        # Title
        ttk.Label(frame, text="Theme Preview Widget Test", 
                 font=("Segoe UI", 18, "bold")).pack(pady=10)
        
        # Preview area
        preview_frame = ttk.Frame(frame)
        preview_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Sample theme data
        sample_theme = {
            "name": "Test Theme",
            "description": "A sample theme for testing",
            "primary_accent": "#1976D2",
            "secondary_accent": "#42A5F5",
            "background": "#F7F9FB",
            "surface": "#FFFFFF",
            "text_primary": "#222B45",
            "text_secondary": "#6B778C",
            "border": "#D1D9E6",
            "success": "#43A047",
            "warning": "#FFA000",
            "danger": "#D32F2F"
        }
        
        self.preview_widget = ThemePreviewWidget(preview_frame, sample_theme, size=300)
        self.preview_widget.pack(fill=BOTH, expand=True)
        
        # Preview controls
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=X, padx=20, pady=10)
        
        ttk.Button(control_frame, text="🔄 Update Preview", 
                  command=self.update_preview).pack(side=LEFT, padx=5)
        ttk.Button(control_frame, text="🎨 Random Colors", 
                  command=self.random_colors).pack(side=LEFT, padx=5)
    
    def create_settings_test(self):
        """Test the settings panel"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="⚙️ Settings")
        
        # Title
        ttk.Label(frame, text="Settings Panel Test", 
                 font=("Segoe UI", 18, "bold")).pack(pady=10)
        
        # Settings panel
        self.settings_panel = SettingsPanel(frame, self)
        self.settings_panel.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
    
    def on_theme_selected(self, theme_name: str):
        """Handle theme selection"""
        self.selected_theme_label.config(text=f"Selected: {theme_name}")
        print(f"Theme selected: {theme_name}")
    
    def on_color_changed(self, color_name: str, color_value: str):
        """Handle color change"""
        print(f"Color changed: {color_name} = {color_value}")
    
    def get_selected_theme(self):
        """Get the selected theme"""
        theme_name = self.theme_selector.get_selected_theme()
        print(f"Current selected theme: {theme_name}")
    
    def save_test_theme(self):
        """Save current colors as a test theme"""
        colors = {}
        for color_key, picker in self.color_pickers.items():
            colors[color_key] = picker.get_color()
        
        if self.color_palette.create_custom_theme("Test Theme", colors, "Test theme from color picker"):
            print("Test theme saved successfully!")
        else:
            print("Failed to save test theme")
    
    def reset_colors(self):
        """Reset colors to defaults"""
        default_colors = {
            "primary_accent": "#1976D2",
            "secondary_accent": "#42A5F5",
            "background": "#F7F9FB",
            "surface": "#FFFFFF",
            "text_primary": "#222B45",
            "text_secondary": "#6B778C",
            "border": "#D1D9E6"
        }
        
        for color_key, picker in self.color_pickers.items():
            picker.set_color(default_colors.get(color_key, "#000000"))
    
    def apply_to_preview(self):
        """Apply current colors to preview"""
        colors = {}
        for color_key, picker in self.color_pickers.items():
            colors[color_key] = picker.get_color()
        
        # Update preview widget
        if hasattr(self, 'preview_widget'):
            self.preview_widget.destroy()
        
        theme_data = {
            "name": "Custom Preview",
            "description": "Custom colors from picker",
            **colors,
            "success": "#43A047",
            "warning": "#FFA000",
            "danger": "#D32F2F"
        }
        
        self.preview_widget = ThemePreviewWidget(self.preview_widget.master, theme_data, size=300)
        self.preview_widget.pack(fill=BOTH, expand=True)
    
    def update_preview(self):
        """Update the preview with current colors"""
        self.apply_to_preview()
    
    def random_colors(self):
        """Generate random colors for testing"""
        import random
        
        def random_hex():
            return f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"
        
        for picker in self.color_pickers.values():
            picker.set_color(random_hex())
    
    def show_all_themes(self):
        """Show all available themes"""
        themes = self.color_palette.get_all_themes()
        print(f"Available themes: {list(themes.keys())}")
        
        for name, theme in themes.items():
            print(f"\n{name}: {theme.get('description', 'No description')}")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        self.settings_manager.reset_to_defaults()
        print("Settings reset to defaults")
    
    def open_settings(self):
        """Open settings in a new window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("IronWall Settings")
        settings_window.geometry("1200x800")
        
        settings_panel = SettingsPanel(settings_window, self)
    
    def run(self):
        """Run the test application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ColorPaletteTest()
    app.run() 