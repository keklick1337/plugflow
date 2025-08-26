
from plugflow import BasePlugin
import tkinter as tk
from tkinter import messagebox

class ReversePlugin(BasePlugin):
    name = "text_reverse"
    version = "1.0.0"
    priority = 50

    def on_load(self, manager):
        """Called when plugin is loaded - can access app context"""
        app = self.context.get("app")
        if app:
            # Add menu item to Tools menu
            app.tools_menu.add_command(
                label="Reverse Current Text", 
                command=self.reverse_current_text
            )
            app.log(f"Plugin {self.name} added menu item")

    def reverse_current_text(self):
        """Reverse text currently in the input field"""
        app = self.context.get("app")
        if app:
            current_text = app.text_var.get()
            if current_text:
                reversed_text = current_text[::-1]
                app.text_var.set(reversed_text)
                app.log(f"Reversed text: '{current_text}' -> '{reversed_text}'")
            else:
                app.log("No text to reverse")

    def handle_command(self, command: str, args: str):
        """Handle /reverse command"""
        if command == "reverse":
            if args:
                return f"Reversed: {args[::-1]}"
            else:
                return "Usage: /reverse <text>"
        return None

    def commands(self):
        """Return command definitions for plugin menu integration"""
        return {
            "Reverse Text": self.reverse_text_command
        }

    def reverse_text_command(self, text: str):
        """Command function that can be called from plugin menu"""
        if text:
            return text[::-1]
        else:
            return "No text provided"
