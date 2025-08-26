from plugflow import BasePlugin
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os

class FileOperationsPlugin(BasePlugin):
    name = "file_operations"
    version = "1.0.0"
    priority = 70

    def on_load(self, manager):
        """Initialize plugin and add file operations menu"""
        app = self.context.get("app")
        if app:
            # Create File Operations submenu
            file_ops_menu = tk.Menu(app.file_menu, tearoff=0)
            app.file_menu.add_cascade(label="File Operations", menu=file_ops_menu)
            
            file_ops_menu.add_command(label="Save Text to File", command=self.save_text_to_file)
            file_ops_menu.add_command(label="Load Text from File", command=self.load_text_from_file)
            file_ops_menu.add_separator()
            file_ops_menu.add_command(label="Export Log", command=self.export_log)
            file_ops_menu.add_command(label="Save App State", command=self.save_app_state)
            file_ops_menu.add_command(label="Load App State", command=self.load_app_state)
            
            app.log(f"Plugin {self.name} added file operations menu")

    def save_text_to_file(self):
        """Save current text widget content to a file"""
        app = self.context.get("app")
        if app:
            content = app.text_widget.get("1.0", tk.END).strip()
            if not content:
                messagebox.showwarning("Warning", "No content to save")
                return
            
            filename = filedialog.asksaveasfilename(
                title="Save Text",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    app.log(f"Text saved to {filename}")
                    messagebox.showinfo("Success", f"Text saved to {os.path.basename(filename)}")
                except Exception as e:
                    app.log(f"Error saving file: {e}")
                    messagebox.showerror("Error", f"Failed to save file: {e}")

    def load_text_from_file(self):
        """Load text from a file into the text widget"""
        app = self.context.get("app")
        if app:
            filename = filedialog.askopenfilename(
                title="Load Text",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Ask if user wants to append or replace
                    result = messagebox.askyesnocancel(
                        "Load Text",
                        f"Loaded {len(content)} characters from {os.path.basename(filename)}\n\n"
                        "Yes: Append to current text\n"
                        "No: Replace current text\n"
                        "Cancel: Don't load"
                    )
                    
                    if result is True:  # Append
                        app.text_widget.insert(tk.END, "\n--- Loaded from file ---\n")
                        app.text_widget.insert(tk.END, content)
                    elif result is False:  # Replace
                        app.text_widget.delete("1.0", tk.END)
                        app.text_widget.insert("1.0", content)
                    
                    if result is not None:
                        app.text_widget.see(tk.END)
                        app.log(f"Text loaded from {filename}")
                        
                except Exception as e:
                    app.log(f"Error loading file: {e}")
                    messagebox.showerror("Error", f"Failed to load file: {e}")

    def export_log(self):
        """Export the activity log to a file"""
        app = self.context.get("app")
        if app:
            log_content = app.log_text.get("1.0", tk.END).strip()
            if not log_content:
                messagebox.showwarning("Warning", "No log content to export")
                return
            
            filename = filedialog.asksaveasfilename(
                title="Export Log",
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(log_content)
                    app.log(f"Log exported to {filename}")
                    messagebox.showinfo("Success", f"Log exported to {os.path.basename(filename)}")
                except Exception as e:
                    app.log(f"Error exporting log: {e}")
                    messagebox.showerror("Error", f"Failed to export log: {e}")

    def save_app_state(self):
        """Save current application state to JSON"""
        app = self.context.get("app")
        if app:
            state = {
                "input_text": app.text_var.get(),
                "main_text": app.text_widget.get("1.0", tk.END),
                "plugins": app.plugin_manager.list_plugins(),
                "window_geometry": app.root.geometry()
            }
            
            filename = filedialog.asksaveasfilename(
                title="Save App State",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(state, f, indent=2, ensure_ascii=False)
                    app.log(f"App state saved to {filename}")
                    messagebox.showinfo("Success", f"App state saved to {os.path.basename(filename)}")
                except Exception as e:
                    app.log(f"Error saving app state: {e}")
                    messagebox.showerror("Error", f"Failed to save app state: {e}")

    def load_app_state(self):
        """Load application state from JSON"""
        app = self.context.get("app")
        if app:
            filename = filedialog.askopenfilename(
                title="Load App State",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                    
                    # Restore state
                    if "input_text" in state:
                        app.text_var.set(state["input_text"])
                    
                    if "main_text" in state:
                        app.text_widget.delete("1.0", tk.END)
                        app.text_widget.insert("1.0", state["main_text"])
                    
                    if "window_geometry" in state:
                        app.root.geometry(state["window_geometry"])
                    
                    app.log(f"App state loaded from {filename}")
                    messagebox.showinfo("Success", f"App state loaded from {os.path.basename(filename)}")
                    
                except Exception as e:
                    app.log(f"Error loading app state: {e}")
                    messagebox.showerror("Error", f"Failed to load app state: {e}")

    def handle_command(self, command: str, args: str):
        """Handle file operation commands"""
        if command == "save":
            if args:
                app = self.context.get("app")
                if app:
                    try:
                        content = app.text_widget.get("1.0", tk.END).strip()
                        with open(args, 'w', encoding='utf-8') as f:
                            f.write(content)
                        return f"Text saved to {args}"
                    except Exception as e:
                        return f"Error saving file: {e}"
            return "Usage: /save <filename>"
        
        elif command == "load":
            if args:
                app = self.context.get("app")
                if app:
                    try:
                        with open(args, 'r', encoding='utf-8') as f:
                            content = f.read()
                        app.text_widget.insert(tk.END, f"\n--- Loaded from {args} ---\n")
                        app.text_widget.insert(tk.END, content)
                        return f"Text loaded from {args}"
                    except Exception as e:
                        return f"Error loading file: {e}"
            return "Usage: /load <filename>"
        
        return None
