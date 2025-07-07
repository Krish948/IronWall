import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
from datetime import datetime
import csv

# Try to import optional dependencies
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Charts will be disabled.")

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas as pdf_canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Import local modules
try:
    from utils import scan_history
    from utils.logger import logger, EventType
except ImportError as e:
    print(f"Warning: Could not import local modules: {e}")

class ReportsPanel(ttk.Frame):
    def __init__(self, parent, system_monitor, threat_db, quarantine_manager):
        super().__init__(parent)
        self.system_monitor = system_monitor
        self.threat_db = threat_db
        self.quarantine_manager = quarantine_manager
        self.theme = 'dark'  # or inherit from main window
        self.pack(fill='both', expand=True)
        self._create_widgets()

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
                'success': '#43A047',
                'warn': '#FFA000',
                'info': '#1976D2',
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
                'success': '#43A047',
                'warn': '#FFA000',
                'info': '#1976D2',
            }

    def _badge(self, value, kind):
        # Returns (icon, color) for severity/event type/status
        icons = {
            'Critical': ('🛑', self._get_colors()['danger']),
            'High': ('⚠️', self._get_colors()['danger']),
            'Moderate': ('🟠', self._get_colors()['warn']),
            'Medium': ('🟠', self._get_colors()['warn']),
            'Low': ('🟢', self._get_colors()['success']),
            'Success': ('✅', self._get_colors()['success']),
            'Failed': ('❌', self._get_colors()['danger']),
            'Blocked': ('🚫', self._get_colors()['danger']),
            'Warning': ('⚠️', self._get_colors()['warn']),
            'Info': ('ℹ️', self._get_colors()['info']),
            'Scan': ('🔍', self._get_colors()['info']),
            'Threat': ('🦠', self._get_colors()['danger']),
            'Quarantine': ('📦', self._get_colors()['warn']),
            'Update': ('⬆️', self._get_colors()['info']),
            'Alert': ('🚨', self._get_colors()['danger']),
            'Heuristic': ('🤖', self._get_colors()['info']),
            'Firewall': ('🔥', self._get_colors()['warn']),
        }
        icon, color = icons.get(value, ('', self._get_colors()['text']))
        return icon, color

    def _set_row_style(self, tree, row, sev, typ=None):
        # Set row foreground color based on severity/type
        color = self._get_colors()['text']
        if sev:
            sev = sev.capitalize()
            if sev == 'Critical':
                color = self._get_colors()['danger']
            elif sev == 'High':
                color = self._get_colors()['danger']
            elif sev in ('Moderate', 'Medium'):
                color = self._get_colors()['warn']
            elif sev == 'Low':
                color = self._get_colors()['success']
        if typ:
            if typ == 'Blocked':
                color = self._get_colors()['danger']
            elif typ == 'Success':
                color = self._get_colors()['success']
        tree.tag_configure(row, foreground=color)

    def _create_widgets(self):
        colors = self._get_colors()
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill='x', pady=(10, 0))
        icon = ttk.Label(header_frame, text='📑', font=('Segoe UI Emoji', 32))
        icon.pack(side='left', padx=(20, 10))
        title = ttk.Label(header_frame, text='Reports & Audit Logs', font=('Segoe UI', 22, 'bold'))
        title.pack(side='left', pady=8)
        subtitle = ttk.Label(header_frame, text='Access real-time and historical security data', font=('Segoe UI', 12, 'italic'))
        subtitle.pack(side='left', padx=20, pady=8)
        # Main notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=30, pady=20)
        # Tabs
        self._create_security_reports_tab()
        self._create_threats_blocked_tab()
        self._create_scan_reports_tab()
        self._create_response_time_tab()
        self._create_update_reports_tab()
        # Footer
        footer = ttk.Label(self, text='Export, search, and filter your security data. Data updates in real time.', font=('Segoe UI', 9, 'italic'))
        footer.pack(side='bottom', pady=8)

    # --- Security Reports Tab ---
    def _create_security_reports_tab(self):
        frame = ttk.Frame(self.notebook)
        frame.pack(fill='both', expand=True)
        self.notebook.add(frame, text='🛡 Security Reports')
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(filter_frame, text='Date Range:').pack(side='left')
        
        # Use DateEntry if available, otherwise use basic Entry
        self.sec_start_date = ttk.Entry(filter_frame, width=12)
        self.sec_end_date = ttk.Entry(filter_frame, width=12)
        # Set default dates
        self.sec_start_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.sec_end_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        self.sec_start_date.pack(side='left', padx=2)
        ttk.Label(filter_frame, text='to').pack(side='left')
        self.sec_end_date.pack(side='left', padx=2)
        
        ttk.Label(filter_frame, text='Type:').pack(side='left', padx=(10,2))
        self.sec_type_var = tk.StringVar(value='All')
        self.sec_type_combo = ttk.Combobox(filter_frame, textvariable=self.sec_type_var, values=['All', 'Alert', 'Heuristic', 'Firewall', 'Scan', 'Threat', 'Quarantine', 'Update'], width=12, state='readonly')
        self.sec_type_combo.pack(side='left', padx=2)
        ttk.Label(filter_frame, text='Severity:').pack(side='left', padx=(10,2))
        self.sec_severity_var = tk.StringVar(value='All')
        self.sec_severity_combo = ttk.Combobox(filter_frame, textvariable=self.sec_severity_var, values=['All', 'Critical', 'High', 'Medium', 'Low'], width=10, state='readonly')
        self.sec_severity_combo.pack(side='left', padx=2)
        ttk.Label(filter_frame, text='Status:').pack(side='left', padx=(10,2))
        self.sec_status_var = tk.StringVar(value='All')
        self.sec_status_combo = ttk.Combobox(filter_frame, textvariable=self.sec_status_var, values=['All', 'Success', 'Failed', 'Blocked', 'Warning', 'Info', 'Error'], width=10, state='readonly')
        self.sec_status_combo.pack(side='left', padx=2)
        ttk.Button(filter_frame, text='Filter', command=self._load_security_reports).pack(side='left', padx=8)
        ttk.Label(filter_frame, text='Search:').pack(side='left', padx=(10,2))
        self.sec_search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.sec_search_var, width=18)
        search_entry.pack(side='left', padx=2)
        search_entry.bind('<Return>', lambda e: self._load_security_reports())
        columns = ('Time', 'Type', 'Status', 'Severity', 'Description')
        self.sec_tree = ttk.Treeview(frame, columns=columns, show='headings', height=16)
        
        # Configure row height and styling to prevent overlapping
        style = ttk.Style()
        style.configure('Treeview', rowheight=28, font=('Segoe UI', 11))
        
        for col in columns:
            self.sec_tree.heading(col, text=col)
            self.sec_tree.column(col, width=120 if col!='Description' else 320, anchor='center')
        self.sec_tree.pack(fill='both', expand=True, padx=10, pady=5)
        export_frame = ttk.Frame(frame)
        export_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(export_frame, text='Export CSV', command=lambda: self._export_tree(self.sec_tree, 'security_reports.csv', fmt='csv')).pack(side='left')
        self._load_security_reports()

    def _load_security_reports(self):
        try:
            self.sec_tree.delete(*self.sec_tree.get_children())
            
            # Get date range
            try:
                start = datetime.strptime(self.sec_start_date.get(), '%Y-%m-%d').date()
                end = datetime.strptime(self.sec_end_date.get(), '%Y-%m-%d').date()
            except:
                start = datetime.now().date()
                end = datetime.now().date()
            
            type_map = {
                'Alert': [EventType.PROTECTION_ALERT],
                'Heuristic': [EventType.THREAT_DETECTED],
                'Firewall': [EventType.SYSTEM_EVENT],
                'Scan': [EventType.SCAN_STARTED, EventType.SCAN_COMPLETED, EventType.SCAN_FAILED],
                'Threat': [EventType.THREAT_DETECTED, EventType.THREAT_QUARANTINED, EventType.THREAT_DELETED, EventType.THREAT_RESTORED],
                'Quarantine': [EventType.QUARANTINE_ACTION],
                'Update': [EventType.UPDATE_STARTED, EventType.UPDATE_COMPLETED, EventType.UPDATE_FAILED],
                'All': None
            }
            selected_type = self.sec_type_var.get()
            event_types = type_map[selected_type] if selected_type in type_map and selected_type != 'All' else None
            severity = self.sec_severity_var.get()
            status = self.sec_status_var.get()
            search = self.sec_search_var.get().strip()
            
            logs = logger.get_logs(
                event_types=event_types,
                start_date=datetime.combine(start, datetime.min.time()),
                end_date=datetime.combine(end, datetime.max.time()),
                search_query=search
            )
            
            print(f'[DEBUG] Loaded {len(logs)} logs for reports panel.')
            found = False
            for i, log in enumerate(logs):
                sev = log.get('severity', '').capitalize()
                stat = log.get('status', '').capitalize()
                desc = log.get('description', '')
                t = log.get('timestamp', '')
                t_fmt = t[:19].replace('T', ' ') if t else ''
                typ = log.get('event_type', '').replace('_', ' ').title()
                
                # Advanced filtering
                if severity != 'All' and sev != severity:
                    continue
                if status != 'All' and stat != status:
                    continue
                
                # Add icon to type
                icon, _ = self._badge(typ, 'type')
                typ_with_icon = f"{icon} {typ}" if icon else typ
                
                # Insert into tree
                item = self.sec_tree.insert('', 'end', values=(t_fmt, typ_with_icon, stat, sev, desc))
                self._set_row_style(self.sec_tree, item, sev, stat)
                found = True
            
            if not found:
                self.sec_tree.insert('', 'end', values=("No data found for the selected filters.", "", "", "", ""))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load security reports: {str(e)}")

    # --- Threats Blocked Tab ---
    def _create_threats_blocked_tab(self):
        frame = ttk.Frame(self.notebook)
        frame.pack(fill='both', expand=True)
        self.notebook.add(frame, text='🚨 Threats Blocked')
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(filter_frame, text='Source:').pack(side='left')
        self.threat_source_var = tk.StringVar(value='All')
        self.threat_source_combo = ttk.Combobox(filter_frame, textvariable=self.threat_source_var, values=['All', 'Scan', 'Web', 'USB', 'Test Scan'], width=10, state='readonly')
        self.threat_source_combo.pack(side='left', padx=2)
        ttk.Label(filter_frame, text='Severity:').pack(side='left', padx=(10,2))
        self.threat_severity_var = tk.StringVar(value='All')
        self.threat_severity_combo = ttk.Combobox(filter_frame, textvariable=self.threat_severity_var, values=['All', 'Critical', 'High', 'Moderate', 'Low'], width=10, state='readonly')
        self.threat_severity_combo.pack(side='left', padx=2)
        ttk.Button(filter_frame, text='Filter', command=self._load_threats_blocked).pack(side='left', padx=8)
        ttk.Label(filter_frame, text='Search:').pack(side='left', padx=(10,2))
        self.threat_search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.threat_search_var, width=18)
        search_entry.pack(side='left', padx=2)
        search_entry.bind('<Return>', lambda e: self._load_threats_blocked())
        columns = ('Time', 'File', 'Type', 'Path', 'Source', 'Severity', 'Details')
        self.threats_tree = ttk.Treeview(frame, columns=columns, show='headings', height=16)
        
        # Configure row height and styling to prevent overlapping
        style = ttk.Style()
        style.configure('Treeview', rowheight=28, font=('Segoe UI', 11))
        
        vsb2 = ttk.Scrollbar(frame, orient='vertical', command=self.threats_tree.yview)
        hsb2 = ttk.Scrollbar(frame, orient='horizontal', command=self.threats_tree.xview)
        self.threats_tree.configure(yscrollcommand=vsb2.set, xscrollcommand=hsb2.set)
        self.threats_tree.pack(side='left', fill='both', expand=True, padx=10, pady=5)
        vsb2.pack(side='right', fill='y')
        hsb2.pack(side='bottom', fill='x')
        self.threats_tree.bind('<Motion>', self._on_threat_hover)
        export_frame = ttk.Frame(frame)
        export_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(export_frame, text='Export CSV', command=lambda: self._export_tree(self.threats_tree, 'threats_blocked.csv', fmt='csv')).pack(side='left')
        self._load_threats_blocked()

    def _load_threats_blocked(self):
        try:
            self.threats_tree.delete(*self.threats_tree.get_children())
            source = self.threat_source_var.get()
            severity = self.threat_severity_var.get()
            search = self.threat_search_var.get().strip().lower()
            
            # Get quarantine items
            try:
                items = self.quarantine_manager.list_items()
            except:
                items = []
            
            for i, item in enumerate(items):
                origin = item.get('origin', 'Scan')
                if source != 'All' and origin != source:
                    continue
                sev = item.get('severity', '').capitalize()
                if severity != 'All' and sev != severity:
                    continue
                if search and search not in item.get('file_name', '').lower() and search not in item.get('threat_type', '').lower():
                    continue
                t = item.get('date_quarantined', item.get('quarantine_date', ''))
                file = item.get('file_name', item.get('quarantine_name', ''))
                typ = item.get('threat_type', '')
                path = item.get('original_path', '')
                details = f"MD5: {item.get('md5', '')}\nSHA256: {item.get('sha256', '')}\nOrigin: {origin}"
                icon, color = self._badge(sev, 'severity')
                row_id = self.threats_tree.insert('', 'end', values=(t, file, typ, path, origin, f"{icon} {sev}", details), tags=(f'sev_{sev}',))
                self._set_row_style(self.threats_tree, f'sev_{sev}', sev)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load threats blocked: {str(e)}")

    def _on_threat_hover(self, event):
        # Show tooltip with details if hovering over Details column
        try:
            region = self.threats_tree.identify('region', event.x, event.y)
            if region == 'cell':
                row_id = self.threats_tree.identify_row(event.y)
                col = self.threats_tree.identify_column(event.x)
                if col == '#7':  # Details column
                    values = self.threats_tree.item(row_id, 'values')
                    if values:
                        details = values[6]
                        x = event.x_root + 10
                        y = event.y_root + 10
                        self._show_tooltip(x, y, details)
                else:
                    self._hide_tooltip()
            else:
                self._hide_tooltip()
        except:
            pass

    def _show_tooltip(self, x, y, text):
        if hasattr(self, '_tooltip') and self._tooltip:
            self._tooltip.destroy()
        self._tooltip = tw = tk.Toplevel(self)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=text, justify='left', background='#23272f', foreground='white', relief='solid', borderwidth=1, font=('Segoe UI', 10, 'normal'))
        label.pack(ipadx=8, ipady=4)

    def _hide_tooltip(self):
        if hasattr(self, '_tooltip') and self._tooltip:
            self._tooltip.destroy()
            self._tooltip = None

    # --- Scan Reports Tab ---
    def _create_scan_reports_tab(self):
        frame = ttk.Frame(self.notebook)
        frame.pack(fill='both', expand=True)
        self.notebook.add(frame, text='✅ Scan Reports')
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(filter_frame, text='Scan Type:').pack(side='left')
        self.scan_type_var = tk.StringVar(value='All')
        self.scan_type_combo = ttk.Combobox(filter_frame, textvariable=self.scan_type_var, values=['All', 'Quick', 'Full', 'Custom', 'Boot', 'Deep'], width=10, state='readonly')
        self.scan_type_combo.pack(side='left', padx=2)
        ttk.Label(filter_frame, text='Threat Status:').pack(side='left', padx=(10,2))
        self.scan_threat_status_var = tk.StringVar(value='All')
        self.scan_threat_status_combo = ttk.Combobox(filter_frame, textvariable=self.scan_threat_status_var, values=['All', 'Pattern Match', 'Clean', 'Obfuscated'], width=14, state='readonly')
        self.scan_threat_status_combo.pack(side='left', padx=2)
        ttk.Label(filter_frame, text='Date Range:').pack(side='left', padx=(10,2))
        self.scan_start_date = ttk.Entry(filter_frame, width=12)
        self.scan_start_date.pack(side='left', padx=2)
        ttk.Label(filter_frame, text='to').pack(side='left')
        self.scan_end_date = ttk.Entry(filter_frame, width=12)
        self.scan_end_date.pack(side='left', padx=2)
        ttk.Button(filter_frame, text='Filter', command=self._load_scan_reports).pack(side='left', padx=8)
        ttk.Label(filter_frame, text='Search:').pack(side='left', padx=(10,2))
        self.scan_search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.scan_search_var, width=18)
        search_entry.pack(side='left', padx=2)
        search_entry.bind('<Return>', lambda e: self._load_scan_reports())
        columns = ('Time', 'File', 'Type', 'Status', 'Threat', 'Size', 'Path')
        self.scan_tree = ttk.Treeview(frame, columns=columns, show='headings', height=16)
        
        # Configure row height and styling to prevent overlapping
        style = ttk.Style()
        style.configure('Treeview', rowheight=28, font=('Segoe UI', 11))
        
        vsb = ttk.Scrollbar(frame, orient='vertical', command=self.scan_tree.yview)
        hsb = ttk.Scrollbar(frame, orient='horizontal', command=self.scan_tree.xview)
        self.scan_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.scan_tree.pack(side='left', fill='both', expand=True, padx=10, pady=5)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        export_frame = ttk.Frame(frame)
        export_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(export_frame, text='Export CSV', command=lambda: self._export_tree(self.scan_tree, 'scan_reports.csv', fmt='csv')).pack(side='left')
        self._load_scan_reports()

    def _load_scan_reports(self):
        try:
            self.scan_tree.delete(*self.scan_tree.get_children())
            scan_type = self.scan_type_var.get()
            threat_status = self.scan_threat_status_var.get()
            search = self.scan_search_var.get().strip().lower()
            
            # Get scan history
            try:
                scan_data = scan_history.load_scan_history()
            except:
                scan_data = []
            
            for entry in scan_data:
                typ = entry.get('scan_type', 'Custom')
                if scan_type != 'All' and typ != scan_type:
                    continue
                threat = entry.get('threat_type', 'Clean')
                if threat_status != 'All' and threat != threat_status:
                    continue
                if search and search not in entry.get('file_name', '').lower():
                    continue
                t = entry.get('timestamp', 0)
                t_fmt = datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S') if t else ''
                file = entry.get('file_name', '')
                status = entry.get('status', 'Scanned')
                size = entry.get('file_size', 0)
                size_fmt = f"{size:,} bytes" if size else "Unknown"
                path = entry.get('file_path', '')
                icon, _ = self._badge(threat, 'threat')
                threat_with_icon = f"{icon} {threat}" if icon else threat
                item = self.scan_tree.insert('', 'end', values=(t_fmt, file, typ, status, threat_with_icon, size_fmt, path))
                self._set_row_style(self.scan_tree, item, 'High' if threat != 'Clean' else 'Low')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load scan reports: {str(e)}")

    # --- Response Time Tab ---
    def _create_response_time_tab(self):
        frame = ttk.Frame(self.notebook)
        frame.pack(fill='both', expand=True)
        self.notebook.add(frame, text='⚡ Response Time')
        if MATPLOTLIB_AVAILABLE:
            fig, ax = plt.subplots(figsize=(10, 6))
            self._plot_response_time(ax)
            canvas = FigureCanvasTkAgg(fig, frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        else:
            # Fallback: show text info
            info_frame = ttk.Frame(frame)
            info_frame.pack(fill='both', expand=True, padx=20, pady=20)
            ttk.Label(info_frame, text='Response Time Metrics', font=('Segoe UI', 16, 'bold')).pack(pady=10)
            ttk.Label(info_frame, text='Matplotlib not available for charts.\nInstall matplotlib to view response time graphs.', font=('Segoe UI', 12)).pack(pady=20)

    def _plot_response_time(self, ax):
        try:
            # Sample data - in real implementation, get from system monitor
            times = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']
            response_times = [120, 95, 85, 110, 130, 100]  # milliseconds
            
            ax.plot(times, response_times, marker='o', linewidth=2, markersize=8, color='#00D4FF')
            ax.set_title('System Response Time (24h)', fontsize=14, fontweight='bold')
            ax.set_xlabel('Time', fontsize=12)
            ax.set_ylabel('Response Time (ms)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.set_facecolor('#f8f9fa')
        except Exception as e:
            ax.text(0.5, 0.5, f'Error loading chart: {str(e)}', ha='center', va='center', transform=ax.transAxes)

    # --- Update Reports Tab ---
    def _create_update_reports_tab(self):
        frame = ttk.Frame(self.notebook)
        frame.pack(fill='both', expand=True)
        self.notebook.add(frame, text='⬆️ Update Reports')
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(filter_frame, text='Update Type:').pack(side='left')
        self.update_type_var = tk.StringVar(value='All')
        self.update_type_combo = ttk.Combobox(filter_frame, textvariable=self.update_type_var, values=['All', 'Virus Definitions', 'Engine', 'UI', 'System'], width=15, state='readonly')
        self.update_type_combo.pack(side='left', padx=2)
        ttk.Label(filter_frame, text='Status:').pack(side='left', padx=(10,2))
        self.update_status_var = tk.StringVar(value='All')
        self.update_status_combo = ttk.Combobox(filter_frame, textvariable=self.update_status_var, values=['All', 'Success', 'Failed', 'Pending'], width=10, state='readonly')
        self.update_status_combo.pack(side='left', padx=2)
        ttk.Button(filter_frame, text='Filter', command=self._load_update_reports).pack(side='left', padx=8)
        ttk.Label(filter_frame, text='Search:').pack(side='left', padx=(10,2))
        self.update_search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.update_search_var, width=18)
        search_entry.pack(side='left', padx=2)
        search_entry.bind('<Return>', lambda e: self._load_update_reports())
        columns = ('Time', 'Type', 'Status', 'Version', 'Size', 'Details')
        self.update_tree = ttk.Treeview(frame, columns=columns, show='headings', height=16)
        
        # Configure row height and styling to prevent overlapping
        style = ttk.Style()
        style.configure('Treeview', rowheight=28, font=('Segoe UI', 11))
        
        vsb3 = ttk.Scrollbar(frame, orient='vertical', command=self.update_tree.yview)
        hsb3 = ttk.Scrollbar(frame, orient='horizontal', command=self.update_tree.xview)
        self.update_tree.configure(yscrollcommand=vsb3.set, xscrollcommand=hsb3.set)
        self.update_tree.pack(side='left', fill='both', expand=True, padx=10, pady=5)
        vsb3.pack(side='right', fill='y')
        hsb3.pack(side='bottom', fill='x')
        export_frame = ttk.Frame(frame)
        export_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(export_frame, text='Export CSV', command=lambda: self._export_tree(self.update_tree, 'update_reports.csv', fmt='csv')).pack(side='left')
        self._load_update_reports()

    def _load_update_reports(self):
        try:
            self.update_tree.delete(*self.update_tree.get_children())
            update_type = self.update_type_var.get()
            status = self.update_status_var.get()
            search = self.update_search_var.get().strip().lower()
            
            # Sample update data - in real implementation, get from update system
            updates = [
                {'time': '2024-01-15 10:30:00', 'type': 'Virus Definitions', 'status': 'Success', 'version': '2024.1.15', 'size': '2.5 MB', 'details': 'Updated 15,432 signatures'},
                {'time': '2024-01-14 15:45:00', 'type': 'Engine', 'status': 'Success', 'version': '2.1.0', 'size': '8.2 MB', 'details': 'Performance improvements and bug fixes'},
                {'time': '2024-01-13 09:20:00', 'type': 'UI', 'status': 'Failed', 'version': '1.5.2', 'size': '1.8 MB', 'details': 'Network timeout during download'},
            ]
            
            for update in updates:
                typ = update['type']
                if update_type != 'All' and typ != update_type:
                    continue
                stat = update['status']
                if status != 'All' and stat != status:
                    continue
                if search and search not in typ.lower() and search not in update['details'].lower():
                    continue
                
                icon, _ = self._badge(stat, 'status')
                stat_with_icon = f"{icon} {stat}" if icon else stat
                item = self.update_tree.insert('', 'end', values=(
                    update['time'], typ, stat_with_icon, update['version'], update['size'], update['details']
                ))
                self._set_row_style(self.update_tree, item, 'High' if stat == 'Failed' else 'Low', stat)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load update reports: {str(e)}")

    def _export_tree(self, tree, filename, fmt='csv'):
        try:
            if fmt == 'csv':
                file_path = filedialog.asksaveasfilename(
                    defaultextension='.csv',
                    filetypes=[('CSV files', '*.csv'), ('All files', '*.*')]
                )
                if file_path:
                    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        # Write headers
                        headers = []
                        for col in tree['columns']:
                            headers.append(tree.heading(col)['text'])
                        writer.writerow(headers)
                        # Write data
                        for item in tree.get_children():
                            values = tree.item(item)['values']
                            writer.writerow(values)
                    messagebox.showinfo('Export Successful', f'Data exported to:\n{file_path}')
        except Exception as e:
            messagebox.showerror('Export Error', f'Failed to export data:\n{str(e)}') 