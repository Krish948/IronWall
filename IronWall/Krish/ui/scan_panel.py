import tkinter as tk
from ttkbootstrap import ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from datetime import datetime, timedelta
import os
import time
import threading
import psutil
import logging

class ScanPanel(ttk.Frame):
    def __init__(self, parent, scan_callbacks=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.scan_callbacks = scan_callbacks or {}
        self.selected_paths = []
        self.quick_scan_files = []  # Store user-added files for quick scan
        self.quick_scan_folders = []  # Store user-added folders for quick scan
        self.boot_scan_enabled = tk.BooleanVar(value=False)
        self.heuristic_enabled = tk.BooleanVar(value=True)
        self.compressed_enabled = tk.BooleanVar(value=True)
        self.cloud_enabled = tk.BooleanVar(value=False)
        self.cpu_limit = tk.IntVar(value=80)
        self.scan_type = tk.StringVar(value='Quick')
        self.last_scanned = {}
        
        # Time tracking variables
        self.scan_start_time = None
        self.scan_elapsed_time = tk.StringVar(value='00:00:00')
        self.scan_eta = tk.StringVar(value='--:--:--')
        self.scan_speed = tk.StringVar(value='0 files/sec')
        self.scan_status = tk.StringVar(value='Ready to scan')
        self.scan_phase = tk.StringVar(value='Idle')
        self.total_files_estimate = 0
        self.files_scanned = 0
        self.scan_speed_history = []
        self.update_timer = None
        self._progress_mode = None  # Track current progress bar mode
        
        self._build_ui()

    def _build_ui(self):
        try:
            # Main layout: left (scan types), center (progress/status), bottom (controls/summary)
            main_frame = ttk.Frame(self)
            main_frame.pack(fill='both', expand=True)
            main_frame.columnconfigure(1, weight=1)
            main_frame.rowconfigure(0, weight=1)

            # --- Scan Types Panel ---
            try:
                scan_types_frame = ttk.LabelFrame(main_frame, text='🧪 Scan Types', padding=12)
                scan_types_frame.pack(side='left', fill='y', padx=(10, 0), pady=10)
                types = [
                    ('Quick', 'Scans key system areas (memory, registry, startup folders)'),
                    ('Custom', 'Select files/folders to scan'),
                    ('Boot', 'Run scan on next system restart'),
                ]
                for typ, desc in types:
                    row = ttk.Frame(scan_types_frame)
                    row.pack(fill='x', pady=4)
                    if typ == 'Custom':
                        btn = ttk.Button(row, text=f'{self._icon_for_type(typ)} {typ} Scan', style='TButton',
                                         command=lambda t=typ: self._on_scan_type_selected(t))
                    else:
                        btn = ttk.Button(row, text=f'{self._icon_for_type(typ)} {typ} Scan', style='Accent.TButton' if typ=='Quick' else 'TButton',
                                         command=lambda t=typ: self._on_scan_type_selected_and_start(t))
                    btn.pack(side='left')
                    Tooltip(btn, desc)
                    last = self.last_scanned.get(typ, 'Never')
                    last_lbl = ttk.Label(row, text=f'Last: {last}', font=('Segoe UI', 9, 'italic'))
                    last_lbl.pack(side='left', padx=8)
                    if typ == 'Quick':
                        quick_file_btn = ttk.Button(row, text='+ Add File', command=self._add_quick_file)
                        quick_file_btn.pack(side='left', padx=2)
                        Tooltip(quick_file_btn, 'Add individual files to include in Quick Scan')
                        quick_folder_btn = ttk.Button(row, text='+ Add Folder', command=self._add_quick_folder)
                        quick_folder_btn.pack(side='left', padx=2)
                        Tooltip(quick_folder_btn, 'Add folders to include in Quick Scan')
                        self.quick_files_frame = ttk.Frame(scan_types_frame)
                        self.quick_files_frame.pack(fill='x', padx=24, pady=(0, 2))
                        self._show_quick_files()
                    if typ == 'Boot':
                        boot_toggle = ttk.Checkbutton(row, variable=self.boot_scan_enabled, text='Enable', style='Switch.TCheckbutton')
                        boot_toggle.pack(side='left', padx=4)
                        Tooltip(boot_toggle, 'Run scan at next system boot')
                # Custom scan path management
                self.custom_paths_frame = ttk.Frame(scan_types_frame)
                self.custom_paths_frame.pack(fill='x', pady=2)
                if self.scan_type.get() == 'Custom':
                    self._show_custom_paths()
            except Exception as e:
                logging.exception('Error creating Scan Types panel:')
                tk.Label(main_frame, text=f'Scan Types Error: {e}', fg='red').pack(side='left')

            # --- Center: Progress & Status ---
            try:
                center_frame = ttk.Frame(main_frame)
                center_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
                


                # --- Resource Usage Panel ---
                try:
                    resource_frame = ttk.Frame(center_frame)
                    resource_frame.pack(fill='x', pady=(0, 8))
                    self.cpu_label = ttk.Label(resource_frame, text='CPU: --%', font=('Segoe UI', 10, 'bold'))
                    self.cpu_label.pack(side='left', padx=8)
                    self.ram_label = ttk.Label(resource_frame, text='RAM: --%', font=('Segoe UI', 10, 'bold'))
                    self.ram_label.pack(side='left', padx=8)
                    self._update_resource_usage()
                except Exception as e:
                    logging.exception('Error creating Resource Usage panel:')
                    tk.Label(center_frame, text=f'Resource Panel Error: {e}', fg='red').pack(fill='x')

                # Enhanced Progress/Status Frame
                try:
                    status_frame = ttk.LabelFrame(center_frame, text='⏱ Scan Progress & Status', padding=12)
                    status_frame.pack(fill='x')
                    
                    # Time and Speed Information
                    time_frame = ttk.Frame(status_frame)
                    time_frame.pack(fill='x', pady=(0, 8))
                    
                    # Row 1: Elapsed Time and ETA
                    time_row1 = ttk.Frame(time_frame)
                    time_row1.pack(fill='x', pady=2)
                    ttk.Label(time_row1, text='⏱ Elapsed:', font=('Segoe UI', 10, 'bold')).pack(side='left')
                    ttk.Label(time_row1, textvariable=self.scan_elapsed_time, font=('Segoe UI', 11, 'bold'), foreground='#1976D2').pack(side='left', padx=4)
                    ttk.Label(time_row1, text='| ⏳ ETA:', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=(16, 0))
                    ttk.Label(time_row1, textvariable=self.scan_eta, font=('Segoe UI', 11, 'bold'), foreground='#FF9800').pack(side='left', padx=4)
                    ttk.Label(time_row1, text='| 🚀 Speed:', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=(16, 0))
                    ttk.Label(time_row1, textvariable=self.scan_speed, font=('Segoe UI', 11, 'bold'), foreground='#4CAF50').pack(side='left', padx=4)
                    
                    # Row 2: Scan Statistics
                    stat_row = ttk.Frame(time_frame)
                    stat_row.pack(fill='x', pady=2)
                    self.files_scanned_var = tk.IntVar(value=0)
                    self.threats_found_var = tk.IntVar(value=0)
                    ttk.Label(stat_row, text='📁 Files Scanned:').pack(side='left')
                    ttk.Label(stat_row, textvariable=self.files_scanned_var, font=('Segoe UI', 11, 'bold')).pack(side='left', padx=4)
                    ttk.Label(stat_row, text='| 🚨 Threats Detected:').pack(side='left', padx=8)
                    ttk.Label(stat_row, textvariable=self.threats_found_var, font=('Segoe UI', 11, 'bold'), foreground='#d9534f').pack(side='left', padx=4)
                    # Total files available for scanning
                    self.total_files_var = tk.IntVar(value=0)
                    ttk.Label(stat_row, text='| 📦 Total Files:').pack(side='left', padx=8)
                    ttk.Label(stat_row, textvariable=self.total_files_var, font=('Segoe UI', 11, 'bold'), foreground='#1976D2').pack(side='left', padx=4)
                    
                    # Row 3: Current Status and Phase
                    status_row = ttk.Frame(time_frame)
                    status_row.pack(fill='x', pady=2)
                    ttk.Label(status_row, text='📊 Status:', font=('Segoe UI', 10, 'bold')).pack(side='left')
                    ttk.Label(status_row, textvariable=self.scan_status, font=('Segoe UI', 10, 'italic'), foreground='#666666').pack(side='left', padx=4)
                    ttk.Label(status_row, text='| 🔄 Phase:', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=(16, 0))
                    ttk.Label(status_row, textvariable=self.scan_phase, font=('Segoe UI', 10, 'italic'), foreground='#1976D2').pack(side='left', padx=4)
                    
                    # Current file being scanned
                    self.current_file_var = tk.StringVar(value='Ready to scan')
                    current_file_frame = ttk.Frame(status_frame)
                    current_file_frame.pack(fill='x', pady=4)
                    ttk.Label(current_file_frame, text='📄 Current:', font=('Segoe UI', 10, 'bold')).pack(side='left')
                    ttk.Label(current_file_frame, textvariable=self.current_file_var, font=('Segoe UI', 10, 'italic'), foreground='#333333').pack(side='left', padx=4)
                    
                    # Progress bar with percentage
                    self.progress_var = tk.DoubleVar(value=0)
                    self.progress_pct_var = tk.StringVar(value='Scan Progress: 0%')
                    self.progress_pct_label = ttk.Label(status_frame, textvariable=self.progress_pct_var, font=('Segoe UI', 10, 'bold'))
                    self.progress_pct_label.pack(anchor='w', pady=(4, 0))
                    self.progressbar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100, length=420, style='TProgressbar', mode='determinate')
                    self.progressbar.pack(fill='x', pady=8)
                    
                    # Animated icon (placeholder)
                    self.anim_icon = ttk.Label(status_frame, text='🔄', font=('Segoe UI', 18))
                    self.anim_icon.pack(side='right', padx=8)
                    
                    # File-level feedback (Treeview)
                    results_frame = ttk.LabelFrame(center_frame, text='📋 File Scan Details', padding=8)
                    results_frame.pack(fill='both', expand=True, pady=8)
                    columns = ('File', 'Path', 'Size', 'Type', 'Threat', 'Status', 'Time')
                    self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=8)
                    
                    # Configure row height and styling to prevent overlapping
                    style = ttk.Style()
                    style.configure('Treeview', rowheight=28, font=('Segoe UI', 11))
                    
                    col_widths = {
                        'File': 160,
                        'Path': 280,
                        'Size': 80,
                        'Type': 80,
                        'Threat': 100,
                        'Status': 100,
                        'Time': 80
                    }
                    for col in columns:
                        anchor = 'w' if col in ['File', 'Path', 'Threat'] else 'center'
                        self.results_tree.heading(col, text=col, anchor=anchor)
                        self.results_tree.column(col, width=col_widths[col], anchor=anchor, stretch=True)
                    
                    # Add vertical and horizontal scrollbars
                    vsb = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_tree.yview)
                    hsb = ttk.Scrollbar(results_frame, orient='horizontal', command=self.results_tree.xview)
                    self.results_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
                    self.results_tree.pack(side='left', fill='both', expand=True)
                    vsb.pack(side='right', fill='y')
                    hsb.pack(side='bottom', fill='x')
                except Exception as e:
                    logging.exception('Error creating Status Frame:')
                    tk.Label(center_frame, text=f'Status Frame Error: {e}', fg='red').pack(fill='x')
            except Exception as e:
                logging.exception('Error creating Center Frame:')
                tk.Label(main_frame, text=f'Center Frame Error: {e}', fg='red').pack(side='left')

            # --- Bottom: Controls & Post-Scan Summary ---
            controls_frame = ttk.Frame(self)
            controls_frame.pack(fill='x', pady=(0, 8))
            self.start_btn = ttk.Button(controls_frame, text='Start', style='Success.TButton', command=self._on_start_scan)
            self.start_btn.pack(side='left', padx=6)
            self.pause_btn = ttk.Button(controls_frame, text='Pause', style='TButton', command=self._on_pause_scan)
            self.pause_btn.pack(side='left', padx=6)
            self.resume_btn = ttk.Button(controls_frame, text='Resume', style='Accent.TButton', command=self._on_resume_scan)
            self.resume_btn.pack(side='left', padx=6)
            self.stop_btn = ttk.Button(controls_frame, text='Stop', style='Danger.TButton', command=self._on_stop_scan)
            self.stop_btn.pack(side='left', padx=6)
            # Add Refresh button
            self.refresh_btn = ttk.Button(controls_frame, text='Refresh', style='Info.TButton', command=self._on_refresh_scan_panel)
            self.refresh_btn.pack(side='left', padx=6)
            
            # Post-scan summary (hidden until scan completes)
            self.summary_frame = ttk.LabelFrame(self, text='📊 Post-Scan Summary', padding=10)
            # ... add summary widgets here (hidden by default)
            
            # --- Scan Engine Options ---
            options_frame = ttk.LabelFrame(self, text='⚙ Scan Engine Options', padding=10)
            options_frame.pack(fill='x', padx=10, pady=4)
            ttk.Checkbutton(options_frame, text='Scan compressed files (ZIP, RAR, etc.)', variable=self.compressed_enabled).pack(side='left', padx=8)
            ttk.Checkbutton(options_frame, text='Heuristic engine ON', variable=self.heuristic_enabled).pack(side='left', padx=8)
            ttk.Checkbutton(options_frame, text='Cloud-based scan assist', variable=self.cloud_enabled).pack(side='left', padx=8)
            ttk.Label(options_frame, text='CPU usage limit:').pack(side='left', padx=(16,2))
            ttk.Scale(options_frame, from_=10, to=100, variable=self.cpu_limit, orient='horizontal', length=120).pack(side='left')
            ttk.Label(options_frame, textvariable=self.cpu_limit, width=3).pack(side='left')
        except Exception as e:
            logging.exception('Error building ScanPanel UI:')
            tk.Label(self, text=f'ScanPanel UI Error: {e}', fg='red').pack(fill='both', expand=True)

    def _icon_for_type(self, typ):
        return {
            'Quick': '⚡',
            'Full': '🗂',
            'Deep': '🧬',
            'Custom': '🗃',
            'Boot': '💻',
        }.get(typ, '🔍')

    def _on_scan_type_selected(self, typ):
        self.scan_type.set(typ)
        if typ == 'Custom':
            self._show_custom_paths()
        else:
            for w in self.custom_paths_frame.winfo_children():
                w.destroy()

    def _show_custom_paths(self):
        for w in self.custom_paths_frame.winfo_children():
            w.destroy()
        ttk.Label(self.custom_paths_frame, text='Paths to scan:').pack(anchor='w', fill='x')
        for p in self.selected_paths:
            ttk.Label(self.custom_paths_frame, text=p, font=('Segoe UI', 9)).pack(anchor='w', fill='x', padx=2)
        btn_frame = ttk.Frame(self.custom_paths_frame)
        btn_frame.pack(anchor='w', pady=2)
        ttk.Button(btn_frame, text='+ Add Folder', command=self._add_custom_path).pack(side='left', padx=2)
        ttk.Button(btn_frame, text='+ Add File', command=self._add_custom_file).pack(side='left', padx=2)
        ttk.Button(btn_frame, text='- Remove', command=self._remove_custom_path).pack(side='left', padx=2)

    def _add_custom_path(self):
        path = filedialog.askdirectory(title='Select folder to scan')
        if path:
            self.selected_paths.append(path)
            self._show_custom_paths()

    def _add_custom_file(self):
        files = filedialog.askopenfilenames(title='Select file(s) to scan')
        if files:
            self.selected_paths.extend(files)
            self._show_custom_paths()

    def _remove_custom_path(self):
        if self.selected_paths:
            self.selected_paths.pop()
            self._show_custom_paths()

    def _on_start_scan(self):
        # Stub: connect to scan logic
        if self.scan_callbacks.get('start'):
            scan_type = self.scan_type.get()
            if scan_type == 'Quick':
                scan_paths = list(self.quick_scan_files) + list(self.quick_scan_folders)
            elif scan_type == 'Full':
                # For Full Scan, scan the root directory (entire system)
                scan_paths = [os.path.abspath(os.sep)]
            else:
                scan_paths = self.selected_paths
            self.scan_callbacks['start'](scan_type, scan_paths)
        self._show_scan_progress()

    def _on_pause_scan(self):
        if self.scan_callbacks.get('pause'):
            self.scan_callbacks['pause']()

    def _on_resume_scan(self):
        if self.scan_callbacks.get('resume'):
            self.scan_callbacks['resume']()

    def _on_stop_scan(self):
        if self.scan_callbacks.get('stop'):
            self.scan_callbacks['stop']()

    def _show_scan_progress(self):
        # Show/hide widgets as needed for scan progress
        pass

    def show_post_scan_summary(self, summary):
        # Show the summary frame with results
        self.summary_frame.pack(fill='x', padx=10, pady=8)
        # Populate summary widgets (total files, threats, actions, duration, export options)
        # ...

    def _on_scan_type_selected_and_start(self, typ):
        self.scan_type.set(typ)
        self._on_start_scan()

    def _add_quick_file(self):
        files = filedialog.askopenfilenames(title='Select file(s) to add to Quick Scan')
        if files:
            self.quick_scan_files.extend(files)
            self._show_quick_files()

    def _add_quick_folder(self):
        folder = filedialog.askdirectory(title='Select folder to add to Quick Scan')
        if folder:
            self.quick_scan_folders.append(folder)
            self._show_quick_files()

    def _show_quick_files(self):
        for w in self.quick_files_frame.winfo_children():
            w.destroy()
        if self.quick_scan_files or self.quick_scan_folders:
            ttk.Label(self.quick_files_frame, text='Quick Scan will also include:').pack(anchor='w', fill='x')
            for f in self.quick_scan_files:
                ttk.Label(self.quick_files_frame, text=f, font=('Segoe UI', 9, 'italic')).pack(anchor='w', fill='x', padx=2)
            for d in self.quick_scan_folders:
                ttk.Label(self.quick_files_frame, text=f'[Folder] {d}', font=('Segoe UI', 9, 'italic')).pack(anchor='w', fill='x', padx=2)
            ttk.Button(self.quick_files_frame, text='Clear', command=self._clear_quick_files).pack(anchor='w', pady=2)

    def _clear_quick_files(self):
        self.quick_scan_files.clear()
        self.quick_scan_folders.clear()
        self._show_quick_files()

    def start_time_tracking(self):
        """Start the time tracking for the scan"""
        self.scan_start_time = time.time()
        self.files_scanned = 0
        self.scan_speed_history = []
        self._update_time_display()
        
    def stop_time_tracking(self):
        """Stop the time tracking"""
        if self.update_timer:
            self.after_cancel(self.update_timer)
            self.update_timer = None
            
    def _update_time_display(self):
        """Update the time display every second"""
        if self.scan_start_time:
            elapsed = time.time() - self.scan_start_time
            elapsed_str = str(timedelta(seconds=int(elapsed)))
            self.scan_elapsed_time.set(elapsed_str)
            
            # Calculate ETA if we have files scanned
            if self.files_scanned > 0 and self.total_files_estimate > 0:
                avg_speed = self.files_scanned / elapsed if elapsed > 0 else 0
                remaining_files = self.total_files_estimate - self.files_scanned
                eta_seconds = remaining_files / avg_speed if avg_speed > 0 else 0
                eta_str = str(timedelta(seconds=int(eta_seconds))) if eta_seconds > 0 else '--:--:--'
                self.scan_eta.set(eta_str)
            else:
                self.scan_eta.set('--:--:--')
            
            # Update scan speed
            if elapsed > 0:
                current_speed = self.files_scanned / elapsed
                self.scan_speed_history.append(current_speed)
                if len(self.scan_speed_history) > 10:  # Keep last 10 samples
                    self.scan_speed_history.pop(0)
                avg_speed = sum(self.scan_speed_history) / len(self.scan_speed_history)
                self.scan_speed.set(f'{avg_speed:.1f} files/sec')
            else:
                self.scan_speed.set('0 files/sec')
        
        # Schedule next update
        self.update_timer = self.after(1000, self._update_time_display)
        
    def set_progress_mode(self, mode):
        """Switch progress bar between determinate and indeterminate mode."""
        if self._progress_mode == mode:
            return  # No change needed
        self._progress_mode = mode
        self.progressbar.stop()
        if mode == 'indeterminate':
            self.progressbar.config(mode='indeterminate')
            self.progressbar.start(20)
            self.progress_pct_var.set('Scanning...')
            print('[DEBUG] Progress bar set to indeterminate mode')
        else:
            self.progressbar.config(mode='determinate')
            self.progress_pct_var.set('Scan Progress: 0%')
            print('[DEBUG] Progress bar set to determinate mode')

    def update_scan_progress(self, current_file, progress, stats):
        """Update scan progress with enhanced information"""
        def do_update():
            # Decide mode based on total_files_estimate
            mode = 'determinate' if self.total_files_estimate else 'indeterminate'
            self.set_progress_mode(mode)
            if stats:
                files_scanned = stats.get('files_scanned', self.files_scanned)
                threats_found = stats.get('threats_found', 0)
                self.threats_found_var.set(threats_found)
                self.files_scanned_var.set(files_scanned)
                self.files_scanned = files_scanned
            if self._progress_mode == 'determinate' and progress is not None:
                self.progress_var.set(progress)
                self.progress_pct_var.set(f'Scan Progress: {progress:.1f}%')
                print(f'[DEBUG] Progress bar value set to {progress:.1f}%')
            elif self._progress_mode == 'indeterminate':
                self.progress_pct_var.set('Scanning...')
                print('[DEBUG] Progress bar in indeterminate mode (no value set)')
            if current_file:
                filename = os.path.basename(current_file)
                self.current_file_var.set(f'{filename} ({current_file})')
            if progress is not None and self._progress_mode == 'determinate':
                if progress < 10:
                    self.scan_phase.set('Initializing')
                    self.scan_status.set('Preparing scan environment...')
                elif progress < 30:
                    self.scan_phase.set('System Scan')
                    self.scan_status.set('Scanning system files and registry...')
                elif progress < 60:
                    self.scan_phase.set('File Analysis')
                    self.scan_status.set('Analyzing file contents and patterns...')
                elif progress < 90:
                    self.scan_phase.set('Threat Detection')
                    self.scan_status.set('Detecting and analyzing threats...')
                else:
                    self.scan_phase.set('Finalizing')
                    self.scan_status.set('Completing scan and generating report...')
            elif self._progress_mode == 'indeterminate':
                self.scan_phase.set('Scanning')
                self.scan_status.set('Scanning files...')
        self.after(0, do_update)

    def set_scan_complete(self, total_files, total_threats, scan_duration):
        """Set scan completion status"""
        self.scan_phase.set('Complete')
        self.scan_status.set(f'Scan completed in {str(timedelta(seconds=int(scan_duration)))}')
        self.files_scanned_var.set(total_files)
        self.threats_found_var.set(total_threats)
        # Ensure progress bar is full
        self.set_progress_mode('determinate')
        self.progress_var.set(100)
        self.progress_pct_var.set('Scan Progress: 100.0%')
        self.stop_time_tracking()

    def destroy(self):
        self.stop_time_tracking()
        super().destroy()

    def set_total_files(self, total):
        self.total_files_var.set(total)

    def _on_refresh_scan_panel(self):
        """Reset the scan panel UI to its initial state."""
        self.scan_status.set('Ready to scan')
        self.scan_phase.set('Idle')
        self.scan_elapsed_time.set('00:00:00')
        self.scan_eta.set('--:--:--')
        self.scan_speed.set('0 files/sec')
        self.files_scanned_var.set(0)
        self.threats_found_var.set(0)
        self.total_files_var.set(0)
        self.progress_var.set(0)
        self.progress_pct_var.set('Scan Progress: 0%')
        self.current_file_var.set('Ready to scan')
        # Clear results table
        if hasattr(self, 'results_tree'):
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
        # Hide summary frame if visible
        if hasattr(self, 'summary_frame'):
            self.summary_frame.pack_forget()
        # Reset scan type to Quick
        self.scan_type.set('Quick')
        # Reset quick/custom files/folders
        self.quick_scan_files.clear()
        self.quick_scan_folders.clear()
        self.selected_paths.clear()
        self._show_quick_files()
        self._show_custom_paths()



    def _update_resource_usage(self):
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        self.cpu_label.config(text=f'CPU: {cpu:.1f}%')
        self.ram_label.config(text=f'RAM: {ram:.1f}%')
        self.after(1000, self._update_resource_usage)

# Tooltip helper (simple)
class Tooltip:
    def __init__(self, widget, text, delay=400):
        self.widget = widget
        self.text = text
        self.delay = delay  # milliseconds
        self.tip = None
        self.after_id = None
        widget.bind('<Enter>', self.schedule)
        widget.bind('<Leave>', self.hide)

    def schedule(self, event=None):
        self.unschedule()
        self.after_id = self.widget.after(self.delay, lambda: self.show(event))

    def unschedule(self):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None

    def show(self, event=None):
        if self.tip:
            return
        # Prefer event coordinates if available
        if event and hasattr(event, 'x_root') and hasattr(event, 'y_root'):
            x = event.x_root + 10
            y = event.y_root + 10
        else:
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + 20
        self.tip = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f'+{x}+{y}')
        tw.attributes('-topmost', True)
        label = tk.Label(tw, text=self.text, background='#232946', foreground='white', relief='solid', borderwidth=1, font=('Segoe UI', 9, 'normal'))
        label.pack(ipadx=4, ipady=2)

    def hide(self, event=None):
        self.unschedule()
        if self.tip:
            self.tip.destroy()
            self.tip = None 