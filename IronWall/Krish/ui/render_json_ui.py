import tkinter as tk
from tkinter import ttk
import json
import os
import itertools

# Modern, beautiful color palette
GRADIENT_COLORS = [
    ('#232946', '#5f6caf'),
    ('#393e6b', '#232946'),
    ('#232946', '#f6c177'),
    ('#5f6caf', '#eebbc3'),
    ('#232946', '#a3ffe3'),
]
COLORS = {
    'frame_bg': '#2d3142',
    'label_fg': '#e0e1dd',
    'label_bold_fg': '#f6c177',
    'label_danger_fg': '#ff595e',
    'button_palette': ['#eebbc3', '#f6c177', '#a3ffe3', '#ffadad', '#b5ead7', '#c7ceea'],
    'button_fg': '#232946',
    'button_hover_bg': '#f6c177',
    'button_press_bg': '#b5ead7',
    'progress_fg': '#f6c177',
    'table_header_bg': '#393e6b',
    'table_header_fg': '#eebbc3',
    'table_row_bg': '#393e6b',
    'table_row_fg': '#eebbc3',
    'table_row_hover': '#f6c177',
}
FONT = ('Segoe UI', 13, 'normal')
FONT_BOLD = ('Segoe UI', 13, 'bold')
FONT_ITALIC = ('Segoe UI', 12, 'italic')

# Button icons (using emoji for cross-platform support)
BUTTON_ICONS = {
    'Quick Scan': '🔍',
    'Stop': '⏹️',
    '⏸️ Pause': '⏸️',
    '▶️ Resume': '▶️',
    'Deep Scan: OFF': '🧬',
    'Deep Scan: ON': '🧬',
}

# Load the JSON UI description
json_path = os.path.join(os.path.dirname(__file__), 'scan_ui.json')
with open(json_path, 'r', encoding='utf-8') as f:
    ui_json = json.load(f)

# Backend logic example: update label on scan
class Backend:
    def __init__(self):
        self.status_label = None
    def start_quick_scan(self):
        if self.status_label:
            self.status_label.config(text='Scan started!')

backend = Backend()

# Button hover, press animation, and color cycling
class AnimatedButton(ttk.Button):
    color_index = 0
    def __init__(self, master=None, action=None, **kw):
        text = kw.get('text', '')
        icon = BUTTON_ICONS.get(text, '')
        if icon and not text.startswith(icon):
            kw['text'] = f'{icon} {text}'
        super().__init__(master, **kw)
        palette = COLORS['button_palette']
        self.btn_color = palette[AnimatedButton.color_index % len(palette)]
        AnimatedButton.color_index += 1
        self.default_bg = self.btn_color
        self.default_fg = COLORS['button_fg']
        style_name = f'Custom.TButton{AnimatedButton.color_index}'
        hover_style_name = f'Hover.TButton{AnimatedButton.color_index}'
        press_style_name = f'Press.TButton{AnimatedButton.color_index}'
        style = ttk.Style()
        style.configure(style_name, background=self.btn_color, foreground=self.default_fg, font=FONT_BOLD, relief='flat', borderwidth=0)
        style.map(style_name, background=[('active', COLORS['button_hover_bg'])])
        style.configure(hover_style_name, background=COLORS['button_hover_bg'], foreground=self.default_fg, font=FONT_BOLD, relief='flat', borderwidth=0)
        style.configure(press_style_name, background=COLORS['button_press_bg'], foreground=self.default_fg, font=FONT_BOLD, relief='flat', borderwidth=0)
        self['style'] = style_name
        self._style_name = style_name
        self._hover_style_name = hover_style_name
        self._press_style_name = press_style_name
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<ButtonPress-1>', self.on_press)
        self.bind('<ButtonRelease-1>', self.on_release)
        if action:
            self.config(command=action)
    def on_enter(self, e):
        self.configure(style=self._hover_style_name)
    def on_leave(self, e):
        self.configure(style=self._style_name)
    def on_press(self, e):
        self.configure(style=self._press_style_name)
    def on_release(self, e):
        self.configure(style=self._hover_style_name)

# Animated gradient background
def draw_gradient(canvas, width, height, start_color, end_color):
    r1, g1, b1 = canvas.winfo_rgb(start_color)
    r2, g2, b2 = canvas.winfo_rgb(end_color)
    r_ratio = float(r2 - r1) / height
    g_ratio = float(g2 - g1) / height
    b_ratio = float(b2 - b1) / height
    for i in range(height):
        nr = int(r1 + (r_ratio * i)) >> 8
        ng = int(g1 + (g_ratio * i)) >> 8
        nb = int(b1 + (b_ratio * i)) >> 8
        color = f'#{nr:02x}{ng:02x}{nb:02x}'
        canvas.create_line(0, i, width, i, fill=color)

def animate_gradient(canvas, width, height, color_pairs):
    color_cycle = itertools.cycle(color_pairs)
    def next_frame():
        start, end = next(color_cycle)
        draw_gradient(canvas, width, height, start, end)
        canvas.after(1200, next_frame)
    next_frame()

# Table with row hover highlight
class HoverTreeview(ttk.Treeview):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_row = None
        self.bind('<Motion>', self.on_motion)
        self.tag_configure('hover', background=COLORS['table_row_hover'], foreground=COLORS['table_row_fg'])
    def on_motion(self, event):
        row = self.identify_row(event.y)
        if self._last_row and self._last_row != row:
            self.item(self._last_row, tags=())
        if row:
            self.item(row, tags=('hover',))
            self._last_row = row

# Rounded corners and drop shadow for frames (simulated with padding and bg)
def rounded_shadow_frame(parent, **kwargs):
    outer = tk.Frame(parent, bg='#1a1a2e')
    outer.pack(fill='x', padx=18, pady=14, anchor='n')
    inner = tk.LabelFrame(outer, **kwargs)
    inner.pack(fill='x', padx=8, pady=8)
    return inner

def build_ui(parent, node, button_parent=None):
    node_type = node.get('type')
    if node_type == 'Page':
        parent.title(node.get('title', 'IronWall Modern UI'))
        width, height = 950, 650
        parent.geometry(f'{width}x{height}')
        # Draw animated gradient background
        canvas = tk.Canvas(parent, width=width, height=height, highlightthickness=0)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        animate_gradient(canvas, width, height, GRADIENT_COLORS)
        # Place a frame on top for content
        content = tk.Frame(parent, bg='', highlightthickness=0)
        content.place(relx=0, rely=0, relwidth=1, relheight=1)
        for child in node.get('children', []):
            build_ui(content, child)
    elif node_type == 'Frame':
        frame = rounded_shadow_frame(parent, text=node.get('title', ''), bg=COLORS['frame_bg'], fg=COLORS['label_fg'], font=FONT_BOLD, bd=2, relief='ridge')
        for child in node.get('children', []):
            build_ui(frame, child, button_parent=frame)
    elif node_type == 'Label':
        style = node.get('style', '')
        fg = COLORS['label_fg']
        font = FONT
        if style == 'bold':
            font = FONT_BOLD
            fg = COLORS['label_bold_fg']
        elif style == 'italic':
            font = FONT_ITALIC
        if node.get('color') == 'danger':
            fg = COLORS['label_danger_fg']
        label = tk.Label(parent, text=node['text'], font=font, fg=fg, bg=COLORS['frame_bg'])
        label.pack(side='left', padx=7, pady=2)
        # For demo: if this is the "Files Scanned" label, let backend update it
        if node['text'].startswith('Files Scanned:'):
            backend.status_label = label
    elif node_type == 'Button':
        action = None
        if node.get('action') == 'start_folder_scan':
            action = backend.start_quick_scan
        button = AnimatedButton(button_parent or parent, text=node['text'], action=action)
        button.pack(side='right', padx=10, pady=6)
    elif node_type == 'ProgressBar':
        pb = ttk.Progressbar(parent, maximum=node.get('max', 100), value=node.get('value', 0), length=420, mode='indeterminate', style='Custom.Horizontal.TProgressbar')
        pb.pack(fill='x', pady=14, padx=24)
        pb.start(20)  # Animate
    elif node_type == 'Table':
        columns = node.get('columns', [])
        style = ttk.Style()
        style.configure('Custom.Treeview.Heading', background=COLORS['table_header_bg'], foreground=COLORS['table_header_fg'], font=FONT_BOLD)
        style.configure('Custom.Treeview', 
                       background=COLORS['table_row_bg'], 
                       foreground=COLORS['table_row_fg'], 
                       fieldbackground=COLORS['table_row_bg'], 
                       font=FONT,
                       rowheight=28)  # Ensure proper row height to prevent overlapping
        tree = HoverTreeview(parent, columns=columns, show='headings', height=8, style='Custom.Treeview')
        for col in columns:
            tree.heading(col, text=col, anchor='center')
            tree.column(col, width=120 if col != 'Full Path' else 250, anchor='center')
        for row in node.get('rows', []):
            tree.insert('', 'end', values=row)
        tree.pack(fill='both', expand=True, padx=14, pady=8)
        tree.tag_configure('oddrow', background=COLORS['table_row_bg'])
        tree.tag_configure('evenrow', background='#232946')

if __name__ == '__main__':
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Custom.Horizontal.TProgressbar', troughcolor=COLORS['frame_bg'], background=COLORS['progress_fg'])
    build_ui(root, ui_json)
    # Fade-in animation (if supported)
    try:
        root.attributes('-alpha', 0.0)
        def fade_in():
            alpha = root.attributes('-alpha')
            if alpha < 1.0:
                root.attributes('-alpha', min(alpha + 0.05, 1.0))
                root.after(20, fade_in)
        fade_in()
    except Exception:
        pass
    root.mainloop() 