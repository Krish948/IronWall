"""
IronWall Antivirus - Advanced Features Panel
Comprehensive UI for all advanced security features
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
from datetime import datetime
from typing import Dict, List, Any

class AdvancedFeaturesPanel(ttk.Frame):
    def __init__(self, parent, scanner, system_monitor, threat_db):
        super().__init__(parent)
        self.parent = parent
        self.scanner = scanner
        self.system_monitor = system_monitor
        self.threat_db = threat_db
        
        # Initialize advanced components
        self.ai_engine = None
        self.process_monitor = None
        self.sandbox = None
        self.cloud_intel = None
        self.network_protection = None
        self.ransomware_shield = None
        self.restore_point = None
        
        self._initialize_components()
        self._create_widgets()
        self._start_monitoring()
    
    def _initialize_components(self):
        """Initialize advanced security components"""
        try:
            from core.ai_engine import AIBehavioralEngine
            from core.process_monitor import ProcessMonitor
            from core.sandbox import SandboxExecution
            from core.cloud_intelligence import CloudThreatIntelligence
            from core.network_protection import NetworkProtection
            from core.ransomware_shield import RansomwareShield
            from core.restore_point import RestorePointCreator
            
            self.ai_engine = AIBehavioralEngine()
            self.process_monitor = ProcessMonitor(self.threat_db)
            self.sandbox = SandboxExecution()
            self.cloud_intel = CloudThreatIntelligence()
            self.network_protection = NetworkProtection()
            self.ransomware_shield = RansomwareShield()
            self.restore_point = RestorePointCreator()
            
        except ImportError as e:
            messagebox.showwarning("Advanced Features", f"Some advanced features are not available: {e}")
    
    def _create_widgets(self):
        """Create the UI widgets"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self._create_ai_tab()
        self._create_process_monitor_tab()
        self._create_sandbox_tab()
        self._create_cloud_intel_tab()
        self._create_network_tab()
        self._create_ransomware_tab()
        self._create_restore_point_tab()
    
    def _create_ai_tab(self):
        """Create AI/ML Behavioral Engine tab"""
        ai_frame = ttk.Frame(self.notebook)
        ai_frame.pack(fill='both', expand=True)
        self.notebook.add(ai_frame, text="🤖 AI Engine")
        
        # AI Engine Status
        status_frame = ttk.LabelFrame(ai_frame, text="AI Engine Status", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.ai_status_label = ttk.Label(status_frame, text="Initializing...")
        self.ai_status_label.pack()
        
        # File Analysis
        analysis_frame = ttk.LabelFrame(ai_frame, text="File Analysis", padding=10)
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # File selection
        file_frame = ttk.Frame(analysis_frame)
        file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(file_frame, text="File:").pack(side=tk.LEFT)
        self.ai_file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.ai_file_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Browse", command=self._browse_ai_file).pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Analyze", command=self._analyze_file_ai).pack(side=tk.LEFT, padx=5)
        
        # Analysis results
        self.ai_results_text = tk.Text(analysis_frame, height=15, wrap=tk.WORD)
        ai_scrollbar = ttk.Scrollbar(analysis_frame, orient=tk.VERTICAL, command=self.ai_results_text.yview)
        self.ai_results_text.configure(yscrollcommand=ai_scrollbar.set)
        
        self.ai_results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ai_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_process_monitor_tab(self):
        """Create Process Monitor tab"""
        proc_frame = ttk.Frame(self.notebook)
        proc_frame.pack(fill='both', expand=True)
        self.notebook.add(proc_frame, text="🔄 Process Monitor")
        
        # Control buttons
        control_frame = ttk.Frame(proc_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="Refresh", command=self._refresh_processes).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Show Suspicious", command=self._show_suspicious_processes).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Show All", command=self._show_all_processes).pack(side=tk.LEFT, padx=5)
        
        # Process list
        list_frame = ttk.LabelFrame(proc_frame, text="Running Processes", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for processes
        columns = ('PID', 'Name', 'CPU %', 'Memory %', 'Risk Score', 'Status')
        self.process_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=100)
        
        process_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=process_scrollbar.set)
        
        self.process_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        process_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right-click menu
        self.process_menu = tk.Menu(self, tearoff=0)
        self.process_menu.add_command(label="Kill Process", command=self._kill_selected_process)
        self.process_menu.add_command(label="Block Process", command=self._block_selected_process)
        self.process_menu.add_command(label="View Details", command=self._view_process_details)
        
        self.process_tree.bind("<Button-3>", self._show_process_menu)
    
    def _create_sandbox_tab(self):
        """Create Sandbox Execution tab"""
        sandbox_frame = ttk.Frame(self.notebook)
        sandbox_frame.pack(fill='both', expand=True)
        self.notebook.add(sandbox_frame, text="🧪 Sandbox")
        
        # File selection
        file_frame = ttk.LabelFrame(sandbox_frame, text="Sandbox Analysis", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(file_frame, text="File:").pack(side=tk.LEFT)
        self.sandbox_file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.sandbox_file_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Browse", command=self._browse_sandbox_file).pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Execute", command=self._execute_sandbox).pack(side=tk.LEFT, padx=5)
        
        # Sessions
        sessions_frame = ttk.LabelFrame(sandbox_frame, text="Active Sessions", padding=10)
        sessions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Sessions list
        self.sessions_listbox = tk.Listbox(sessions_frame, height=8)
        sessions_scrollbar = ttk.Scrollbar(sessions_frame, orient=tk.VERTICAL, command=self.sessions_listbox.yview)
        self.sessions_listbox.configure(yscrollcommand=sessions_scrollbar.set)
        
        self.sessions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sessions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Session controls
        session_controls = ttk.Frame(sessions_frame)
        session_controls.pack(fill=tk.X, pady=5)
        
        ttk.Button(session_controls, text="Refresh Sessions", command=self._refresh_sessions).pack(side=tk.LEFT, padx=5)
        ttk.Button(session_controls, text="View Results", command=self._view_sandbox_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(session_controls, text="Cleanup All", command=self._cleanup_sessions).pack(side=tk.LEFT, padx=5)
        
        # Results display
        results_frame = ttk.LabelFrame(sandbox_frame, text="Analysis Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.sandbox_results_text = tk.Text(results_frame, height=10, wrap=tk.WORD)
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.sandbox_results_text.yview)
        self.sandbox_results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.sandbox_results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_cloud_intel_tab(self):
        """Create Cloud Intelligence tab"""
        cloud_frame = ttk.Frame(self.notebook)
        cloud_frame.pack(fill='both', expand=True)
        self.notebook.add(cloud_frame, text="☁️ Cloud Intel")
        
        # File/URL check
        check_frame = ttk.LabelFrame(cloud_frame, text="Threat Intelligence Check", padding=10)
        check_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(check_frame, text="File/URL:").pack(side=tk.LEFT)
        self.cloud_input = tk.StringVar()
        ttk.Entry(check_frame, textvariable=self.cloud_input, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(check_frame, text="Check", command=self._check_cloud_intel).pack(side=tk.LEFT, padx=5)
        
        # Results
        results_frame = ttk.LabelFrame(cloud_frame, text="Intelligence Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.cloud_results_text = tk.Text(results_frame, height=20, wrap=tk.WORD)
        cloud_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.cloud_results_text.yview)
        self.cloud_results_text.configure(yscrollcommand=cloud_scrollbar.set)
        
        self.cloud_results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cloud_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_network_tab(self):
        """Create Network Protection tab"""
        network_frame = ttk.Frame(self.notebook)
        network_frame.pack(fill='both', expand=True)
        self.notebook.add(network_frame, text="🌐 Network")
        
        # Controls
        controls_frame = ttk.LabelFrame(network_frame, text="Network Controls", padding=10)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Block IP
        ip_frame = ttk.Frame(controls_frame)
        ip_frame.pack(fill=tk.X, pady=2)
        ttk.Label(ip_frame, text="Block IP:").pack(side=tk.LEFT)
        self.block_ip_var = tk.StringVar()
        ttk.Entry(ip_frame, textvariable=self.block_ip_var, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(ip_frame, text="Block", command=self._block_ip).pack(side=tk.LEFT, padx=5)
        
        # Block Domain
        domain_frame = ttk.Frame(controls_frame)
        domain_frame.pack(fill=tk.X, pady=2)
        ttk.Label(domain_frame, text="Block Domain:").pack(side=tk.LEFT)
        self.block_domain_var = tk.StringVar()
        ttk.Entry(domain_frame, textvariable=self.block_domain_var, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(domain_frame, text="Block", command=self._block_domain).pack(side=tk.LEFT, padx=5)
        
        # Block Port
        port_frame = ttk.Frame(controls_frame)
        port_frame.pack(fill=tk.X, pady=2)
        ttk.Label(port_frame, text="Block Port:").pack(side=tk.LEFT)
        self.block_port_var = tk.StringVar()
        ttk.Entry(port_frame, textvariable=self.block_port_var, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(port_frame, text="Block", command=self._block_port).pack(side=tk.LEFT, padx=5)
        
        # Statistics
        stats_frame = ttk.LabelFrame(network_frame, text="Network Statistics", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.network_stats_text = tk.Text(stats_frame, height=15, wrap=tk.WORD)
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.network_stats_text.yview)
        self.network_stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        self.network_stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Refresh button
        ttk.Button(network_frame, text="Refresh Stats", command=self._refresh_network_stats).pack(pady=5)
    
    def _create_ransomware_tab(self):
        """Create Ransomware Shield tab"""
        ransom_frame = ttk.Frame(self.notebook)
        ransom_frame.pack(fill='both', expand=True)
        self.notebook.add(ransom_frame, text="🔐 Ransomware Shield")
        
        # Protection status
        status_frame = ttk.LabelFrame(ransom_frame, text="Protection Status", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.ransomware_status_label = ttk.Label(status_frame, text="Initializing...")
        self.ransomware_status_label.pack()
        
        # Controls
        controls_frame = ttk.LabelFrame(ransom_frame, text="Protection Controls", padding=10)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(controls_frame, text="View Statistics", command=self._show_ransomware_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="View Activities", command=self._show_ransomware_activities).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Cleanup Backups", command=self._cleanup_ransomware_backups).pack(side=tk.LEFT, padx=5)
        
        # Protected directories
        dir_frame = ttk.LabelFrame(ransom_frame, text="Protected Directories", padding=10)
        dir_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.protected_dirs_listbox = tk.Listbox(dir_frame, height=8)
        dir_scrollbar = ttk.Scrollbar(dir_frame, orient=tk.VERTICAL, command=self.protected_dirs_listbox.yview)
        self.protected_dirs_listbox.configure(yscrollcommand=dir_scrollbar.set)
        
        self.protected_dirs_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dir_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Directory controls
        dir_controls = ttk.Frame(dir_frame)
        dir_controls.pack(fill=tk.X, pady=5)
        
        ttk.Button(dir_controls, text="Add Directory", command=self._add_protected_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(dir_controls, text="Remove Directory", command=self._remove_protected_directory).pack(side=tk.LEFT, padx=5)
    
    def _create_restore_point_tab(self):
        """Create Restore Point tab"""
        restore_frame = ttk.Frame(self.notebook)
        restore_frame.pack(fill='both', expand=True)
        self.notebook.add(restore_frame, text="🔄 Restore Points")
        
        # Create restore point
        create_frame = ttk.LabelFrame(restore_frame, text="Create Restore Point", padding=10)
        create_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(create_frame, text="Description:").pack(side=tk.LEFT)
        self.restore_description = tk.StringVar()
        ttk.Entry(create_frame, textvariable=self.restore_description, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(create_frame, text="Create", command=self._create_restore_point).pack(side=tk.LEFT, padx=5)
        
        # Restore points list
        list_frame = ttk.LabelFrame(restore_frame, text="Available Restore Points", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for restore points
        columns = ('ID', 'Description', 'Created', 'Type')
        self.restore_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.restore_tree.heading(col, text=col)
            self.restore_tree.column(col, width=150)
        
        restore_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.restore_tree.yview)
        self.restore_tree.configure(yscrollcommand=restore_scrollbar.set)
        
        self.restore_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        restore_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Controls
        controls_frame = ttk.Frame(restore_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Refresh", command=self._refresh_restore_points).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Restore", command=self._restore_system).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Delete", command=self._delete_restore_point).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Statistics", command=self._show_restore_stats).pack(side=tk.LEFT, padx=5)
    
    def _start_monitoring(self):
        """Start background monitoring"""
        def update_loop():
            while True:
                try:
                    self._update_ai_status()
                    self._update_network_stats()
                    self._update_ransomware_status()
                    self._update_restore_points()
                    self.parent.after(5000, lambda: None)  # Update every 5 seconds
                except Exception as e:
                    print(f"Advanced panel update error: {e}")
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
    
    # AI Engine methods
    def _browse_ai_file(self):
        file_path = filedialog.askopenfilename(title="Select file for AI analysis")
        if file_path:
            self.ai_file_path.set(file_path)
    
    def _analyze_file_ai(self):
        if not self.ai_engine:
            messagebox.showerror("Error", "AI Engine not available")
            return
        
        file_path = self.ai_file_path.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a file")
            return
        
        def analyze():
            try:
                result = self.ai_engine.analyze_file(file_path)
                self.ai_results_text.delete(1.0, tk.END)
                self.ai_results_text.insert(tk.END, json.dumps(result, indent=2))
            except Exception as e:
                messagebox.showerror("Error", f"Analysis failed: {e}")
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def _update_ai_status(self):
        if self.ai_engine:
            info = self.ai_engine.get_model_info()
            status = f"AI Engine: {'Loaded' if info['models_loaded'] else 'Not Available'}"
            self.ai_status_label.config(text=status)
    
    # Process Monitor methods
    def _refresh_processes(self):
        if not self.process_monitor:
            return
        
        # Clear existing items
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        # Get processes
        processes = self.process_monitor.get_process_list(50)
        
        for proc in processes:
            self.process_tree.insert('', tk.END, values=(
                proc.get('pid', 'N/A'),
                proc.get('name', 'N/A'),
                f"{proc.get('cpu_percent', 0):.1f}",
                f"{proc.get('memory_percent', 0):.1f}",
                f"{proc.get('risk_score', 0):.2f}",
                proc.get('status', 'N/A')
            ))
    
    def _show_suspicious_processes(self):
        if not self.process_monitor:
            return
        
        # Clear existing items
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        # Get suspicious processes
        suspicious = self.process_monitor.get_suspicious_processes()
        
        for proc in suspicious:
            self.process_tree.insert('', tk.END, values=(
                proc.get('pid', 'N/A'),
                proc.get('name', 'N/A'),
                f"{proc.get('cpu_percent', 0):.1f}",
                f"{proc.get('memory_percent', 0):.1f}",
                f"{proc.get('risk_score', 0):.2f}",
                'Suspicious'
            ))
    
    def _show_all_processes(self):
        self._refresh_processes()
    
    def _show_process_menu(self, event):
        try:
            self.process_tree.selection()
            self.process_menu.post(event.x_root, event.y_root)
        except:
            pass
    
    def _kill_selected_process(self):
        selection = self.process_tree.selection()
        if selection:
            item = self.process_tree.item(selection[0])
            pid = int(item['values'][0])
            
            if messagebox.askyesno("Confirm", f"Kill process {pid}?"):
                if self.process_monitor:
                    success = self.process_monitor.kill_process(pid)
                    if success:
                        self._refresh_processes()
                        messagebox.showinfo("Success", f"Process {pid} killed")
                    else:
                        messagebox.showerror("Error", f"Failed to kill process {pid}")
    
    def _block_selected_process(self):
        selection = self.process_tree.selection()
        if selection:
            item = self.process_tree.item(selection[0])
            pid = int(item['values'][0])
            
            if messagebox.askyesno("Confirm", f"Block process {pid}?"):
                if self.process_monitor:
                    success = self.process_monitor.block_process(pid)
                    if success:
                        self._refresh_processes()
                        messagebox.showinfo("Success", f"Process {pid} blocked")
                    else:
                        messagebox.showerror("Error", f"Failed to block process {pid}")
    
    def _view_process_details(self):
        selection = self.process_tree.selection()
        if selection:
            item = self.process_tree.item(selection[0])
            details = f"PID: {item['values'][0]}\n"
            details += f"Name: {item['values'][1]}\n"
            details += f"CPU: {item['values'][2]}\n"
            details += f"Memory: {item['values'][3]}\n"
            details += f"Risk Score: {item['values'][4]}\n"
            details += f"Status: {item['values'][5]}"
            
            messagebox.showinfo("Process Details", details)
    
    # Sandbox methods
    def _browse_sandbox_file(self):
        file_path = filedialog.askopenfilename(title="Select file for sandbox analysis")
        if file_path:
            self.sandbox_file_path.set(file_path)
    
    def _execute_sandbox(self):
        if not self.sandbox:
            messagebox.showerror("Error", "Sandbox not available")
            return
        
        file_path = self.sandbox_file_path.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a file")
            return
        
        def execute():
            try:
                session_id = self.sandbox.create_sandbox_session(file_path)
                result = self.sandbox.execute_in_sandbox(session_id)
                
                self.sandbox_results_text.delete(1.0, tk.END)
                self.sandbox_results_text.insert(tk.END, json.dumps(result, indent=2))
                
                self._refresh_sessions()
                messagebox.showinfo("Success", f"Sandbox execution completed: {session_id}")
            except Exception as e:
                messagebox.showerror("Error", f"Sandbox execution failed: {e}")
        
        threading.Thread(target=execute, daemon=True).start()
    
    def _refresh_sessions(self):
        if not self.sandbox:
            return
        
        self.sessions_listbox.delete(0, tk.END)
        sessions = self.sandbox.get_all_sessions()
        
        for session in sessions:
            self.sessions_listbox.insert(tk.END, f"{session['session_id']} - {session['status']}")
    
    def _view_sandbox_results(self):
        selection = self.sessions_listbox.curselection()
        if selection:
            session_id = self.sessions_listbox.get(selection[0]).split(' - ')[0]
            session_info = self.sandbox.get_session_info(session_id)
            
            if session_info:
                self.sandbox_results_text.delete(1.0, tk.END)
                self.sandbox_results_text.insert(tk.END, json.dumps(session_info, indent=2))
    
    def _cleanup_sessions(self):
        if self.sandbox:
            self.sandbox.cleanup_all_sessions()
            self._refresh_sessions()
            messagebox.showinfo("Success", "All sandbox sessions cleaned up")
    
    # Cloud Intelligence methods
    def _check_cloud_intel(self):
        if not self.cloud_intel:
            messagebox.showerror("Error", "Cloud Intelligence not available")
            return
        
        input_value = self.cloud_input.get()
        if not input_value:
            messagebox.showerror("Error", "Please enter a file path, hash, or URL")
            return
        
        def check():
            try:
                if input_value.startswith('http'):
                    result = self.cloud_intel.check_url(input_value)
                else:
                    # Assume it's a file path or hash
                    if os.path.exists(input_value):
                        import hashlib
                        with open(input_value, 'rb') as f:
                            file_hash = hashlib.md5(f.read()).hexdigest()
                        result = self.cloud_intel.check_file_hash(file_hash)
                    else:
                        result = self.cloud_intel.check_file_hash(input_value)
                
                self.cloud_results_text.delete(1.0, tk.END)
                self.cloud_results_text.insert(tk.END, json.dumps(result, indent=2))
            except Exception as e:
                messagebox.showerror("Error", f"Cloud check failed: {e}")
        
        threading.Thread(target=check, daemon=True).start()
    
    # Network Protection methods
    def _block_ip(self):
        if not self.network_protection:
            return
        
        ip = self.block_ip_var.get()
        if ip:
            self.network_protection.add_blocked_ip(ip)
            self.block_ip_var.set("")
            self._refresh_network_stats()
            messagebox.showinfo("Success", f"IP {ip} blocked")
    
    def _block_domain(self):
        if not self.network_protection:
            return
        
        domain = self.block_domain_var.get()
        if domain:
            self.network_protection.add_blocked_domain(domain)
            self.block_domain_var.set("")
            self._refresh_network_stats()
            messagebox.showinfo("Success", f"Domain {domain} blocked")
    
    def _block_port(self):
        if not self.network_protection:
            return
        
        try:
            port = int(self.block_port_var.get())
            self.network_protection.add_blocked_port(port)
            self.block_port_var.set("")
            self._refresh_network_stats()
            messagebox.showinfo("Success", f"Port {port} blocked")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid port number")
    
    def _refresh_network_stats(self):
        if not self.network_protection:
            return
        
        stats = self.network_protection.get_network_stats()
        
        self.network_stats_text.delete(1.0, tk.END)
        self.network_stats_text.insert(tk.END, json.dumps(stats, indent=2))
    
    def _update_network_stats(self):
        self._refresh_network_stats()
    
    # Ransomware Shield methods
    def _show_ransomware_stats(self):
        if not self.ransomware_shield:
            return
        
        stats = self.ransomware_shield.get_protection_stats()
        messagebox.showinfo("Ransomware Protection Stats", json.dumps(stats, indent=2))
    
    def _show_ransomware_activities(self):
        if not self.ransomware_shield:
            return
        
        activities = self.ransomware_shield.get_suspicious_activities()
        if activities:
            messagebox.showinfo("Suspicious Activities", json.dumps(activities, indent=2))
        else:
            messagebox.showinfo("Suspicious Activities", "No suspicious activities detected")
    
    def _cleanup_ransomware_backups(self):
        if not self.ransomware_shield:
            return
        
        days = 30  # Default to 30 days
        self.ransomware_shield.cleanup_old_backups(days)
        messagebox.showinfo("Success", f"Cleaned up backups older than {days} days")
    
    def _add_protected_directory(self):
        if not self.ransomware_shield:
            return
        
        directory = filedialog.askdirectory(title="Select directory to protect")
        if directory:
            self.ransomware_shield.add_protected_directory(directory)
            self._refresh_protected_directories()
            messagebox.showinfo("Success", f"Added {directory} to protected directories")
    
    def _remove_protected_directory(self):
        if not self.ransomware_shield:
            return
        
        selection = self.protected_dirs_listbox.curselection()
        if selection:
            directory = self.protected_dirs_listbox.get(selection[0])
            self.ransomware_shield.remove_protected_directory(directory)
            self._refresh_protected_directories()
            messagebox.showinfo("Success", f"Removed {directory} from protected directories")
    
    def _refresh_protected_directories(self):
        if not self.ransomware_shield:
            return
        
        self.protected_dirs_listbox.delete(0, tk.END)
        stats = self.ransomware_shield.get_protection_stats()
        # This would need to be implemented in the ransomware shield
        # For now, just show the stats
        self.protected_dirs_listbox.insert(tk.END, f"Protected files: {stats.get('protected_files', 0)}")
    
    def _update_ransomware_status(self):
        if not self.ransomware_shield:
            return
        
        stats = self.ransomware_shield.get_protection_stats()
        status = f"Monitoring: {'Active' if stats.get('monitoring_active', False) else 'Inactive'}"
        status += f" | Protected Files: {stats.get('protected_files', 0)}"
        self.ransomware_status_label.config(text=status)
    
    # Restore Point methods
    def _create_restore_point(self):
        if not self.restore_point:
            return
        
        description = self.restore_description.get()
        if not description:
            messagebox.showerror("Error", "Please enter a description")
            return
        
        def create():
            try:
                restore_id = self.restore_point.create_restore_point("manual", description)
                if restore_id:
                    self.restore_description.set("")
                    self._refresh_restore_points()
                    messagebox.showinfo("Success", f"Restore point created: {restore_id}")
                else:
                    messagebox.showerror("Error", "Failed to create restore point")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create restore point: {e}")
        
        threading.Thread(target=create, daemon=True).start()
    
    def _refresh_restore_points(self):
        if not self.restore_point:
            return
        
        # Clear existing items
        for item in self.restore_tree.get_children():
            self.restore_tree.delete(item)
        
        # Get restore points
        points = self.restore_point.list_restore_points()
        
        for point in points:
            self.restore_tree.insert('', tk.END, values=(
                point.get('id', 'N/A'),
                point.get('description', 'N/A'),
                point.get('created_at', 'N/A')[:19],  # Truncate timestamp
                point.get('type', 'N/A')
            ))
    
    def _restore_system(self):
        selection = self.restore_tree.selection()
        if selection:
            item = self.restore_tree.item(selection[0])
            restore_id = item['values'][0]
            
            if messagebox.askyesno("Confirm", f"Restore system to point {restore_id}?\nThis will restart your computer."):
                def restore():
                    try:
                        success = self.restore_point.restore_system(restore_id)
                        if success:
                            messagebox.showinfo("Success", "System restore initiated. Computer will restart.")
                        else:
                            messagebox.showerror("Error", "Failed to restore system")
                    except Exception as e:
                        messagebox.showerror("Error", f"Restore failed: {e}")
                
                threading.Thread(target=restore, daemon=True).start()
    
    def _delete_restore_point(self):
        selection = self.restore_tree.selection()
        if selection:
            item = self.restore_tree.item(selection[0])
            restore_id = item['values'][0]
            
            if messagebox.askyesno("Confirm", f"Delete restore point {restore_id}?"):
                success = self.restore_point.delete_restore_point(restore_id)
                if success:
                    self._refresh_restore_points()
                    messagebox.showinfo("Success", f"Restore point {restore_id} deleted")
                else:
                    messagebox.showerror("Error", f"Failed to delete restore point {restore_id}")
    
    def _show_restore_stats(self):
        if not self.restore_point:
            return
        
        stats = self.restore_point.get_restore_point_stats()
        messagebox.showinfo("Restore Point Statistics", json.dumps(stats, indent=2))
    
    def _update_restore_points(self):
        self._refresh_restore_points() 