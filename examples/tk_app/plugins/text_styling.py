from plugflow import BasePlugin
import tkinter as tk
from tkinter import messagebox, colorchooser
import random

class TextStylePlugin(BasePlugin):
    name = "text_styling"
    version = "1.0.0"
    priority = 60

    def __init__(self, context=None, **kwargs):
        super().__init__(context, **kwargs)
        self.current_color = "#000000"
        self.style_tags_created = False

    def on_load(self, manager):
        """Initialize plugin and add UI elements"""
        app = self.context.get("app")
        if app:
            # Create a submenu for styling options
            style_menu = tk.Menu(app.tools_menu, tearoff=0)
            app.tools_menu.add_cascade(label="Text Styling", menu=style_menu)
            
            style_menu.add_command(label="Choose Text Color", command=self.choose_color)
            style_menu.add_command(label="Add Random Symbol", command=self.add_random_emoji)
            style_menu.add_command(label="Make Text Bold", command=self.make_bold)
            style_menu.add_separator()
            style_menu.add_command(label="Clear All Formatting", command=self.clear_formatting)
            
            app.log(f"Plugin {self.name} added styling menu")
            
            # Initialize text widget tags for styling
            self.setup_text_tags()

    def setup_text_tags(self):
        """Setup text tags for styling in the text widget"""
        app = self.context.get("app")
        if app and hasattr(app, 'text_widget') and not self.style_tags_created:
            app.text_widget.tag_config("colored", foreground=self.current_color)
            app.text_widget.tag_config("bold", font=("Consolas", 11, "bold"))
            app.text_widget.tag_config("italic", font=("Consolas", 11, "italic"))
            self.style_tags_created = True

    def choose_color(self):
        """Open color chooser dialog"""
        app = self.context.get("app")
        color = colorchooser.askcolor(title="Choose text color")
        
        if color[1]:  # color[1] is the hex value
            self.current_color = color[1]
            if app:
                app.text_widget.tag_config("colored", foreground=self.current_color)
                app.log(f"Text color changed to {self.current_color}")
                messagebox.showinfo("Color Changed", f"New text color: {self.current_color}")

    def add_random_emoji(self):
        """Add a random symbol to the input field"""
        symbols = ["*", "#", "@", "+", "-", "=", "~", "^", "%", "&"]
        symbol = random.choice(symbols)
        
        app = self.context.get("app")
        if app:
            current_text = app.text_var.get()
            app.text_var.set(current_text + symbol)
            app.log(f"Added symbol: {symbol}")

    def make_bold(self):
        """Apply bold formatting to the last added text"""
        app = self.context.get("app")
        if app:
            # Get current text widget content
            content = app.text_widget.get("1.0", tk.END)
            if content.strip():
                # Apply bold to the last line
                lines = content.split('\n')
                if len(lines) > 1:
                    last_line_start = f"{len(lines)-1}.0"
                    last_line_end = f"{len(lines)-1}.end"
                    app.text_widget.tag_add("bold", last_line_start, last_line_end)
                    app.log("Applied bold formatting to last line")

    def clear_formatting(self):
        """Clear all text formatting"""
        app = self.context.get("app")
        if app:
            app.text_widget.tag_remove("colored", "1.0", tk.END)
            app.text_widget.tag_remove("bold", "1.0", tk.END)
            app.text_widget.tag_remove("italic", "1.0", tk.END)
            app.log("Cleared all text formatting")

    def handle_command(self, command: str, args: str):
        """Handle styling commands"""
        if command == "color":
            if args in ["red", "blue", "green", "black"]:
                color_map = {"red": "#FF0000", "blue": "#0000FF", "green": "#00FF00", "black": "#000000"}
                self.current_color = color_map[args]
                app = self.context.get("app")
                if app:
                    app.text_widget.tag_config("colored", foreground=self.current_color)
                return f"Text color changed to {args}"
            else:
                return "Usage: /color <red|blue|green|black>"
        
        elif command == "symbol":
            symbols = ["*", "#", "@", "+", "-"]
            return f"Random symbol: {random.choice(symbols)}"
        
        return None

    def filter_message(self, text: str):
        """Add styling effects to certain patterns"""
        if text.startswith("*") and text.endswith("*") and len(text) > 2:
            # Bold text indicated by *text*
            return text[1:-1].upper()  # Remove asterisks and make uppercase
        return None
