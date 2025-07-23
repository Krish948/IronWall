"""
IronWall Antivirus - Theme Preview Widget
Shows live preview of color themes
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Dict, List, Optional, Callable

class ThemePreviewWidget(ttk.Frame):
    """Widget for previewing color themes"""
    
    def __init__(self, parent, theme_data: Dict[str, str], size: int = 120, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme_data = theme_data
        self.size = size
        self.create_preview()
    
    def create_preview(self):
        """Create the theme preview"""
        # Main preview frame - use tk.Frame for background colors
        border_color = self.theme_data.get("border", "#D1D9E6")
        preview_frame = tk.Frame(self, relief="solid", borderwidth=2, bg=border_color)
        preview_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Header bar (simulating app header)
        header_bg = self.theme_data.get("primary_accent", "#1976D2")
        header_frame = tk.Frame(preview_frame, bg=header_bg, height=20)
        header_frame.pack(fill=X, pady=(2, 0))
        header_frame.pack_propagate(False)
        
        # Header title
        header_text_color = self.theme_data.get("text_primary", "#FFFFFF")
        header_label = tk.Label(header_frame, text="IronWall", 
                               bg=header_bg, fg=header_text_color,
                               font=("Segoe UI", 8, "bold"))
        header_label.pack(side=LEFT, padx=5, pady=2)
        
        # Sidebar (simulating app sidebar)
        sidebar_bg = self.theme_data.get("surface", "#FFFFFF")
        sidebar_frame = tk.Frame(preview_frame, bg=sidebar_bg, width=30)
        sidebar_frame.pack(side=LEFT, fill=Y, pady=2)
        sidebar_frame.pack_propagate(False)
        
        # Sidebar buttons
        for i in range(3):
            btn_bg = self.theme_data.get("secondary_accent", "#42A5F5")
            btn = tk.Frame(sidebar_frame, bg=btn_bg, width=20, height=15)
            btn.pack(pady=2, padx=5)
        
        # Main content area
        content_bg = self.theme_data.get("background", "#F7F9FB")
        content_frame = tk.Frame(preview_frame, bg=content_bg)
        content_frame.pack(side=LEFT, fill=BOTH, expand=True, pady=2, padx=2)
        
        # Content elements
        text_color = self.theme_data.get("text_primary", "#222B45")
        secondary_color = self.theme_data.get("text_secondary", "#6B778C")
        
        # Title
        title_label = tk.Label(content_frame, text="Dashboard", 
                              bg=content_bg, fg=text_color,
                              font=("Segoe UI", 7, "bold"))
        title_label.pack(anchor=W, padx=5, pady=2)
        
        # Status indicators
        status_frame = tk.Frame(content_frame, bg=content_bg)
        status_frame.pack(fill=X, padx=5, pady=2)
        
        # Status dots
        success_color = self.theme_data.get("success", "#43A047")
        warning_color = self.theme_data.get("warning", "#FFA000")
        danger_color = self.theme_data.get("danger", "#D32F2F")
        info_color = self.theme_data.get("info", "#1976D2")
        
        for color in [success_color, warning_color, danger_color, info_color]:
            dot = tk.Frame(status_frame, bg=color, width=8, height=8)
            dot.pack(side=LEFT, padx=1)
        
        # Sample text
        sample_text = tk.Label(content_frame, text="Sample content", 
                              bg=content_bg, fg=secondary_color,
                              font=("Segoe UI", 6))
        sample_text.pack(anchor=W, padx=5, pady=1)
        
        # Info/Success/Warning/Danger labels
        info_label = tk.Label(content_frame, text="Info", bg=content_bg, fg=info_color, font=("Segoe UI", 6, "italic"))
        info_label.pack(anchor=W, padx=5, pady=1)
        success_label = tk.Label(content_frame, text="Success", bg=content_bg, fg=success_color, font=("Segoe UI", 6, "bold"))
        success_label.pack(anchor=W, padx=5, pady=1)
        warning_label = tk.Label(content_frame, text="Warning", bg=content_bg, fg=warning_color, font=("Segoe UI", 6, "bold"))
        warning_label.pack(anchor=W, padx=5, pady=1)
        danger_label = tk.Label(content_frame, text="Danger", bg=content_bg, fg=danger_color, font=("Segoe UI", 6, "bold"))
        danger_label.pack(anchor=W, padx=5, pady=1)

class ThemeSelectorWidget(ttk.Frame):
    """Widget for selecting themes with preview"""
    
    def __init__(self, parent, themes: Dict[str, Dict[str, str]], 
                 on_theme_selected: Optional[Callable] = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.themes = themes
        self.on_theme_selected = on_theme_selected
        self.selected_theme = tk.StringVar()
        self.create_widget()
    
    def create_widget(self):
        """Create the theme selector widget"""
        # Theme list frame
        list_frame = ttk.Frame(self)
        list_frame.pack(side=LEFT, fill=Y, padx=(0, 10))
        
        # Title
        ttk.Label(list_frame, text="Available Themes", 
                 font=("Segoe UI", 12, "bold")).pack(anchor=W, pady=(0, 10))
        
        # Theme listbox with scrollbar
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill=BOTH, expand=True)
        
        self.theme_listbox = tk.Listbox(listbox_frame, height=8, 
                                       font=("Segoe UI", 10),
                                       selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=VERTICAL, 
                                 command=self.theme_listbox.yview)
        self.theme_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.theme_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Populate themes
        for theme_name in self.themes.keys():
            self.theme_listbox.insert(tk.END, theme_name)
        
        # Bind selection event
        self.theme_listbox.bind('<<ListboxSelect>>', self.on_theme_change)
        
        # Preview frame
        preview_frame = ttk.Frame(self)
        preview_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # Preview title
        self.preview_title = ttk.Label(preview_frame, text="Theme Preview", 
                                      font=("Segoe UI", 12, "bold"))
        self.preview_title.pack(anchor=W, pady=(0, 10))
        
        # Preview description
        self.preview_desc = ttk.Label(preview_frame, text="", 
                                     font=("Segoe UI", 9), wraplength=200)
        self.preview_desc.pack(anchor=W, pady=(0, 10))
        
        # Preview widget
        self.preview_widget = None
        
        # Select first theme by default
        if self.themes:
            first_theme = list(self.themes.keys())[0]
            self.theme_listbox.selection_set(0)
            self.update_preview(first_theme)
    
    def on_theme_change(self, event):
        """Handle theme selection change"""
        selection = self.theme_listbox.curselection()
        if selection:
            theme_name = self.theme_listbox.get(selection[0])
            self.selected_theme.set(theme_name)
            self.update_preview(theme_name)
            
            if self.on_theme_selected:
                self.on_theme_selected(theme_name)
    
    def update_preview(self, theme_name: str):
        """Update the preview for the selected theme"""
        theme_data = self.themes.get(theme_name, {})
        
        # Update title and description
        self.preview_title.config(text=f"{theme_name} Theme")
        self.preview_desc.config(text=theme_data.get("description", ""))
        
        # Update preview widget
        if self.preview_widget:
            self.preview_widget.destroy()
        
        self.preview_widget = ThemePreviewWidget(self, theme_data, size=150)
        self.preview_widget.pack(fill=BOTH, expand=True)
    
    def get_selected_theme(self) -> str:
        """Get the currently selected theme name"""
        return self.selected_theme.get()
    
    def set_selected_theme(self, theme_name: str):
        """Set the selected theme"""
        for i, name in enumerate(self.themes.keys()):
            if name == theme_name:
                self.theme_listbox.selection_clear(0, tk.END)
                self.theme_listbox.selection_set(i)
                self.theme_listbox.see(i)
                self.update_preview(theme_name)
                break

class ColorPickerWidget(ttk.Frame):
    """Widget for picking custom colors"""
    
    def __init__(self, parent, color_name: str, initial_color: str = "#000000",
                 on_color_changed: Optional[Callable] = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.color_name = color_name
        self.initial_color = initial_color
        self.on_color_changed = on_color_changed
        self.current_color = tk.StringVar(value=initial_color)
        self.create_widget()
    
    def create_widget(self):
        """Create the color picker widget"""
        # Label
        ttk.Label(self, text=f"{self.color_name.replace('_', ' ').title()}:").pack(side=LEFT)
        
        # Color preview button
        self.color_btn = tk.Button(self, text="", width=3, height=1,
                                  bg=self.current_color.get(),
                                  command=self.pick_color)
        self.color_btn.pack(side=LEFT, padx=5)
        
        # Color entry
        self.color_entry = ttk.Entry(self, textvariable=self.current_color, width=10)
        self.color_entry.pack(side=LEFT, padx=5)
        
        # Bind entry change
        self.current_color.trace('w', self.on_entry_change)
    
    def pick_color(self):
        """Open color picker dialog"""
        from tkinter import colorchooser
        color = colorchooser.askcolor(self.current_color.get(), 
                                     title=f"Choose {self.color_name}")
        if color[1]:  # color[1] contains the hex color
            self.current_color.set(color[1])
            self.update_color_preview()
    
    def on_entry_change(self, *args):
        """Handle color entry change"""
        self.update_color_preview()
        if self.on_color_changed:
            self.on_color_changed(self.color_name, self.current_color.get())
    
    def update_color_preview(self):
        """Update the color preview button"""
        try:
            self.color_btn.configure(bg=self.current_color.get())
        except:
            pass  # Invalid color format
    
    def get_color(self) -> str:
        """Get the current color value"""
        return self.current_color.get()
    
    def set_color(self, color: str):
        """Set the color value"""
        self.current_color.set(color)
        self.update_color_preview() 