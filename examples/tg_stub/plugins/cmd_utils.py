from plugflow import BasePlugin
import time
import random

class TimePlugin(BasePlugin):
    name = "time"
    version = "1.0.0"
    description = "Provides current time and date information"
    
    def get_commands(self):
        """Return list of commands this plugin handles"""
        return ["/time", "/date"]
    
    def handle_command(self, command: str, args: str):
        if command == "time":
            current_time = time.strftime("%H:%M:%S")
            return f"Current time: {current_time}"
        elif command == "date":
            current_date = time.strftime("%Y-%m-%d (%A)")
            return f"Current date: {current_date}"
        
        return None

class RandomPlugin(BasePlugin):
    name = "random"
    version = "1.0.0"
    description = "Generate random numbers and make random choices"
    
    def get_commands(self):
        """Return list of commands this plugin handles"""
        return ["/random", "/roll", "/flip"]
    
    def handle_command(self, command: str, args: str):
        if command == "random":
            if args:
                try:
                    max_num = int(args)
                    result = random.randint(1, max_num)
                    return f"Random number (1-{max_num}): {result}"
                except ValueError:
                    return "Please provide a valid number: /random 100"
            else:
                result = random.randint(1, 100)
                return f"Random number (1-100): {result}"
        
        elif command == "roll":
            # Dice roll
            result = random.randint(1, 6)
            return f"Dice roll: {result}"
        
        elif command == "flip":
            # Coin flip
            result = random.choice(["Heads", "Tails"])
            return f"Coin flip: {result}"
        
        return None

class StatusPlugin(BasePlugin):
    name = "status"
    version = "1.0.0"
    description = "Shows bot status and system information"
    
    def __init__(self, context=None, **kwargs):
        super().__init__(context, **kwargs)
        self.start_time = time.time()
        self.command_count = 0
    
    def get_commands(self):
        """Return list of commands this plugin handles"""
        return ["/status", "/uptime", "/stats"]
    
    def handle_command(self, command: str, args: str):
        self.command_count += 1
        
        if command == "status":
            uptime = int(time.time() - self.start_time)
            return f"Bot Status: Online | Uptime: {uptime}s | Commands processed: {self.command_count}"
        
        elif command == "uptime":
            uptime = int(time.time() - self.start_time)
            hours = uptime // 3600
            minutes = (uptime % 3600) // 60
            seconds = uptime % 60
            return f"Uptime: {hours}h {minutes}m {seconds}s"
        
        elif command == "stats":
            return f"Session Statistics:\n" \
                   f"  Commands processed: {self.command_count}\n" \
                   f"  Session duration: {int(time.time() - self.start_time)}s"
        
        return None
    
    def on_load(self, manager):
        """Called when plugin is loaded"""
        context = self.context or {}
        if context.get("debug"):
            print(f"[DEBUG] Status plugin loaded at {time.strftime('%H:%M:%S')}")
