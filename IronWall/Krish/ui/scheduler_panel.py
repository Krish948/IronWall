import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading

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

class SchedulerPanel(ttk.Frame):
    def __init__(self, parent, scan_callback=None):
        super().__init__(parent)
        self.scan_callback = scan_callback
        self._create_widgets()
        self.refresh()

    def _create_widgets(self):
        """Create the main scheduler interface"""
        colors = self._get_colors()
        
        # Header
        header_frame = ttk.Frame(self, style='TFrame')
        header_frame.pack(fill='x', pady=(10, 0))
        icon = ttk.Label(header_frame, text='📅', font=('Segoe UI Emoji', 32), background=colors['bg'], foreground=colors['accent'])
        icon.pack(side='left', padx=(20, 10))
        title = ttk.Label(header_frame, text='Scan Scheduler', font=('Segoe UI', 22, 'bold'), background=colors['bg'], foreground=colors['accent'])
        title.pack(side='left', pady=8)
        subtitle = ttk.Label(header_frame, text='Automate scan routines and monitor performance', font=('Segoe UI', 12, 'italic'), background=colors['bg'], foreground=colors['text'])
        subtitle.pack(side='left', padx=20, pady=8)
        
        # Add new schedule button
        add_btn = ttk.Button(header_frame, text='➕ Add Schedule', style='Accent.TButton', command=self._add_new_schedule)
        add_btn.pack(side='right', padx=20)
        Tooltip(add_btn, 'Add New Scan Schedule')

        # Main container with left and right panels
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=30, pady=20)
        main_frame.columnconfigure(0, weight=2)  # Left panel (schedules)
        main_frame.columnconfigure(1, weight=1)  # Right panel (statistics)
        main_frame.rowconfigure(0, weight=1)

        # Left panel - Scheduled Scans
        self._create_schedules_panel(main_frame, colors)
        
        # Right panel - Statistics Dashboard
        self._create_statistics_panel(main_frame, colors)
        
        # Load initial data
        self._load_scheduled_scans()
        self._load_scan_statistics()

    def _create_schedules_panel(self, parent, colors):
        """Create the left panel with scheduled scans list"""
        schedules_frame = ttk.LabelFrame(parent, text="📋 Scheduled Scans", padding=16, style='TLabelframe')
        schedules_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        # Create treeview for scheduled scans
        columns = ('Type', 'Time', 'Day', 'Enabled', 'Last Run', 'Status', 'Actions')
        self.schedules_tree = ttk.Treeview(schedules_frame, columns=columns, show='headings', height=15, style='Treeview')
        
        # Configure row height and styling to prevent overlapping
        style = ttk.Style()
        style.configure('Treeview', rowheight=28, font=('Segoe UI', 11))
        
        # Configure columns
        column_configs = [
            ('Type', 140, 'w'),
            ('Time', 120, 'center'),
            ('Day', 100, 'center'),
            ('Enabled', 100, 'center'),
            ('Last Run', 180, 'w'),
            ('Status', 120, 'center'),
            ('Actions', 120, 'center')
        ]
        
        for col, width, anchor in column_configs:
            self.schedules_tree.heading(col, text=col, anchor=anchor)
            self.schedules_tree.column(col, width=width, anchor=anchor, stretch=True)
        
        # Add scrollbars for scheduled scans
        vscroll = ttk.Scrollbar(schedules_frame, orient='vertical', command=self.schedules_tree.yview)
        hscroll = ttk.Scrollbar(schedules_frame, orient='horizontal', command=self.schedules_tree.xview)
        self.schedules_tree.configure(yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)
        self.schedules_tree.pack(side='left', fill='both', expand=True)
        vscroll.pack(side='right', fill='y')
        hscroll.pack(side='bottom', fill='x')
        
        # Bind selection event
        self.schedules_tree.bind('<<TreeviewSelect>>', self._on_schedule_select)
        
        # Control buttons frame
        controls_frame = ttk.Frame(schedules_frame)
        controls_frame.pack(fill='x', pady=(10, 0))
        
        self.run_now_btn = ttk.Button(controls_frame, text='▶️ Run Now', style='Success.TButton', command=self._run_selected_schedule)
        self.run_now_btn.pack(side='left', padx=(0, 10))
        
        self.edit_btn = ttk.Button(controls_frame, text='✏️ Edit', style='Accent.TButton', command=self._edit_selected_schedule)
        self.edit_btn.pack(side='left', padx=(0, 10))
        
        self.delete_btn = ttk.Button(controls_frame, text='🗑️ Delete', style='Danger.TButton', command=self._delete_selected_schedule)
        self.delete_btn.pack(side='left', padx=(0, 10))
        
        # Disable buttons initially
        self.run_now_btn.state(['disabled'])
        self.edit_btn.state(['disabled'])
        self.delete_btn.state(['disabled'])

    def _create_statistics_panel(self, parent, colors):
        """Create the right panel with scan statistics"""
        stats_frame = ttk.LabelFrame(parent, text="📊 Scan Statistics", padding=16, style='TLabelframe')
        stats_frame.grid(row=0, column=1, sticky='nsew')
        
        # Statistics summary
        summary_frame = ttk.Frame(stats_frame)
        summary_frame.pack(fill='x', pady=(0, 15))
        
        # Create stat boxes
        self.total_schedules_label = ttk.Label(summary_frame, text="📋 Total Schedules: 0", font=('Segoe UI', 13, 'bold'), style='TLabel')
        self.total_schedules_label.pack(anchor='w', pady=5)
        
        self.active_schedules_label = ttk.Label(summary_frame, text="✅ Active Schedules: 0", font=('Segoe UI', 13, 'bold'), style='TLabel')
        self.active_schedules_label.pack(anchor='w', pady=5)
        
        self.completed_scans_label = ttk.Label(summary_frame, text="🎯 Completed Scans: 0", font=('Segoe UI', 13, 'bold'), style='TLabel')
        self.completed_scans_label.pack(anchor='w', pady=5)
        
        self.failed_scans_label = ttk.Label(summary_frame, text="❌ Failed Scans: 0", font=('Segoe UI', 13, 'bold'), foreground=colors['danger'], style='TLabel')
        self.failed_scans_label.pack(anchor='w', pady=5)
        
        # Upcoming scans section
        upcoming_frame = ttk.LabelFrame(stats_frame, text="⏰ Upcoming Scans", padding=10)
        upcoming_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Create treeview for upcoming scans
        upcoming_columns = ('Type', 'Next Run', 'Status')
        self.upcoming_tree = ttk.Treeview(upcoming_frame, columns=upcoming_columns, show='headings', height=8, style='Treeview')
        
        # Configure row height and styling to prevent overlapping
        style = ttk.Style()
        style.configure('Treeview', rowheight=28, font=('Segoe UI', 11))
        
        # Configure columns
        upcoming_column_configs = [
            ('Type', 140, 'w'),
            ('Next Run', 180, 'w'),
            ('Status', 120, 'center')
        ]
        
        for col, width, anchor in upcoming_column_configs:
            self.upcoming_tree.heading(col, text=col, anchor=anchor)
            self.upcoming_tree.column(col, width=width, anchor=anchor, stretch=True)
        
        # Add scrollbars for upcoming scans
        vscroll2 = ttk.Scrollbar(upcoming_frame, orient='vertical', command=self.upcoming_tree.yview)
        hscroll2 = ttk.Scrollbar(upcoming_frame, orient='horizontal', command=self.upcoming_tree.xview)
        self.upcoming_tree.configure(yscrollcommand=vscroll2.set, xscrollcommand=hscroll2.set)
        self.upcoming_tree.pack(side='left', fill='both', expand=True)
        vscroll2.pack(side='right', fill='y')
        hscroll2.pack(side='bottom', fill='x')

    def _load_scheduled_scans(self):
        """Load scheduled scans into the treeview"""
        # Clear existing items
        for item in self.schedules_tree.get_children():
            self.schedules_tree.delete(item)
        
        # Create some mock schedules for demonstration
        mock_schedules = [
            {
                'scan_type': 'Quick Scan',
                'time': '09:00',
                'day': 'Daily',
                'enabled': True,
                'last_run': '2024-01-15 09:00',
                'status': 'Completed'
            },
            {
                'scan_type': 'Custom Scan',
                'time': '14:30',
                'day': 'Weekly',
                'enabled': True,
                'last_run': '2024-01-13 14:30',
                'status': 'Failed'
            }
        ]
        
        for i, schedule in enumerate(mock_schedules):
            # Format time
            time_str = schedule.get('time', '09:00')
            day_str = schedule.get('day', 'Daily')
            enabled_str = '✓' if schedule.get('enabled', True) else '✗'
            last_run = schedule.get('last_run', 'Never')
            status = schedule.get('status', 'Ready')
            
            # Color code status
            if status == 'Running':
                status = '🔄 Running'
            elif status == 'Completed':
                status = '✅ Completed'
            elif status == 'Failed':
                status = '❌ Failed'
            else:
                status = '⏳ Ready'
            
            values = (
                schedule.get('scan_type', 'Quick Scan'),
                time_str,
                day_str,
                enabled_str,
                last_run,
                status,
                '▶️ ✏️ 🗑️'  # Action buttons placeholder
            )
            
            # Add with alternating row colors
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.schedules_tree.insert('', 'end', values=values, tags=(tag,))

    def _load_scan_statistics(self):
        """Load scan statistics into the dashboard"""
        # Use mock data for statistics
        total_schedules = 2
        active_schedules = 2
        completed_scans = 1
        failed_scans = 1
        
        # Update labels
        self.total_schedules_label.config(text=f"📋 Total Schedules: {total_schedules}")
        self.active_schedules_label.config(text=f"✅ Active Schedules: {active_schedules}")
        self.completed_scans_label.config(text=f"🎯 Completed Scans: {completed_scans}")
        self.failed_scans_label.config(text=f"❌ Failed Scans: {failed_scans}")
        
        # Load upcoming scans
        self._load_upcoming_scans()

    def _load_upcoming_scans(self):
        """Load upcoming scans into the treeview"""
        # Clear existing items
        for item in self.upcoming_tree.get_children():
            self.upcoming_tree.delete(item)
        
        # Create mock upcoming scans
        mock_upcoming = [
            {'type': 'Quick Scan', 'next_run': '2024-01-16 09:00', 'status': 'Scheduled'},
            {'type': 'Custom Scan', 'next_run': '2024-01-20 14:30', 'status': 'Scheduled'}
        ]
        
        for i, scan in enumerate(mock_upcoming):
            values = (
                scan['type'],
                scan['next_run'],
                scan['status']
            )
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.upcoming_tree.insert('', 'end', values=values, tags=(tag,))

    def _on_schedule_select(self, event):
        """Handle schedule selection"""
        selection = self.schedules_tree.selection()
        if selection:
            # Enable action buttons
            self.run_now_btn.state(['!disabled'])
            self.edit_btn.state(['!disabled'])
            self.delete_btn.state(['!disabled'])
        else:
            # Disable action buttons
            self.run_now_btn.state(['disabled'])
            self.edit_btn.state(['disabled'])
            self.delete_btn.state(['disabled'])

    def _add_new_schedule(self):
        """Add a new scan schedule"""
        # Create a simple dialog for adding new schedule
        dialog = tk.Toplevel(self)
        dialog.title("Add New Scan Schedule")
        dialog.geometry("400x300")
        dialog.configure(bg=self._get_colors()['bg'])
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.winfo_rootx() + 50, self.winfo_rooty() + 50))
        
        # Schedule type
        ttk.Label(dialog, text="Scan Type:", font=('Segoe UI', 12)).pack(pady=5)
        scan_type_var = tk.StringVar(value="Quick Scan")
        scan_type_combo = ttk.Combobox(dialog, textvariable=scan_type_var, 
                                      values=["Quick Scan", "Custom Scan"],
                                      state="readonly")
        scan_type_combo.pack(pady=5)
        
        # Time
        ttk.Label(dialog, text="Time:", font=('Segoe UI', 12)).pack(pady=5)
        time_var = tk.StringVar(value="09:00")
        time_entry = ttk.Entry(dialog, textvariable=time_var)
        time_entry.pack(pady=5)
        
        # Day/Frequency
        ttk.Label(dialog, text="Frequency:", font=('Segoe UI', 12)).pack(pady=5)
        frequency_var = tk.StringVar(value="Daily")
        frequency_combo = ttk.Combobox(dialog, textvariable=frequency_var,
                                      values=["Daily", "Weekly", "Monthly", "Once"],
                                      state="readonly")
        frequency_combo.pack(pady=5)
        
        # Enable checkbox
        enabled_var = tk.BooleanVar(value=True)
        enabled_check = ttk.Checkbutton(dialog, text="Enable Schedule", variable=enabled_var)
        enabled_check.pack(pady=10)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def save_schedule():
            # For now, just refresh the display with the new schedule
            # In a real implementation, this would save to a database or file
            messagebox.showinfo("Success", f"New {scan_type_var.get()} schedule added successfully!")
            dialog.destroy()
            # Refresh the display
            self._load_scheduled_scans()
            self._load_scan_statistics()
        
        ttk.Button(button_frame, text="Save", style='Accent.TButton', command=save_schedule).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)

    def _run_selected_schedule(self):
        """Run the selected schedule immediately"""
        selection = self.schedules_tree.selection()
        if not selection:
            return
        
        item = self.schedules_tree.item(selection[0])
        schedule_type = item['values'][0]
        
        # Update status to running
        self.schedules_tree.set(selection[0], 'Status', '🔄 Running')
        
        # Simulate running the scan
        def run_scan():
            import time
            time.sleep(2)  # Simulate scan time
            self.schedules_tree.set(selection[0], 'Status', '✅ Completed')
            self.schedules_tree.set(selection[0], 'Last Run', datetime.now().strftime('%Y-%m-%d %H:%M'))
            self._load_scan_statistics()
        
        threading.Thread(target=run_scan, daemon=True).start()

    def _edit_selected_schedule(self):
        """Edit the selected schedule"""
        selection = self.schedules_tree.selection()
        if not selection:
            return
        
        # For now, just show a message
        messagebox.showinfo("Edit Schedule", "Edit functionality will be implemented in the next version.")

    def _delete_selected_schedule(self):
        """Delete the selected schedule"""
        selection = self.schedules_tree.selection()
        if not selection:
            return
        
        item = self.schedules_tree.item(selection[0])
        schedule_type = item['values'][0]
        
        if messagebox.askyesno("Delete Schedule", f"Are you sure you want to delete the '{schedule_type}' schedule?"):
            # Remove from treeview
            self.schedules_tree.delete(selection[0])
            # In a real implementation, you would also remove from the scheduler manager
            self._load_scan_statistics()

    def _refresh_panel(self):
        """Refresh the entire panel"""
        for widget in self.winfo_children():
            widget.destroy()
        self._create_widgets()

    def _format_time(self, t):
        if not t:
            return '-'
        try:
            dt = datetime.fromisoformat(t)
            return dt.strftime('%Y-%m-%d %H:%M')
        except Exception:
            return t

    def _get_colors(self):
        """Get color scheme based on theme"""
        # For now, use a default color scheme
        return {
            'bg': '#F7F9FB',
            'accent': '#1976D2',
            'text': '#222B45',
            'danger': '#D32F2F',
            'success': '#43A047',
            'warn': '#FFA000',
            'sidebar': '#E9EEF3',
            'tree_bg': '#E9EEF3',
            'tree_fg': '#222B45',
            'tree_sel': '#1976D2',
            'border': '#D1D9E6',
            'hover': '#E3E8EF',
            'disabled': '#B0B7C3'
        }

    def refresh(self):
        """Refresh the panel data"""
        self._load_scheduled_scans()
        self._load_scan_statistics()

    # Add more methods for run/edit/delete as needed 