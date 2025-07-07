"""
IronWall Antivirus - Quarantine Management Panel
Professional quarantine interface with full threat management capabilities
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from datetime import datetime

class QuarantinePanel:
    def __init__(self, parent, quarantine_manager):
        self.parent = parent
        self.quarantine_manager = quarantine_manager
        self.selected_item = None
        self.create_panel()
    
    def create_panel(self):
        """Create the main quarantine panel"""
        # Main container
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Top section with storage info and controls
        self._create_top_section()
        
        # Middle section with quarantine list and details
        self._create_middle_section()
        
        # Bottom section with action buttons
        self._create_bottom_section()
        
        # Load initial data
        self._load_quarantine_data()
        self._update_storage_info()
    
    def _create_top_section(self):
        """Create top section with storage info and search"""
        top_frame = ttk.LabelFrame(self.main_frame, text="📦 Quarantine Storage & Controls", padding=10)
        top_frame.pack(fill='x', pady=(0, 10))
        
        # Storage info
        storage_frame = ttk.Frame(top_frame)
        storage_frame.pack(fill='x', pady=(0, 10))
        
        self.storage_info_label = ttk.Label(storage_frame, text="Loading storage info...", font=('Segoe UI', 11))
        self.storage_info_label.pack(side='left')
        
        # Search and refresh controls
        controls_frame = ttk.Frame(top_frame)
        controls_frame.pack(fill='x')
        
        ttk.Label(controls_frame, text="Search:").pack(side='left', padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(controls_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side='left', padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self._on_search)
        
        refresh_btn = ttk.Button(controls_frame, text="🔄 Refresh", command=self._refresh_data)
        refresh_btn.pack(side='left', padx=(0, 10))
        
        select_all_btn = ttk.Button(controls_frame, text="☑️ Select All", command=self._select_all)
        select_all_btn.pack(side='left', padx=(0, 10))
        
        clear_selection_btn = ttk.Button(controls_frame, text="❌ Clear Selection", command=self._clear_selection)
        clear_selection_btn.pack(side='left', padx=(0, 10))
        
        cleanup_btn = ttk.Button(controls_frame, text="🧹 Auto Cleanup", command=self._show_cleanup_settings)
        cleanup_btn.pack(side='left')
    
    def _create_middle_section(self):
        """Create middle section with quarantine list and details"""
        middle_frame = ttk.Frame(self.main_frame)
        middle_frame.pack(fill='both', expand=True, pady=(0, 10))
        middle_frame.columnconfigure(0, weight=2)
        middle_frame.columnconfigure(1, weight=1)
        middle_frame.rowconfigure(0, weight=1)
        
        # Quarantine list
        list_frame = ttk.LabelFrame(middle_frame, text="🧬 Quarantined Files", padding=10)
        list_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        # Create treeview for quarantine list
        columns = ('File Name', 'Threat Type', 'Severity', 'Date Quarantined', 'Status')
        self.quarantine_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure row height and styling to prevent overlapping
        style = ttk.Style()
        style.configure('Treeview', rowheight=28, font=('Segoe UI', 11))
        
        column_widths = {
            'File Name': 220,
            'Threat Type': 160,
            'Severity': 100,
            'Date Quarantined': 180,
            'Status': 120
        }
        for col in columns:
            anchor = 'w' if col in ['File Name', 'Threat Type'] else 'center'
            self.quarantine_tree.heading(col, text=col, anchor=anchor)
            self.quarantine_tree.column(col, width=column_widths[col], anchor=anchor, stretch=True)
        
        # Add scrollbars
        vscroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.quarantine_tree.yview)
        hscroll = ttk.Scrollbar(list_frame, orient='horizontal', command=self.quarantine_tree.xview)
        self.quarantine_tree.configure(yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)
        self.quarantine_tree.pack(side='left', fill='both', expand=True)
        vscroll.pack(side='right', fill='y')
        hscroll.pack(side='bottom', fill='x')
        
        # Bind selection event
        self.quarantine_tree.bind('<<TreeviewSelect>>', self._on_item_select)
        
        # Details panel
        details_frame = ttk.LabelFrame(middle_frame, text="🔍 Threat Details", padding=10)
        details_frame.grid(row=0, column=1, sticky='nsew')
        
        # Create text widget for details
        self.details_text = tk.Text(details_frame, wrap='word', height=20, width=40, state='disabled')
        details_scrollbar = ttk.Scrollbar(details_frame, orient='vertical', command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)
        
        self.details_text.pack(side='left', fill='both', expand=True)
        details_scrollbar.pack(side='right', fill='y')
    
    def _create_bottom_section(self):
        """Create bottom section with action buttons"""
        bottom_frame = ttk.LabelFrame(self.main_frame, text="⚙️ Actions", padding=10)
        bottom_frame.pack(fill='x')
        
        # Action buttons
        self.restore_btn = ttk.Button(bottom_frame, text="🔄 Restore File", command=self._restore_file, state='disabled')
        self.restore_btn.pack(side='left', padx=(0, 10))
        
        self.delete_btn = ttk.Button(bottom_frame, text="🗑️ Delete Permanently", command=self._delete_file, state='disabled')
        self.delete_btn.pack(side='left', padx=(0, 10))
        
        self.submit_btn = ttk.Button(bottom_frame, text="☁️ Submit to Cloud Analysis", command=self._submit_to_cloud, state='disabled')
        self.submit_btn.pack(side='left', padx=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(bottom_frame, text="Ready", font=('Segoe UI', 10))
        self.status_label.pack(side='right')
    
    def _load_quarantine_data(self):
        """Load quarantine data into the treeview"""
        # Clear existing items
        for item in self.quarantine_tree.get_children():
            self.quarantine_tree.delete(item)
        
        try:
            # Get quarantine items
            items = self.quarantine_manager.list_items()
            
            for item in items:
                if item.get('status') == 'Pending':  # Only show pending items
                    values = (
                        item.get('file_name', 'Unknown'),
                        item.get('threat_type', 'Unknown'),
                        item.get('severity', 'Unknown'),
                        item.get('date_quarantined', 'Unknown'),
                        item.get('status', 'Unknown')
                    )
                    
                    # Insert with item ID as tags for reference
                    self.quarantine_tree.insert('', 'end', values=values, tags=(item.get('id'),))
            
            # Update status
            self.status_label.config(text=f"Loaded {len(items)} quarantined items")
            
        except Exception as e:
            self.status_label.config(text=f"Error loading data: {e}")
    
    def _update_storage_info(self):
        """Update storage information display"""
        try:
            storage_info = self.quarantine_manager.get_storage_info()
            
            total_items = storage_info.get('total_items', 0)
            total_size = storage_info.get('total_size', 0)
            available_space = storage_info.get('available_space', 0)
            
            # Format sizes
            total_size_mb = total_size / (1024 * 1024)
            available_space_mb = available_space / (1024 * 1024)
            
            info_text = f"📁 Total Items: {total_items} | 📦 Total Size: {total_size_mb:.1f} MB | 💾 Available: {available_space_mb:.1f} MB"
            self.storage_info_label.config(text=info_text)
            
        except Exception as e:
            self.storage_info_label.config(text=f"Error loading storage info: {e}")
    
    def _on_search(self, event=None):
        """Handle search functionality"""
        search_term = self.search_var.get().strip()
        
        # Clear current items
        for item in self.quarantine_tree.get_children():
            self.quarantine_tree.delete(item)
        
        try:
            # Get filtered items
            items = self.quarantine_manager.list_items(search=search_term if search_term else None)
            
            for item in items:
                if item.get('status') == 'Pending':
                    values = (
                        item.get('file_name', 'Unknown'),
                        item.get('threat_type', 'Unknown'),
                        item.get('severity', 'Unknown'),
                        item.get('date_quarantined', 'Unknown'),
                        item.get('status', 'Unknown')
                    )
                    self.quarantine_tree.insert('', 'end', values=values, tags=(item.get('id'),))
            
            self.status_label.config(text=f"Found {len(items)} items matching '{search_term}'")
            
        except Exception as e:
            self.status_label.config(text=f"Search error: {e}")
    
    def _on_item_select(self, event):
        """Handle item selection in treeview"""
        selection = self.quarantine_tree.selection()
        if selection:
            if len(selection) == 1:
                # Single item selected - show details
                item_id = self.quarantine_tree.item(selection[0], 'tags')[0]
                self.selected_item = self.quarantine_manager.get_item_details(item_id)
                self._show_item_details()
            else:
                # Multiple items selected - show summary
                self.selected_item = None
                self._show_multiple_selection_details(selection)
            self._update_action_buttons(True)
        else:
            self.selected_item = None
            self._clear_details()
            self._update_action_buttons(False)
    
    def _show_item_details(self):
        """Show detailed information about selected item"""
        if not self.selected_item:
            return
        
        # Enable text widget for editing
        self.details_text.config(state='normal')
        self.details_text.delete(1.0, tk.END)
        
        # Format details
        details = f"""🔍 THREAT DETAILS

📄 File Information:
   Name: {self.selected_item.get('file_name', 'Unknown')}
   Original Path: {self.selected_item.get('original_path', 'Unknown')}
   File Size: {self.selected_item.get('file_size', 0)} bytes
   Creation Date: {self.selected_item.get('creation_date', 'Unknown')}

🦠 Threat Information:
   Type: {self.selected_item.get('threat_type', 'Unknown')}
   Severity: {self.selected_item.get('severity', 'Unknown')}
   Risk Level: {self.selected_item.get('risk_level', 'Unknown')}
   Description: {self.selected_item.get('description', 'No description available')}

🔐 Security Details:
   MD5 Hash: {self.selected_item.get('md5', 'Unknown')}
   SHA256 Hash: {self.selected_item.get('sha256', 'Unknown')}
   Threat Signature: {self.selected_item.get('signature', 'Unknown')}

📅 Quarantine Information:
   Date Quarantined: {self.selected_item.get('date_quarantined', 'Unknown')}
   Status: {self.selected_item.get('status', 'Unknown')}
   Origin: {self.selected_item.get('origin', 'Unknown')}
"""
        
        self.details_text.insert(1.0, details)
        self.details_text.config(state='disabled')
    
    def _clear_details(self):
        """Clear the details panel"""
        self.details_text.config(state='normal')
        self.details_text.delete(1.0, tk.END)
        self.details_text.config(state='disabled')
    
    def _update_action_buttons(self, enabled):
        """Update action button states"""
        state = 'normal' if enabled else 'disabled'
        self.restore_btn.config(state=state)
        self.delete_btn.config(state=state)
        self.submit_btn.config(state=state)
    
    def _restore_file(self):
        """Restore selected file(s)"""
        # Get all selected items
        selection = self.quarantine_tree.selection()
        if not selection:
            self.selected_item = None
            self._clear_details()
            self._update_action_buttons(False)
            return
        
        # Get details for all selected items
        selected_items = []
        for item in selection:
            item_id = self.quarantine_tree.item(item, 'tags')[0]
            item_details = self.quarantine_manager.get_item_details(item_id)
            if item_details:
                selected_items.append(item_details)
        
        if not selected_items:
            self._clear_details()
            self._update_action_buttons(False)
            return
        
        # Confirmation dialog
        if len(selected_items) == 1:
            # Single item
            item = selected_items[0]
            result = messagebox.askyesno(
                "Restore File",
                f"Are you sure you want to restore this file?\n\n"
                f"File: {item.get('file_name')}\n"
                f"Threat Type: {item.get('threat_type')}\n\n"
                f"This will move the file back to its original location.",
                icon='warning'
            )
        else:
            # Multiple items
            result = messagebox.askyesno(
                "Restore Files",
                f"Are you sure you want to restore {len(selected_items)} files?\n\n"
                f"This will move all selected files back to their original locations.",
                icon='warning'
            )
        
        if result:
            success_count = 0
            failed_count = 0
            
            for item in selected_items:
                try:
                    success, message = self.quarantine_manager.restore_file(item['id'])
                    if success:
                        success_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    failed_count += 1
            
            # Update status
            if success_count > 0 and failed_count == 0:
                self.status_label.config(text=f"Restored {success_count} file(s) successfully")
            elif success_count > 0 and failed_count > 0:
                self.status_label.config(text=f"Restored {success_count} file(s), {failed_count} failed")
            else:
                self.status_label.config(text=f"Failed to restore {failed_count} file(s)")
            
            # Always refresh and clear selection after action
            self._refresh_data()
            self.selected_item = None
            self._clear_details()
            self._update_action_buttons(False)
    
    def _delete_file(self):
        """Permanently delete selected file(s)"""
        # Get all selected items
        selection = self.quarantine_tree.selection()
        if not selection:
            self.selected_item = None
            self._clear_details()
            self._update_action_buttons(False)
            return
        
        # Get details for all selected items
        selected_items = []
        for item in selection:
            item_id = self.quarantine_tree.item(item, 'tags')[0]
            item_details = self.quarantine_manager.get_item_details(item_id)
            if item_details:
                selected_items.append(item_details)
        
        if not selected_items:
            self._clear_details()
            self._update_action_buttons(False)
            return
        
        # Confirmation dialog
        if len(selected_items) == 1:
            # Single item
            item = selected_items[0]
            result = messagebox.askyesno(
                "Delete File",
                f"Are you sure you want to PERMANENTLY DELETE this file?\n\n"
                f"File: {item.get('file_name')}\n"
                f"Threat Type: {item.get('threat_type')}\n\n"
                f"This action cannot be undone!",
                icon='warning'
            )
        else:
            # Multiple items
            result = messagebox.askyesno(
                "Delete Files",
                f"Are you sure you want to PERMANENTLY DELETE {len(selected_items)} files?\n\n"
                f"This action cannot be undone!",
                icon='warning'
            )
        
        if result:
            success_count = 0
            failed_count = 0
            
            for item in selected_items:
                try:
                    success, message = self.quarantine_manager.delete_quarantined_file(item['id'])
                    if success:
                        success_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    failed_count += 1
            
            # Update status
            if success_count > 0 and failed_count == 0:
                self.status_label.config(text=f"Deleted {success_count} file(s) successfully")
            elif success_count > 0 and failed_count > 0:
                self.status_label.config(text=f"Deleted {success_count} file(s), {failed_count} failed")
            else:
                self.status_label.config(text=f"Failed to delete {failed_count} file(s)")
            
            # Always refresh and clear selection after action
            self._refresh_data()
            self.selected_item = None
            self._clear_details()
            self._update_action_buttons(False)
    
    def _submit_to_cloud(self):
        """Submit file to cloud analysis (future enhancement)"""
        messagebox.showinfo(
            "Cloud Analysis",
            "Cloud analysis feature is planned for future releases.\n\n"
            "This will allow you to submit suspicious files to advanced "
            "cloud-based threat analysis services."
        )
    
    def _show_cleanup_settings(self):
        """Show auto-cleanup settings dialog"""
        # Create settings dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Auto Cleanup Settings")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"400x300+{x}+{y}")
        
        # Settings content
        ttk.Label(dialog, text="🧹 Auto Cleanup Rules", font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        # Auto-delete files older than X days
        days_frame = ttk.Frame(dialog)
        days_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(days_frame, text="Auto-delete files older than:").pack(side='left')
        days_var = tk.StringVar(value="30")
        days_entry = ttk.Entry(days_frame, textvariable=days_var, width=10)
        days_entry.pack(side='left', padx=(5, 5))
        ttk.Label(days_frame, text="days").pack(side='left')
        
        # Max quarantine size
        size_frame = ttk.Frame(dialog)
        size_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(size_frame, text="Maximum quarantine size:").pack(side='left')
        size_var = tk.StringVar(value="1000")
        size_entry = ttk.Entry(size_frame, textvariable=size_var, width=10)
        size_entry.pack(side='left', padx=(5, 5))
        ttk.Label(size_frame, text="MB").pack(side='left')
        
        # Apply button
        def apply_cleanup():
            try:
                max_days = int(days_var.get())
                max_size = int(size_var.get()) * 1024 * 1024  # Convert to bytes
                
                success = self.quarantine_manager.apply_cleanup_rules(max_days=max_days, max_size=max_size)
                if success:
                    messagebox.showinfo("Success", "Cleanup rules applied successfully!")
                    self._refresh_data()
                else:
                    messagebox.showinfo("Info", "No files were cleaned up.")
                
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for days and size.")
        
        ttk.Button(dialog, text="Apply Cleanup Rules", command=apply_cleanup).pack(pady=20)
    
    def _sort_treeview(self, column):
        """Sort treeview by column"""
        # This is a simplified sort - in a real implementation, you'd want more sophisticated sorting
        items = [(self.quarantine_tree.set(item, column), item) for item in self.quarantine_tree.get_children('')]
        items.sort()
        
        for index, (val, item) in enumerate(items):
            self.quarantine_tree.move(item, '', index)
    
    def _refresh_data(self):
        """Refresh all data"""
        self._load_quarantine_data()
        self._update_storage_info()
        self.status_label.config(text="Data refreshed")
    
    def _select_all(self):
        """Select all items in the quarantine tree"""
        # Clear current selection
        self.quarantine_tree.selection_remove(*self.quarantine_tree.get_children())
        
        # Select all items
        for item in self.quarantine_tree.get_children():
            self.quarantine_tree.selection_add(item)
    
    def _clear_selection(self):
        """Clear the selection in the quarantine tree"""
        # Clear current selection
        self.quarantine_tree.selection_remove(*self.quarantine_tree.get_children())
    
    def _show_multiple_selection_details(self, selection):
        """Show details for multiple selected items"""
        # Enable text widget for editing
        self.details_text.config(state='normal')
        self.details_text.delete(1.0, tk.END)
        
        # Get details for all selected items
        selected_items = []
        for item in selection:
            item_id = self.quarantine_tree.item(item, 'tags')[0]
            item_details = self.quarantine_manager.get_item_details(item_id)
            if item_details:
                selected_items.append(item_details)
        
        if not selected_items:
            self.details_text.insert(1.0, "No items selected")
            self.details_text.config(state='disabled')
            return
        
        # Show summary information
        details = f"""🔍 MULTIPLE ITEMS SELECTED

📊 Selection Summary:
   Total Items: {len(selected_items)}
   
📋 Selected Files:"""
        
        # List all selected files
        for i, item in enumerate(selected_items, 1):
            details += f"\n   {i}. {item.get('file_name', 'Unknown')} ({item.get('threat_type', 'Unknown')})"
        
        # Show threat type breakdown
        threat_types = {}
        severities = {}
        for item in selected_items:
            threat_type = item.get('threat_type', 'Unknown')
            severity = item.get('severity', 'Unknown')
            threat_types[threat_type] = threat_types.get(threat_type, 0) + 1
            severities[severity] = severities.get(severity, 0) + 1
        
        details += f"\n\n🦠 Threat Type Breakdown:"
        for threat_type, count in threat_types.items():
            details += f"\n   {threat_type}: {count}"
        
        details += f"\n\n⚠️ Severity Breakdown:"
        for severity, count in severities.items():
            details += f"\n   {severity}: {count}"
        
        details += f"\n\n💡 Actions Available:"
        details += f"\n   • Restore all selected files"
        details += f"\n   • Delete all selected files permanently"
        
        self.details_text.insert(1.0, details)
        self.details_text.config(state='disabled')
    
    def destroy(self):
        """Clean up the panel"""
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy() 