
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import argparse
import logging
from plugflow import PluginManager

# Path to local plugins
PLUGINS_DIR = __file__.replace("app.py", "plugins")

def setup_logging(debug_mode: bool) -> None:
    """Setup logging based on debug mode"""
    if debug_mode:
        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        # Enable PlugFlow debug logging explicitly
        logging.getLogger('plugflow').setLevel(logging.DEBUG)
        print("Debug mode enabled - PlugFlow logs will be shown in console")
    else:
        # Set to WARNING level to suppress PlugFlow debug logs
        logging.basicConfig(level=logging.WARNING)

class App:
    def __init__(self, root, debug_mode: bool = False):
        self.root = root
        self.debug_mode = debug_mode
        self.root.title("PlugFlow Tkinter Demo" + (" (Debug)" if debug_mode else ""))
        self.root.geometry("800x600")
        
        # Create main UI elements
        self.setup_ui()
        
        # Initialize plugin manager with app context (hot reload disabled initially)
        context = {
            "app": self,
            "root": self.root,
            "text_widget": self.text_widget,
            "input_widget": self.input_entry,
            "log_widget": self.log_text
        }
        
        self.plugin_manager = PluginManager(
            plugins_paths=[PLUGINS_DIR],
            context=context,
            hot_reload=debug_mode  # Enable hot reload in debug mode
        )
        
        # Load all plugins and let them initialize the UI
        self.plugin_manager.load_all()
        self.log("PlugFlow Tkinter Demo started")
        self.log(f"Loaded plugins: {', '.join(self.plugin_manager.list_plugins())}")
        
        # Let plugins modify the UI after creation
        self.plugin_manager.dispatch_event("ui_initialized", {"app": self})
        
        # Start periodic refresh for hot-reloaded plugins
        self.refresh_ui_periodically()

    def setup_ui(self):
        """Create the main UI structure"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Input section with help button
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        header_frame.columnconfigure(1, weight=1)
        
        ttk.Label(header_frame, text="Text Input:").grid(row=0, column=0, sticky="w")
        
        # Help button in top right corner
        self.help_btn = ttk.Button(header_frame, text="Plugin Help", command=self.show_plugin_help)
        self.help_btn.grid(row=0, column=2, sticky="e")
        
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        input_frame.columnconfigure(0, weight=1)
        
        self.text_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_frame, textvariable=self.text_var, font=("Arial", 12))
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.process_btn = ttk.Button(input_frame, text="Process", command=self.process_text)
        self.process_btn.grid(row=0, column=1)
        
        # Main text area
        ttk.Label(main_frame, text="Main Content:").grid(row=2, column=0, sticky="nw", pady=(5, 0))
        
        self.text_widget = scrolledtext.ScrolledText(
            main_frame, 
            height=15, 
            font=("Consolas", 11),
            wrap=tk.WORD
        )
        self.text_widget.grid(row=2, column=1, sticky="nsew", pady=(5, 5))
        
        # Log area
        ttk.Label(main_frame, text="Activity Log:").grid(row=3, column=0, sticky="nw")
        
        self.log_text = scrolledtext.ScrolledText(
            main_frame, 
            height=5, 
            font=("Arial", 9),
            background="#f8f8f8",
            foreground="#333333",
            insertbackground="#000000"
        )
        self.log_text.grid(row=3, column=1, sticky="ew", pady=(5, 0))
        
        # Create menu bar
        self.setup_menu()
        
        # Bind Enter key to process text
        self.input_entry.bind('<Return>', lambda e: self.process_text())

    def setup_menu(self):
        """Setup the main menu bar"""
        self.menubar = tk.Menu(self.root)
        
        # File menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="Clear Text", command=self.clear_text)
        self.file_menu.add_command(label="Clear Log", command=self.clear_log)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        
        # Plugins menu (will be populated by plugins)
        self.plugins_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Plugins", menu=self.plugins_menu)
        
        # Tools menu (plugins can add items here)
        self.tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=self.tools_menu)
        
        # Help menu
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.help_menu.add_command(label="About", command=self.show_about)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)
        
        self.root.config(menu=self.menubar)

    def log(self, message):
        """Add a message to the log area"""
        self.log_text.insert(tk.END, f"[{self.get_timestamp()}] {message}\n")
        self.log_text.see(tk.END)

    def get_timestamp(self):
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")

    def clear_text(self):
        """Clear the main text area"""
        self.text_widget.delete(1.0, tk.END)
        self.log("Text area cleared")

    def clear_log(self):
        """Clear the log area"""
        self.log_text.delete(1.0, tk.END)

    def show_about(self):
        """Show about dialog"""
        about_text = """PlugFlow Tkinter Demo

This application demonstrates the PlugFlow plugin system with a tkinter GUI.

Features:
• Dynamic plugin loading
• Hot-reload support
• Plugin-driven UI modifications
• Context menu integration

Try adding new plugins to the plugins/ folder!"""
        messagebox.showinfo("About", about_text)

    def process_text(self):
        """Process text through the plugin system"""
        text = self.text_var.get().strip()
        if not text:
            self.log("No text to process")
            return
        
        self.log(f"Processing: '{text}'")
        
        # Process through plugin message handling
        responses = self.plugin_manager.handle_message(text)
        
        if responses:
            for response in responses:
                if response:
                    self.text_widget.insert(tk.END, f"> {text}\n")
                    self.text_widget.insert(tk.END, f"< {response}\n\n")
                    self.log(f"Plugin response: {response}")
            self.text_widget.see(tk.END)
        else:
            # If no plugin handled it, just add to text area
            self.text_widget.insert(tk.END, f"[INPUT] {text}\n")
            self.text_widget.see(tk.END)
            self.log("No plugin responses")
        
        # Clear input
        self.text_var.set("")

    def refresh_menu_from_plugins(self):
        """Refresh plugin menu items"""
        # Clear existing plugin menu items
        self.plugins_menu.delete(0, "end")
        
        # Add plugin status
        plugins = self.plugin_manager.list_plugins()
        if plugins:
            for plugin_name in plugins:
                plugin = self.plugin_manager.get(plugin_name)
                if plugin:
                    status = "Active"
                    self.plugins_menu.add_command(
                        label=f"{plugin_name} ({status})",
                        command=lambda p=plugin_name: self.show_plugin_info(p)
                    )
        else:
            self.plugins_menu.add_command(label="No plugins loaded", state="disabled")
        
        self.plugins_menu.add_separator()
        self.plugins_menu.add_command(label="Reload All Plugins", command=self.reload_plugins)

    def show_plugin_info(self, plugin_name):
        """Show information about a specific plugin"""
        plugin = self.plugin_manager.get(plugin_name)
        if plugin:
            info = f"Plugin: {plugin_name}\n"
            info += f"Version: {getattr(plugin, 'version', 'unknown')}\n"
            info += f"Priority: {getattr(plugin, 'priority', 100)}\n"
            info += f"Type: {type(plugin).__name__}"
            messagebox.showinfo(f"Plugin Info: {plugin_name}", info)

    def reload_plugins(self):
        """Manually reload all plugins"""
        self.log("Reloading plugins...")
        self.plugin_manager.load_all()
        self.refresh_menu_from_plugins()
        self.plugin_manager.dispatch_event("ui_refreshed", {"app": self})
        self.log(f"Reloaded plugins: {', '.join(self.plugin_manager.list_plugins())}")

    def show_plugin_help(self):
        """Show plugin help window with plugin list and details"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Plugin Help")
        help_window.geometry("800x600")
        help_window.resizable(True, True)
        
        # Create main frame
        main_frame = ttk.Frame(help_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create horizontal paned window
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left frame for plugin list
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Installed Plugins:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Plugin listbox
        plugin_listbox = tk.Listbox(left_frame, font=("Arial", 10))
        plugin_listbox.pack(fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Right frame for plugin details
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        ttk.Label(right_frame, text="Plugin Details:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Plugin details text
        details_text = scrolledtext.ScrolledText(
            right_frame, 
            font=("Arial", 10),
            background="#f8f8f8",
            foreground="#333333",
            wrap=tk.WORD
        )
        details_text.pack(fill=tk.BOTH, expand=True)
        
        # Populate plugin list
        plugins = []
        for plugin_name in self.plugin_manager.list_plugins():
            plugin = self.plugin_manager.get(plugin_name)
            if plugin:
                display_name = f"{plugin.name} v{getattr(plugin, 'version', '1.0.0')}"
                plugins.append((display_name, plugin))
                plugin_listbox.insert(tk.END, display_name)
        
        def on_plugin_select(event):
            """Handle plugin selection"""
            selection = plugin_listbox.curselection()
            if selection:
                idx = selection[0]
                if idx < len(plugins):
                    plugin_name, plugin = plugins[idx]
                    show_plugin_details(plugin)
        
        def show_plugin_details(plugin):
            """Show details for selected plugin"""
            details_text.delete(1.0, tk.END)
            
            # Plugin basic info
            details = f"Plugin: {plugin.name}\n"
            details += f"Version: {getattr(plugin, 'version', '1.0.0')}\n"
            details += f"Priority: {getattr(plugin, 'priority', 10)}\n"
            details += f"Author: Vladislav Tislenko (keklick1337)\n\n"
            
            # Plugin description based on name
            descriptions = {
                "text_reverse": "Provides text reversal functionality through the Tools menu. Simply click 'Reverse Current Text' to reverse the content in the main text area.",
                "text_styling": "Advanced text formatting plugin with color picker and symbol insertion. Offers text styling options through the Tools menu including color changes and random symbol insertion.",
                "file_operations": "File operations plugin that adds save and load functionality to the File menu. Allows saving current text to files and loading content from text files.",
                "text_analysis": "Comprehensive text analysis plugin that provides detailed statistics about text content. Includes word count, character analysis, readability scoring, and maintains analysis history.",
                "uppercase": "Simple text transformation plugin that converts text to uppercase format. Available through the Tools menu.",
                "text_uppercase": "Enhanced version of the uppercase plugin with additional text transformation capabilities."
            }
            
            description = descriptions.get(plugin.name, "A PlugFlow plugin that extends the application functionality.")
            details += f"Description:\n{description}\n\n"
            
            # Plugin capabilities
            details += "Capabilities:\n"
            
            if hasattr(plugin, 'handle_command') and callable(plugin.handle_command):
                details += "• Command handling\n"
            
            if hasattr(plugin, 'filter_message') and callable(plugin.filter_message):
                details += "• Message filtering\n"
            
            if hasattr(plugin, 'on_event') and callable(plugin.on_event):
                details += "• Event handling\n"
            
            if hasattr(plugin, 'on_load') and callable(plugin.on_load):
                details += "• UI integration\n"
            
            # Commands supported (if any)
            if plugin.name == "text_reverse":
                details += "\nSupported Commands:\n• /reverse - Reverse text\n"
            elif plugin.name == "text_styling":
                details += "\nSupported Commands:\n• /color <color> - Change text color\n• /symbol - Get random symbol\n"
            elif plugin.name == "text_analysis":
                details += "\nSupported Commands:\n• /analyze - Analyze current text\n• /stats - Quick statistics\n• /history - Show analysis history\n"
            
            details_text.insert(1.0, details)
        
        # Bind selection event
        plugin_listbox.bind('<<ListboxSelect>>', on_plugin_select)
        
        # Show details for first plugin if available
        if plugins:
            plugin_listbox.selection_set(0)
            show_plugin_details(plugins[0][1])
        
        # Close button
        close_btn = ttk.Button(main_frame, text="Close", command=help_window.destroy)
        close_btn.pack(pady=(10, 0))

    def refresh_ui_periodically(self):
        """Periodically refresh UI for hot-reloaded plugins"""
        self.refresh_menu_from_plugins()
        # Check every 2 seconds
        self.root.after(2000, self.refresh_ui_periodically)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PlugFlow Tkinter GUI Example")
    parser.add_argument("--debug", "-d", action="store_true", 
                       help="Enable debug mode with verbose logging and hot reload")
    args = parser.parse_args()
    
    setup_logging(args.debug)
    
    root = tk.Tk()
    app = App(root, debug_mode=args.debug)
    
    try:
        root.mainloop()
    finally:
        # Clean up plugin manager
        app.plugin_manager.stop()
