
from plugflow import BasePlugin
import tkinter as tk
from tkinter import messagebox, simpledialog

class UppercasePlugin(BasePlugin):
    name = "text_uppercase"
    version = "1.1.0"
    priority = 40

    def __init__(self, context=None, **kwargs):
        super().__init__(context, **kwargs)
        self.auto_uppercase = False  # Plugin setting

    def on_load(self, manager):
        """Initialize plugin and add UI elements"""
        app = self.context.get("app")
        if app:
            # Add multiple menu items to Tools menu
            app.tools_menu.add_command(
                label="Uppercase Current Text", 
                command=self.uppercase_current_text
            )
            app.tools_menu.add_command(
                label="Toggle Auto-Uppercase", 
                command=self.toggle_auto_uppercase
            )
            app.tools_menu.add_separator()
            
            # Add to File menu as well
            app.file_menu.add_command(
                label="Batch Process Text...", 
                command=self.batch_process_dialog
            )
            
            app.log(f"Plugin {self.name} initialized with UI elements")

    def on_event(self, event: str, data, manager):
        """Handle application events"""
        if event == "ui_refreshed":
            app = data.get("app")
            if app:
                app.log(f"Plugin {self.name} noticed UI refresh")

    def uppercase_current_text(self):
        """Convert current input text to uppercase"""
        app = self.context.get("app")
        if app:
            current_text = app.text_var.get()
            if current_text:
                uppercase_text = current_text.upper()
                app.text_var.set(uppercase_text)
                app.log(f"Uppercased: '{current_text}' -> '{uppercase_text}'")
            else:
                messagebox.showwarning("Warning", "No text to convert")

    def toggle_auto_uppercase(self):
        """Toggle automatic uppercase filtering"""
        app = self.context.get("app")
        self.auto_uppercase = not self.auto_uppercase
        status = "enabled" if self.auto_uppercase else "disabled"
        
        if app:
            app.log(f"Auto-uppercase {status}")
        
        messagebox.showinfo(
            "Auto-Uppercase", 
            f"Auto-uppercase is now {status}\n\n"
            f"When enabled, text starting with '!' will be automatically converted to uppercase."
        )

    def batch_process_dialog(self):
        """Show dialog for batch text processing"""
        app = self.context.get("app")
        
        text = simpledialog.askstring(
            "Batch Process", 
            "Enter text to process (will be converted to uppercase):"
        )
        
        if text:
            processed = text.upper()
            if app:
                app.text_widget.insert(tk.END, f"[BATCH] Input: {text}\n")
                app.text_widget.insert(tk.END, f"[BATCH] Output: {processed}\n\n")
                app.text_widget.see(tk.END)
                app.log(f"Batch processed: {len(text)} characters")

    def filter_message(self, text: str):
        """Filter messages - auto uppercase if enabled and starts with !"""
        if self.auto_uppercase and text.startswith("!"):
            app = self.context.get("app")
            processed = text[1:].upper()  # Remove ! and uppercase
            if app:
                app.log(f"Auto-uppercase filter: '{text}' -> '{processed}'")
            return processed
        return None  # No filtering

    def handle_command(self, command: str, args: str):
        """Handle /upper command"""
        if command in ["upper", "uppercase"]:
            if args:
                return f"Uppercase: {args.upper()}"
            else:
                return "Usage: /upper <text>"
        return None

    def commands(self):
        """Commands for the old plugin menu system"""
        return {
            "Uppercase Text": self.uppercase_command
        }

    def uppercase_command(self, text: str):
        """Legacy command interface"""
        return text.upper() if text else "No text provided"

class Uppercase(BasePlugin):
    name = "uppercase"

    def commands(self):
        return {"Uppercase current text": self.up}

    def up(self, text: str):
        return text.upper()

    def filter_message(self, text: str):
        # Automatically uppercase text if it starts with !
        if text.startswith("!"):
            return text[1:].upper()
        return None
