"""
IronWall Antivirus - Settings Panel
Comprehensive settings interface with all major antivirus configurations
"""

import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from utils.settings_manager import get_settings_manager
from utils.color_palette import get_color_palette
from utils import scan_history
from ui.theme_preview import ThemeSelectorWidget, ColorPickerWidget
import sys

class SettingsPanel:
    """Comprehensive settings panel for IronWall Antivirus"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.settings_manager = get_settings_manager()
        
        # Create the main settings window
        self.create_settings_window()
        
    def create_settings_window(self):
        """Create the main settings window with notebook tabs"""
        # Create main container
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(header_frame, text="⚙️ IronWall Settings", 
                 font=("Segoe UI", 24, "bold")).pack(side=LEFT)
        
        # Action buttons
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side=RIGHT)
        
        ttk.Button(btn_frame, text="💾 Save All", style="success.TButton",
                  command=self.save_all_settings).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Reset", style="warning.TButton",
                  command=self.reset_settings).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="📤 Export", style="info.TButton",
                  command=self.export_settings).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="📥 Import", style="info.TButton",
                  command=self.import_settings).pack(side=LEFT, padx=5)
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=BOTH, expand=True)
        
        # Create all settings tabs
        self.create_protection_tab()
        self.create_scanning_tab()
        self.create_scheduling_tab()
        self.create_notifications_tab()
        self.create_updates_tab()
        self.create_performance_tab()
        self.create_quarantine_tab()
        self.create_privacy_tab()
        self.create_appearance_tab()
        
    def create_protection_tab(self):
        """Create Protection Settings tab"""
        frame = ttk.Frame(self.notebook)
        frame.pack(fill='both', expand=True)
        self.notebook.add(frame, text="🛡️ Protection")
        
        # Real-time Protection
        self.create_section(frame, "Real-time Protection", [
            ("real_time_protection", "Enable Real-time Protection", "protection", "checkbox"),
            ("firewall_protection", "Enable Firewall Protection", "protection", "checkbox"),
            ("usb_protection", "USB & External Drive Protection", "protection", "checkbox"),
            ("safe_browsing", "Safe Browsing Protection", "protection", "checkbox"),
            ("webcam_microphone_control", "Webcam & Microphone Access Control", "protection", "checkbox"),
        ])
        
        # Heuristic Scanning
        self.create_section(frame, "Heuristic Scanning", [
            ("heuristic_scanning", "Heuristic Level", "protection", "combobox", 
             ["Low", "Medium", "High"])
        ])
        
    def create_scanning_tab(self):
        """Create Scanning Control tab"""
        frame = ttk.Frame(self.notebook)
        frame.pack(fill='both', expand=True)
        self.notebook.add(frame, text="🧪 Scan Control")
        
        # Scan Types
        self.create_section(frame, "Scan Configuration", [
            ("default_scan_type", "Default Scan Type", "scanning", "combobox",
             ["Quick", "Full", "Deep", "Custom"]),
            ("scan_compressed_files", "Scan Compressed Files", "scanning", "checkbox"),
            ("scan_startup_programs", "Scan Startup Programs", "scanning", "checkbox"),
        ])
        
        # Exclusions
        self.create_exclusions_section(frame)
        
    def create_scheduling_tab(self):
        """Create Scan Scheduling tab"""
        frame = ttk.Frame(self.notebook)
        frame.pack(fill='both', expand=True)
        self.notebook.add(frame, text="📅 Scheduling")
        
        # Scheduled Scans
        self.create_section(frame, "Scheduled Scans", [
            ("enable_scheduled_scans", "Enable Scheduled Scans", "scheduling", "checkbox"),
            ("scan_frequency", "Scan Frequency", "scheduling", "combobox",
             ["Daily", "Weekly", "Monthly"]),
            ("auto_delete_threats", "Auto-delete Threats", "scheduling", "checkbox"),
        ])
        
        # Time Selection
        time_frame = ttk.LabelFrame(frame, text="Scan Time", padding=10)
        time_frame.pack(fill=X, pady=10, padx=10)
        
        self.scan_time_var = tk.StringVar(
            value=self.settings_manager.get_setting("scheduling", "scan_time", "02:00")
        )
        ttk.Label(time_frame, text="Scan Time:").pack(side=LEFT)
        time_entry = ttk.Entry(time_frame, textvariable=self.scan_time_var, width=10)
        time_entry.pack(side=LEFT, padx=10)
        ttk.Label(time_frame, text="(HH:MM format)").pack(side=LEFT)
        
        # Store references to variables
        self.scheduling_enable_var = getattr(self, 'enable_scheduled_scans_var', None)
        self.scan_frequency_var = getattr(self, 'scan_frequency_var', None)
        self.auto_delete_threats_var = getattr(self, 'auto_delete_threats_var', None)
        
    def create_notifications_tab(self):
        """Create Notifications tab"""
        frame = ttk.Frame(self.notebook)
        frame.pack(fill='both', expand=True)
        self.notebook.add(frame, text="🔔 Notifications")
        
        self.create_section(frame, "Notification Settings", [
            ("threat_alerts", "Threat Alerts", "notifications", "checkbox"),
            ("scan_results_summary", "Scan Results Summary", "notifications", "checkbox"),
            ("silent_mode", "Silent Mode (Log-only)", "notifications", "checkbox"),
            ("notification_sound", "Notification Sound", "notifications", "checkbox"),
        ])
        
    def create_updates_tab(self):
        """Create Updates & Cloud tab"""
        frame = ttk.Frame(self.notebook)
        frame.pack(fill='both', expand=True)
        self.notebook.add(frame, text="🌐 Updates & Cloud")
        
        # Auto Updates
        self.create_section(frame, "Automatic Updates", [
            ("auto_update_definitions", "Auto-update Virus Definitions", "updates", "checkbox"),
            ("auto_update_app", "Auto-update Application", "updates", "checkbox"),
            ("cloud_threat_detection", "Cloud Threat Detection", "updates", "checkbox"),
        ])
        
        # Manual Update Button
        update_frame = ttk.Frame(frame)
        update_frame.pack(fill=X, pady=10, padx=10)
        ttk.Button(update_frame, text="🔄 Check for Updates", 
                  style="info.TButton", command=self.check_for_updates).pack()
        
    def create_performance_tab(self):
        """Create Performance Settings tab"""
        frame = ttk.Frame(self.notebook)
        frame.pack(fill='both', expand=True)
        self.notebook.add(frame, text="📊 Performance")
        
        # CPU Usage
        cpu_frame = ttk.LabelFrame(frame, text="CPU Usage Limiter", padding=10)
        cpu_frame.pack(fill=X, pady=10, padx=10)
        
        self.cpu_limit_var = tk.IntVar(
            value=self.settings_manager.get_setting("performance", "cpu_usage_limit", 50)
        )
        ttk.Label(cpu_frame, text="CPU Usage Limit:").pack(side=LEFT)
        cpu_scale = ttk.Scale(cpu_frame, from_=10, to=100, 
                             variable=self.cpu_limit_var, orient=HORIZONTAL)
        cpu_scale.pack(side=LEFT, fill=X, expand=True, padx=10)
        self.cpu_label = ttk.Label(cpu_frame, text=f"{self.cpu_limit_var.get()}%")
        self.cpu_label.pack(side=LEFT)
        
        # Performance Options
        self.create_section(frame, "Performance Options", [
            ("ram_optimization", "RAM Optimization", "performance", "checkbox"),
            ("background_scan", "Background Scan", "performance", "checkbox"),
            ("idle_scan_mode", "Idle Scan Mode", "performance", "checkbox"),
            ("battery_saver_mode", "Battery Saver Mode", "performance", "checkbox"),
        ])
        
        # Bind CPU scale update
        cpu_scale.configure(command=self.update_cpu_label)
        
    def create_quarantine_tab(self):
        """Create Quarantine & Threat Control tab"""
        frame = ttk.Frame(self.notebook)
        frame.pack(fill='both', expand=True)
        self.notebook.add(frame, text="🧼 Quarantine")
        
        # Auto-delete Settings
        auto_frame = ttk.LabelFrame(frame, text="Auto-delete Settings", padding=10)
        auto_frame.pack(fill=X, pady=10, padx=10)
        
        self.auto_delete_var = tk.IntVar(
            value=self.settings_manager.get_setting("quarantine", "auto_delete_after_days", 30)
        )
        ttk.Label(auto_frame, text="Auto-delete threats after:").pack(side=LEFT)
        delete_spin = ttk.Spinbox(auto_frame, from_=1, to=365, 
                                 textvariable=self.auto_delete_var, width=10)
        delete_spin.pack(side=LEFT, padx=10)
        ttk.Label(auto_frame, text="days").pack(side=LEFT)
        
        # Quarantine Settings
        self.create_section(frame, "Quarantine Settings", [
            ("enable_file_submission", "Enable Manual File Submission", "quarantine", "checkbox"),
        ])
        
        # Quarantine Folder
        folder_frame = ttk.LabelFrame(frame, text="Quarantine Folder", padding=10)
        folder_frame.pack(fill=X, pady=10, padx=10)
        
        self.quarantine_folder_var = tk.StringVar(
            value=self.settings_manager.get_setting("quarantine", "quarantine_folder", "quarantine")
        )
        ttk.Entry(folder_frame, textvariable=self.quarantine_folder_var).pack(side=LEFT, fill=X, expand=True)
        ttk.Button(folder_frame, text="Browse", 
                  command=self.browse_quarantine_folder).pack(side=LEFT, padx=5)
        
        # Max Size
        size_frame = ttk.LabelFrame(frame, text="Maximum Quarantine Size", padding=10)
        size_frame.pack(fill=X, pady=10, padx=10)
        
        self.max_size_var = tk.IntVar(
            value=self.settings_manager.get_setting("quarantine", "max_quarantine_size_mb", 1000)
        )
        ttk.Label(size_frame, text="Max size:").pack(side=LEFT)
        size_spin = ttk.Spinbox(size_frame, from_=100, to=10000, 
                               textvariable=self.max_size_var, width=10)
        size_spin.pack(side=LEFT, padx=10)
        ttk.Label(size_frame, text="MB").pack(side=LEFT)
        
    def create_privacy_tab(self):
        """Create Privacy & Security tab"""
        frame = ttk.Frame(self.notebook)
        frame.pack(fill='both', expand=True)
        self.notebook.add(frame, text="🔒 Privacy")
        
        # Data Sharing
        self.create_section(frame, "Data & Privacy", [
            ("data_sharing", "Anonymous Usage Statistics", "privacy", "checkbox"),
            ("auto_log_clearing", "Auto-log Clearing", "privacy", "checkbox"),
            ("block_telemetry", "Block Telemetry from Other Apps", "privacy", "checkbox"),
        ])
        
        # Log Retention
        log_frame = ttk.LabelFrame(frame, text="Log Retention", padding=10)
        log_frame.pack(fill=X, pady=10, padx=10)
        
        self.log_retention_var = tk.IntVar(
            value=self.settings_manager.get_setting("privacy", "log_retention_days", 30)
        )
        for days in [7, 30, 90]:
            ttk.Radiobutton(log_frame, text=f"{days} days", 
                           variable=self.log_retention_var, value=days).pack(anchor=W)
        
    def create_appearance_tab(self):
        """Create Appearance & Interface tab with enhanced Color Palette features"""
        frame = ttk.Frame(self.notebook)
        frame.pack(fill='both', expand=True)
        self.notebook.add(frame, text="🎨 Appearance")
        
        # Import color palette
        self.color_palette = get_color_palette()
        
        # Create scrollable frame for better layout
        canvas = tk.Canvas(frame)
        v_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")

        # Mouse wheel scrolling (vertical)
        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception as e:
                print(f"Error in mousewheel handler: {e}")
        
        # Mouse wheel scrolling (horizontal with Shift)
        def _on_shift_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception as e:
                print(f"Error in shift mousewheel handler: {e}")
        
        # Windows/Mac/Linux bindings
        scrollable_frame.bind_all("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)
        scrollable_frame.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux scroll up
        scrollable_frame.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux scroll down

        # 1. Predefined Theme Selection
        theme_frame = ttk.LabelFrame(scrollable_frame, text="🎨 Predefined Themes", padding=15)
        theme_frame.pack(fill=X, pady=10, padx=10)
        
        # Theme selector with preview
        self.theme_selector = ThemeSelectorWidget(
            theme_frame, 
            self.color_palette.get_all_themes(),
            on_theme_selected=self.on_theme_selected
        )
        self.theme_selector.pack(fill=BOTH, expand=True, pady=10)
        
        # Set current theme
        current_theme = self.settings_manager.get_setting("appearance", "color_theme", "Light")
        self.theme_selector.set_selected_theme(current_theme)
        
        # 2. Custom Color Palette
        custom_frame = ttk.LabelFrame(scrollable_frame, text="🖌 Custom Color Palette", padding=15)
        custom_frame.pack(fill=X, pady=10, padx=10)
        
        # Enable custom colors toggle
        self.use_custom_colors_var = tk.BooleanVar(
            value=self.settings_manager.get_setting("appearance", "use_custom_colors", False)
        )
        ttk.Checkbutton(custom_frame, text="Enable Custom Colors", 
                       variable=self.use_custom_colors_var,
                       command=self.toggle_custom_colors).pack(anchor=W, pady=(0, 10))
        
        # Custom color pickers
        self.color_pickers = {}
        custom_colors = self.settings_manager.get_setting("appearance", "custom_colors", {})
        
        color_options = [
            ("primary_accent", "Primary Accent"),
            ("secondary_accent", "Secondary Accent"),
            ("background", "Background"),
            ("surface", "Surface"),
            ("text_primary", "Primary Text"),
            ("text_secondary", "Secondary Text"),
            ("border", "Border")
        ]
        
        for color_key, color_label in color_options:
            initial_color = custom_colors.get(color_key, "#000000")
            picker = ColorPickerWidget(
                custom_frame, 
                color_label, 
                initial_color,
                on_color_changed=self.on_custom_color_changed
            )
            picker.pack(fill=X, pady=2)
            self.color_pickers[color_key] = picker
        
        # Custom theme management
        custom_theme_frame = ttk.Frame(custom_frame)
        custom_theme_frame.pack(fill=X, pady=10)
        
        ttk.Button(custom_theme_frame, text="💾 Save as Custom Theme", 
                  style="success.TButton",
                  command=self.save_custom_theme).pack(side=LEFT, padx=5)
        ttk.Button(custom_theme_frame, text="📤 Export Theme", 
                  style="info.TButton",
                  command=self.export_theme).pack(side=LEFT, padx=5)
        ttk.Button(custom_theme_frame, text="📥 Import Theme", 
                  style="info.TButton",
                  command=self.import_theme).pack(side=LEFT, padx=5)
        
        # 3. Live Preview & Apply
        preview_frame = ttk.LabelFrame(scrollable_frame, text="🖥 Live Preview & Apply", padding=15)
        preview_frame.pack(fill=X, pady=10, padx=10)
        
        # Preview area
        self.preview_area = ttk.Frame(preview_frame, relief="solid", borderwidth=2, height=200)
        self.preview_area.pack(fill=X, pady=10)
        self.preview_area.pack_propagate(False)
        
        # Action buttons
        action_frame = ttk.Frame(preview_frame)
        action_frame.pack(fill=X, pady=10)
        
        ttk.Button(action_frame, text="✅ Apply Theme", 
                  style="success.TButton",
                  command=self.apply_theme).pack(side=LEFT, padx=5)
        ttk.Button(action_frame, text="🔄 Reset to Default", 
                  style="warning.TButton",
                  command=self.reset_theme).pack(side=LEFT, padx=5)
        
        # Sync with system theme
        self.sync_system_var = tk.BooleanVar(
            value=self.settings_manager.get_setting("appearance", "sync_with_system", False)
        )
        ttk.Checkbutton(action_frame, text="🔄 Sync with System Theme", 
                       variable=self.sync_system_var).pack(side=RIGHT, padx=5)
        
        # 4. Original Appearance Options
        options_frame = ttk.LabelFrame(scrollable_frame, text="⚙️ Interface Options", padding=15)
        options_frame.pack(fill=X, pady=10, padx=10)
        
        # ttkbootstrap theme selection
        ttk.Label(options_frame, text="ttkbootstrap Theme:").pack(anchor=W)
        self.ttkbootstrap_theme_var = tk.StringVar(
            value=self.settings_manager.get_setting("appearance", "ttkbootstrap_theme", "flatly")
        )
        ttkbootstrap_themes = ["flatly", "morph", "cyborg", "darkly", "solar", "superhero", "cosmo", "journal"]
        ttkbootstrap_combo = ttk.Combobox(options_frame, textvariable=self.ttkbootstrap_theme_var, 
                                         values=ttkbootstrap_themes, state="readonly")
        ttkbootstrap_combo.pack(fill=X, pady=(0, 10))
        
        # Other appearance options
        self.create_section(options_frame, "Interface Options", [
            ("high_contrast", "High Contrast Mode", "appearance", "checkbox"),
            ("animations", "Enable Animations", "appearance", "checkbox"),
        ])
        
        # Font Size
        font_frame = ttk.LabelFrame(options_frame, text="Font Size", padding=10)
        font_frame.pack(fill=X, pady=10)
        
        self.font_size_var = tk.StringVar(
            value=self.settings_manager.get_setting("appearance", "font_size", "normal")
        )
        for size in ["small", "normal", "large"]:
            ttk.Radiobutton(font_frame, text=size.title(), 
                           variable=self.font_size_var, value=size).pack(anchor=W)
        
        # Language
        lang_frame = ttk.LabelFrame(options_frame, text="Language", padding=10)
        lang_frame.pack(fill=X, pady=10)
        
        self.language_var = tk.StringVar(
            value=self.settings_manager.get_setting("appearance", "language", "en")
        )
        languages = [("English", "en"), ("Spanish", "es"), ("French", "fr"), ("German", "de")]
        for lang_name, lang_code in languages:
            ttk.Radiobutton(lang_frame, text=lang_name, 
                           variable=self.language_var, value=lang_code).pack(anchor=W)
        
        # Initialize custom colors state
        self.toggle_custom_colors()
        
        # Update preview
        self.update_preview()
    
    def on_theme_selected(self, theme_name: str):
        """Handle theme selection"""
        self.settings_manager.set_setting("appearance", "color_theme", theme_name)
        self.update_preview()
    
    def on_custom_color_changed(self, color_name: str, color_value: str):
        """Handle custom color change"""
        custom_colors = self.settings_manager.get_setting("appearance", "custom_colors", {})
        custom_colors[color_name.lower().replace(" ", "_")] = color_value
        self.settings_manager.set_setting("appearance", "custom_colors", custom_colors)
        self.update_preview()
    
    def toggle_custom_colors(self):
        """Toggle custom colors on/off"""
        enabled = self.use_custom_colors_var.get()
        for picker in self.color_pickers.values():
            for widget in picker.winfo_children():
                widget.configure(state="normal" if enabled else "disabled")
        self.update_preview()
    
    def update_preview(self):
        """Update the live preview"""
        # Clear preview area
        for widget in self.preview_area.winfo_children():
            widget.destroy()
        
        # Get current theme data
        if self.use_custom_colors_var.get():
            # Use custom colors
            custom_colors = self.settings_manager.get_setting("appearance", "custom_colors", {})
            theme_data = {
                "name": "Custom Theme",
                "description": "User-defined custom colors",
                **custom_colors
            }
        else:
            # Use selected predefined theme
            theme_name = self.theme_selector.get_selected_theme()
            theme_data = self.color_palette.get_theme(theme_name) or {}
        
        # Create preview widget
        from ui.theme_preview import ThemePreviewWidget
        preview = ThemePreviewWidget(self.preview_area, theme_data, size=200)
        preview.pack(fill=BOTH, expand=True, padx=10, pady=10)
    
    def apply_theme(self):
        """Apply the current theme"""
        try:
            # Save current settings
            self.save_appearance_settings()
            
            # Apply theme to main window if available
            if hasattr(self, 'main_window') and hasattr(self.main_window, 'apply_color_theme'):
                self.main_window.apply_color_theme()
            
            messagebox.showinfo("Success", "Theme applied successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply theme: {e}")
    
    def reset_theme(self):
        """Reset theme to default"""
        if messagebox.askyesno("Reset Theme", "Reset to default Light theme?"):
            self.theme_selector.set_selected_theme("Light")
            self.use_custom_colors_var.set(False)
            self.sync_system_var.set(False)
            
            # Reset custom colors to defaults
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
            
            self.settings_manager.set_setting("appearance", "custom_colors", default_colors)
            self.update_preview()
    
    def save_custom_theme(self):
        """Save current colors as a custom theme"""
        from tkinter import simpledialog
        
        theme_name = simpledialog.askstring("Save Custom Theme", "Enter theme name:")
        if not theme_name:
            return
        
        # Get current colors
        colors = {}
        for color_key, picker in self.color_pickers.items():
            colors[color_key] = picker.get_color()
        
        # Create theme
        if self.color_palette.create_custom_theme(theme_name, colors, "Custom user theme"):
            messagebox.showinfo("Success", f"Custom theme '{theme_name}' saved!")
            # Refresh theme selector
            self.theme_selector.themes = self.color_palette.get_all_themes()
            self.theme_selector.set_selected_theme(theme_name)
        else:
            messagebox.showerror("Error", "Failed to save custom theme")
    
    def export_theme(self):
        """Export current theme"""
        theme_name = self.theme_selector.get_selected_theme()
        if not theme_name:
            messagebox.showwarning("Warning", "Please select a theme to export")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title=f"Export {theme_name} Theme"
        )
        if filepath:
            if self.color_palette.export_theme(theme_name, filepath):
                messagebox.showinfo("Success", f"Theme exported to:\n{filepath}")
            else:
                messagebox.showerror("Error", "Failed to export theme")
    
    def import_theme(self):
        """Import a theme from file"""
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import Theme"
        )
        
        if filepath:
            if self.color_palette.import_theme(filepath):
                messagebox.showinfo("Success", "Theme imported successfully!")
                # Refresh theme selector
                self.theme_selector.themes = self.color_palette.get_all_themes()
            else:
                messagebox.showerror("Error", "Failed to import theme")
    
    def create_exclusions_section(self, parent):
        """Create exclusions management section"""
        excl_frame = ttk.LabelFrame(parent, text="Scan Exclusions", padding=10)
        excl_frame.pack(fill=BOTH, expand=True, pady=10, padx=10)
        
        # Create notebook for different exclusion types
        excl_notebook = ttk.Notebook(excl_frame)
        excl_notebook.pack(fill=BOTH, expand=True)
        
        # Files tab
        files_frame = ttk.Frame(excl_notebook)
        excl_notebook.add(files_frame, text="Files")
        self.create_exclusion_list(files_frame, "files", "scanning")
        
        # Folders tab
        folders_frame = ttk.Frame(excl_notebook)
        excl_notebook.add(folders_frame, text="Folders")
        self.create_exclusion_list(folders_frame, "folders", "scanning")
        
        # Extensions tab
        extensions_frame = ttk.Frame(excl_notebook)
        excl_notebook.add(extensions_frame, text="Extensions")
        self.create_exclusion_list(extensions_frame, "extensions", "scanning")
    
    def create_exclusion_list(self, parent, excl_type, category):
        """Create exclusion list management"""
        # Load current exclusions
        exclusions = self.settings_manager.get_setting(category, "exclusions", {})
        current_list = exclusions.get(excl_type, [])
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=BOTH, expand=True, pady=5)
        
        listbox = tk.Listbox(list_frame, height=8)
        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Populate listbox
        for item in current_list:
            listbox.insert(tk.END, item)
        
        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=X, pady=5)
        
        ttk.Button(btn_frame, text="Add", 
                  command=lambda: self.add_exclusion(listbox, excl_type, category)).pack(side=LEFT, padx=2)
        ttk.Button(btn_frame, text="Remove", 
                  command=lambda: self.remove_exclusion(listbox, excl_type, category)).pack(side=LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear All", 
                  command=lambda: self.clear_exclusions(listbox, excl_type, category)).pack(side=LEFT, padx=2)
        
        # Store reference
        setattr(self, f"{excl_type}_listbox", listbox)
    
    # Event handlers
    def update_cpu_label(self, value):
        """Update CPU usage label"""
        self.cpu_label.config(text=f"{int(float(value))}%")
    
    def add_exclusion(self, listbox, excl_type, category):
        """Add exclusion to list"""
        from tkinter import simpledialog
        
        item = simpledialog.askstring("Add Exclusion", f"Enter {excl_type} to exclude:")
        if item:
            listbox.insert(tk.END, item)
            self.save_exclusions(listbox, excl_type, category)
    
    def remove_exclusion(self, listbox, excl_type, category):
        """Remove selected exclusion"""
        selection = listbox.curselection()
        if selection:
            listbox.delete(selection)
            self.save_exclusions(listbox, excl_type, category)
    
    def clear_exclusions(self, listbox, excl_type, category):
        """Clear all exclusions"""
        if messagebox.askyesno("Clear Exclusions", f"Clear all {excl_type} exclusions?"):
            listbox.delete(0, tk.END)
            self.save_exclusions(listbox, excl_type, category)
    
    def save_exclusions(self, listbox, excl_type, category):
        """Save exclusions to settings"""
        exclusions = self.settings_manager.get_setting(category, "exclusions", {})
        exclusions[excl_type] = list(listbox.get(0, tk.END))
        self.settings_manager.set_setting(category, "exclusions", exclusions)
    
    def browse_quarantine_folder(self):
        """Browse for quarantine folder"""
        folder = filedialog.askdirectory(title="Select Quarantine Folder")
        if folder:
            self.quarantine_folder_var.set(folder)
    
    def check_for_updates(self):
        """Check for updates"""
        messagebox.showinfo("Updates", "Checking for updates...\nThis feature will be implemented in future versions.")
    
    def create_section(self, parent, title, settings_list):
        """Create a settings section with multiple controls"""
        section = ttk.LabelFrame(parent, text=title, padding=10)
        section.pack(fill=X, pady=10, padx=10)
        
        for setting_id, label, category, control_type, *args in settings_list:
            frame = ttk.Frame(section)
            frame.pack(fill=X, pady=2)
            
            if control_type == "checkbox":
                var = tk.BooleanVar(
                    value=self.settings_manager.get_setting(category, setting_id, False)
                )
                cb = ttk.Checkbutton(frame, text=label, variable=var)
                cb.pack(anchor=W)
                setattr(self, f"{setting_id}_var", var)
                
            elif control_type == "combobox":
                var = tk.StringVar(
                    value=self.settings_manager.get_setting(category, setting_id, args[0] if args else "")
                )
                ttk.Label(frame, text=label).pack(side=LEFT)
                combo = ttk.Combobox(frame, textvariable=var, values=args[0], state="readonly")
                combo.pack(side=RIGHT, fill=X, expand=True, padx=(10, 0))
                setattr(self, f"{setting_id}_var", var)
        
    def reset_protection_settings(self):
        """Reset protection settings to defaults"""
        self.real_time_protection_var.set(True)
        self.firewall_protection_var.set(True)
        self.usb_protection_var.set(True)
        self.heuristic_scanning_var.set("Medium")
        self.safe_browsing_var.set(True)
        self.webcam_microphone_control_var.set(True)
        
    def reset_scanning_settings(self):
        """Reset scanning settings to defaults"""
        self.default_scan_type_var.set("Quick")
        self.scan_compressed_files_var.set(True)
        self.scan_startup_programs_var.set(True)
        
        # Clear exclusions
        self.files_listbox.delete(0, tk.END)
        self.folders_listbox.delete(0, tk.END)
        self.extensions_listbox.delete(0, tk.END)
        
    def save_protection_settings(self):
        """Save protection settings"""
        if hasattr(self, 'real_time_protection_var'):
            self.settings_manager.set_setting("protection", "real_time_protection", 
                                             self.real_time_protection_var.get())
        if hasattr(self, 'firewall_protection_var'):
            self.settings_manager.set_setting("protection", "firewall_protection", 
                                             self.firewall_protection_var.get())
        if hasattr(self, 'usb_protection_var'):
            self.settings_manager.set_setting("protection", "usb_protection", 
                                             self.usb_protection_var.get())
        if hasattr(self, 'safe_browsing_var'):
            self.settings_manager.set_setting("protection", "safe_browsing", 
                                             self.safe_browsing_var.get())
        if hasattr(self, 'webcam_microphone_control_var'):
            self.settings_manager.set_setting("protection", "webcam_microphone_control", 
                                             self.webcam_microphone_control_var.get())
        if hasattr(self, 'heuristic_scanning_var'):
            self.settings_manager.set_setting("protection", "heuristic_scanning", 
                                             self.heuristic_scanning_var.get())
    
    def save_scanning_settings(self):
        """Save scanning settings"""
        if hasattr(self, 'default_scan_type_var'):
            self.settings_manager.set_setting("scanning", "default_scan_type", 
                                             self.default_scan_type_var.get())
        if hasattr(self, 'scan_compressed_files_var'):
            self.settings_manager.set_setting("scanning", "scan_compressed_files", 
                                             self.scan_compressed_files_var.get())
        if hasattr(self, 'scan_startup_programs_var'):
            self.settings_manager.set_setting("scanning", "scan_startup_programs", 
                                             self.scan_startup_programs_var.get())
    
    def save_appearance_settings(self):
        """Save appearance settings including color palette features"""
        # Original appearance settings
        self.settings_manager.set_setting("appearance", "ttkbootstrap_theme", 
                                         self.ttkbootstrap_theme_var.get())
        self.settings_manager.set_setting("appearance", "font_size", 
                                         self.font_size_var.get())
        self.settings_manager.set_setting("appearance", "high_contrast", 
                                         self.high_contrast_var.get())
        self.settings_manager.set_setting("appearance", "animations", 
                                         self.animations_var.get())
        self.settings_manager.set_setting("appearance", "language", 
                                         self.language_var.get())
        
        # Color palette settings
        if hasattr(self, 'theme_selector'):
            self.settings_manager.set_setting("appearance", "color_theme", 
                                             self.theme_selector.get_selected_theme())
        
        if hasattr(self, 'use_custom_colors_var'):
            self.settings_manager.set_setting("appearance", "use_custom_colors", 
                                             self.use_custom_colors_var.get())
        
        if hasattr(self, 'sync_system_var'):
            self.settings_manager.set_setting("appearance", "sync_with_system", 
                                             self.sync_system_var.get())
        
        # Save custom colors
        if hasattr(self, 'color_pickers'):
            custom_colors = {}
            for color_key, picker in self.color_pickers.items():
                custom_colors[color_key] = picker.get_color()
            self.settings_manager.set_setting("appearance", "custom_colors", custom_colors)
    
    def save_scheduling_settings(self):
        """Save scheduling settings"""
        if hasattr(self, 'enable_scheduled_scans_var'):
            self.settings_manager.set_setting("scheduling", "enable_scheduled_scans", 
                                             self.enable_scheduled_scans_var.get())
        if hasattr(self, 'scan_frequency_var'):
            self.settings_manager.set_setting("scheduling", "scan_frequency", 
                                             self.scan_frequency_var.get())
        if hasattr(self, 'scan_time_var'):
            self.settings_manager.set_setting("scheduling", "scan_time", 
                                             self.scan_time_var.get())
        if hasattr(self, 'auto_delete_threats_var'):
            self.settings_manager.set_setting("scheduling", "auto_delete_threats", 
                                             self.auto_delete_threats_var.get())
    
    def save_notification_settings(self):
        """Save notification settings"""
        if hasattr(self, 'threat_alerts_var'):
            self.settings_manager.set_setting("notifications", "threat_alerts", 
                                             self.threat_alerts_var.get())
        if hasattr(self, 'scan_results_summary_var'):
            self.settings_manager.set_setting("notifications", "scan_results_summary", 
                                             self.scan_results_summary_var.get())
        if hasattr(self, 'silent_mode_var'):
            self.settings_manager.set_setting("notifications", "silent_mode", 
                                             self.silent_mode_var.get())
        if hasattr(self, 'notification_sound_var'):
            self.settings_manager.set_setting("notifications", "notification_sound", 
                                             self.notification_sound_var.get())
    
    def save_update_settings(self):
        """Save update settings"""
        if hasattr(self, 'auto_update_definitions_var'):
            self.settings_manager.set_setting("updates", "auto_update_definitions", 
                                             self.auto_update_definitions_var.get())
        if hasattr(self, 'auto_update_app_var'):
            self.settings_manager.set_setting("updates", "auto_update_app", 
                                             self.auto_update_app_var.get())
        if hasattr(self, 'cloud_threat_detection_var'):
            self.settings_manager.set_setting("updates", "cloud_threat_detection", 
                                             self.cloud_threat_detection_var.get())
    
    def save_performance_settings(self):
        """Save performance settings"""
        if hasattr(self, 'cpu_limit_var'):
            self.settings_manager.set_setting("performance", "cpu_usage_limit", 
                                             self.cpu_limit_var.get())
        if hasattr(self, 'ram_optimization_var'):
            self.settings_manager.set_setting("performance", "ram_optimization", 
                                             self.ram_optimization_var.get())
        if hasattr(self, 'background_scan_var'):
            self.settings_manager.set_setting("performance", "background_scan", 
                                             self.background_scan_var.get())
        if hasattr(self, 'idle_scan_mode_var'):
            self.settings_manager.set_setting("performance", "idle_scan_mode", 
                                             self.idle_scan_mode_var.get())
        if hasattr(self, 'battery_saver_mode_var'):
            self.settings_manager.set_setting("performance", "battery_saver_mode", 
                                             self.battery_saver_mode_var.get())
    
    def save_quarantine_settings(self):
        """Save quarantine settings"""
        if hasattr(self, 'auto_delete_var'):
            self.settings_manager.set_setting("quarantine", "auto_delete_after_days", 
                                             self.auto_delete_var.get())
        if hasattr(self, 'quarantine_folder_var'):
            self.settings_manager.set_setting("quarantine", "quarantine_folder", 
                                             self.quarantine_folder_var.get())
        if hasattr(self, 'max_size_var'):
            self.settings_manager.set_setting("quarantine", "max_quarantine_size_mb", 
                                             self.max_size_var.get())
        if hasattr(self, 'enable_file_submission_var'):
            self.settings_manager.set_setting("quarantine", "enable_file_submission", 
                                             self.enable_file_submission_var.get())
    
    def save_privacy_settings(self):
        """Save privacy settings"""
        if hasattr(self, 'data_sharing_var'):
            self.settings_manager.set_setting("privacy", "data_sharing", 
                                             self.data_sharing_var.get())
        if hasattr(self, 'log_retention_var'):
            self.settings_manager.set_setting("privacy", "log_retention_days", 
                                             self.log_retention_var.get())
        if hasattr(self, 'auto_log_clearing_var'):
            self.settings_manager.set_setting("privacy", "auto_log_clearing", 
                                             self.auto_log_clearing_var.get())
        if hasattr(self, 'block_telemetry_var'):
            self.settings_manager.set_setting("privacy", "block_telemetry", 
                                             self.block_telemetry_var.get())
    
    def save_all_settings(self):
        """Save all settings from all categories"""
        try:
            # Save all category settings
            self.save_protection_settings()
            self.save_scanning_settings()
            self.save_scheduling_settings()
            self.save_notification_settings()
            self.save_update_settings()
            self.save_performance_settings()
            self.save_quarantine_settings()
            self.save_privacy_settings()
            self.save_appearance_settings()
            
            # Save exclusions if they exist
            if hasattr(self, 'files_listbox'):
                self.save_exclusions(self.files_listbox, "files", "scanning")
            if hasattr(self, 'folders_listbox'):
                self.save_exclusions(self.folders_listbox, "folders", "scanning")
            if hasattr(self, 'extensions_listbox'):
                self.save_exclusions(self.extensions_listbox, "extensions", "scanning")
            
            messagebox.showinfo("Success", "All settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def reset_settings(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", 
                              "This will reset ALL settings to defaults.\nThis action cannot be undone.\n\nContinue?"):
            try:
                self.reset_all_settings()
                messagebox.showinfo("Success", "All settings have been reset to defaults.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {e}")
    
    def export_settings(self):
        """Export all settings to file"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Settings"
        )
        
        if filepath:
            try:
                # Save current settings first
                self.save_all_settings()
                
                # Export settings
                if self.settings_manager.export_settings(filepath):
                    messagebox.showinfo("Success", f"Settings exported to:\n{filepath}")
                else:
                    messagebox.showerror("Error", "Failed to export settings")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export settings: {e}")
    
    def import_settings(self):
        """Import settings from file"""
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import Settings"
        )
        
        if filepath:
            if messagebox.askyesno("Import Settings", 
                                  "This will replace all current settings.\nThis action cannot be undone.\n\nContinue?"):
                try:
                    if self.settings_manager.import_settings(filepath):
                        messagebox.showinfo("Success", "Settings imported successfully!")
                        # Refresh the UI with imported settings
                        self.__init__(self.parent, self.main_window)
                    else:
                        messagebox.showerror("Error", "Failed to import settings")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to import settings: {e}")
    
    def reset_all_data(self):
        """Reset all IronWall data to factory defaults"""
        try:
            from utils.data_reset import DataResetManager
            
            # Show confirmation dialog
            if not messagebox.askyesno("Reset All Data", 
                                      "⚠️  WARNING: This will reset ALL IronWall data to factory defaults!\n\n"
                                      "This includes:\n"
                                      "• All settings\n"
                                      "• Scan history\n"
                                      "• Quarantine\n"
                                      "• Threat database\n"
                                      "• System logs\n"
                                      "• Scheduled scans\n"
                                      "• Backup data\n\n"
                                      "This action cannot be undone!\n\n"
                                      "Continue?"):
                return
            
            # Create data reset manager
            data_reset_manager = DataResetManager()
            
            # Show progress dialog
            progress_window = tk.Toplevel(self.parent)
            progress_window.title("Resetting Data...")
            progress_window.geometry("400x200")
            progress_window.transient(self.parent)
            progress_window.grab_set()
            
            # Center the window
            progress_window.update_idletasks()
            x = (progress_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (progress_window.winfo_screenheight() // 2) - (200 // 2)
            progress_window.geometry(f"400x200+{x}+{y}")
            
            # Progress widgets
            ttk.Label(progress_window, text="🔄 Resetting IronWall data...", 
                     font=("Arial", 12, "bold")).pack(pady=20)
            
            status_label = ttk.Label(progress_window, text="Initializing...")
            status_label.pack(pady=10)
            
            progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
            progress_bar.pack(fill='x', padx=20, pady=10)
            progress_bar.start()
            
            # Perform reset in background thread
            def perform_reset():
                try:
                    status_label.config(text="Creating backup...")
                    progress_window.update()
                    
                    # Perform the reset
                    results = data_reset_manager.reset_all_data(create_backup=True)
                    
                    # Show results
                    success_count = sum(1 for success in results.values() if success)
                    total_count = len(results)
                    
                    progress_window.destroy()
                    
                    if success_count == total_count:
                        # Show verification of reset
                        verification_text = f"✅ All data has been reset successfully!\n\n"
                        verification_text += f"Operations completed: {success_count}/{total_count}\n\n"
                        verification_text += "Data that was reset:\n"
                        verification_text += "• Settings restored to factory defaults\n"
                        verification_text += "• Scan history cleared\n"
                        verification_text += "• Quarantine emptied\n"
                        verification_text += "• Threat database cleared\n"
                        verification_text += "• System logs cleared\n"
                        verification_text += "• Scheduled scans removed\n"
                        verification_text += "• Backup data cleared\n\n"
                        verification_text += "A backup was created before the reset."
                        
                        messagebox.showinfo("Reset Complete", verification_text)
                    else:
                        messagebox.showwarning("Reset Partially Complete", 
                                             f"⚠️  Reset completed with some issues.\n\n"
                                             f"Successful operations: {success_count}/{total_count}")
                        
                        # Show detailed results
                        result_text = "Reset Results:\n\n"
                        for operation, success in results.items():
                            status = "✅" if success else "❌"
                            result_text += f"{status} {operation.replace('_', ' ').title()}\n"
                        
                        messagebox.showinfo("Detailed Results", result_text)
                    
                    # Refresh the settings panel
                    try:
                        # Clear the current settings panel
                        for widget in self.main_frame.winfo_children():
                            widget.destroy()
                        
                        # Recreate the settings panel
                        self.create_settings_window()
                        
                        # Show success message
                        messagebox.showinfo("Settings Refreshed", 
                                          "Settings panel has been refreshed with default values.")
                    except Exception as refresh_error:
                        print(f"Error refreshing settings panel: {refresh_error}")
                        messagebox.showinfo("Settings Refreshed", 
                                          "Data reset completed. Please restart the application to see all changes.")
                    
                except Exception as e:
                    progress_window.destroy()
                    messagebox.showerror("Reset Error", f"Failed to reset data:\n{e}")
                    import traceback
                    traceback.print_exc()
            
            # Start reset thread
            import threading
            reset_thread = threading.Thread(target=perform_reset)
            reset_thread.daemon = True
            reset_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize data reset: {e}")
            import traceback
            traceback.print_exc() 