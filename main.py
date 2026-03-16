import tkinter as tk
from tkinter import ttk, simpledialog

class ExcalidrawClone:
    def __init__(self, root):
        self.root = root
        self.root.title("PaPy")
        self.root.geometry("1000x600")

        # State variables
        self.brush_color = "black"
        self.brush_size = 2
        self.tool = "pencil"  # Options: pencil, line, rect, eraser
        self.start_x = None
        self.start_y = None
        self.current_shape = None # To track the shape currently being drawn
        self.selected_item = None
        self.history = []
        
        # Theming
        self.themes = {
            "light": {"bg": "#F0F0F0", "fg": "black", "canvas_bg": "white"},
            "dark": {"bg": "#2E2E2E", "fg": "white", "canvas_bg": "#3C3C3C"}
        }
        self.theme = "light"
        self.style = ttk.Style(self.root)

        self.create_widgets()
        self.setup_bindings()
        self.apply_theme()

    def create_widgets(self):
        # 1. Toolbar Frame
        self.toolbar = ttk.Frame(self.root, padding=5)
        self.toolbar.pack(side=tk.LEFT, fill=tk.Y)

        # Use ttk.Button for a more modern look
        # Tools buttons
        ttk.Button(self.toolbar, text="↖", command=lambda: self.set_tool("select")).pack(pady=2, fill=tk.X)
        ttk.Button(self.toolbar, text="✎", command=lambda: self.set_tool("pencil")).pack(pady=2, fill=tk.X)
        ttk.Button(self.toolbar, text="─", command=lambda: self.set_tool("line")).pack(pady=2, fill=tk.X)
        ttk.Button(self.toolbar, text="□", command=lambda: self.set_tool("rect")).pack(pady=2, fill=tk.X)
        ttk.Button(self.toolbar, text="○", command=lambda: self.set_tool("circle")).pack(pady=2, fill=tk.X)
        
        ttk.Separator(self.toolbar, orient='horizontal').pack(fill='x', pady=10)

        # Color presets
        ttk.Label(self.toolbar, text="Color").pack(pady=(5, 0))
        self.color_frame = ttk.Frame(self.toolbar)
        self.color_frame.pack(pady=2)
        colors = ["black", "red", "green", "blue", "yellow", "white"]
        for color in colors:
            # Using tk.Button to be able to set background color
            tk.Button(self.color_frame, bg=color, width=2, relief="solid", borderwidth=1, command=lambda c=color: self.set_brush_color(c)).pack(side=tk.LEFT, padx=1)

        # Brush size presets
        ttk.Label(self.toolbar, text="Brush Size").pack(pady=(10, 0))
        self.size_frame = ttk.Frame(self.toolbar)
        self.size_frame.pack(pady=2)
        sizes = [("S", 2), ("M", 5), ("L", 10), ("XL", 20)]
        for text, size in sizes:
            ttk.Button(self.size_frame, text=text, width=3, command=lambda s=size: self.set_brush_size(s)).pack(side=tk.LEFT)

        ttk.Separator(self.toolbar, orient='horizontal').pack(fill='x', pady=10)
        
        ttk.Button(self.toolbar, text="🗑", command=self.delete_selected_item).pack(pady=2, fill=tk.X)
        ttk.Button(self.toolbar, text="⌫", command=lambda: self.set_tool("eraser")).pack(pady=2, fill=tk.X)
        ttk.Button(self.toolbar, text="✗", command=self.clear_canvas).pack(pady=2, fill=tk.X)

        ttk.Separator(self.toolbar, orient='horizontal').pack(fill='x', pady=10)
        ttk.Button(self.toolbar, text="🌙", command=self.toggle_theme).pack(pady=2, fill=tk.X)

        # 2. Canvas
        self.canvas = tk.Canvas(self.root, bg="white", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def setup_bindings(self):
        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.root.bind("<Delete>", self.delete_selected_item)
        self.root.bind("<Control-z>", self.undo)

    def set_tool(self, tool_name):
        self.tool = tool_name
        if self.tool == "select":
            self.canvas.config(cursor="arrow")
        else:
            self.canvas.config(cursor="cross")
        print(f"Tool selected: {self.tool}")

    def clear_canvas(self):
        self.canvas.delete("all")

    def on_button_press(self, event):
        # Store starting coordinates
        self.start_x = event.x
        self.start_y = event.y
        self.current_shape = None # Reset current shape ID

        if self.tool == "select":
            # Find item under mouse
            items = self.canvas.find_withtag("current")
            if items:
                self.selected_item = items[0]
            else:
                self.selected_item = None
        
        elif self.tool == "pencil":
            # Start a new continuous line object
            self.current_shape = self.canvas.create_line(self.start_x, self.start_y, self.start_x, self.start_y, 
                                    fill=self.brush_color, width=self.brush_size, 
                                    capstyle=tk.ROUND, smooth=True)

    def set_brush_color(self, color):
        self.brush_color = color
        if self.selected_item:
            try:
                item_type = self.canvas.type(self.selected_item)
                if item_type in ["text", "line"]:
                    self.canvas.itemconfig(self.selected_item, fill=self.brush_color)
                elif item_type in ["rectangle", "oval"]:
                    self.canvas.itemconfig(self.selected_item, outline=self.brush_color)
            except:
                pass

    def set_brush_size(self, size):
        self.brush_size = float(size)
        if self.selected_item:
            try:
                item_type = self.canvas.type(self.selected_item)
                if item_type == "text":
                    font_size = max(int(self.brush_size * 4), 8)
                    self.canvas.itemconfig(self.selected_item, font=("Arial", font_size))
                else:
                    self.canvas.itemconfig(self.selected_item, width=self.brush_size)
            except:
                pass

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.apply_theme()

    def apply_theme(self):
        colors = self.themes[self.theme]
        self.root.config(bg=colors['bg'])
        self.canvas.config(bg=colors['canvas_bg'])

        # Configure frames
        self.toolbar.config(style='TFrame')
        self.color_frame.config(style='TFrame')
        self.size_frame.config(style='TFrame')

        # Configure ttk styles
        self.style.theme_use('default')
        self.style.configure('TFrame', background=colors['bg'])
        self.style.configure('TLabel', background=colors['bg'], foreground=colors['fg'])
        # NOTE: TButton background color might not change on all OSes (e.g., macOS)
        self.style.configure('TButton', foreground=colors['fg'], background=colors['bg'], font=('Arial', 12))
        self.style.map('TButton', background=[('active', colors['bg'])])
        self.style.configure('TSeparator', background=colors['fg'])

    def delete_selected_item(self, event=None):
        if self.selected_item:
            self.canvas.delete(self.selected_item)
            self.selected_item = None
            
    def undo(self, event=None):
        if self.history:
            item_id = self.history.pop()
            # Check if item exists before trying to delete
            if self.canvas.find_withtag(item_id):
                self.canvas.delete(item_id)

    def on_double_click(self, event):
        # Check if we are clicking on an existing text item
        items = self.canvas.find_withtag("current")
        if items and self.canvas.type(items[0]) == "text":
            item_id = items[0]
            # It's a text item, let's edit it
            current_text = self.canvas.itemcget(item_id, 'text')
            new_text = simpledialog.askstring(
                "Edit Text",
                "Update text:",
                initialvalue=current_text,
                parent=self.root
            )
            if new_text is not None:
                self.canvas.itemconfig(item_id, text=new_text)
        else:
            # If not on a text item, create a new one
            self.create_new_text(event)

    def create_new_text(self, event):
        text = simpledialog.askstring("Input", "Enter text:", parent=self.root)
        if text:
            font_size = max(int(self.brush_size * 4), 8) # Make font size relative to brush size, with a minimum
            item = self.canvas.create_text(event.x, event.y, text=text,
                                    fill=self.brush_color,
                                    font=("Arial", font_size))
            self.history.append(item)

    def on_mouse_drag(self, event):
        if self.start_x is None or self.start_y is None:
            return

        if self.tool == "select":
            if self.selected_item:
                dx = event.x - self.start_x
                dy = event.y - self.start_y
                self.canvas.move(self.selected_item, dx, dy)
                self.start_x = event.x
                self.start_y = event.y

        elif self.tool == "pencil":
            # Extend the existing line instead of creating new segments
            coords = self.canvas.coords(self.current_shape)
            coords.extend([event.x, event.y])
            self.canvas.coords(self.current_shape, *coords)
        
        elif self.tool == "eraser":
            # Eraser is just a thick white line
            item = self.canvas.create_line(self.start_x, self.start_y, event.x, event.y, 
                                    fill="white", width=20, capstyle=tk.ROUND)
            self.history.append(item)
            self.start_x = event.x
            self.start_y = event.y

        elif self.tool in ["rect", "line", "circle"]:
            # For shapes, we delete the temporary shape from the previous drag frame
            if self.current_shape:
                self.canvas.delete(self.current_shape)
            
            if self.tool == "rect":
                self.current_shape = self.canvas.create_rectangle(
                    self.start_x, self.start_y, event.x, event.y, outline=self.brush_color, width=self.brush_size)
            elif self.tool == "line":
                self.current_shape = self.canvas.create_line(
                    self.start_x, self.start_y, event.x, event.y, fill=self.brush_color, width=self.brush_size)
            elif self.tool == "circle":
                self.current_shape = self.canvas.create_oval(
                    self.start_x, self.start_y, event.x, event.y, outline=self.brush_color, width=self.brush_size)

    def on_button_release(self, event):
        # Finalize the drawing
        if self.current_shape:
            self.history.append(self.current_shape)
        self.start_x = None
        self.start_y = None
        self.current_shape = None

if __name__ == "__main__":
    root = tk.Tk()
    app = ExcalidrawClone(root)
    root.mainloop()
