"""
Simple test to check settings panel display
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

def simple_test():
    """Simple test without settings panel"""
    root = ttk.Window(themename='flatly')
    root.title("Simple Test")
    root.geometry("800x600")
    
    # Add a simple label
    label = ttk.Label(root, text="Testing ttkbootstrap display", font=("Segoe UI", 16))
    label.pack(pady=20)
    
    # Add a button
    btn = ttk.Button(root, text="Test Button", style="success.TButton")
    btn.pack(pady=10)
    
    print("Simple test window created")
    root.mainloop()

if __name__ == "__main__":
    simple_test() 