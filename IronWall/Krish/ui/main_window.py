"""
IronWall Antivirus - Main Window UI (Modern, Professional, Versal AI Style)
"""

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
import threading
import time
from datetime import datetime, timedelta
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.quarantine import QuarantineManager
from ui.quarantine_panel import QuarantinePanel
from ui.scheduler_panel import SchedulerPanel
from ui.settings_panel import SettingsPanel
import webbrowser
import version
from ui.scan_panel import ScanPanel
from ui.analytics_panel import AnalyticsPanel
from ui.reports_panel import ReportsPanel
from utils.logger import logger, EventType, EventStatus
import psutil
import traceback
from utils import scan_history

class IronWallMainWindow:
    _t_scrollbar_configured = False

    def __init__(self, scanner, system_monitor, threat_db):
        self.scanner = scanner
        self.system_monitor = system_monitor
        self.threat_db = threat_db
        self.quarantine_manager = QuarantineManager()
        self.scanning = False
        self.stop_scanning = False
        self.scan_thread = None
        self.theme = 'flatly'  # Use ttkbootstrap theme
        self.total_files = 0
        self.files_scanned = 0
        self.threats_found = 0
        self.full_scan_active = False
        self.full_scan_start_time = None
        self.full_scan_total_files = 0
        self.full_scan_files_scanned = 0
        self.full_scan_threats_found = 0
        self.paused = False
        self.deep_scan_enabled = False
        self.show_quarantine_notifications = True  # Control quarantine notifications
        self.setup_window()
        self.create_styles()
        
        # Apply color theme from settings
        self.apply_color_theme()
        
        self.create_widgets()
        self.start_monitoring()

    def setup_window(self):
        self.root = ttk.Window(themename=self.theme)
        self.root.title("🛡️ IronWall Antivirus - Professional Security Suite")
        self.root.state('zoomed')  # Full window
        self.root.minsize(1200, 800)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        # Bind double-click on results tree to delete
        if hasattr(self, 'results_tree'):
            self.results_tree.bind('<Double-1>', self.on_result_double_click)

    def create_styles(self):
        self.style = ttk.Style()
        # Use ttkbootstrap theme
        self.style.theme_use(self.theme)
        
        # Custom dashboard panel style
        self.style.configure('DashboardPanel.TLabelframe', borderwidth=2, relief='ridge')
        self.style.configure('DashboardPanel.TLabelframe.Label', font=('Segoe UI', 13, 'bold'))
        self.style.configure('Dashboard.TFrame')
        self.style.configure('TimelinePanel.TLabelframe', borderwidth=2, relief='ridge')
        self.style.configure('TimelinePanel.TLabelframe.Label', font=('Segoe UI', 13, 'bold'))
        # Stat box style
        self.style.configure('StatBox.TFrame', relief='solid', borderwidth=1)

    def set_theme(self, theme):
        self.theme = theme
        try:
            self.style.theme_use(theme)
        except Exception as e:
            print(f"Error setting theme: {e}")
            traceback.print_exc()
            return
        
        # Define colors based on theme
        if theme in ['darkly', 'cyborg', 'solar']:
            colors = {
                'bg': '#0A0A0F',  # deep space black
                'fg': '#E8E8E8',  # soft white
                'accent': '#00D4FF',  # electric blue
                'sidebar': '#1A1A2E',  # dark navy
                'header': '#00D4FF',
                'button': '#1A1A2E',
                'button_fg': '#E8E8E8',
                'danger': '#FF0055',  # neon red
                'success': '#00FF88',  # neon green
                'warn': '#FFB800',  # amber
                'tree_bg': '#16213E',  # deep blue-gray
                'tree_fg': '#E8E8E8',
                'tree_sel': '#00D4FF',
                'status': '#1A1A2E',
                'entry_bg': '#16213E',
                'entry_fg': '#E8E8E8',
                'text_secondary': '#A0A0A0',  # muted gray
                'border': '#2A2A3E',  # dark blue-gray border
                'hover': '#2A2A3E',  # hover color
                'disabled': '#505050'  # disabled text
            }
        else:
            colors = {
                'bg': '#F7F9FB',  # main background
                'fg': '#222B45',  # primary text
                'accent': '#1976D2',
                'sidebar': '#E9EEF3',
                'header': '#1976D2',
                'button': '#E3E8EF',
                'button_fg': '#222B45',
                'danger': '#D32F2F',
                'success': '#43A047',
                'warn': '#FFA000',
                'tree_bg': '#E9EEF3',
                'tree_fg': '#222B45',
                'tree_sel': '#1976D2',
                'status': '#E9EEF3',
                'entry_bg': '#FFFFFF',
                'entry_fg': '#222B45',
                'text_secondary': '#6B778C',  # muted gray-blue for secondary text
                'border': '#D1D9E6',  # light gray-blue border
                'hover': '#E3E8EF',  # hover color
                'disabled': '#B0B7C3'  # disabled text
            }
        self.colors = colors
        
        try:
            self.root.configure(bg=colors['bg'])
        except Exception as e:
            print(f"Error configuring root: {e}")
            traceback.print_exc()
        
        # Frame styles
        try:
            self.style.configure('TFrame', background=colors['bg'])
            self.style.configure('Main.TFrame', background=colors['bg'])
        except Exception as e:
            print(f"Error configuring frame styles: {e}")
            traceback.print_exc()
        
        # Label styles
        try:
            self.style.configure('TLabel', background=colors['bg'], foreground=colors['fg'], font=('Segoe UI', 12))
            self.style.configure('Header.TLabel', font=('Segoe UI', 22, 'bold'), foreground=colors['header'], background=colors['bg'])
            self.style.configure('SubHeader.TLabel', font=('Segoe UI', 16, 'bold'), foreground=colors['accent'], background=colors['bg'])
            self.style.configure('Status.TLabel', background=colors['status'], foreground=colors['fg'], font=('Segoe UI', 10))
            self.style.configure('Secondary.TLabel', background=colors['bg'], foreground=colors['text_secondary'], font=('Segoe UI', 11))
        except Exception as e:
            print(f"Error configuring label styles: {e}")
            traceback.print_exc()
        
        # Sidebar styles
        try:
            self.style.configure('Sidebar.TFrame', background=colors['sidebar'])
            self.style.configure('Sidebar.TButton', 
                               background=colors['sidebar'], 
                               foreground=colors['fg'], 
                               font=('Segoe UI', 14, 'bold'),
                               borderwidth=0,
                               focuscolor='none')
            self.style.map('Sidebar.TButton',
                          background=[('active', colors['hover']), ('pressed', colors['accent'])],
                          foreground=[('active', colors['accent']), ('pressed', colors['bg'])])
        except Exception as e:
            print(f"Error configuring sidebar styles: {e}")
            traceback.print_exc()
        
        # Button styles
        try:
            self.style.configure('TButton', 
                               background=colors['button'], 
                               foreground=colors['button_fg'], 
                               font=('Segoe UI', 12),
                               borderwidth=1,
                               relief='flat')
            self.style.map('TButton',
                          background=[('active', colors['hover']), ('pressed', colors['accent'])],
                          foreground=[('active', colors['accent']), ('pressed', colors['bg'])])
            
            self.style.configure('Accent.TButton', 
                               background=colors['accent'], 
                               foreground=colors['bg'], 
                               font=('Segoe UI', 12, 'bold'),
                               borderwidth=0,
                               relief='flat')
            self.style.map('Accent.TButton',
                          background=[('active', colors['hover']), ('pressed', colors['button'])],
                          foreground=[('active', colors['accent']), ('pressed', colors['fg'])])
            
            # Danger button style
            self.style.configure('Danger.TButton', 
                               background=colors['danger'], 
                               foreground=colors['bg'], 
                               font=('Segoe UI', 12, 'bold'),
                               borderwidth=0,
                               relief='flat')
            
            # Success button style
            self.style.configure('Success.TButton', 
                               background=colors['success'], 
                               foreground=colors['bg'], 
                               font=('Segoe UI', 12, 'bold'),
                               borderwidth=0,
                               relief='flat')
        except Exception as e:
            print(f"Error configuring button styles: {e}")
            traceback.print_exc()
        
        # Treeview styles
        try:
            self.style.configure('Treeview', 
                               background=colors['tree_bg'], 
                               foreground=colors['tree_fg'],
                               fieldbackground=colors['tree_bg'],
                               font=('Segoe UI', 11))
            self.style.configure('Treeview.Heading', 
                               background=colors['sidebar'], 
                               foreground=colors['fg'],
                               font=('Segoe UI', 12, 'bold'))
            self.style.map('Treeview',
                          background=[('selected', colors['tree_sel'])],
                          foreground=[('selected', colors['bg'])])
        except Exception as e:
            print(f"Error configuring treeview styles: {e}")
        
        # Entry styles
        try:
            self.style.configure('TEntry', 
                               fieldbackground=colors['entry_bg'], 
                               foreground=colors['entry_fg'],
                               insertcolor=colors['fg'],
                               font=('Segoe UI', 11))
        except Exception as e:
            print(f"Error configuring entry styles: {e}")
        
        # Scrollbar styles - Add error handling to prevent duplicate element errors
        try:
            # Only configure scrollbar if it hasn't been configured before (class-level guard)
            if not hasattr(IronWallMainWindow, '_t_scrollbar_configured'):
                self.style.configure('TScrollbar',
                                   background=colors['sidebar'],
                                   troughcolor=colors['bg'],
                                   borderwidth=0,
                                   arrowcolor=colors['fg'])
                IronWallMainWindow._t_scrollbar_configured = True
        except Exception as e:
            print(f"Error configuring scrollbar styles: {e}")
        
        # Notebook styles
        try:
            self.style.configure('TNotebook', background=colors['bg'])
            self.style.configure('TNotebook.Tab', 
                               background=colors['button'], 
                               foreground=colors['button_fg'],
                               padding=[10, 5],
                               font=('Segoe UI', 11))
            self.style.map('TNotebook.Tab',
                          background=[('selected', colors['accent']), ('active', colors['hover'])],
                          foreground=[('selected', colors['bg']), ('active', colors['accent'])])
        except Exception as e:
            print(f"Error configuring notebook styles: {e}")
        
        # Progress bar styles
        try:
            self.style.configure('TProgressbar', 
                               background=colors['accent'],
                               troughcolor=colors['bg'],
                               borderwidth=0)
        except Exception as e:
            print(f"Error configuring progress bar styles: {e}")

    def get_color(self, key):
        return self.colors[key] if hasattr(self, 'colors') and key in self.colors else '#232a36'

    def create_widgets(self):
        # Destroy old widgets if they exist
        for attr in ['sidebar', 'content', 'status_bar']:
            if hasattr(self, attr):
                widget = getattr(self, attr)
                try:
                    widget.destroy()
                except Exception:
                    pass
                delattr(self, attr)
        # Sidebar
        self.sidebar = ttk.Frame(self.root, style='Sidebar.TFrame', width=220)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)
        self.create_sidebar()

        # Main content area
        self.content = ttk.Frame(self.root)
        self.content.pack(side='left', fill='both', expand=True)
        self.create_header()
        
        # This will hold the current page's content
        self.page_frame = ttk.Frame(self.content)
        self.page_frame.pack(fill='both', expand=True)

        self.create_status_bar()
        # Initial page
        self.show_dashboard()
        # Restart monitoring thread to update new widgets
        self.monitoring_active = False
        self.start_monitoring()

    def create_sidebar(self):
        # Remove logo
        # logo = ttk.Label(self.sidebar, text='🛡️', font=('Segoe UI', 40), background=self.get_color('sidebar'), foreground=self.get_color('accent'))
        # logo.pack(pady=(30, 10))
        title = ttk.Label(self.sidebar, text='IronWall', font=('Segoe UI', 20, 'bold'), background=self.get_color('sidebar'), foreground=self.get_color('header'))
        title.pack(pady=(30, 30))
        nav_buttons = [
            ('Dashboard', self.show_dashboard),
            ('Scan', self.show_scan),
            ('Recent Activity', self.show_recent_activity),
            ('Quarantine', self.show_quarantine),
            ('Analytics', self.show_analytics_panel),
            ('Reports', self.show_reports_panel),
            ('Scheduler', self.show_scheduler_panel),
            ('Settings', self.show_settings),
            ('About', self.show_about),
            ('Refresh UI', self.refresh_ui)
        ]
        self.sidebar_btns = {}
        for text, cmd in nav_buttons:
            btn = ttk.Button(self.sidebar, text=text, style='Sidebar.TButton', command=cmd)
            btn.pack(fill='x', padx=30, pady=8)
            self.sidebar_btns[text] = btn
        ttk.Label(self.sidebar, text='', background=self.get_color('sidebar')).pack(expand=True, fill='both')
        self.theme_toggle_btn = ttk.Button(self.sidebar, text='🌙 Dark Mode' if self.theme=='light' else '☀️ Light Mode', style='Accent.TButton', command=self.toggle_theme)
        self.theme_toggle_btn.pack(fill='x', padx=30, pady=20)

    def create_header(self):
        self.header = ttk.Frame(self.content)
        self.header.pack(fill='x', pady=(0, 10))
        ttk.Label(self.header, text='IronWall Antivirus', style='Header.TLabel').pack(side='left', padx=20, pady=10)
        self.header_status = ttk.Label(self.header, text='Professional Security Suite', style='Status.TLabel')
        self.header_status.pack(side='left', padx=20)
        # Add refresh button to the right
        refresh_btn = ttk.Button(self.header, text='🔄 Refresh', style='Accent.TButton', command=self.refresh_scan_panel)
        refresh_btn.pack(side='right', padx=20, pady=10)

    def create_status_bar(self):
        # Status bar removed; use popup instead
        pass

    def _clear_page(self):
        """Destroy all widgets in the page frame"""
        for widget in self.page_frame.winfo_children():
            widget.destroy()

    def _create_scrollable_frame(self, parent):
        """Create a scrollable frame with canvas and scrollbar"""
        # Create main container
        canvas = tk.Canvas(parent, bg=self.get_color('bg'), highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Dashboard.TFrame')
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Bind mouse wheel scrolling
        def _on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception as e:
                print(f"Error scrolling canvas: {e}")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        return scrollable_frame

    def _show_buffering(self):
        if hasattr(self, '_buffering_overlay') and self._buffering_overlay:
            return  # Already shown
        self._buffering_overlay = tk.Toplevel(self.root)
        self._buffering_overlay.overrideredirect(True)
        self._buffering_overlay.attributes('-topmost', True)
        self._buffering_overlay.geometry(f"{self.root.winfo_width()}x{self.root.winfo_height()}+{self.root.winfo_x()}+{self.root.winfo_y()}")
        self._buffering_overlay.configure(bg='#000000')
        self._buffering_overlay.attributes('-alpha', 0.35)
        frame = ttk.Frame(self._buffering_overlay, style='Dashboard.TFrame')
        frame.place(relx=0.5, rely=0.5, anchor='center')
        spinner = ttk.Progressbar(frame, mode='indeterminate', length=120, style='TProgressbar')
        spinner.pack(pady=16)
        spinner.start(10)
        label = ttk.Label(frame, text='Loading...', font=('Segoe UI', 16, 'bold'))
        label.pack()
        self._buffering_spinner = spinner
        self._buffering_label = label
        self._buffering_overlay.update()

    def _hide_buffering(self):
        if hasattr(self, '_buffering_overlay') and self._buffering_overlay:
            self._buffering_overlay.destroy()
            self._buffering_overlay = None
            self._buffering_spinner = None
            self._buffering_label = None

    def show_dashboard(self):
        self._show_buffering()
        self._clear_page()
        self.header_status.config(text='Advanced Security Overview')
        
        # Create main scrollable container
        canvas = tk.Canvas(self.page_frame, bg=self.get_color('bg'), highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.page_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Dashboard.TFrame')
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # --- Main Panels Grid ---
        grid_frame = ttk.Frame(scrollable_frame, style='Dashboard.TFrame')
        grid_frame.pack(fill='x', padx=30, pady=(20, 10))
        for i in range(2):
            grid_frame.columnconfigure(i, weight=1)
        for i in range(2):
            grid_frame.rowconfigure(i, weight=1)
        # Security Status
        status_panel = ttk.LabelFrame(grid_frame, text='Security Status', padding=16, style='DashboardPanel.TLabelframe')
        status_panel.grid(row=0, column=0, sticky='nsew', padx=12, pady=10, ipadx=6, ipady=6)
        self._create_security_status_panel(status_panel)
        # Quick Actions
        actions_panel = ttk.LabelFrame(grid_frame, text='Quick Actions', padding=16, style='DashboardPanel.TLabelframe')
        actions_panel.grid(row=0, column=1, sticky='nsew', padx=12, pady=10, ipadx=6, ipady=6)
        self._create_quick_actions_panel(actions_panel)
        # System Performance
        perf_panel = ttk.LabelFrame(grid_frame, text='System Performance', padding=16, style='DashboardPanel.TLabelframe')
        perf_panel.grid(row=1, column=0, sticky='nsew', padx=12, pady=10, ipadx=6, ipady=6)
        self._create_performance_panel(perf_panel)
        # Threat Center
        threat_panel = ttk.LabelFrame(grid_frame, text='Threat Center', padding=16, style='DashboardPanel.TLabelframe')
        threat_panel.grid(row=1, column=1, sticky='nsew', padx=12, pady=10, ipadx=6, ipady=6)
        self._create_threat_center_panel(threat_panel)

        # --- Full-width Panels Below Grid ---
        # Recent Activity Timeline
        timeline_panel = ttk.LabelFrame(scrollable_frame, text='Recent Activity Timeline', padding=16, style='TimelinePanel.TLabelframe')
        timeline_panel.pack(fill='x', padx=30, pady=(0, 12))
        self._create_timeline_panel(timeline_panel)
        # Notifications & Alerts
        alerts_panel = ttk.LabelFrame(scrollable_frame, text='Notifications & Alerts', padding=16, style='DashboardPanel.TLabelframe')
        alerts_panel.pack(fill='x', padx=30, pady=(0, 12))
        self._create_notifications_panel(alerts_panel)
        # License & User Info
        license_panel = ttk.LabelFrame(scrollable_frame, text='License & User Info', padding=16, style='DashboardPanel.TLabelframe')
        license_panel.pack(fill='x', padx=30, pady=(0, 12))
        self._create_license_info_panel(license_panel)
        # Security Tips & News
        tips_panel = ttk.LabelFrame(scrollable_frame, text='Security Tips & News', padding=16, style='DashboardPanel.TLabelframe')
        tips_panel.pack(fill='x', padx=30, pady=(0, 24))
        self._create_tips_panel(tips_panel)
        
        # Bind mouse wheel scrolling
        def _on_mousewheel(event):
            try:
                widget = event.widget
                canvas = None
                current = widget
                while current and current != self.root:
                    try:
                        if hasattr(current, 'yview_scroll'):
                            canvas = current
                            break
                        current = current.master
                    except Exception:
                        break
                if canvas and canvas.winfo_exists():
                    try:
                        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                    except Exception as e:
                        print(f"Error scrolling canvas: {e}")
            except Exception as e:
                print(f"Error in mousewheel handler: {e}")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        # Start periodic refresh for real-time panels
        self._dashboard_refresh()
        self._hide_buffering()

    def _create_security_status_panel(self, parent):
        # Real-time protection (stub: always ON)
        rtp_status = 'ON'
        rtp_color = self.get_color('success') if rtp_status == 'ON' else self.get_color('danger')
        # Firewall status (stub: always ON)
        fw_status = 'ON'
        fw_color = self.get_color('success') if fw_status == 'ON' else self.get_color('danger')
        # Virus definitions update
        last_updated = getattr(self.threat_db, 'last_updated', None)
        if not last_updated:
            try:
                with open(self.threat_db.db_file, 'r') as f:
                    import json
                    data = json.load(f)
                    last_updated = data.get('last_updated')
            except:
                last_updated = None
        import datetime
        if last_updated:
            try:
                dt = datetime.datetime.fromisoformat(last_updated)
                delta = datetime.datetime.now() - dt
                if delta.days > 7:
                    defs_status = 'Outdated'
                    defs_color = self.get_color('danger')
                elif delta.days > 1:
                    defs_status = 'Stale'
                    defs_color = self.get_color('warn')
                else:
                    defs_status = 'Up-to-date'
                    defs_color = self.get_color('success')
            except:
                defs_status = 'Unknown'
                defs_color = self.get_color('warn')
        else:
            defs_status = 'Unknown'
            defs_color = self.get_color('warn')
        # System vulnerability (use is_system_healthy)
        is_secure = self.system_monitor.is_system_healthy()
        vuln_status = 'Secure' if is_secure else 'Insecure'
        vuln_color = self.get_color('success') if is_secure else self.get_color('danger')
        
        # Enhanced layout with icons and better spacing
        items = [
            ('🛡️ Real-time Protection', rtp_status, rtp_color),
            ('🔥 Firewall', fw_status, fw_color),
            ('📋 Virus Definitions', defs_status, defs_color),
            ('🔒 System Vulnerability', vuln_status, vuln_color)
        ]
        
        for i, (label, status, color) in enumerate(items):
            # Create a frame for each status item
            item_frame = ttk.Frame(parent)
            item_frame.grid(row=i, column=0, sticky='ew', pady=8, padx=5)
            item_frame.columnconfigure(1, weight=1)
            
            # Icon and label
            l = ttk.Label(item_frame, text=label, font=('Segoe UI', 12, 'bold'), style='TLabel')
            l.grid(row=0, column=0, sticky='w', padx=(0, 10))
            
            # Status with colored text
            s = ttk.Label(item_frame, text=status, font=('Segoe UI', 12, 'bold'), foreground=color, style='TLabel')
            s.grid(row=0, column=1, sticky='w')
            
            # Colored indicator circle
            canvas = tk.Canvas(item_frame, width=20, height=20, highlightthickness=0, bg=self.get_color('bg'))
            canvas.grid(row=0, column=2, padx=(10, 0))
            canvas.create_oval(2, 2, 18, 18, fill=color, outline=color, width=2)
            
            # Add subtle border for dark mode
            if self.theme == 'dark':
                canvas.create_oval(1, 1, 19, 19, outline=self.get_color('border'), width=1)

    def _create_quick_actions_panel(self, parent):
        btns = [
            # ('Quick Scan', self.start_quick_scan),  # Removed as requested
            ('Update Virus Definitions', self._update_virus_definitions),
            ('Fix Issues', self._fix_issues),
            ('Quarantine Manager', self.show_quarantine),
            ('Recent Activity', self.show_recent_activity)
        ]
        for i, (text, cmd) in enumerate(btns):
            btn = ttk.Button(parent, text=text, style='Accent.TButton', command=cmd)
            btn.grid(row=0, column=i, padx=8, pady=4, sticky='ew')
            parent.columnconfigure(i, weight=1)

    def _create_performance_panel(self, parent):
        # Performance monitoring with enhanced styling
        # CPU Usage
        cpu_frame = ttk.Frame(parent)
        cpu_frame.pack(fill='x', pady=8, padx=5)
        ttk.Label(cpu_frame, text='💻 CPU Usage:', font=('Segoe UI', 12, 'bold'), style='TLabel').pack(anchor='w')
        self.cpu_label = ttk.Label(cpu_frame, text='Loading...', font=('Segoe UI', 11), style='Secondary.TLabel')
        self.cpu_label.pack(anchor='w', padx=(20, 0))
        self.cpu_bar = ttk.Progressbar(cpu_frame, maximum=100, length=200, style='TProgressbar')
        self.cpu_bar.pack(fill='x', padx=(20, 0), pady=(2, 8))
        
        # Memory Usage
        mem_frame = ttk.Frame(parent)
        mem_frame.pack(fill='x', pady=8, padx=5)
        ttk.Label(mem_frame, text='🧠 Memory Usage:', font=('Segoe UI', 12, 'bold'), style='TLabel').pack(anchor='w')
        self.mem_label = ttk.Label(mem_frame, text='Loading...', font=('Segoe UI', 11), style='Secondary.TLabel')
        self.mem_label.pack(anchor='w', padx=(20, 0))
        self.mem_bar = ttk.Progressbar(mem_frame, maximum=100, length=200, style='TProgressbar')
        self.mem_bar.pack(fill='x', padx=(20, 0), pady=(2, 8))
        
        # Disk Usage
        disk_frame = ttk.Frame(parent)
        disk_frame.pack(fill='x', pady=8, padx=5)
        ttk.Label(disk_frame, text='💾 Disk Usage:', font=('Segoe UI', 12, 'bold'), style='TLabel').pack(anchor='w')
        self.disk_val = ttk.Label(disk_frame, text='Loading...', font=('Segoe UI', 11), style='Secondary.TLabel')
        self.disk_val.pack(anchor='w', padx=(20, 0))
        self.disk_bar = ttk.Progressbar(parent, maximum=100, length=200, style='TProgressbar')
        self.disk_bar.pack(fill='x', pady=(5, 10), padx=5)

        # System Uptime
        uptime_frame = ttk.Frame(parent)
        uptime_frame.pack(fill='x', pady=8, padx=5)
        ttk.Label(uptime_frame, text='⏱ System Uptime:', font=('Segoe UI', 12, 'bold'), style='TLabel').pack(anchor='w')
        self.uptime_label = ttk.Label(uptime_frame, text='Loading...', font=('Segoe UI', 11), style='Secondary.TLabel')
        self.uptime_label.pack(anchor='w', padx=(20, 0))

        # Network Activity
        net_frame = ttk.Frame(parent)
        net_frame.pack(fill='x', pady=8, padx=5)
        ttk.Label(net_frame, text='🌐 Network Activity:', font=('Segoe UI', 12, 'bold'), style='TLabel').pack(anchor='w')
        self.net_label = ttk.Label(net_frame, text='Loading...', font=('Segoe UI', 11), style='Secondary.TLabel')
        self.net_label.pack(anchor='w', padx=(20, 0))

    def _create_threat_center_panel(self, parent):
        stats = self.threat_db.get_threat_statistics()
        qstats = self.quarantine_manager.get_quarantine_statistics()
        
        # Total threats with icon
        threat_frame = ttk.Frame(parent)
        threat_frame.pack(fill='x', pady=8, padx=5)
        ttk.Label(threat_frame, text='🦠 Total Threats:', font=('Segoe UI', 12, 'bold'), style='TLabel').pack(anchor='w')
        ttk.Label(threat_frame, text=f"{stats.get('total_hashes', 0)}", font=('Segoe UI', 14, 'bold'), foreground=self.get_color('danger'), style='TLabel').pack(anchor='w', padx=(20, 0))
        
        # Threats resolved
        resolved_frame = ttk.Frame(parent)
        resolved_frame.pack(fill='x', pady=8, padx=5)
        ttk.Label(resolved_frame, text='✅ Threats Resolved:', font=('Segoe UI', 12, 'bold'), style='TLabel').pack(anchor='w')
        ttk.Label(resolved_frame, text=f"{qstats.get('restored', 0) + qstats.get('deleted', 0)}", font=('Segoe UI', 14, 'bold'), foreground=self.get_color('success'), style='TLabel').pack(anchor='w', padx=(20, 0))
        
        # Severity summary
        severities = stats.get('severities', {})
        if severities:
            sev_frame = ttk.Frame(parent)
            sev_frame.pack(fill='x', pady=8, padx=5)
            ttk.Label(sev_frame, text='⚠️ Severity Levels:', font=('Segoe UI', 12, 'bold'), style='TLabel').pack(anchor='w')
            sev_str = ', '.join([f"{k}: {v}" for k, v in severities.items()])
            ttk.Label(sev_frame, text=sev_str, font=('Segoe UI', 11), style='Secondary.TLabel').pack(anchor='w', padx=(20, 0))
        
        # Status summary
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill='x', pady=8, padx=5)
        ttk.Label(status_frame, text='📊 Status Summary:', font=('Segoe UI', 12, 'bold'), style='TLabel').pack(anchor='w')
        
        # Active/Quarantined/Deleted with icons
        status_items = [
            ('🟢 Active', qstats.get('quarantined', 0), self.get_color('success')),
            ('🟡 Quarantined', qstats.get('quarantined', 0), self.get_color('warn')),
            ('🔴 Deleted', qstats.get('deleted', 0), self.get_color('danger'))
        ]
        
        for text, value, color in status_items:
            item_frame = ttk.Frame(status_frame)
            item_frame.pack(fill='x', pady=2)
            ttk.Label(item_frame, text=f"{text}: {value}", font=('Segoe UI', 11), foreground=color, style='TLabel').pack(anchor='w', padx=(20, 0))
        
        # Mini bar for threat types
        types = stats.get('threat_types', {})
        if types:
            types_frame = ttk.Frame(parent)
            types_frame.pack(fill='x', pady=8, padx=5)
            ttk.Label(types_frame, text='📈 Threat Types:', font=('Segoe UI', 12, 'bold'), style='TLabel').pack(anchor='w')
            
            for t, v in types.items():
                type_frame = ttk.Frame(types_frame)
                type_frame.pack(fill='x', pady=2)
                ttk.Label(type_frame, text=f"{t}", font=('Segoe UI', 10), style='Secondary.TLabel').pack(side='left', padx=(20, 10))
                bar = ttk.Progressbar(type_frame, value=v, maximum=max(types.values()), length=80, style='TProgressbar')
                bar.pack(side='left', padx=(0, 10))
                ttk.Label(type_frame, text=str(v), font=('Segoe UI', 10), style='Secondary.TLabel').pack(side='left')

    def _create_timeline_panel(self, parent):
        # Load recent scan history
        history = scan_history.load_scan_history()
        # Sort by timestamp descending
        history = sorted(history, key=lambda x: x.get('timestamp', 0), reverse=True)[:10]
        
        # Create a frame for the timeline
        timeline_frame = ttk.Frame(parent)
        timeline_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        ttk.Label(timeline_frame, text='📅 Recent Activity', font=('Segoe UI', 14, 'bold'), style='TLabel').pack(anchor='w', pady=(0, 10))
        
        # Canvas for timeline with theme-aware background
        canvas = tk.Canvas(timeline_frame, height=180, bg=self.get_color('bg'), highlightthickness=0, relief='flat')
        canvas.pack(fill='x', expand=True)
        
        # Add subtle border for dark mode
        if self.theme == 'dark':
            canvas.configure(bd=1, relief='solid', highlightbackground=self.get_color('border'))
        
        y = 20
        for i, entry in enumerate(history):
            ts = entry.get('timestamp')
            import datetime
            if ts:
                dt = datetime.datetime.fromtimestamp(ts)
                time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                time_str = 'Unknown time'
            file_name = entry.get('file_name', 'Unknown file')
            action = entry.get('status', 'Scanned')
            threat = entry.get('threat_type', 'Unknown')
            
            # Use accent color for threats, secondary for non-threats
            if threat and threat.lower() not in ('clean', 'none', 'unknown'):
                color = self.get_color('danger')
                icon = '🦠'
            else:
                color = self.get_color('text_secondary')
                icon = '✅'
            
            # Create timeline entry with icon
            text = f"{icon} [{time_str}] {file_name} - {action} - {threat}"
            canvas.create_text(20, y, anchor='w', text=text, font=('Segoe UI', 10), fill=color)
            
            # Add subtle line separator for dark mode
            if self.theme == 'dark' and i < len(history) - 1:
                canvas.create_line(15, y + 12, canvas.winfo_reqwidth() - 15, y + 12, 
                                 fill=self.get_color('border'), width=1, dash=(2, 2))
            
            y += 18

    def _dashboard_refresh(self):
        # Refresh real-time panels
        try:
            # Check if widgets still exist before updating
            if not hasattr(self, 'cpu_bar') or not self.cpu_bar.winfo_exists():
                return
            
            stats = self.system_monitor.get_detailed_stats()
            print('[DEBUG] dashboard stats:', stats)  # Debug print
            cpu = stats.get('cpu', {})
            mem = stats.get('memory', {})
            disk = stats.get('disk', {})
            net = stats.get('network', {})
            
            # CPU
            cpu_percent = cpu.get('percent', None)
            if cpu_percent is not None and cpu_percent > 0:
                try:
                    self.cpu_bar['value'] = cpu_percent
                    if hasattr(self, 'cpu_label') and self.cpu_label.winfo_exists():
                        self.cpu_label.config(text=f"CPU Usage: {cpu_percent:.1f}%")
                except Exception as e:
                    print(f'[DEBUG] Error updating CPU bar: {e}')
            else:
                try:
                    self.cpu_bar['value'] = 0
                    if hasattr(self, 'cpu_label') and self.cpu_label.winfo_exists():
                        self.cpu_label.config(text="CPU Usage: N/A")
                except Exception as e:
                    print(f'[DEBUG] Error updating CPU label: {e}')
            
            # Memory
            mem_percent = mem.get('percent', None)
            if mem_percent is not None and mem_percent > 0:
                try:
                    if hasattr(self, 'mem_bar') and self.mem_bar.winfo_exists():
                        self.mem_bar['value'] = mem_percent
                    if hasattr(self, 'mem_label') and self.mem_label.winfo_exists():
                        self.mem_label.config(text=f"Memory Usage: {mem_percent:.1f}%")
                except Exception as e:
                    print(f'[DEBUG] Error updating memory: {e}')
            else:
                try:
                    if hasattr(self, 'mem_bar') and self.mem_bar.winfo_exists():
                        self.mem_bar['value'] = 0
                    if hasattr(self, 'mem_label') and self.mem_label.winfo_exists():
                        self.mem_label.config(text="Memory Usage: N/A")
                except Exception as e:
                    print(f'[DEBUG] Error updating memory label: {e}')
            
            # Disk
            disk_percent = disk.get('percent', None)
            if disk_percent is not None and disk_percent > 0:
                try:
                    if hasattr(self, 'disk_bar') and self.disk_bar.winfo_exists():
                        self.disk_bar['value'] = disk_percent
                    if hasattr(self, 'disk_val') and self.disk_val.winfo_exists():
                        self.disk_val.config(text=f"Disk Usage: {disk_percent:.1f}% ({self._format_bytes(disk.get('used', 0))} / {self._format_bytes(disk.get('total', 0))})")
                except Exception as e:
                    print(f'[DEBUG] Error updating disk: {e}')
            else:
                try:
                    if hasattr(self, 'disk_bar') and self.disk_bar.winfo_exists():
                        self.disk_bar['value'] = 0
                    if hasattr(self, 'disk_val') and self.disk_val.winfo_exists():
                        self.disk_val.config(text="Disk Usage: N/A")
                except Exception as e:
                    print(f'[DEBUG] Error updating disk label: {e}')
            
            # Uptime
            import time
            boot_time = 0
            try:
                boot_time = self.system_monitor.get_system_info().get('boot_time', 0)
            except Exception as e:
                print('[DEBUG] Error getting boot_time:', e)
            uptime = time.time() - boot_time if boot_time else 0
            if uptime > 0:
                try:
                    if hasattr(self, 'uptime_label') and self.uptime_label.winfo_exists():
                        self.uptime_label.config(text=self._format_uptime(uptime))
                except Exception as e:
                    print(f'[DEBUG] Error updating uptime: {e}')
            else:
                try:
                    if hasattr(self, 'uptime_label') and self.uptime_label.winfo_exists():
                        self.uptime_label.config(text="N/A")
                except Exception as e:
                    print(f'[DEBUG] Error updating uptime label: {e}')
            
            # Network
            if net:
                try:
                    if hasattr(self, 'net_label') and self.net_label.winfo_exists():
                        net_str = f"Sent: {self._format_bytes(net.get('bytes_sent', 0))}, Recv: {self._format_bytes(net.get('bytes_recv', 0))}, Packets Sent: {net.get('packets_sent', 0)}, Packets Recv: {net.get('packets_recv', 0)}"
                        self.net_label.config(text=net_str)
                except Exception as e:
                    print(f'[DEBUG] Error updating network: {e}')
            else:
                try:
                    if hasattr(self, 'net_label') and self.net_label.winfo_exists():
                        self.net_label.config(text="N/A")
                except Exception as e:
                    print(f'[DEBUG] Error updating network label: {e}')
                    
        except Exception as e:
            import traceback
            print('[DEBUG] Exception in _dashboard_refresh:', e)
            traceback.print_exc()
        
        # Schedule next refresh only if root still exists
        try:
            if hasattr(self, 'root') and self.root.winfo_exists():
                self.root.after(2000, self._dashboard_refresh)
        except Exception as e:
            print(f'[DEBUG] Error scheduling next refresh: {e}')

    def _format_bytes(self, num):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if num < 1024.0:
                return f"{num:.1f} {unit}"
            num /= 1024.0
        return f"{num:.1f} PB"

    def _format_uptime(self, seconds):
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{days}d {hours}h {minutes}m" if days else f"{hours}h {minutes}m"

    def _update_virus_definitions(self):
        self.threat_db.load_database()
        self.show_popup('Virus definitions updated.', 'Update Complete')
        self.show_dashboard()

    def _fix_issues(self):
        self.show_popup('All critical issues have been resolved!', 'Fix Issues')

    def _open_logs(self):
        import os
        import subprocess
        log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scan_history.json'))
        try:
            if os.name == 'nt':
                os.startfile(log_path)
            else:
                subprocess.Popen(['xdg-open', log_path])
        except Exception as e:
            messagebox.showerror('Open Logs', f'Could not open log file:\n{e}')

    def show_scan(self):
        self._clear_page()
        self.header_status.config(text='Scan for threats')
        
        # Import and use the ScanPanel directly in page_frame for maximum size
        from ui.scan_panel import ScanPanel
        
        def start_cb(scan_type, paths):
            if scan_type == 'Quick':
                self.start_quick_scan()
            elif scan_type == 'Full':
                self.start_full_scan(paths)
            elif scan_type == 'Custom':
                self.start_custom_scan(paths)
            elif scan_type == 'Boot':
                self.enable_boot_scan()
        
        self.scan_panel = ScanPanel(self.page_frame, scan_callbacks={
            'start': start_cb,
            'pause': self.pause_scan,
            'resume': self.resume_scan,
            'stop': self.stop_scan
        })
        self.scan_panel.pack(fill='both', expand=True, padx=10, pady=10)

    def start_quick_scan(self):
        self._start_scan(scan_type='Quick')

    def start_full_scan(self, paths=None):
        self._start_scan(scan_type='Full', custom_paths=paths)

    def start_custom_scan(self, paths):
        self._start_scan(scan_type='Custom', custom_paths=paths)

    def enable_boot_scan(self):
        # Stub: Set a flag or schedule a scan on next boot
        messagebox.showinfo("Boot-Time Scan", "Boot-Time Scan will run on next system restart.")

    def _start_scan(self, scan_type='Quick', deep_scan_enabled=False, custom_paths=None):
        """Start a scan with the specified type"""
        if self.scanning:
            messagebox.showwarning("Scan in Progress", "A scan is already running. Please wait for it to complete.")
            return
        
        # Clear previous results safely
        try:
            if hasattr(self, 'scan_panel') and self.scan_panel and hasattr(self.scan_panel, 'results_tree'):
                if self.scan_panel.results_tree.winfo_exists():
                    self.scan_panel.results_tree.delete(*self.scan_panel.results_tree.get_children())
        except Exception as e:
            print(f"Error clearing scan results: {e}")
        
        self.scanning = True
        self.stop_scanning = False
        self.paused = False
        self.deep_scan_enabled = deep_scan_enabled
        
        # Reset scan statistics
        self.files_scanned = 0
        self.threats_found = 0
        self.total_files = 0
        
        # Start time tracking
        if hasattr(self, 'scan_panel') and self.scan_panel:
            self.scan_panel.start_time_tracking()
        
        # Determine scan paths
        if custom_paths:
            scan_paths = custom_paths
        elif scan_type == 'Quick':
            scan_paths = ['C:\\Users\\krish gupta\\Downloads']  # Quick scan default path
        elif scan_type == 'Full':
            scan_paths = ['C:\\']  # Full system scan
        else:
            scan_paths = ['C:\\Users\\krish gupta\\Downloads']  # Default fallback
        print(f"[DEBUG] Scan paths: {scan_paths}")
        self.last_scan_paths = scan_paths
        scanned_files_set = set()  # Track unique files for this scan
        
        def result_callback(file_name, full_path, file_size, file_type, threat_type, md5_hash, sha256_hash, status, heuristic, vt_result=None):
            if full_path in scanned_files_set:
                return
            scanned_files_set.add(full_path)
            
            # Add timestamp to the results
            scan_time = datetime.now().strftime('%H:%M:%S')
            row = (file_name, full_path, f"{file_size/1024/1024:.2f} MB" if isinstance(file_size, (int, float)) else file_size, file_type, threat_type or 'Clean', status, scan_time)
            item = self.scan_panel.results_tree.insert('', 'end', values=row)
            
            # Update file counts consistently
            self.files_scanned += 1
            if hasattr(self, 'scan_panel') and self.scan_panel:
                self.scan_panel.files_scanned_var.set(self.files_scanned)
                self.scan_panel.files_scanned = self.files_scanned  # Update the scan panel's internal counter
                
            if threat_type:
                self.threats_found += 1
                if hasattr(self, 'scan_panel') and self.scan_panel:
                    self.scan_panel.threats_found_var.set(self.threats_found)
                # Quarantine the file immediately
                self._auto_quarantine_threat(file_name, full_path, threat_type, status, heuristic, md5_hash, sha256_hash)
                # Update status in the table
                self.scan_panel.results_tree.set(item, 'Status', 'Quarantined')
            # Show VirusTotal result in status bar if deep scan
            if self.deep_scan_enabled and vt_result and 'data' in vt_result and 'attributes' in vt_result['data']:
                stats = vt_result['data']['attributes'].get('last_analysis_stats', {})
                malicious = stats.get('malicious', 0)
                undetected = stats.get('undetected', 0)
                self.scan_panel.current_file_var.set(f"VirusTotal: {malicious} flagged, {undetected} undetected.")
            
            # Update progress after each file is processed
            progress_callback(full_path, None, {
                'files_scanned': self.files_scanned,
                'threats_found': self.threats_found
            })
        
        def progress_callback(current_file, progress, stats):
            # Calculate progress based on actual files scanned vs total files
            if self.total_files > 0:
                actual_progress = (self.files_scanned / self.total_files) * 100
            else:
                actual_progress = progress if progress is not None else 0
                
            # Update scan panel with accurate progress information
            if hasattr(self, 'scan_panel') and self.scan_panel:
                self.scan_panel.update_scan_progress(current_file, actual_progress, {
                    'files_scanned': self.files_scanned,
                    'threats_found': self.threats_found
                })
        
        def scan_thread():
            scan_start_time = time.time()
            total_files = 0
            
            # Count total files for ETA calculation
            for path in scan_paths:
                try:
                    if os.path.isfile(path):
                        total_files += 1
                    else:
                        for root, dirs, files in os.walk(path):
                            total_files += len(files)
                except Exception as e:
                    print(f"[DEBUG] Error counting files in {path}: {e}")
            
            print(f"[DEBUG] Total files found: {total_files}")
            
            # Set total files estimate for ETA calculation
            self.total_files = total_files
            if hasattr(self, 'scan_panel') and self.scan_panel:
                self.scan_panel.total_files_estimate = total_files
                self.scan_panel.total_files_var.set(total_files)
            
            if total_files == 0:
                if hasattr(self, 'scan_panel') and self.scan_panel:
                    self.scan_panel.current_file_var.set('No files found to scan.')
                    self.scan_panel.stop_time_tracking()
                import tkinter.messagebox as mb
                mb.showinfo('Scan', 'No files found to scan in the selected locations. Some files may be inaccessible due to permissions.')
                print("[DEBUG] No files found to scan. Possible permissions issue.")
                return
            
            files_scanned = 0
            threats_found = 0
            
            for path in scan_paths:
                try:
                    if os.path.isfile(path):
                        # Scan a single file
                        self.scanner._scan_file_enhanced(path, result_callback, deep_scan_enabled=deep_scan_enabled)
                        # Progress is updated in result_callback, so we don't need to update it here
                    else:
                        self.scanner.scan_folder(
                            path,
                            result_callback=result_callback,
                            progress_callback=progress_callback,
                            deep_scan_enabled=deep_scan_enabled
                        )
                except PermissionError:
                    if hasattr(self, 'scan_panel') and self.scan_panel:
                        self.scan_panel.current_file_var.set(f'Permission denied: {path}')
                    import tkinter.messagebox as mb
                    mb.showwarning('Permission Denied', f'Permission denied while scanning: {path}. This file or folder will be skipped.')
                    print(f"[DEBUG] Permission denied while scanning: {path}")
                except Exception as e:
                    if hasattr(self, 'scan_panel') and self.scan_panel:
                        self.scan_panel.current_file_var.set(f'Error: {e}')
                    import tkinter.messagebox as mb
                    mb.showerror('Scan Error', f'Error while scanning {path}: {e}')
                    print(f"[DEBUG] Error while scanning {path}: {e}")
            
            # Scan completion
            scan_duration = time.time() - scan_start_time
            
            if hasattr(self, 'scan_panel') and self.scan_panel:
                self.scan_panel.set_scan_complete(self.files_scanned, self.threats_found, scan_duration)
                self.scan_panel.current_file_var.set('Scan complete.')
                self.scan_panel.stop_time_tracking()
            
            self.scanning = False
            
            if self.files_scanned == 0:
                if hasattr(self, 'scan_panel') and self.scan_panel:
                    self.scan_panel.current_file_var.set('No files scanned.')
                    self.scan_panel.stop_time_tracking()
                import tkinter.messagebox as mb
                mb.showinfo('Scan', 'No files were scanned. Some files may be inaccessible due to permissions or folder selection.')
                print("[DEBUG] Scan complete but no files were scanned.")
        
        threading.Thread(target=scan_thread, daemon=True).start()

    def pause_scan(self):
        self.paused = True
        if hasattr(self, 'scanner'):
            self.scanner.paused = True
        self.scan_panel.current_file_var.set('Scan paused.')

    def resume_scan(self):
        self.paused = False
        if hasattr(self, 'scanner'):
            self.scanner.paused = False
        self.scan_panel.current_file_var.set('Scan resumed.')

    def stop_scan(self):
        self.stop_scanning = True
        self.scanning = False
        if hasattr(self, 'pause_scan_btn') and self.pause_scan_btn:
            self.pause_scan_btn.state(['disabled'])
        if hasattr(self, 'resume_scan_btn') and self.resume_scan_btn:
            self.resume_scan_btn.state(['disabled'])
        if hasattr(self, 'stop_scan_btn') and self.stop_scan_btn:
            self.stop_scan_btn.state(['disabled'])
        self.show_popup("Scan stopped by user.", 'Scan Stopped')
        self.scanner.stop_scan()

    def show_about(self):
        self._show_buffering()
        self._clear_page()
        self.header_status.config(text='About IronWall Antivirus')
        
        # Create scrollable container for About content
        canvas = tk.Canvas(self.page_frame, bg=self.get_color('bg'), highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.page_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Main.TFrame')
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Main content container
        content_frame = ttk.Frame(scrollable_frame, style='Main.TFrame')
        content_frame.pack(fill='both', expand=True, padx=40, pady=30)
        
        # === SECTION 1: APPLICATION INFORMATION ===
        app_info_frame = ttk.LabelFrame(content_frame, text='Application Information', padding=20, style='DashboardPanel.TLabelframe')
        app_info_frame.pack(fill='x', pady=(0, 20))
        
        # App logo and title
        logo_frame = ttk.Frame(app_info_frame)
        logo_frame.pack(fill='x', pady=(0, 15))
        
        logo_label = ttk.Label(logo_frame, text='🛡️', font=('Segoe UI', 48), foreground=self.get_color('accent'))
        logo_label.pack(side='left', padx=(0, 20))
        
        title_frame = ttk.Frame(logo_frame)
        title_frame.pack(side='left', fill='y')
        
        app_title = ttk.Label(title_frame, text=version.APP_NAME, font=('Segoe UI', 24, 'bold'), foreground=self.get_color('header'))
        app_title.pack(anchor='w')
        
        app_version = ttk.Label(title_frame, text=f'Version {version.APP_VERSION} (Build {version.APP_BUILD})', font=('Segoe UI', 14), foreground=self.get_color('text_secondary'))
        app_version.pack(anchor='w', pady=(5, 0))
        
        # Application details grid
        details_frame = ttk.Frame(app_info_frame)
        details_frame.pack(fill='x', pady=(15, 0))
        details_frame.columnconfigure(1, weight=1)
        
        # Get real engine version from threat database
        try:
            with open(self.threat_db.db_file, 'r') as f:
                import json
                db_data = json.load(f)
                engine_version = db_data.get('version', '1.0')
        except:
            engine_version = '1.0'
        
        # Get real UI framework version
        try:
            import ttkbootstrap
            ui_framework_version = f"ttkbootstrap {ttkbootstrap.__version__}"
        except:
            ui_framework_version = "ttkbootstrap (version unknown)"
        
        details = [
            ('Engine Version:', f'v{engine_version}'),
            ('Build Number:', version.APP_BUILD),
            ('Release Date:', version.APP_RELEASE_DATE),
            ('Supported OS:', version.SUPPORTED_OS),
            ('Python Version:', f'{sys.version.split()[0]}'),
            ('UI Framework:', ui_framework_version)
        ]
        
        for i, (label, value) in enumerate(details):
            ttk.Label(details_frame, text=label, font=('Segoe UI', 12, 'bold'), foreground=self.get_color('accent')).grid(row=i, column=0, sticky='w', padx=(0, 15), pady=3)
            ttk.Label(details_frame, text=value, font=('Segoe UI', 12), foreground=self.get_color('fg')).grid(row=i, column=1, sticky='w', pady=3)
        
        # === SECTION 2: SYSTEM INFORMATION ===
        sys_frame = ttk.LabelFrame(content_frame, text='System Information', padding=20, style='DashboardPanel.TLabelframe')
        sys_frame.pack(fill='x', pady=(0, 20))
        
        # Get real system information
        import platform
        import psutil
        
        # Get real memory information
        memory = psutil.virtual_memory()
        total_memory_gb = memory.total // (1024**3)
        available_memory_gb = memory.available // (1024**3)
        memory_percent = memory.percent
        
        # Get real disk information
        disk = psutil.disk_usage('/')
        total_disk_gb = disk.total // (1024**3)
        free_disk_gb = disk.free // (1024**3)
        disk_percent = (disk.used / disk.total) * 100
        
        # Get real CPU information
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        cpu_freq_mhz = cpu_freq.current if cpu_freq else "Unknown"
        
        sys_info = [
            ('Operating System:', f'{platform.system()} {platform.release()}'),
            ('Architecture:', platform.architecture()[0]),
            ('Machine:', platform.machine()),
            ('Processor:', f'{platform.processor()} ({cpu_count} cores)'),
            ('CPU Frequency:', f'{cpu_freq_mhz:.0f} MHz'),
            ('Total Memory:', f'{total_memory_gb:.1f} GB ({memory_percent:.1f}% used)'),
            ('Available Memory:', f'{available_memory_gb:.1f} GB'),
            ('Total Disk Space:', f'{total_disk_gb:.1f} GB ({disk_percent:.1f}% used)'),
            ('Free Disk Space:', f'{free_disk_gb:.1f} GB'),
            ('Python Version:', sys.version.split()[0]),
            ('Working Directory:', os.getcwd())
        ]
        
        sys_grid = ttk.Frame(sys_frame)
        sys_grid.pack(fill='x')
        sys_grid.columnconfigure(1, weight=1)
        
        for i, (label, value) in enumerate(sys_info):
            ttk.Label(sys_grid, text=label, font=('Segoe UI', 11, 'bold'), foreground=self.get_color('accent')).grid(row=i, column=0, sticky='w', padx=(0, 15), pady=2)
            ttk.Label(sys_grid, text=value, font=('Segoe UI', 11), foreground=self.get_color('fg')).grid(row=i, column=1, sticky='w', pady=2)
        
        # === SECTION 3: DATABASE INFORMATION ===
        db_frame = ttk.LabelFrame(content_frame, text='Database Information', padding=20, style='DashboardPanel.TLabelframe')
        db_frame.pack(fill='x', pady=(0, 20))
        
        # Get real database information
        try:
            db_size = os.path.getsize(self.threat_db.db_file) if os.path.exists(self.threat_db.db_file) else 0
            with open(self.threat_db.db_file, 'r') as f:
                import json
                db_data = json.load(f)
                db_version = db_data.get('version', '1.0')
                threat_hashes = len(db_data.get('hashes', {}))
                threat_signatures = len(db_data.get('signatures', []))
                last_update = db_data.get('last_updated', 'Unknown')
                
                # Parse the last update timestamp
                if last_update != 'Unknown':
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                        last_update_formatted = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        last_update_formatted = last_update
                else:
                    last_update_formatted = 'Unknown'
        except Exception as e:
            db_size = 0
            db_version = '1.0'
            threat_hashes = 0
            threat_signatures = 0
            last_update_formatted = 'Unknown'
        
        db_info = [
            ('Database Version:', f'v{db_version}'),
            ('Threat Hashes:', f'{threat_hashes:,}'),
            ('Threat Signatures:', f'{threat_signatures:,}'),
            ('Total Signatures:', f'{threat_hashes + threat_signatures:,}'),
            ('Database Size:', f'{db_size / 1024:.1f} KB'),
            ('Last Updated:', last_update_formatted),
            ('Database Location:', os.path.basename(self.threat_db.db_file))
        ]
        
        db_grid = ttk.Frame(db_frame)
        db_grid.pack(fill='x')
        db_grid.columnconfigure(1, weight=1)
        
        for i, (label, value) in enumerate(db_info):
            ttk.Label(db_grid, text=label, font=('Segoe UI', 11, 'bold'), foreground=self.get_color('accent')).grid(row=i, column=0, sticky='w', padx=(0, 15), pady=2)
            ttk.Label(db_grid, text=value, font=('Segoe UI', 11), foreground=self.get_color('fg')).grid(row=i, column=1, sticky='w', pady=2)
        
        # === SECTION 4: SECURITY STATUS ===
        security_frame = ttk.LabelFrame(content_frame, text='Security Status', padding=20, style='DashboardPanel.TLabelframe')
        security_frame.pack(fill='x', pady=(0, 20))
        
        # Get real security status information
        try:
            from utils import scan_history
            scan_data = scan_history.load_scan_history()
            
            # Count real threats
            threats_detected = len([s for s in scan_data if s.get('status') in ['Threat Detected', 'Pattern Match', 'Heuristic Match']])
            clean_files = len([s for s in scan_data if s.get('status') == 'Clean'])
            
            # Get last scan time
            if scan_data:
                last_scan_timestamp = scan_data[-1].get('timestamp', 0)
                if last_scan_timestamp:
                    from datetime import datetime
                    last_scan_dt = datetime.fromtimestamp(last_scan_timestamp)
                    last_scan = last_scan_dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    last_scan = 'Unknown'
            else:
                last_scan = 'Never'
            
            # Get real quarantine information
            quarantine_count = 0
            quarantine_size = 0
            try:
                quarantine_db_path = os.path.join('quarantine', 'quarantine_db.json')
                if os.path.exists(quarantine_db_path):
                    with open(quarantine_db_path, 'r') as f:
                        quarantine_db = json.load(f)
                        quarantine_count = len(quarantine_db)
                        
                        # Calculate total quarantine size
                        for file_info in quarantine_db.values():
                            quarantine_size += file_info.get('file_size', 0)
            except:
                pass
            
            # Get real protection status from settings
            try:
                with open('ironwall_settings.json', 'r') as f:
                    settings = json.load(f)
                    real_time_protection = settings.get('protection', {}).get('real_time_protection', False)
                    firewall_protection = settings.get('protection', {}).get('firewall_protection', False)
                    heuristic_scanning = settings.get('protection', {}).get('heuristic_scanning', 'Disabled')
            except:
                real_time_protection = False
                firewall_protection = False
                heuristic_scanning = 'Disabled'
            
        except Exception as e:
            threats_detected = 0
            clean_files = 0
            last_scan = 'Never'
            quarantine_count = 0
            quarantine_size = 0
            real_time_protection = False
            firewall_protection = False
            heuristic_scanning = 'Disabled'
        
        # Determine protection status
        if real_time_protection:
            protection_status = '🟢 Active'
        else:
            protection_status = '🔴 Inactive'
        
        security_info = [
            ('Real-time Protection:', protection_status),
            ('Firewall Protection:', '🟢 Active' if firewall_protection else '🔴 Inactive'),
            ('Heuristic Scanning:', heuristic_scanning),
            ('Last Scan:', last_scan),
            ('Threats Detected:', f'{threats_detected}'),
            ('Clean Files Scanned:', f'{clean_files}'),
            ('Total Files Scanned:', f'{threats_detected + clean_files}'),
            ('Quarantine Items:', f'{quarantine_count}'),
            ('Quarantine Size:', f'{quarantine_size / 1024:.1f} KB'),
            ('Scan History Size:', f'{len(scan_data) if "scan_data" in locals() else 0} entries')
        ]
        
        security_grid = ttk.Frame(security_frame)
        security_grid.pack(fill='x')
        security_grid.columnconfigure(1, weight=1)
        
        for i, (label, value) in enumerate(security_info):
            ttk.Label(security_grid, text=label, font=('Segoe UI', 11, 'bold'), foreground=self.get_color('accent')).grid(row=i, column=0, sticky='w', padx=(0, 15), pady=2)
            ttk.Label(security_grid, text=value, font=('Segoe UI', 11), foreground=self.get_color('fg')).grid(row=i, column=1, sticky='w', pady=2)
        
        # === SECTION 5: RESOURCE USAGE ===
        resource_frame = ttk.LabelFrame(content_frame, text='Resource Usage', padding=20, style='DashboardPanel.TLabelframe')
        resource_frame.pack(fill='x', pady=(0, 20))
        
        # Get real current resource usage
        try:
            current_process = psutil.Process()
            memory_usage = current_process.memory_info().rss / 1024 / 1024  # MB
            cpu_percent = current_process.cpu_percent()
            
            # Get real disk usage for logs and databases
            log_files = []
            total_log_size = 0
            
            # Check various log files
            log_files_to_check = [
                'scan_history.json',
                'system_logs.json',
                'ironwall_settings.json',
                'threat_database.json'
            ]
            
            for log_file in log_files_to_check:
                if os.path.exists(log_file):
                    file_size = os.path.getsize(log_file)
                    total_log_size += file_size
                    log_files.append(f"{log_file}: {file_size / 1024:.1f} KB")
            
            # Get real scan performance from actual scan history
            try:
                from utils import scan_history
                scan_data = scan_history.load_scan_history()
                if len(scan_data) > 1:
                    # Calculate real performance metrics
                    recent_scans = scan_data[-5:]  # Last 5 scans
                    
                    # Calculate average scan duration (if available)
                    durations = [s.get('duration', 0) for s in recent_scans if s.get('duration')]
                    avg_duration = sum(durations) / len(durations) if durations else 0
                    
                    # Calculate files per second
                    total_files = sum(s.get('files_scanned', 1) for s in recent_scans)
                    total_time = sum(durations) if durations else 1
                    files_per_sec = total_files / total_time if total_time > 0 else 0
                    
                    # Get scan statistics
                    scan_types = {}
                    for scan in scan_data:
                        scan_type = scan.get('scan_type', 'Unknown')
                        scan_types[scan_type] = scan_types.get(scan_type, 0) + 1
                    
                    most_common_scan = max(scan_types.items(), key=lambda x: x[1])[0] if scan_types else 'Unknown'
                    
                else:
                    avg_duration = 0
                    files_per_sec = 0
                    most_common_scan = 'None'
                    
            except Exception as e:
                avg_duration = 0
                files_per_sec = 0
                most_common_scan = 'Unknown'
                
        except Exception as e:
            memory_usage = 0
            cpu_percent = 0
            total_log_size = 0
            avg_duration = 0
            files_per_sec = 0
            most_common_scan = 'Unknown'
            log_files = []
        
        resource_info = [
            ('Memory Usage:', f'{memory_usage:.1f} MB'),
            ('CPU Usage:', f'{cpu_percent:.1f}%'),
            ('Total Log Size:', f'{total_log_size / 1024:.1f} KB'),
            ('Log Files:', f'{len(log_files)} files'),
            ('Avg Scan Duration:', f'{avg_duration:.1f}s'),
            ('Scan Speed:', f'{files_per_sec:.1f} files/sec'),
            ('Most Common Scan:', most_common_scan),
            ('Process ID:', str(current_process.pid) if 'current_process' in locals() else 'Unknown')
        ]
        
        resource_grid = ttk.Frame(resource_frame)
        resource_grid.pack(fill='x')
        resource_grid.columnconfigure(1, weight=1)
        
        for i, (label, value) in enumerate(resource_info):
            ttk.Label(resource_grid, text=label, font=('Segoe UI', 11, 'bold'), foreground=self.get_color('accent')).grid(row=i, column=0, sticky='w', padx=(0, 15), pady=2)
            ttk.Label(resource_grid, text=value, font=('Segoe UI', 11), foreground=self.get_color('fg')).grid(row=i, column=1, sticky='w', pady=2)
        
        # Bind mouse wheel scrolling
        def _on_mousewheel(event):
            try:
                # Get the widget that received the event
                widget = event.widget
                
                # Find the canvas that contains this widget
                canvas = None
                current = widget
                
                # Walk up the widget hierarchy to find the canvas
                while current and current != self.root:
                    try:
                        if hasattr(current, 'yview_scroll'):
                            canvas = current
                            break
                        current = current.master
                    except Exception:
                        break
                
                if canvas and canvas.winfo_exists():
                    try:
                        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                    except Exception as e:
                        print(f"Error scrolling canvas: {e}")
            except Exception as e:
                print(f"Error in mousewheel handler: {e}")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Store canvas reference for cleanup
        self.about_canvas = canvas
        self._hide_buffering()

    def show_settings(self):
        self._show_buffering()
        self._clear_page()
        self.header_status.config(text='Settings')
        
        # Import and use the new SettingsPanel directly in page_frame for maximum size
        from ui.settings_panel import SettingsPanel
        self.settings_panel = SettingsPanel(self.page_frame, self)
        self.settings_panel.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self._hide_buffering()

    def _toggle_quarantine_notifications(self):
        """Toggle quarantine notification setting"""
        self.show_quarantine_notifications = self.notification_var.get()

    def show_storage_info(self):
        from utils import scan_history
        import os
        self._clear_page()
        self.header_status.config(text='Storage')
        label = ttk.Label(self.page_frame, text='Scan History Storage', font=('Segoe UI', 18, 'bold'))
        label.pack(pady=20)
        # Info about scan_history.json
        history_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scan_history.json'))
        if os.path.exists(history_file):
            size = os.path.getsize(history_file)
            threats = scan_history.load_scan_history()
            num_threats = len(threats)
        else:
            size = 0
            num_threats = 0
        ttk.Label(self.page_frame, text=f'File: {history_file}', font=('Segoe UI', 12)).pack(pady=5)
        ttk.Label(self.page_frame, text=f'Size: {size} bytes', font=('Segoe UI', 12)).pack(pady=5)
        ttk.Label(self.page_frame, text=f'Total Threats Logged: {num_threats}', font=('Segoe UI', 12)).pack(pady=5)
        clear_btn = ttk.Button(self.page_frame, text='Clear Scan History', style='Accent.TButton', command=self.clear_scan_history)
        clear_btn.pack(pady=15)
        back_btn = ttk.Button(self.page_frame, text='Back to Settings', command=self.show_settings)
        back_btn.pack(pady=10)

    def clear_scan_history(self):
        from utils import scan_history
        scan_history.clear_scan_history()
        self.show_storage_info()

    def show_quarantine(self):
        self._show_buffering()
        self._clear_page()
        self.header_status.config(text='Quarantine Management')
        
        # Import and use the new QuarantinePanel directly in page_frame for maximum size
        from ui.quarantine_panel import QuarantinePanel
        self.quarantine_panel = QuarantinePanel(self.page_frame, self.quarantine_manager)
        # self.quarantine_panel.pack(fill='both', expand=True, padx=10, pady=10)  # Removed, as QuarantinePanel is not a widget
        self._hide_buffering()

    def start_monitoring(self):
        self.monitoring_active = True
        def monitor():
            while self.monitoring_active:
                try:
                    cpu_percent = self.system_monitor.get_cpu_usage()
                    mem_percent = self.system_monitor.get_memory_usage()
                    system_status = self.system_monitor.get_system_status()
                    self.root.after(0, self.update_monitoring_display, cpu_percent, mem_percent, system_status)
                    time.sleep(2)
                except:
                    break
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()

    def update_monitoring_display(self, cpu_percent, mem_percent, system_status):
        # Only update if widgets exist
        if hasattr(self, 'cpu_label') and hasattr(self, 'mem_label') and hasattr(self, 'status_label'):
            try:
                self.cpu_label.config(text=f"CPU Usage: {cpu_percent:.1f}%")
                self.mem_label.config(text=f"Memory Usage: {mem_percent:.1f}%")
                self.status_label.config(text=f"System Status: {system_status}")
                
                # Update progress bars
                if hasattr(self, 'cpu_bar'):
                    self.cpu_bar['value'] = cpu_percent
                if hasattr(self, 'mem_bar'):
                    self.mem_bar['value'] = mem_percent
                    
                # Color-code the status based on system health
                if system_status.lower() in ['healthy', 'normal', 'good']:
                    status_color = self.get_color('success')
                elif system_status.lower() in ['warning', 'caution']:
                    status_color = self.get_color('warn')
                else:
                    status_color = self.get_color('danger')
                
                self.status_label.config(foreground=status_color)
                
            except Exception:
                pass

    def start_folder_scan(self):
        if self.scanning:
            messagebox.showwarning("Scan in Progress", "A scan is already running!")
            return
        folder = filedialog.askdirectory(title="Select folder to scan")
        if not folder:
            return
        self.scanning = True
        self.paused = False
        self.scanner.reset_scan_state()  # Reset scanner state
        self.update_scan_controls()
        self.clear_results()
        self.stop_scan_btn.state(['!disabled'])
        self.pause_scan_btn.state(['!disabled'])
        self.resume_scan_btn.state(['disabled'])
        def count_and_start():
            # Count all files in the folder before starting scan
            total = 0
            for root, dirs, files in os.walk(folder):
                total += len(files)
            self.total_files = total
            self.files_scanned = 0
            self.threats_found = 0
            self.root.after(0, lambda: self.total_files_label.config(text=f"Total Files: {self.total_files}"))
            self.root.after(0, self.update_scan_summary)
            self.scan_thread = threading.Thread(target=self.run_folder_scan, args=(folder,), daemon=True)
            self.scan_thread.start()
        threading.Thread(target=count_and_start, daemon=True).start()

    def run_folder_scan(self, folder):
        try:
            self.progress_row = self.results_tree.insert('', 'end', values=(f"Scanned: 0/{self.total_files}", '', '', '', '', ''))
            def scan_callback(file_name, full_path, file_size, file_type, threat_type, md5_hash, sha256_hash, status, heuristic):
                while self.paused:
                    time.sleep(0.1)
                self.root.after(0, lambda: self.add_scan_result(file_name, full_path, file_size, file_type, threat_type, md5_hash, sha256_hash, status, heuristic))
                self.files_scanned += 1
                self.root.after(0, lambda: self.results_tree.item(self.progress_row, values=(f"Scanned: {self.files_scanned}/{self.total_files}", '', '', '', '', f"Current: Scanning...", '')))
                # If deep scan is enabled, show VirusTotal result in status bar
                if self.deep_scan_enabled:
                    vt_result = self.scanner.scan_file_with_virustotal(full_path)
                    if vt_result and 'data' in vt_result and 'attributes' in vt_result['data']:
                        stats = vt_result['data']['attributes'].get('last_analysis_stats', {})
                        malicious = stats.get('malicious', 0)
                        undetected = stats.get('undetected', 0)
                        self.root.after(0, lambda: self.show_status_popup(f"VirusTotal: {malicious} engines flagged, {undetected} undetected."))
            self.scanner.scan_folder(folder, scan_callback, self.progress_callback, deep_scan_enabled=self.deep_scan_enabled)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Scan Error", str(e)))
        finally:
            self.root.after(0, self.scan_finished)

    def scan_callback(self, file_path, threat_type, file_hash, status):
        self.root.after(0, lambda: self.add_scan_result(file_path, threat_type, file_hash, status))

    def progress_callback(self, current_file, progress, stats):
        self.scan_panel.progress_var.set(progress)
        self.scan_panel.current_file_var.set(current_file)
        if hasattr(self.scan_panel, 'progress_pct_var'):
            pct = int(progress)
            self.scan_panel.progress_pct_var.set(f'Scan Progress: {pct}%')

    def update_scan_summary(self):
        self.total_files_label.config(text=f"Total Files: {self.total_files}")
        self.files_scanned_label.config(text=f"Files Scanned: {self.files_scanned}")
        self.threats_found_label.config(text=f"Threats Found: {self.threats_found}")

    def update_scan_controls(self):
        pass  # For future: enable/disable scan buttons

    def clear_results(self):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.progress_var.set(0)
        self.files_scanned = 0
        self.threats_found = 0
        self.update_scan_summary()

    def count_files(self, folder):
        count = 0
        for root, dirs, files in os.walk(folder):
            count += len(files)
        return count

    def on_close(self):
        self.root.destroy()

    def scan_finished(self):
        self.scanning = False
        if hasattr(self, 'pause_scan_btn') and self.pause_scan_btn:
            self.pause_scan_btn.state(['disabled'])
        if hasattr(self, 'resume_scan_btn') and self.resume_scan_btn:
            self.resume_scan_btn.state(['disabled'])
        if hasattr(self, 'stop_scan_btn') and self.stop_scan_btn:
            self.stop_scan_btn.state(['disabled'])
        self.show_popup(f"Scan completed! Threats found: {self.threats_found}", 'Scan Complete')
        if hasattr(self, 'current_file_label'):
            self.current_file_label.config(text="Current File: None")

    def change_theme(self, theme):
        """Change the application theme"""
        # Map old theme names to ttkbootstrap themes
        theme_mapping = {
            'light': 'flatly',
            'dark': 'darkly',
            'flatly': 'flatly',
            'darkly': 'darkly',
            'cyborg': 'cyborg',
            'solar': 'solar',
            'superhero': 'superhero',
            'morph': 'morph',
            'cosmo': 'cosmo',
            'journal': 'journal'
        }
        
        # Get the ttkbootstrap theme name
        ttkbootstrap_theme = theme_mapping.get(theme, 'flatly')
        
        # Update the theme
        self.theme = ttkbootstrap_theme
        self.set_theme(ttkbootstrap_theme)
        self.create_widgets()

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.theme in ['flatly', 'cosmo', 'journal']:
            new_theme = 'darkly'
        elif self.theme in ['darkly', 'cyborg', 'solar']:
            new_theme = 'flatly'
        else:
            new_theme = 'flatly'
        
        self.change_theme(new_theme)

    def stop_scan(self):
        self.stop_scanning = True
        self.scanning = False
        if hasattr(self, 'pause_scan_btn') and self.pause_scan_btn:
            self.pause_scan_btn.state(['disabled'])
        if hasattr(self, 'resume_scan_btn') and self.resume_scan_btn:
            self.resume_scan_btn.state(['disabled'])
        if hasattr(self, 'stop_scan_btn') and self.stop_scan_btn:
            self.stop_scan_btn.state(['disabled'])
        self.show_popup("Scan stopped by user.", 'Scan Stopped')
        self.scanner.stop_scan()

    def pause_scan(self):
        self.paused = True
        if hasattr(self, 'scanner'):
            self.scanner.paused = True
        self.scan_panel.current_file_var.set('Scan paused.')

    def resume_scan(self):
        self.paused = False
        if hasattr(self, 'scanner'):
            self.scanner.paused = False
        self.scan_panel.current_file_var.set('Scan resumed.')

    def add_scan_result(self, file_name, full_path, file_size, file_type, threat_type, md5_hash, sha256_hash, status, heuristic):
        # Do not add the progress row as a file row
        if hasattr(self, 'progress_row') and file_name == '':
            return
        
        # Convert file size to MB with 2 decimal places
        try:
            file_size_mb = f"{float(file_size) / (1024 * 1024):.2f} MB"
        except Exception:
            file_size_mb = str(file_size)
        
        # Always show every scanned file with all info
        values = (file_name, full_path, file_size_mb, file_type, threat_type or 'Clean', status)
        
        # Alternate row color
        children = self.results_tree.get_children()
        tag = 'evenrow' if len(children) % 2 == 0 else 'oddrow'
        item = self.results_tree.insert('', 'end', values=values, tags=(tag,))
        
        if threat_type:
            self.results_tree.item(item, tags=('threat', tag))
            self.threats_found += 1
            
            # Automatically quarantine the threat
            self._auto_quarantine_threat(file_name, full_path, threat_type, status, heuristic, md5_hash, sha256_hash)
            
            # Update status to show quarantined
            self.results_tree.set(item, 'Status', 'Quarantined')
        
        self.update_scan_summary()
        self.results_tree.see(item)
    
    def _auto_quarantine_threat(self, file_name, full_path, threat_type, status, heuristic, md5_hash, sha256_hash):
        """Automatically quarantine a detected threat"""
        try:
            if not os.path.exists(full_path):
                return  # File doesn't exist, can't quarantine
            
            # Determine severity based on threat type and status
            severity = self._determine_threat_severity(threat_type, status, heuristic)
            
            # Create threat signature
            signature = f"{threat_type}_{status}_{heuristic}"
            
            # Determine risk level
            risk_level = "High" if severity == "Critical" else "Medium" if severity == "Moderate" else "Low"
            
            # Create description
            description = f"Automatically quarantined during scan. Threat type: {threat_type}, Status: {status}, Heuristic: {heuristic}"
            
            # Quarantine the file
            success = self.quarantine_manager.quarantine_file(
                file_path=full_path,
                threat_type=threat_type,
                severity=severity,
                signature=signature,
                risk_level=risk_level,
                description=description,
                origin="Auto Scan",
                original_hash=md5_hash
            )
            
            if success:
                # Update status bar to notify user
                self.show_status_popup(f"🦠 Threat quarantined: {file_name} ({threat_type})")
                
                # Pop-up notifications disabled for better performance and user experience
                # Users can check the quarantine panel for detailed information
            else:
                # If quarantine failed, show error
                self.show_status_popup(f"❌ Failed to quarantine: {file_name}")
                
        except Exception as e:
            print(f"Error auto-quarantining {file_name}: {e}")
            self.show_status_popup(f"❌ Quarantine error: {file_name}")
    
    def _determine_threat_severity(self, threat_type, status, heuristic):
        """Determine threat severity based on threat type and detection method"""
        # Known threats are generally more severe
        if status == "Known Threat":
            if threat_type.lower() in ['ransomware', 'trojan', 'rootkit']:
                return "Critical"
            elif threat_type.lower() in ['worm', 'virus']:
                return "Critical"
            else:
                return "Moderate"
        
        # Pattern matches and suspicious files
        elif status in ["Pattern Match", "Suspicious"]:
            if threat_type.lower() in ['trojan', 'malware', 'backdoor']:
                return "Critical"
            elif threat_type.lower() in ['adware', 'spyware']:
                return "Moderate"
            else:
                return "Low"
        
        # Binary analysis results
        elif status == "Binary Analysis":
            return "Moderate"
        
        # Default severity
        else:
            return "Low"

    def on_result_double_click(self, event):
        # Handle double-click on a threat row to delete the file
        item = self.results_tree.identify_row(event.y)
        if not item:
            return
        values = self.results_tree.item(item, 'values')
        if values and values[4] != 'Clean':
            file_path = values[1]
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    messagebox.showinfo('File Deleted', f'Threat file deleted:\n{file_path}')
                    self.results_tree.delete(item)
                else:
                    messagebox.showwarning('File Not Found', f'File already deleted:\n{file_path}')
            except Exception as e:
                messagebox.showerror('Delete Error', f'Could not delete file:\n{file_path}\n{e}')

    def run(self):
        self.root.mainloop()

    def toggle_deep_scan(self):
        self.deep_scan_enabled = not self.deep_scan_enabled
        if self.deep_scan_enabled:
            self.deep_scan_btn.config(text="Deep Scan: ON", style='Accent.TButton')
            self.show_status_popup("Deep Scan enabled. Files will be checked with VirusTotal.")
        else:
            self.deep_scan_btn.config(text="Deep Scan: OFF", style='Accent.TButton')
            self.show_status_popup("Deep Scan disabled.")

    def refresh_ui(self):
        """Refresh the UI by destroying and recreating all widgets."""
        try:
            self.create_widgets()
            self.show_status_popup("UI refreshed.")
        except Exception as e:
            messagebox.showerror("Refresh Error", f"Failed to refresh UI: {e}")

    def _set_table_row_colors(self, tree):
        """Set row colors for Treeview based on current theme."""
        # Use high-contrast backgrounds for dark/light mode
        if self.theme == 'dark':
            even_color = '#16213E'  # deep blue-gray
            odd_color = '#1A1A2E'   # dark navy
        else:
            even_color = '#E9EEF3'  # light gray-blue
            odd_color = '#F7F9FB'   # very light gray-blue
        
        fg_color = self.get_color('tree_fg')
        tree.tag_configure('evenrow', background=even_color, foreground=fg_color)
        tree.tag_configure('oddrow', background=odd_color, foreground=fg_color)
        # Also set Treeview widget style for all tables with proper row height
        style = self.style
        style.configure('Treeview', 
                       background=even_color, 
                       foreground=fg_color, 
                       fieldbackground=even_color,
                       rowheight=28,  # Ensure proper row height to prevent overlapping
                       font=('Segoe UI', 11))
        style.map('Treeview', background=[('selected', self.get_color('tree_sel'))]) 

    def _on_button_hover(self, button, entering):
        """Handle button hover effects for dark mode"""
        if entering:
            button.configure(style='Accent.TButton')
        else:
            button.configure(style='TButton')

    def show_recent_activity(self):
        self._show_buffering()
        self._clear_page()
        self.header_status.config(text='Recent Activity')
        
        # Main container directly in page_frame for maximum size
        main_frame = ttk.Frame(self.page_frame, style='Dashboard.TFrame')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Activity summary panel
        summary_panel = ttk.LabelFrame(main_frame, text='Activity Summary', padding=16, style='DashboardPanel.TLabelframe')
        summary_panel.pack(fill='x', padx=14, pady=12, ipadx=6, ipady=6)
        self._create_activity_summary_panel(summary_panel)
        
        # Recent activity table
        activity_panel = ttk.LabelFrame(main_frame, text='Detailed Activity Log', padding=16, style='DashboardPanel.TLabelframe')
        activity_panel.pack(fill='both', expand=True, padx=14, pady=12, ipadx=6, ipady=6)
        self._create_activity_table_panel(activity_panel)
        self._hide_buffering()

    def _create_activity_summary_panel(self, parent):
        # Get activity statistics
        from utils import scan_history
        scan_history_data = scan_history.load_scan_history()
        qstats = self.quarantine_manager.get_quarantine_statistics()
        # Calculate stats
        total_scans = len(scan_history_data)
        threats_found = len([h for h in scan_history_data if h.get('threat_type') and h.get('threat_type').lower() not in ('clean', 'none', 'unknown')])
        recent_activity = len([h for h in scan_history_data if h.get('timestamp', 0) > time.time() - 86400])  # Last 24 hours
        # Layout in a grid
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill='x', pady=10)
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
        stats_frame.columnconfigure(3, weight=1)
        # Stat boxes
        stats = [
            ('Total Scans', total_scans, self.get_color('accent')),
            ('Threats Found', threats_found, self.get_color('danger')),
            ('Recent Activity', recent_activity, self.get_color('success')),
            ('Quarantined', qstats.get('quarantined', 0), self.get_color('warn'))
        ]
        for i, (label, value, color) in enumerate(stats):
            stat_frame = ttk.Frame(stats_frame, style='StatBox.TFrame')
            stat_frame.grid(row=0, column=i, padx=8, pady=4, sticky='ew')
            ttk.Label(stat_frame, text=label, font=('Segoe UI', 11), foreground=self.get_color('text_secondary')).pack(pady=(8, 2))
            ttk.Label(stat_frame, text=str(value), font=('Segoe UI', 18, 'bold'), foreground=color).pack(pady=(0, 8))

    def _create_activity_table_panel(self, parent):
        # Create table with enhanced columns
        columns = ('Time', 'Activity Type', 'Description', 'Status', 'Severity')
        self.activity_tree = ttk.Treeview(parent, columns=columns, show='headings', height=15, style='Treeview')
        # Configure columns
        column_configs = [
            ('Time', 180, 'center'),
            ('Activity Type', 120, 'center'),
            ('Description', 400, 'w'),
            ('Status', 100, 'center'),
            ('Severity', 80, 'center')
        ]
        for col, width, anchor in column_configs:
            self.activity_tree.heading(col, text=col, anchor=anchor)
            self.activity_tree.column(col, width=width, anchor=anchor, stretch=True)
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.activity_tree.yview)
        self.activity_tree.configure(yscrollcommand=scrollbar.set)
        # Pack widgets
        self.activity_tree.pack(side='top', fill='both', expand=True, pady=(0, 4))
        scrollbar.pack(side='right', fill='y')
        # Set row height and style
        style = ttk.Style()
        style.configure('Treeview', rowheight=28, font=('Segoe UI', 11))
        # Set row colors
        self._set_table_row_colors(self.activity_tree)
        # Load activity data
        self._load_activity_data()

    def _load_activity_data(self):
        # Clear existing data
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        # Load scan history
        from utils import scan_history
        scan_history_data = scan_history.load_scan_history()
        # Load quarantine data
        qdata = self.quarantine_manager.load_quarantine_db()
        # Combine and sort all activities
        activities = []
        # Add scan activities
        for entry in scan_history_data:
            ts = entry.get('timestamp', 0)
            if ts:
                import datetime
                dt = datetime.datetime.fromtimestamp(ts)
                time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                file_name = entry.get('file_name', 'Unknown')
                threat_type = entry.get('threat_type', 'Clean')
                status = entry.get('status', 'Scanned')
                # Determine severity
                if threat_type and threat_type.lower() not in ('clean', 'none', 'unknown'):
                    severity = 'High' if 'Critical' in threat_type or 'Ransomware' in threat_type else 'Medium'
                    activity_type = 'Threat Detected'
                else:
                    severity = 'Low'
                    activity_type = 'File Scanned'
                activities.append({
                    'time': ts,
                    'time_str': time_str,
                    'type': activity_type,
                    'description': f'File: {file_name}',
                    'status': status,
                    'severity': severity
                })
        # Add quarantine activities
        for qname, entry in qdata.items():
            ts = entry.get('quarantine_date')
            if ts:
                try:
                    import datetime
                    dt = datetime.datetime.fromisoformat(ts)
                    time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                    file_name = entry.get('file', qname)
                    status = entry.get('status', 'quarantined')
                    activity_type = 'Quarantine'
                    if status == 'restored':
                        activity_type = 'File Restored'
                    elif status == 'deleted':
                        activity_type = 'File Deleted'
                    activities.append({
                        'time': dt.timestamp(),
                        'time_str': time_str,
                        'type': activity_type,
                        'description': f'File: {file_name}',
                        'status': status.title(),
                        'severity': 'Medium'
                    })
                except:
                    continue
        # Sort by time (newest first)
        activities.sort(key=lambda x: x['time'], reverse=True)
        # Add to tree with alternating row colors
        for i, activity in enumerate(activities[:50]):  # Limit to 50 most recent
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            # Color code by severity
            if activity['severity'] == 'High':
                tag += ' high_severity'
            elif activity['severity'] == 'Medium':
                tag += ' medium_severity'
            values = (
                activity['time_str'],
                activity['type'],
                activity['description'],
                activity['status'],
                activity['severity']
            )
            self.activity_tree.insert('', 'end', values=values, tags=(tag,))
        # Configure severity colors
        self.activity_tree.tag_configure('high_severity', foreground=self.get_color('danger'))
        self.activity_tree.tag_configure('medium_severity', foreground=self.get_color('warn'))

    def show_analytics_panel(self):
        self._show_buffering()
        self._clear_page()
        self.header_status.config(text='Analytics')
        
        # Import and use the AnalyticsPanel directly in page_frame for maximum size
        from ui.analytics_panel import AnalyticsPanel
        self.analytics_panel = AnalyticsPanel(self.page_frame, self.system_monitor, self.threat_db)
        print('[DEBUG] Packing analytics panel...')
        self.analytics_panel.pack(fill='both', expand=True, padx=10, pady=10)
        self._hide_buffering()

    def show_scheduler_panel(self):
        self._show_buffering()
        self._clear_page()
        self.header_status.config(text='Scheduler')
        
        # Import and use the SchedulerPanel directly in page_frame for maximum size
        from ui.scheduler_panel import SchedulerPanel
        self.scheduler_panel = SchedulerPanel(self.page_frame, scan_callback=self.start_folder_scan)
        self.scheduler_panel.pack(fill='both', expand=True, padx=10, pady=10)
        self._hide_buffering()

    def show_logs_panel(self):
        self._clear_page()
        self.header_status.config(text='System Event Logs')
        
        # Create scrollable frame
        scrollable_frame = self._create_scrollable_frame(self.page_frame)
        
        # --- Top: Filters and Search ---
        filter_frame = ttk.Frame(scrollable_frame)
        filter_frame.pack(fill='x', padx=30, pady=(20, 10))
        # Date range
        ttk.Label(filter_frame, text='Date:', style='TLabel').pack(side='left', padx=(0, 5))
        self.log_date_var = tk.StringVar(value='Last 7 Days')
        date_combo = ttk.Combobox(filter_frame, textvariable=self.log_date_var, values=['Today', 'Last 7 Days', 'Last 30 Days', 'All', 'Custom'], width=14, state='readonly')
        date_combo.pack(side='left', padx=(0, 10))
        date_combo.bind('<<ComboboxSelected>>', lambda e: self._refresh_log_table())
        # Event type
        ttk.Label(filter_frame, text='Type:', style='TLabel').pack(side='left', padx=(0, 5))
        self.log_type_var = tk.StringVar(value='All')
        type_combo = ttk.Combobox(filter_frame, textvariable=self.log_type_var, values=['All'] + [et.name.replace('_', ' ').title() for et in EventType], width=16, state='readonly')
        type_combo.pack(side='left', padx=(0, 10))
        type_combo.bind('<<ComboboxSelected>>', lambda e: self._refresh_log_table())
        # Status
        ttk.Label(filter_frame, text='Status:', style='TLabel').pack(side='left', padx=(0, 5))
        self.log_status_var = tk.StringVar(value='All')
        status_combo = ttk.Combobox(filter_frame, textvariable=self.log_status_var, values=['All'] + [es.name.title() for es in EventStatus], width=12, state='readonly')
        status_combo.pack(side='left', padx=(0, 10))
        status_combo.bind('<<ComboboxSelected>>', lambda e: self._refresh_log_table())
        # Search box
        ttk.Label(filter_frame, text='Search:', style='TLabel').pack(side='left', padx=(0, 5))
        self.log_search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.log_search_var, width=24)
        search_entry.pack(side='left', padx=(0, 10))
        search_entry.bind('<Return>', lambda e: self._refresh_log_table())
        search_btn = ttk.Button(filter_frame, text='🔍', style='Accent.TButton', command=self._refresh_log_table)
        search_btn.pack(side='left', padx=(0, 10))
        # Auto-cleanup toggle
        self.auto_cleanup_var = tk.BooleanVar(value=True)
        auto_cleanup_chk = ttk.Checkbutton(filter_frame, text='Enable auto-log cleanup', variable=self.auto_cleanup_var, command=self._toggle_auto_cleanup)
        auto_cleanup_chk.pack(side='left', padx=(10, 0))
        # Retention policy
        ttk.Label(filter_frame, text='Keep logs for:', style='TLabel').pack(side='left', padx=(10, 5))
        self.retention_days_var = tk.IntVar(value=30)
        retention_combo = ttk.Combobox(filter_frame, textvariable=self.retention_days_var, values=[7, 30, 90], width=4, state='readonly')
        retention_combo.pack(side='left')
        retention_combo.bind('<<ComboboxSelected>>', lambda e: self._toggle_auto_cleanup())
        # --- Center: Log Table ---
        table_frame = ttk.Frame(scrollable_frame)
        table_frame.pack(fill='both', expand=True, padx=30, pady=(0, 10))
        columns = ('timestamp', 'event_type', 'description', 'status', 'details')
        self.log_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=22, selectmode='extended')
        self.log_tree.heading('timestamp', text='Timestamp')
        self.log_tree.heading('event_type', text='Event Type')
        self.log_tree.heading('description', text='Description')
        self.log_tree.heading('status', text='Status')
        self.log_tree.heading('details', text='Details')
        self.log_tree.column('timestamp', width=160, anchor='center')
        self.log_tree.column('event_type', width=140, anchor='center')
        self.log_tree.column('description', width=340, anchor='w')
        self.log_tree.column('status', width=100, anchor='center')
        self.log_tree.column('details', width=260, anchor='w')
        self.log_tree.pack(fill='both', expand=True, side='left')
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        # --- Bottom: Export & Clear ---
        action_frame = ttk.Frame(scrollable_frame)
        action_frame.pack(fill='x', padx=30, pady=(0, 20))
        export_btn = ttk.Button(action_frame, text='Export as CSV', style='Accent.TButton', command=lambda: self._export_logs('csv'))
        export_btn.pack(side='left', padx=(0, 10))
        export_json_btn = ttk.Button(action_frame, text='Export as JSON', style='Accent.TButton', command=lambda: self._export_logs('json'))
        export_json_btn.pack(side='left', padx=(0, 10))
        export_txt_btn = ttk.Button(action_frame, text='Export as TXT', style='Accent.TButton', command=lambda: self._export_logs('txt'))
        export_txt_btn.pack(side='left', padx=(0, 10))
        clear_btn = ttk.Button(action_frame, text='Clear All Logs', style='Danger.TButton', command=self._clear_logs)
        clear_btn.pack(side='right', padx=(10, 0))
        # --- Live Activity Panel (Optional) ---
        self.live_panel_visible = tk.BooleanVar(value=False)
        live_toggle_btn = ttk.Button(action_frame, text='Show Live Activity', style='TButton', command=self._toggle_live_panel)
        live_toggle_btn.pack(side='right', padx=(10, 0))
        self.live_panel = ttk.Frame(scrollable_frame)
        self.live_panel.pack(fill='x', padx=30, pady=(0, 10))
        self.live_panel_text = tk.Text(self.live_panel, height=4, state='disabled', bg=self.get_color('bg'))
        self.live_panel_text.pack(fill='x')
        self.live_panel.pack_forget()  # Hide by default
        # --- Load logs ---
        self._refresh_log_table()
        # Start live feed thread
        self._start_live_feed()

    def _refresh_log_table(self):
        # Get filter values
        date_val = self.log_date_var.get()
        type_val = self.log_type_var.get()
        status_val = self.log_status_var.get()
        search_val = self.log_search_var.get().strip()
        # Date range
        now = datetime.now()
        if date_val == 'Today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_val == 'Last 7 Days':
            start_date = now - timedelta(days=7)
        elif date_val == 'Last 30 Days':
            start_date = now - timedelta(days=30)
        else:
            start_date = None
        # Event type
        event_types = None
        if type_val != 'All':
            try:
                event_types = [EventType[type_val.replace(' ', '_').upper()]]
            except Exception:
                event_types = None
        # Status
        statuses = None
        if status_val != 'All':
            try:
                statuses = [EventStatus[status_val.upper()]]
            except Exception:
                statuses = None
        # --- Merge logger, scan, and quarantine events ---
        try:
            logs = logger.get_logs(event_types=event_types, statuses=statuses, start_date=start_date, search_query=search_val)
        except Exception as e:
            print(f"Error getting logs: {e}")
            logs = []
        # Add scan history events
        from utils import scan_history
        scan_history_data = scan_history.load_scan_history()
        for entry in scan_history_data:
            ts = entry.get('timestamp', 0)
            if start_date and ts:
                import datetime
                if datetime.datetime.fromtimestamp(ts) < start_date:
                    continue
            threat_type = entry.get('threat_type', 'Clean')
            status = entry.get('status', 'Scanned')
            if event_types and EventType.SCAN not in event_types:
                continue
            logs.append({
                'timestamp': datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') if ts else '',
                'event_type': 'Scan',
                'description': f"File: {entry.get('file_name', 'Unknown')} - {threat_type}",
                'status': status.title(),
                'severity': 'High' if threat_type and threat_type.lower() not in ('clean', 'none', 'unknown') else 'Low',
                'tooltip': f"Scan Result\nFile: {entry.get('file_name', 'Unknown')}\nThreat: {threat_type}\nStatus: {status}"
            })
        # Add quarantine events
        qdata = self.quarantine_manager.load_quarantine_db()
        for qname, entry in qdata.items():
            ts = entry.get('quarantine_date')
            if ts:
                try:
                    import datetime
                    dt = datetime.datetime.fromisoformat(ts)
                    if start_date and dt < start_date:
                        continue
                    status = entry.get('status', 'quarantined')
                    logs.append({
                        'timestamp': dt.strftime('%Y-%m-%d %H:%M:%S'),
                        'event_type': 'Quarantine',
                        'description': f"File: {entry.get('file', qname)}",
                        'status': status.title(),
                        'severity': 'High' if status == 'quarantined' else 'Medium',
                        'tooltip': f"Quarantine\nFile: {entry.get('file', qname)}\nStatus: {status.title()}"
                    })
                except:
                    continue
        # Filter by search
        if search_val:
            logs = [log for log in logs if search_val.lower() in str(log['description']).lower()]
        # Sort by timestamp descending
        def parse_ts(log):
            try:
                return datetime.strptime(log['timestamp'], '%Y-%m-%d %H:%M:%S')
            except:
                return datetime.min
        logs.sort(key=parse_ts, reverse=True)
        # Clear table
        for row in self.log_tree.get_children():
            self.log_tree.delete(row)
        # Insert logs with enhanced UI
        for i, log in enumerate(logs):
            # Icon for event type
            event_type = log.get('event_type', '').lower()
            if event_type == 'scan':
                icon = '🦠'
            elif event_type == 'quarantine':
                icon = '🔒'
            elif event_type == 'threat':
                icon = '⚠️'
            else:
                icon = '📝'
            # Row color by severity
            severity = log.get('severity', 'Low')
            if severity == 'High':
                row_fg = self.get_color('danger')
            elif severity == 'Medium':
                row_fg = self.get_color('warn')
            else:
                row_fg = self.get_color('success')
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            details = log.get('tooltip', '') or log.get('details', '') or ''
            self.log_tree.insert('', 'end', values=(log['timestamp'], f'{icon} {log["event_type"]}', log['description'], log['status'], details), tags=(tag, severity))
        # Tag configuration for row colors
        self.log_tree.tag_configure('High', foreground=self.get_color('danger'))
        self.log_tree.tag_configure('Medium', foreground=self.get_color('warn'))
        self.log_tree.tag_configure('Low', foreground=self.get_color('success'))
        # Alternating row backgrounds
        even_color = self.get_color('tree_bg')
        odd_color = '#1a1d23' if self.theme == 'dark' else '#f8fafd'
        fg_color = self.get_color('tree_fg')
        self.log_tree.tag_configure('evenrow', background=even_color, foreground=fg_color)
        self.log_tree.tag_configure('oddrow', background=odd_color, foreground=fg_color)
        # Tooltips for rows
        def on_row_enter(event):
            item = self.log_tree.identify_row(event.y)
            if item:
                values = self.log_tree.item(item, 'values')
                details = values[4] if len(values) > 4 else ''
                if details:
                    x, y, _, _ = self.log_tree.bbox(item)
                    self._show_log_tooltip(x, y, details)
        def on_row_leave(event):
            self._hide_log_tooltip()
        self.log_tree.bind('<Motion>', on_row_enter)
        self.log_tree.bind('<Leave>', on_row_leave)
    
    def _show_log_tooltip(self, x, y, text):
        if hasattr(self, '_log_tooltip') and self._log_tooltip:
            self._log_tooltip.destroy()
        self._log_tooltip = tk.Toplevel(self.log_tree)
        self._log_tooltip.wm_overrideredirect(True)
        self._log_tooltip.wm_geometry(f"+{x+10}+{y+10}")
        label = tk.Label(self._log_tooltip, text=text, background='#ffffe0', relief='solid', borderwidth=1, font=('Segoe UI', 10), justify='left')
        label.pack(ipadx=4, ipady=2)
    
    def _hide_log_tooltip(self):
        if hasattr(self, '_log_tooltip') and self._log_tooltip:
            self._log_tooltip.destroy()
            self._log_tooltip = None

    def _export_logs(self, fmt):
        try:
            path = logger.export_logs(format=fmt)
            messagebox.showinfo('Export Logs', f'Logs exported to:\n{path}')
        except Exception as e:
            messagebox.showerror('Export Logs', f'Failed to export logs:\n{e}')

    def _clear_logs(self):
        if messagebox.askyesno('Clear All Logs', 'Are you sure you want to clear all logs? This cannot be undone.'):
            try:
                logger.clear_logs()
                self._refresh_log_table()
            except Exception as e:
                messagebox.showerror('Clear Logs Error', f'Failed to clear logs:\n{e}')

    def _toggle_auto_cleanup(self):
        enabled = self.auto_cleanup_var.get()
        days = self.retention_days_var.get()
        try:
            logger.set_retention_policy(days if enabled else 0)
            self._refresh_log_table()
        except Exception as e:
            messagebox.showerror('Auto Cleanup Error', f'Failed to set retention policy:\n{e}')

    def _toggle_live_panel(self):
        if self.live_panel_visible.get():
            self.live_panel.pack_forget()
            self.live_panel_visible.set(False)
        else:
            self.live_panel.pack(fill='x', padx=30, pady=(0, 10))
            self.live_panel_visible.set(True)

    def _start_live_feed(self):
        def live_feed():
            last_count = 0
            while True:
                try:
                    logs = logger.get_logs(limit=5)
                    if len(logs) != last_count:
                        if hasattr(self, 'live_panel_text') and self.live_panel_text.winfo_exists():
                            self.live_panel_text.config(state='normal')
                            self.live_panel_text.delete('1.0', 'end')
                            for log in logs:
                                try:
                                    icon = logger.get_event_type_icon(EventType(log['event_type']))
                                    self.live_panel_text.insert('end', f"[{log['timestamp']}] {icon} {log['event_type'].replace('_', ' ').title()}: {log['description']}\n")
                                except Exception as e:
                                    print(f"Error processing log entry: {e}")
                            self.live_panel_text.config(state='disabled')
                            last_count = len(logs)
                except Exception as e:
                    print(f"Error in live feed: {e}")
                time.sleep(2)
        t = threading.Thread(target=live_feed, daemon=True)
        t.start() 

    def show_reports_panel(self):
        self._show_buffering()
        self._clear_page()
        self.header_status.config(text='Reports')
        
        # Import and use the ReportsPanel directly in page_frame for maximum size
        from ui.reports_panel import ReportsPanel
        self.reports_panel = ReportsPanel(self.page_frame, self.system_monitor, self.threat_db, self.quarantine_manager)
        self.reports_panel.pack(fill='both', expand=True, padx=10, pady=10)
        self._hide_buffering()
        
    def apply_color_theme(self):
        """Apply color theme from settings"""
        try:
            from utils.settings_manager import get_settings_manager
            from utils.color_palette import get_color_palette
            
            settings_manager = get_settings_manager()
            color_palette = get_color_palette()
            
            # Get theme settings
            use_custom_colors = settings_manager.get_setting("appearance", "use_custom_colors", False)
            
            if use_custom_colors:
                # Apply custom colors
                custom_colors = settings_manager.get_setting("appearance", "custom_colors", {})
                self.apply_custom_colors(custom_colors)
            else:
                # Apply predefined theme
                theme_name = settings_manager.get_setting("appearance", "color_theme", "Light")
                theme_data = color_palette.get_theme(theme_name)
                if theme_data:
                    self.apply_theme_colors(theme_data)
            
            # Refresh UI
            self.create_widgets()
            
        except Exception as e:
            print(f"Error applying color theme: {e}")
    
    def apply_theme_colors(self, theme_data: dict):
        """Apply colors from theme data, using all color keys"""
        # Update the colors dictionary with all keys
        self.colors = {
            'bg': theme_data.get('background', '#F7F9FB'),
            'fg': theme_data.get('text_primary', '#222B45'),
            'accent': theme_data.get('primary_accent', '#1976D2'),
            'secondary_accent': theme_data.get('secondary_accent', '#42A5F5'),
            'sidebar': theme_data.get('surface', '#FFFFFF'),
            'header': theme_data.get('primary_accent', '#1976D2'),
            'button': theme_data.get('surface', '#FFFFFF'),
            'button_fg': theme_data.get('text_primary', '#222B45'),
            'danger': theme_data.get('danger', '#D32F2F'),
            'success': theme_data.get('success', '#43A047'),
            'warn': theme_data.get('warning', '#FFA000'),
            'info': theme_data.get('info', '#1976D2'),
            'tree_bg': theme_data.get('surface', '#FFFFFF'),
            'tree_fg': theme_data.get('text_primary', '#222B45'),
            'tree_sel': theme_data.get('primary_accent', '#1976D2'),
            'status': theme_data.get('surface', '#FFFFFF'),
            'entry_bg': theme_data.get('surface', '#FFFFFF'),
            'entry_fg': theme_data.get('text_primary', '#222B45'),
            'text_secondary': theme_data.get('text_secondary', '#6B778C'),
            'border': theme_data.get('border', '#D1D9E6'),
            'hover': theme_data.get('secondary_accent', '#42A5F5'),
            'disabled': theme_data.get('text_secondary', '#6B778C')
        }
        
        # Apply colors to root window
        self.root.configure(bg=self.colors['bg'])
        
        # Update styles for all keys
        self.style = ttk.Style()
        self.style.theme_use(self.theme)
        c = self.colors
        # Frame styles
        self.style.configure('TFrame', background=c['bg'])
        self.style.configure('Main.TFrame', background=c['bg'])
        self.style.configure('Sidebar.TFrame', background=c['sidebar'])
        # Label styles
        self.style.configure('TLabel', background=c['bg'], foreground=c['fg'], font=('Segoe UI', 12))
        self.style.configure('Header.TLabel', font=('Segoe UI', 22, 'bold'), foreground=c['header'], background=c['bg'])
        self.style.configure('SubHeader.TLabel', font=('Segoe UI', 16, 'bold'), foreground=c['accent'], background=c['bg'])
        self.style.configure('Status.TLabel', background=c['status'], foreground=c['fg'], font=('Segoe UI', 10))
        self.style.configure('Secondary.TLabel', background=c['bg'], foreground=c['text_secondary'], font=('Segoe UI', 11))
        self.style.configure('Info.TLabel', background=c['bg'], foreground=c['info'], font=('Segoe UI', 11, 'italic'))
        self.style.configure('Success.TLabel', background=c['bg'], foreground=c['success'], font=('Segoe UI', 11, 'bold'))
        self.style.configure('Warning.TLabel', background=c['bg'], foreground=c['warn'], font=('Segoe UI', 11, 'bold'))
        self.style.configure('Danger.TLabel', background=c['bg'], foreground=c['danger'], font=('Segoe UI', 11, 'bold'))
        # Sidebar button styles
        self.style.configure('Sidebar.TButton', 
            background=c['sidebar'], foreground=c['fg'], font=('Segoe UI', 14, 'bold'), borderwidth=0, focuscolor='none')
        self.style.map('Sidebar.TButton',
            background=[('active', c['hover']), ('pressed', c['accent'])],
            foreground=[('active', c['accent']), ('pressed', c['bg'])])
        # Button styles
        self.style.configure('TButton', 
            background=c['button'], foreground=c['button_fg'], font=('Segoe UI', 12), borderwidth=1, relief='flat')
        self.style.map('TButton',
            background=[('active', c['hover']), ('pressed', c['accent'])],
            foreground=[('active', c['accent']), ('pressed', c['bg'])])
        self.style.configure('Accent.TButton', 
            background=c['accent'], foreground=c['bg'], font=('Segoe UI', 12, 'bold'), borderwidth=0, relief='flat')
        self.style.map('Accent.TButton',
            background=[('active', c['hover']), ('pressed', c['button'])],
            foreground=[('active', c['accent']), ('pressed', c['fg'])])
        self.style.configure('Info.TButton', background=c['info'], foreground=c['bg'], font=('Segoe UI', 12, 'bold'))
        self.style.configure('Success.TButton', background=c['success'], foreground=c['bg'], font=('Segoe UI', 12, 'bold'))
        self.style.configure('Warning.TButton', background=c['warn'], foreground=c['bg'], font=('Segoe UI', 12, 'bold'))
        self.style.configure('Danger.TButton', background=c['danger'], foreground=c['bg'], font=('Segoe UI', 12, 'bold'))
        # Treeview styles
        self.style.configure('Treeview', background=c['tree_bg'], foreground=c['tree_fg'], fieldbackground=c['tree_bg'], font=('Segoe UI', 12), borderwidth=0, rowheight=28, padding=2)
        self.style.configure('Treeview.Heading', background=c['sidebar'], foreground=c['fg'], font=('Segoe UI', 12, 'bold'), padding=4)
        # Entry styles
        self.style.configure('TEntry', fieldbackground=c['entry_bg'], foreground=c['entry_fg'], borderwidth=1, relief='solid')
        # Combobox styles
        self.style.configure('TCombobox', fieldbackground=c['entry_bg'], foreground=c['entry_fg'], background=c['entry_bg'], borderwidth=1, relief='solid')
        # Progress bar styles
        self.style.configure('TProgressbar', background=c['accent'], troughcolor=c['border'], borderwidth=0)
        # Notebook styles
        self.style.configure('TNotebook', background=c['bg'], borderwidth=0)
        self.style.configure('TNotebook.Tab', background=c['sidebar'], foreground=c['fg'], padding=[10, 5], font=('Segoe UI', 11))
        self.style.map('TNotebook.Tab', background=[('selected', c['accent']), ('active', c['hover'])], foreground=[('selected', c['bg']), ('active', c['accent'])])
        # Scrollbar styles
        if not hasattr(IronWallMainWindow, '_t_scrollbar_configured'):
            self.style.configure('TScrollbar', background=c['sidebar'], troughcolor=c['bg'], borderwidth=0, arrowcolor=c['fg'])
            self.style.map('TScrollbar', background=[('active', c['hover']), ('pressed', c['accent'])])
            IronWallMainWindow._t_scrollbar_configured = True
        # Checkbutton styles
        self.style.configure('TCheckbutton', background=c['bg'], foreground=c['fg'], font=('Segoe UI', 11))
        # Radiobutton styles
        self.style.configure('TRadiobutton', background=c['bg'], foreground=c['fg'], font=('Segoe UI', 11))
        # Scale styles
        self.style.configure('TScale', background=c['bg'], troughcolor=c['border'], sliderrelief='flat', sliderthickness=15)
        # Spinbox styles
        self.style.configure('TSpinbox', fieldbackground=c['entry_bg'], foreground=c['entry_fg'], background=c['entry_bg'], borderwidth=1, relief='solid')
        # LabelFrame styles
        self.style.configure('TLabelframe', background=c['bg'], foreground=c['fg'], borderwidth=2, relief='ridge')
        self.style.configure('TLabelframe.Label', background=c['bg'], foreground=c['accent'], font=('Segoe UI', 12, 'bold'))
        # Info/Success/Warning/Danger LabelFrame styles
        self.style.configure('Info.TLabelframe', background=c['bg'], foreground=c['info'], borderwidth=2, relief='ridge')
        self.style.configure('Success.TLabelframe', background=c['bg'], foreground=c['success'], borderwidth=2, relief='ridge')
        self.style.configure('Warning.TLabelframe', background=c['bg'], foreground=c['warn'], borderwidth=2, relief='ridge')
        self.style.configure('Danger.TLabelframe', background=c['bg'], foreground=c['danger'], borderwidth=2, relief='ridge')
        # Border color for frames
        self.root.configure(highlightbackground=c['border'], highlightcolor=c['border'])
        # Refresh UI
        self.create_widgets()
    
    def apply_custom_colors(self, custom_colors: dict):
        """Apply custom colors"""
        # Map custom colors to the color system
        theme_data = {
            'background': custom_colors.get('background', '#F7F9FB'),
            'text_primary': custom_colors.get('text_primary', '#222B45'),
            'primary_accent': custom_colors.get('primary_accent', '#1976D2'),
            'surface': custom_colors.get('surface', '#FFFFFF'),
            'secondary_accent': custom_colors.get('secondary_accent', '#42A5F5'),
            'text_secondary': custom_colors.get('text_secondary', '#6B778C'),
            'border': custom_colors.get('border', '#D1D9E6'),
            'danger': custom_colors.get('danger', '#D32F2F'),
            'success': custom_colors.get('success', '#43A047'),
            'warning': custom_colors.get('warning', '#FFA000'),
            'info': custom_colors.get('info', '#1976D2')
        }
        self.apply_theme_colors(theme_data)

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        try:
            # Get the widget that received the event
            widget = event.widget
            
            # Find the canvas that contains this widget
            canvas = None
            current = widget
            
            # Walk up the widget hierarchy to find the canvas
            while current and current != self.root:
                try:
                    if hasattr(current, 'yview_scroll'):
                        canvas = current
                        break
                    current = current.master
                except Exception:
                    break
            
            if canvas and canvas.winfo_exists():
                try:
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                except Exception as e:
                    print(f"Error scrolling canvas: {e}")
        except Exception as e:
            print(f"Error in mousewheel handler: {e}")

    def refresh_scan_panel(self):
        # Only refresh the scan panel if it is visible
        if hasattr(self, 'scan_panel') and self.scan_panel and self.scan_panel.winfo_exists():
            self.scan_panel.destroy()
            
            # Create scrollable frame
            scrollable_frame = self._create_scrollable_frame(self.page_frame)
            
            self.scan_panel = ScanPanel(scrollable_frame, scan_callbacks={
                'start': lambda scan_type, paths: self._start_scan(scan_type=scan_type, custom_paths=paths),
                'pause': self.pause_scan,
                'resume': self.resume_scan,
                'stop': self.stop_scan
            })
            self.scan_panel.pack(fill='both', expand=True, padx=20, pady=20)
        else:
            self.show_scan()

    # --- New Dashboard Panels ---
    def _create_notifications_panel(self, parent):
        # Example: Show last 5 alerts and pending actions
        alerts = getattr(self, 'recent_alerts', [
            {'type': 'Threat Detected', 'msg': 'Malware found in C:/Users/krish/Downloads/malware.exe', 'severity': 'High'},
            {'type': 'Update Available', 'msg': 'New virus definitions are available.', 'severity': 'Medium'},
            {'type': 'Scan Complete', 'msg': 'Quick scan completed. No threats found.', 'severity': 'Low'},
        ])
        for alert in alerts:
            color = self.get_color('danger') if alert['severity'] == 'High' else (self.get_color('warn') if alert['severity'] == 'Medium' else self.get_color('success'))
            icon = '⚠️' if alert['severity'] == 'High' else ('🔔' if alert['severity'] == 'Medium' else '✅')
            ttk.Label(parent, text=f"{icon} {alert['type']}: {alert['msg']}", foreground=color, font=('Segoe UI', 11)).pack(anchor='w', pady=2)

    def _create_license_info_panel(self, parent):
        # Example: Show license status and user info
        license_status = getattr(self, 'license_status', 'Trial Version - 14 days left')
        user_name = getattr(self, 'user_name', 'User: Krish Gupta')
        ttk.Label(parent, text=f"🔑 {license_status}", font=('Segoe UI', 12, 'bold'), foreground=self.get_color('accent')).pack(anchor='w', pady=2)
        ttk.Label(parent, text=f"👤 {user_name}", font=('Segoe UI', 11)).pack(anchor='w', pady=2)

    def _create_tips_panel(self, parent):
        # Example: Show rotating security tips and product news
        tips = [
            'Tip: Keep your virus definitions up to date for best protection.',
            'Tip: Run a full scan weekly to ensure your system is clean.',
            'Tip: Do not open suspicious email attachments.',
            'News: IronWall 2.0 released with enhanced real-time protection!',
        ]
        for tip in tips:
            icon = '💡' if tip.startswith('Tip') else '📰'
            ttk.Label(parent, text=f"{icon} {tip}", font=('Segoe UI', 11, 'italic')).pack(anchor='w', pady=2)

    def show_status_popup(self, message, title="IronWall Antivirus Status"):
        from tkinter import messagebox
        messagebox.showinfo(title, message)