#!/usr/bin/env python3
"""
Test script to verify table styling and row height configuration
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the current directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_table_styling():
    """Test table styling with proper row height configuration"""
    
    root = tk.Tk()
    root.title("Table Styling Test - IronWall")
    root.geometry("800x600")
    
    # Create main frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Test 1: Basic table with row height configuration
    test1_frame = ttk.LabelFrame(main_frame, text="Test 1: Basic Table with Row Height", padding=10)
    test1_frame.pack(fill='x', pady=(0, 10))
    
    columns = ('Name', 'Type', 'Status', 'Size', 'Path')
    tree1 = ttk.Treeview(test1_frame, columns=columns, show='headings', height=6)
    
    # Configure row height and styling to prevent overlapping
    style = ttk.Style()
    style.configure('Treeview', rowheight=28, font=('Segoe UI', 11))
    
    for col in columns:
        tree1.heading(col, text=col, anchor='center')
        tree1.column(col, width=120, anchor='center', stretch=True)
    
    # Add sample data
    sample_data = [
        ('test1.exe', 'Executable', 'Clean', '1.2 MB', '/path/to/file1'),
        ('document.pdf', 'Document', 'Clean', '2.5 MB', '/path/to/file2'),
        ('malware.txt', 'Text', 'Threat', '0.1 MB', '/path/to/file3'),
        ('image.jpg', 'Image', 'Clean', '3.7 MB', '/path/to/file4'),
        ('script.bat', 'Script', 'Suspicious', '0.5 MB', '/path/to/file5'),
        ('archive.zip', 'Archive', 'Clean', '15.2 MB', '/path/to/file6'),
    ]
    
    for i, data in enumerate(sample_data):
        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        tree1.insert('', 'end', values=data, tags=(tag,))
    
    # Configure alternating row colors
    tree1.tag_configure('evenrow', background='#E9EEF3', foreground='#333333')
    tree1.tag_configure('oddrow', background='#F7F9FB', foreground='#333333')
    
    tree1.pack(fill='x')
    
    # Test 2: Table with scrollbars
    test2_frame = ttk.LabelFrame(main_frame, text="Test 2: Table with Scrollbars", padding=10)
    test2_frame.pack(fill='both', expand=True, pady=(0, 10))
    
    tree2 = ttk.Treeview(test2_frame, columns=columns, show='headings', height=8)
    
    # Configure row height and styling
    style.configure('Treeview', rowheight=28, font=('Segoe UI', 11))
    
    for col in columns:
        tree2.heading(col, text=col, anchor='center')
        tree2.column(col, width=120, anchor='center', stretch=True)
    
    # Add more sample data to test scrolling
    for i in range(20):
        data = (f'file{i}.exe', 'Executable', 'Clean' if i % 3 == 0 else 'Threat', f'{i+1}.{i} MB', f'/path/to/file{i}')
        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        tree2.insert('', 'end', values=data, tags=(tag,))
    
    # Configure alternating row colors
    tree2.tag_configure('evenrow', background='#E9EEF3', foreground='#333333')
    tree2.tag_configure('oddrow', background='#F7F9FB', foreground='#333333')
    
    # Add scrollbars
    vsb = ttk.Scrollbar(test2_frame, orient='vertical', command=tree2.yview)
    hsb = ttk.Scrollbar(test2_frame, orient='horizontal', command=tree2.xview)
    tree2.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    tree2.pack(side='left', fill='both', expand=True)
    vsb.pack(side='right', fill='y')
    hsb.pack(side='bottom', fill='x')
    
    # Status label
    status_label = ttk.Label(main_frame, text="✅ Tables configured with proper row height (28px) to prevent overlapping", 
                            font=('Segoe UI', 10, 'bold'))
    status_label.pack(pady=(10, 0))
    
    root.mainloop()

if __name__ == "__main__":
    test_table_styling() 