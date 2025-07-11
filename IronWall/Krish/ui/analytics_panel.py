import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from utils import scan_history
import os
import threading
import time

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind('<Enter>', self.show)
        widget.bind('<Leave>', self.hide)
    def show(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left', background='#23272f', foreground='white', relief='solid', borderwidth=1, font=('Segoe UI', 10, 'normal'))
        label.pack(ipadx=8, ipady=4)
    def hide(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

class AnalyticsPanel(ttk.Frame):
    def __init__(self, parent, system_monitor, threat_db):
        super().__init__(parent)
        self.system_monitor = system_monitor
        self.threat_db = threat_db
        self.theme = 'dark'  # default theme
        self.loading = False
        self._data_cache = {}  # Cache for data to prevent repeated loading
        self._cache_timestamp = 0
        self.pack(fill='both', expand=True)

        # --- Scrollable Frame Setup ---
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg='#23272f')
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.scrollable_frame.update_idletasks()
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        # Show loading screen first
        self._show_loading_screen()
        # Start async loading
        self._load_async()

    def _on_mousewheel(self, event):
        # For Windows and MacOS
        if event.widget.winfo_toplevel() == self.winfo_toplevel():
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _show_loading_screen(self):
        """Show a loading screen while data is being prepared"""
        colors = self._get_colors()
        # Clear any existing widgets in scrollable_frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        # Create loading frame
        loading_frame = ttk.Frame(self.scrollable_frame)
        loading_frame.pack(expand=True, fill='both')
        
        # Loading icon and text
        loading_label = ttk.Label(loading_frame, text='📊', font=('Segoe UI Emoji', 48), 
                                 background=colors['bg'], foreground=colors['accent'])
        loading_label.pack(pady=(100, 20))
        
        title_label = ttk.Label(loading_frame, text='Loading Analytics...', 
                               font=('Segoe UI', 18, 'bold'), 
                               background=colors['bg'], foreground=colors['accent'])
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(loading_frame, text='Preparing security insights and visualizations', 
                                  font=('Segoe UI', 12), 
                                  background=colors['bg'], foreground=colors['text'])
        subtitle_label.pack(pady=(0, 30))
        
        # Progress bar
        self.progress = ttk.Progressbar(loading_frame, mode='indeterminate', length=300)
        self.progress.pack(pady=(0, 20))
        self.progress.start()
        
        # Status text
        self.status_label = ttk.Label(loading_frame, text='Initializing...', 
                                     font=('Segoe UI', 10), 
                                     background=colors['bg'], foreground=colors['text'])
        self.status_label.pack()

    def _load_async(self):
        """Load analytics data asynchronously"""
        self.loading = True
        
        def load_data():
            try:
                # Update status
                self.after(0, lambda: self.status_label.config(text='Loading scan history...'))
                time.sleep(0.1)  # Small delay to show progress
                
                # Pre-load data
                self.after(0, lambda: self.status_label.config(text='Processing threat data...'))
                time.sleep(0.1)
                
                # Load scan history
                self.after(0, lambda: self.status_label.config(text='Preparing visualizations...'))
                time.sleep(0.1)
                
                # Create UI on main thread
                self.after(0, self._create_widgets)
                
            except Exception as e:
                print(f"Error loading analytics: {e}")
                self.after(0, self._show_error_screen, str(e))
            finally:
                self.loading = False
        
        # Start loading thread
        thread = threading.Thread(target=load_data, daemon=True)
        thread.start()

    def _show_error_screen(self, error_msg):
        """Show error screen if loading fails"""
        colors = self._get_colors()
        
        # Clear loading widgets in scrollable_frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Error frame
        error_frame = ttk.Frame(self.scrollable_frame)
        error_frame.pack(expand=True, fill='both')
        
        # Error icon and text
        error_label = ttk.Label(error_frame, text='⚠️', font=('Segoe UI Emoji', 48), 
                               background=colors['bg'], foreground=colors['danger'])
        error_label.pack(pady=(100, 20))
        
        title_label = ttk.Label(error_frame, text='Analytics Loading Failed', 
                               font=('Segoe UI', 18, 'bold'), 
                               background=colors['bg'], foreground=colors['danger'])
        title_label.pack(pady=(0, 10))
        
        error_text = ttk.Label(error_frame, text=f'Error: {error_msg}', 
                              font=('Segoe UI', 10), 
                              background=colors['bg'], foreground=colors['text'])
        error_text.pack(pady=(0, 30))
        
        # Retry button
        retry_btn = ttk.Button(error_frame, text='Retry', 
                              style='Accent.TButton', 
                              command=self._retry_loading)
        retry_btn.pack()

    def _retry_loading(self):
        """Retry loading analytics"""
        self._show_loading_screen()
        self._load_async()

    def _get_colors(self):
        if self.theme == 'dark':
            return {
                'bg': '#23272f',
                'card': '#23272f',
                'shadow': '#444',
                'accent': '#00D4FF',
                'text': '#E8E8E8',
                'danger': '#dc3545',
                'bar': '#007bff',
                'footer': '#888',
            }
        else:
            return {
                'bg': '#f7f9fb',
                'card': '#ffffff',
                'shadow': '#d1d9e6',
                'accent': '#1976D2',
                'text': '#222B45',
                'danger': '#d32f2f',
                'bar': '#1976D2',
                'footer': '#888',
            }

    def _create_widgets(self):
        """Create the main analytics widgets"""
        try:
            colors = self._get_colors()
            # Clear loading widgets in scrollable_frame
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            # Header
            header_frame = ttk.Frame(self.scrollable_frame, style='TFrame')
            header_frame.pack(fill='x', pady=(10, 0))
            icon = ttk.Label(header_frame, text='📊', font=('Segoe UI Emoji', 32), background=colors['bg'], foreground=colors['accent'])
            icon.pack(side='left', padx=(20, 10))
            title = ttk.Label(header_frame, text='Analytics & Security Insights', font=('Segoe UI', 22, 'bold'), background=colors['bg'], foreground=colors['accent'])
            title.pack(side='left', pady=8)
            subtitle = ttk.Label(header_frame, text='All security insights and visualizations in one view', font=('Segoe UI', 12, 'italic'), background=colors['bg'], foreground=colors['text'])
            subtitle.pack(side='left', padx=20, pady=8)
            # Settings button
            settings_btn = ttk.Button(header_frame, text='⚙️', width=3, style='Accent.TButton', command=self._show_settings)
            settings_btn.pack(side='right', padx=20)
            Tooltip(settings_btn, 'Analytics Settings')
            # Main notebook
            self.notebook = ttk.Notebook(self.scrollable_frame)
            self.notebook.pack(fill='both', expand=True, padx=30, pady=20)
            # Create tabs asynchronously
            print('[DEBUG] Creating analytics tabs...')
            self._create_tabs_async()
        except Exception as e:
            import traceback
            print(f"Error creating analytics widgets: {e}")
            traceback.print_exc()
            messagebox.showerror('Analytics Error', f'Error creating analytics widgets:\n{e}')
            self._show_error_screen(str(e))

    def _create_tabs_async(self):
        """Create tabs asynchronously to prevent UI freezing"""
        def create_tabs():
            try:
                print('[DEBUG] Creating analytics tab content...')
                # Create a single tab for all graphs
                self.all_graphs_frame = ttk.Frame(self.notebook)
                self.notebook.add(self.all_graphs_frame, text='📊 All Analytics')
                # Create a 2x2 grid layout directly in the frame
                # Top row
                top_row = ttk.Frame(self.all_graphs_frame)
                top_row.pack(fill='both', expand=True, padx=20, pady=10)
                # Security Analytics (top-left)
                self.security_frame = self._create_card(top_row, '🛡 Security Analytics')
                self.security_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
                self.after(0, lambda: self._safe_create(self._create_security_analytics, self.security_frame, 'Security Analytics'))
                # Threat Distribution (top-right)
                self.threat_dist_frame = self._create_card(top_row, '☣ Threat Distribution')
                self.threat_dist_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
                self.after(0, lambda: self._safe_create(self._create_threat_distribution, self.threat_dist_frame, 'Threat Distribution'))
                # Bottom row
                bottom_row = ttk.Frame(self.all_graphs_frame)
                bottom_row.pack(fill='both', expand=True, padx=20, pady=10)
                # System Health (bottom-left)
                self.system_health_frame = self._create_card(bottom_row, '💻 System Health')
                self.system_health_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
                self.after(0, lambda: self._safe_create(self._create_system_health, self.system_health_frame, 'System Health'))
                # Weekly Threat Activity (bottom-right)
                self.weekly_threat_frame = self._create_card(bottom_row, '📆 Weekly Threats')
                self.weekly_threat_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
                self.after(0, lambda: self._safe_create(self._create_weekly_threat_activity, self.weekly_threat_frame, 'Weekly Threats'))
            except Exception as e:
                import traceback
                print(f"Error creating tabs: {e}")
                traceback.print_exc()
                self.after(0, lambda: self._show_error_screen(str(e)))
        thread = threading.Thread(target=create_tabs, daemon=True)
        thread.start()

    def _safe_create(self, func, frame, label):
        try:
            print(f'[DEBUG] Creating {label}...')
            func(frame)
        except Exception as e:
            import traceback
            print(f"Error creating {label}: {e}")
            traceback.print_exc()
            messagebox.showerror('Analytics Error', f'Error creating {label}:\n{e}')

    def _show_settings(self):
        win = tk.Toplevel(self)
        win.title('Analytics Settings')
        win.geometry('350x220')
        win.configure(bg=self._get_colors()['bg'])
        ttk.Label(win, text='Analytics Settings', font=('Segoe UI', 16, 'bold')).pack(pady=10)
        # Theme switch
        theme_label = ttk.Label(win, text='Theme:', font=('Segoe UI', 12))
        theme_label.pack(pady=5)
        theme_var = tk.StringVar(value=self.theme)
        def set_theme():
            self.theme = theme_var.get()
            self._refresh_panel()
            win.destroy()
        ttk.Radiobutton(win, text='Dark', variable=theme_var, value='dark').pack()
        ttk.Radiobutton(win, text='Light', variable=theme_var, value='light').pack()
        ttk.Button(win, text='Apply', command=set_theme).pack(pady=10)
        # System Health chart type
        chart_type_label = ttk.Label(win, text='System Health Chart:', font=('Segoe UI', 12))
        chart_type_label.pack(pady=5)
        self.chart_type_var = tk.StringVar(value=getattr(self, 'chart_type', 'line'))
        ttk.Radiobutton(win, text='Line', variable=self.chart_type_var, value='line').pack()
        ttk.Radiobutton(win, text='Bar', variable=self.chart_type_var, value='bar').pack()
        def set_chart_type():
            setattr(self, 'chart_type', self.chart_type_var.get())
            self._refresh_panel()
            win.destroy()
        ttk.Button(win, text='Apply Chart Type', command=set_chart_type).pack(pady=5)

    def _refresh_panel(self):
        """Refresh the entire panel by clearing cache and recreating widgets"""
        try:
            # Clear cache to force fresh data
            self._data_cache.clear()
            
            # Clear existing widgets in scrollable_frame
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            # Recreate widgets
            self._create_widgets()
        except Exception as e:
            print(f"Error refreshing panel: {e}")
            self._show_error_screen(str(e))

    def _clear_cache(self):
        """Clear all cached data"""
        self._data_cache.clear()
        print("Analytics cache cleared")

    def _refresh_chart_data(self, chart_type):
        """Refresh data for a specific chart type"""
        try:
            if chart_type == 'security':
                self._data_cache.pop('scan_type_counts', None)
            elif chart_type == 'threats':
                self._data_cache.pop('threat_distribution', None)
            elif chart_type == 'weekly':
                self._data_cache.pop('weekly_threats', None)
            elif chart_type == 'system':
                self._data_cache.pop('system_health', None)
            print(f"Cache cleared for {chart_type} chart")
        except Exception as e:
            print(f"Error clearing cache for {chart_type}: {e}")

    def _create_card(self, parent, title):
        colors = self._get_colors()
        card = tk.Frame(parent, bg=colors['card'], highlightthickness=0)
        card.pack_propagate(False)
        # Make cards much wider to expand graph length significantly
        card.config(height=350, width=650)  # Increased width from 500 to 650
        # Rounded corners and shadow
        canvas = tk.Canvas(card, width=650, height=350, bg=colors['card'], highlightthickness=0)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        canvas.create_rectangle(10, 10, 640, 340, fill=colors['card'], outline=colors['card'], width=0)
        canvas.create_rectangle(15, 15, 635, 335, fill=colors['card'], outline=colors['shadow'], width=2)
        # Card title
        label = tk.Label(card, text=title, font=('Segoe UI', 12, 'bold'), bg=colors['card'], fg=colors['accent'])
        label.place(x=15, y=12)
        return card

    def _add_divider(self, parent):
        colors = self._get_colors()
        divider = tk.Frame(parent, bg=colors['shadow'], height=2)
        divider.pack(fill='x', padx=30, pady=10)

    # --- Data Processing Helpers ---
    def _get_cached_data(self, key, max_age=30):
        """Get cached data if it's still fresh"""
        current_time = time.time()
        if key in self._data_cache:
            data, timestamp = self._data_cache[key]
            if current_time - timestamp < max_age:  # Cache for 30 seconds
                return data
        return None

    def _set_cached_data(self, key, data):
        """Cache data with current timestamp"""
        self._data_cache[key] = (data, time.time())

    def _get_scan_type_counts(self):
        # Check cache first
        cached = self._get_cached_data('scan_type_counts')
        if cached:
            return cached
        
        try:
            history = scan_history.load_scan_history()
            scan_types = ['Quick', 'Full', 'Custom', 'Deep']
            type_counts = {stype: 0 for stype in scan_types}
            threats_per_type = {stype: 0 for stype in scan_types}
            for entry in history:
                stype = entry.get('scan_type', 'Quick')
                if stype not in type_counts:
                    type_counts[stype] = 0
                    threats_per_type[stype] = 0
                type_counts[stype] += 1
                threat_type = entry.get('threat_type')
                if threat_type and isinstance(threat_type, str) and threat_type.lower() not in ('clean', 'none', 'unknown'):
                    threats_per_type[stype] += 1
            
            result = (type_counts, threats_per_type)
            self._set_cached_data('scan_type_counts', result)
            return result
        except Exception as e:
            print(f"Error loading scan type counts: {e}")
            return ({'Quick': 0, 'Full': 0, 'Custom': 0, 'Deep': 0}, 
                   {'Quick': 0, 'Full': 0, 'Custom': 0, 'Deep': 0})

    def _get_threat_type_distribution(self):
        # Check cache first
        cached = self._get_cached_data('threat_distribution')
        if cached:
            return cached
        
        try:
            history = scan_history.load_scan_history()
            type_counts = {}
            for entry in history:
                ttype = entry.get('threat_type', 'Unknown')
                if ttype and isinstance(ttype, str) and ttype.lower() in ('clean', 'none', 'unknown'):
                    continue
                if ttype and ':' in ttype:
                    ttype = ttype.split(':', 1)[-1].strip()
                type_counts[ttype] = type_counts.get(ttype, 0) + 1
            
            self._set_cached_data('threat_distribution', type_counts)
            return type_counts
        except Exception as e:
            print(f"Error loading threat distribution: {e}")
            return {'No Threats': 1}

    def _get_weekly_threat_activity(self):
        # Check cache first
        cached = self._get_cached_data('weekly_threats')
        if cached:
            return cached
        
        try:
            history = scan_history.load_scan_history()
            week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            day_counts = {d: 0 for d in week_days}
            now = datetime.now()
            for entry in history:
                ts = entry.get('timestamp')
                if not ts:
                    continue
                dt = datetime.fromtimestamp(ts)
                threat_type = entry.get('threat_type')
                if (now - dt).days < 7:
                    day = week_days[dt.weekday()]
                    if threat_type and isinstance(threat_type, str) and threat_type.lower() not in ('clean', 'none', 'unknown'):
                        day_counts[day] += 1
            
            self._set_cached_data('weekly_threats', day_counts)
            return day_counts
        except Exception as e:
            print(f"Error loading weekly threat activity: {e}")
            return {'Mon': 0, 'Tue': 0, 'Wed': 0, 'Thu': 0, 'Fri': 0, 'Sat': 0, 'Sun': 0}

    def _get_system_health_history(self):
        # Check cache first
        cached = self._get_cached_data('system_health')
        if cached:
            return cached
        
        try:
            # Simulate 24h data (since only current stats are available)
            # In a real app, this would be loaded from a log or database
            import random
            x = list(range(24))
            cpu = [random.randint(20, 80) for _ in x]
            ram = [random.randint(30, 90) for _ in x]
            disk = [random.randint(10, 70) for _ in x]
            temp = [random.randint(35, 60) for _ in x]
            
            result = (x, cpu, ram, disk, temp)
            self._set_cached_data('system_health', result)
            return result
        except Exception as e:
            print(f"Error generating system health data: {e}")
            return (list(range(24)), [50]*24, [60]*24, [30]*24, [45]*24)

    # --- Graphs ---
    def _create_security_analytics(self, frame):
        try:
            colors = self._get_colors()
            card = frame
            fig, ax = self._create_matplotlib_figure((7,2.2), colors['card'])  # Increased width from 5 to 7
            self._plot_security_analytics(ax, colors)
            canvas = self._create_canvas(fig, card)
            canvas.get_tk_widget().place(x=15, y=40, width=550, height=200)  # Increased width from 400 to 550
            
            # Add click handler for fullscreen toggle
            self._add_graph_click_handler(canvas, fig, self._plot_security_analytics)
            
            def refresh_security():
                self._refresh_chart_data('security')
                self._plot_security_analytics(ax, colors, canvas)
            
            refresh_btn = ttk.Button(card, text='🔄', width=3, style='Accent.TButton', command=refresh_security)
            refresh_btn.place(x=580, y=12)  # Adjusted position
            Tooltip(refresh_btn, 'Refresh Security Analytics')
            export_btn = ttk.Button(card, text='⬇️', width=3, style='Accent.TButton', command=lambda: self._export_graph(fig, 'security_analytics.png'))
            export_btn.place(x=610, y=12)  # Adjusted position
            Tooltip(export_btn, 'Export as PNG')
            self._add_hover_effect(refresh_btn)
            self._add_hover_effect(export_btn)
            # Full screen button
            self._create_fullscreen_button(card, fig, self._plot_security_analytics)
            print("Security analytics created successfully")
        except Exception as e:
            print(f"Error creating security analytics: {e}")
            self._show_chart_error(card, "Security Analytics", str(e))

    def _plot_security_analytics(self, ax, colors, canvas=None):
        try:
            ax.clear()
            type_counts, threats_per_type = self._get_scan_type_counts()
            scan_types = list(type_counts.keys())
            scans = [type_counts[t] for t in scan_types]
            threats = [threats_per_type[t] for t in scan_types]
            
            if not any(scans) and not any(threats):
                # Show placeholder data if no real data
                scan_types = ['Quick', 'Full', 'Custom', 'Deep']
                scans = [5, 3, 2, 1]
                threats = [2, 1, 1, 0]
            
            x = range(len(scan_types))
            ax.bar(x, scans, width=0.4, label='Scans', align='center', color=colors['bar'])
            ax.bar([i+0.4 for i in x], threats, width=0.4, label='Threats', align='center', color=colors['danger'])
            ax.set_xticks([i+0.2 for i in x])
            ax.set_xticklabels(scan_types)
            ax.set_xlabel('Scan Type', color=colors['text'])
            ax.set_ylabel('Count', color=colors['text'])
            ax.set_title('Number of Scans & Threats per Type', color=colors['accent'])
            ax.legend()
            ax.set_facecolor(colors['card'])
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_color(colors['text'])
            if canvas:
                canvas.draw()
        except Exception as e:
            print(f"Error plotting security analytics: {e}")

    def _create_threat_distribution(self, frame):
        try:
            colors = self._get_colors()
            card = frame
            fig, ax = self._create_matplotlib_figure((6.5,2.5), colors['card'])  # Increased width from 4.5 to 6.5
            self._plot_threat_distribution(ax, colors, fig)
            canvas = self._create_canvas(fig, card)
            canvas.get_tk_widget().place(x=15, y=40, width=550, height=200)  # Increased width from 400 to 550
            
            # Add click handler for fullscreen toggle
            self._add_graph_click_handler(canvas, fig, self._plot_threat_distribution, fig)
            
            def refresh_threats():
                self._refresh_chart_data('threats')
                self._plot_threat_distribution(ax, colors, fig, canvas)
            
            refresh_btn = ttk.Button(card, text='🔄', width=3, style='Accent.TButton', command=refresh_threats)
            refresh_btn.place(x=580, y=12)  # Adjusted position
            Tooltip(refresh_btn, 'Refresh Threat Distribution')
            export_btn = ttk.Button(card, text='⬇️', width=3, style='Accent.TButton', command=lambda: self._export_graph(fig, 'threat_distribution.png'))
            export_btn.place(x=610, y=12)  # Adjusted position
            Tooltip(export_btn, 'Export as PNG')
            self._add_hover_effect(refresh_btn)
            self._add_hover_effect(export_btn)
            # Full screen button
            self._create_fullscreen_button(card, fig, self._plot_threat_distribution, fig)
            # Interactivity: click on pie slice
            def on_click(event):
                for wedge in ax.patches:
                    if wedge.contains_point((event.x, event.y)):
                        idx = ax.patches.index(wedge)
                        labels = list(self._get_threat_type_distribution().keys())
                        if idx < len(labels):
                            messagebox.showinfo('Threat Details', f'Threat Type: {labels[idx]}\nSlice Angle: {getattr(wedge, "get_theta1", lambda: "N/A")()}°')
            fig.canvas.mpl_connect('button_press_event', on_click)
            print("Threat distribution created successfully")
        except Exception as e:
            print(f"Error creating threat distribution: {e}")
            self._show_chart_error(card, "Threat Distribution", str(e))

    def _plot_threat_distribution(self, ax, colors, fig, canvas=None):
        try:
            ax.clear()
            type_counts = self._get_threat_type_distribution()
            labels = list(type_counts.keys())
            sizes = list(type_counts.values())
            
            if not sizes or all(s == 0 for s in sizes):
                labels = ['No Threats Detected']
                sizes = [1]
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, textprops={'color': colors['text']})
            ax.set_title('Threats by Category', color=colors['accent'])
            ax.set_facecolor(colors['card'])
            for text in texts + autotexts:
                text.set_color(colors['text'])
            if canvas:
                canvas.draw()
        except Exception as e:
            print(f"Error plotting threat distribution: {e}")

    def _create_system_health(self, frame):
        try:
            colors = self._get_colors()
            card = frame
            fig, ax = self._create_matplotlib_figure((7,2.2), colors['card'])  # Increased width from 5 to 7
            self._plot_system_health(ax, colors)
            canvas = self._create_canvas(fig, card)
            canvas.get_tk_widget().place(x=15, y=40, width=550, height=200)  # Increased width from 400 to 550
            
            # Add click handler for fullscreen toggle
            self._add_graph_click_handler(canvas, fig, self._plot_system_health)
            
            def refresh_health():
                self._refresh_chart_data('health')
                self._plot_system_health(ax, colors, canvas)
            
            refresh_btn = ttk.Button(card, text='🔄', width=3, style='Accent.TButton', command=refresh_health)
            refresh_btn.place(x=580, y=12)  # Adjusted position
            Tooltip(refresh_btn, 'Refresh System Health')
            export_btn = ttk.Button(card, text='⬇️', width=3, style='Accent.TButton', command=lambda: self._export_graph(fig, 'system_health.png'))
            export_btn.place(x=610, y=12)  # Adjusted position
            Tooltip(export_btn, 'Export as PNG')
            self._add_hover_effect(refresh_btn)
            self._add_hover_effect(export_btn)
            # Full screen button
            self._create_fullscreen_button(card, fig, self._plot_system_health)
            print("System health created successfully")
        except Exception as e:
            print(f"Error creating system health: {e}")
            self._show_chart_error(card, "System Health", str(e))

    def _plot_system_health(self, ax, colors, canvas=None):
        try:
            ax.clear()
            x, cpu, ram, disk, temp = self._get_system_health_history()
            chart_type = getattr(self, 'chart_type', 'line')
            if chart_type == 'bar':
                ax.bar(x, cpu, label='CPU Usage (%)', color=colors['bar'], alpha=0.7)
                ax.bar(x, ram, label='RAM Usage (%)', color='#43A047', alpha=0.5)
                ax.bar(x, disk, label='Disk Activity (%)', color='#FFA000', alpha=0.5)
                ax.bar(x, temp, label='Temperature (°C)', color=colors['danger'], alpha=0.5)
            else:
                ax.plot(x, cpu, label='CPU Usage (%)', linewidth=2, color=colors['bar'])
                ax.plot(x, ram, label='RAM Usage (%)', linewidth=2, color='#43A047')
                ax.plot(x, disk, label='Disk Activity (%)', linewidth=2, color='#FFA000')
                ax.plot(x, temp, label='Temperature (°C)', linewidth=2, color=colors['danger'])
            ax.set_xlabel('Hour (Last 24h)', color=colors['text'])
            ax.set_ylabel('Usage / Temp', color=colors['text'])
            ax.set_title('System Health Metrics', color=colors['accent'])
            ax.legend()
            ax.set_facecolor(colors['card'])
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_color(colors['text'])
            if canvas:
                canvas.draw()
        except Exception as e:
            print(f"Error plotting system health: {e}")

    def _create_weekly_threat_activity(self, frame):
        try:
            colors = self._get_colors()
            card = frame
            fig, ax = self._create_matplotlib_figure((7,2.2), colors['card'])  # Increased width from 5 to 7
            self._plot_weekly_threat_activity(ax, colors)
            canvas = self._create_canvas(fig, card)
            canvas.get_tk_widget().place(x=15, y=40, width=550, height=200)  # Increased width from 400 to 550
            
            # Add click handler for fullscreen toggle
            self._add_graph_click_handler(canvas, fig, self._plot_weekly_threat_activity)
            
            def refresh_weekly():
                self._refresh_chart_data('weekly')
                self._plot_weekly_threat_activity(ax, colors, canvas)
            
            refresh_btn = ttk.Button(card, text='🔄', width=3, style='Accent.TButton', command=refresh_weekly)
            refresh_btn.place(x=580, y=12)  # Adjusted position
            Tooltip(refresh_btn, 'Refresh Weekly Threats')
            export_btn = ttk.Button(card, text='⬇️', width=3, style='Accent.TButton', command=lambda: self._export_graph(fig, 'weekly_threats.png'))
            export_btn.place(x=610, y=12)  # Adjusted position
            Tooltip(export_btn, 'Export as PNG')
            self._add_hover_effect(refresh_btn)
            self._add_hover_effect(export_btn)
            # Full screen button
            self._create_fullscreen_button(card, fig, self._plot_weekly_threat_activity)
            print("Weekly threat activity created successfully")
        except Exception as e:
            print(f"Error creating weekly threat activity: {e}")
            self._show_chart_error(card, "Weekly Threat Activity", str(e))

    def _plot_weekly_threat_activity(self, ax, colors, canvas=None):
        try:
            ax.clear()
            day_counts = self._get_weekly_threat_activity()
            days = list(day_counts.keys())
            threats = list(day_counts.values())
            
            if not any(threats):
                # Show placeholder data if no real data
                threats = [2, 5, 3, 6, 4, 1, 0]
            
            bars = ax.bar(days, threats, color=colors['danger'], alpha=0.7)
            ax.set_xlabel('Day of Week', color=colors['text'])
            ax.set_ylabel('Threats Detected', color=colors['text'])
            ax.set_title('Threats Detected per Day', color=colors['accent'])
            ax.set_facecolor(colors['card'])
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_color(colors['text'])
            for bar, value in zip(bars, threats):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1, f'{value}', ha='center', va='bottom', color=colors['text'])
            if canvas:
                canvas.draw()
        except Exception as e:
            print(f"Error plotting weekly threat activity: {e}")

    def _export_graph(self, fig, filename):
        file_path = filedialog.asksaveasfilename(defaultextension='.png', initialfile=filename, filetypes=[('PNG files', '*.png')])
        if file_path:
            fig.savefig(file_path)
            messagebox.showinfo('Export', f'Graph exported to {file_path}')

    def _add_hover_effect(self, btn):
        def on_enter(e):
            btn.config(style='Accent.TButton')
        def on_leave(e):
            btn.config(style='TButton')
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)

    def _show_chart_error(self, card, chart_name, error_msg):
        """Show error message for individual chart"""
        colors = self._get_colors()
        
        # Clear existing content
        for widget in card.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget("text") != chart_name:
                widget.destroy()
        
        # Error message
        error_label = ttk.Label(card, text=f'⚠️ {chart_name} Error', 
                               font=('Segoe UI', 14, 'bold'), 
                               background=colors['card'], foreground=colors['danger'])
        error_label.place(x=40, y=100)
        
        error_text = ttk.Label(card, text=f'Failed to load chart: {error_msg}', 
                              font=('Segoe UI', 10), 
                              background=colors['card'], foreground=colors['text'])
        error_text.place(x=40, y=130)
        
        # Retry button
        retry_btn = ttk.Button(card, text='Retry', 
                              style='Accent.TButton', 
                              command=lambda: self._retry_chart(card, chart_name))
        retry_btn.place(x=40, y=160)

    def _retry_chart(self, card, chart_name):
        """Retry creating a specific chart"""
        try:
            # Clear error widgets
            for widget in card.winfo_children():
                if isinstance(widget, tk.Label) and widget.cget("text") != chart_name:
                    widget.destroy()
            
            # Recreate chart
            if chart_name == "Security Analytics":
                self._create_security_analytics(card)
            elif chart_name == "Threat Distribution":
                self._create_threat_distribution(card)
            elif chart_name == "System Health":
                self._create_system_health(card)
            elif chart_name == "Weekly Threat Activity":
                self._create_weekly_threat_activity(card)
        except Exception as e:
            print(f"Error retrying chart {chart_name}: {e}")

    def _create_matplotlib_figure(self, figsize, facecolor):
        """Create matplotlib figure with error handling"""
        try:
            return plt.subplots(figsize=figsize, facecolor=facecolor)
        except Exception as e:
            print(f"Error creating matplotlib figure: {e}")
            # Try with different backend or fallback
            try:
                plt.switch_backend('Agg')  # Use non-interactive backend
                return plt.subplots(figsize=figsize, facecolor=facecolor)
            except Exception as e2:
                print(f"Error with fallback backend: {e2}")
                raise e

    def _create_canvas(self, fig, master):
        """Create canvas with error handling"""
        try:
            canvas = FigureCanvasTkAgg(fig, master=master)
            canvas.draw()
            return canvas
        except Exception as e:
            print(f"Error creating canvas: {e}")
            raise e

    def _add_graph_click_handler(self, canvas, fig, plot_func, *plot_args):
        """Add click handler to canvas for toggling fullscreen view"""
        def on_canvas_click(event):
            # Check if click is within the canvas bounds
            if 0 <= event.x <= canvas.get_tk_widget().winfo_width() and 0 <= event.y <= canvas.get_tk_widget().winfo_height():
                # Add a small delay to avoid conflicts with other click handlers
                self.after(50, lambda: self._toggle_fullscreen_graph(fig, plot_func, *plot_args))
        
        canvas.get_tk_widget().bind('<Button-1>', on_canvas_click)
        # Add cursor change to indicate clickable
        canvas.get_tk_widget().bind('<Enter>', lambda e: canvas.get_tk_widget().config(cursor='hand2'))
        canvas.get_tk_widget().bind('<Leave>', lambda e: canvas.get_tk_widget().config(cursor=''))
        
        # Add tooltip to indicate clickable
        Tooltip(canvas.get_tk_widget(), 'Click to expand to full screen')

    def _toggle_fullscreen_graph(self, fig, plot_func, *plot_args):
        """Toggle between fullscreen and normal view for a graph"""
        # Check if there's already a fullscreen window for this graph
        if hasattr(self, '_fullscreen_window') and self._fullscreen_window.winfo_exists():
            # Close fullscreen window
            self._fullscreen_window.destroy()
            delattr(self, '_fullscreen_window')
        else:
            # Open fullscreen window
            self._show_fullscreen_graph(fig, plot_func, *plot_args)

    def _create_fullscreen_button(self, parent, fig, plot_func, *plot_args):
        """Add a full screen button to the graph card"""
        btn = ttk.Button(parent, text='⛶', width=3, style='Accent.TButton', command=lambda: self._show_fullscreen_graph(fig, plot_func, *plot_args))
        btn.place(x=640, y=12)  # Adjusted for wider card width (650px)
        Tooltip(btn, 'Full Screen')
        self._add_hover_effect(btn)

    def _show_fullscreen_graph(self, fig, plot_func, *plot_args):
        """Show the selected graph in a full screen Toplevel window"""
        # Store reference to fullscreen window
        self._fullscreen_window = tk.Toplevel(self)
        fullscreen_win = self._fullscreen_window
        fullscreen_win.attributes('-fullscreen', True)
        fullscreen_win.configure(bg=self._get_colors()['bg'])
        fullscreen_win.focus_set()
        fullscreen_win.grab_set()
        fullscreen_win.title('Full Screen Graph')

        # Exit full screen on Esc
        fullscreen_win.bind('<Escape>', lambda e: self._toggle_fullscreen_graph(fig, plot_func, *plot_args))
        # Exit button
        exit_btn = ttk.Button(fullscreen_win, text='✖', style='Danger.TButton', command=lambda: self._toggle_fullscreen_graph(fig, plot_func, *plot_args))
        exit_btn.place(x=20, y=20)
        Tooltip(exit_btn, 'Exit Full Screen')

        # Re-plot the graph in the new window
        fig_full, ax_full = self._create_matplotlib_figure((16, 9), self._get_colors()['card'])
        plot_func(ax_full, self._get_colors(), *plot_args)
        canvas_full = self._create_canvas(fig_full, fullscreen_win)
        canvas_full.get_tk_widget().pack(fill='both', expand=True, padx=40, pady=40)
        
        # Add click handler to fullscreen canvas to toggle back (with different tooltip)
        def add_fullscreen_click_handler(canvas, fig, plot_func, *plot_args):
            """Add click handler to fullscreen canvas for toggling back to normal view"""
            def on_canvas_click(event):
                # Check if click is within the canvas bounds
                if 0 <= event.x <= canvas.get_tk_widget().winfo_width() and 0 <= event.y <= canvas.get_tk_widget().winfo_height():
                    # Add a small delay to avoid conflicts with other click handlers
                    self.after(50, lambda: self._toggle_fullscreen_graph(fig, plot_func, *plot_args))
            
            canvas.get_tk_widget().bind('<Button-1>', on_canvas_click)
            # Add cursor change to indicate clickable
            canvas.get_tk_widget().bind('<Enter>', lambda e: canvas.get_tk_widget().config(cursor='hand2'))
            canvas.get_tk_widget().bind('<Leave>', lambda e: canvas.get_tk_widget().config(cursor=''))
            
            # Add tooltip to indicate clickable
            Tooltip(canvas.get_tk_widget(), 'Click to minimize')
        
        add_fullscreen_click_handler(canvas_full, fig_full, plot_func, *plot_args)
        
        # Add a label to indicate click to minimize
        info_label = ttk.Label(fullscreen_win, text='Click anywhere on the graph to minimize', 
                              font=('Segoe UI', 12), 
                              background=self._get_colors()['bg'], 
                              foreground=self._get_colors()['text'])
        info_label.pack(side='bottom', pady=10)
        
        print("Full screen graph created successfully") 