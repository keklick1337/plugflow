
from plugflow import BasePlugin

class Echo(BasePlugin):
    name = "echo"
    version = "1.0.0"
    description = "Echoes back the text you send"
    
    def get_commands(self):
        """Return list of commands this plugin handles"""
        return ["/echo"]

    def handle_command(self, command: str, args: str):
        if command == "echo":
            if args:
                return f"Echo: {args}"
            else:
                return "Echo: (nothing to echo - try '/echo hello world')"

class Ping(BasePlugin):
    name = "ping"
    version = "1.0.0" 
    description = "Simple ping-pong response for testing bot connectivity"
    
    def get_commands(self):
        """Return list of commands this plugin handles"""
        return ["/ping"]
    
    def handle_command(self, command: str, args: str):
        if command == "ping":
            return "Pong! Bot is working correctly."
