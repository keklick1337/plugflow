
from plugflow import BasePlugin
import re

# Example bad words list (in real use, this might be loaded from a file)
BAD_WORDS = {"damn", "hell", "crap", "stupid", "dumb"}

class ProfanityFilter(BasePlugin):
    name = "profanity_filter"
    version = "1.0.0"
    description = "Filters and censors inappropriate language in messages"
    priority = 10  # High priority - filter should run before commands
    
    def __init__(self, context=None, **kwargs):
        super().__init__(context, **kwargs)
        self.filtered_count = 0
        
    def get_commands(self):
        """Return list of commands this plugin handles"""
        return ["/filter_stats"]

    def filter_message(self, text: str):
        """Filter profanity from messages"""
        original_text = text
        
        def replace_word(match):
            word = match.group(0)
            return word[0] + "*" * (len(word) - 1)
        
        # Create regex pattern for bad words
        pattern = re.compile(
            r"\b(" + "|".join(map(re.escape, BAD_WORDS)) + r")\b", 
            re.IGNORECASE
        )
        
        # Apply filter
        filtered_text = pattern.sub(replace_word, text)
        
        # Count if we filtered something
        if filtered_text != original_text:
            self.filtered_count += 1
            # Log in debug mode
            context = self.context or {}
            if context.get("debug"):
                print(f"[FILTER] Censored message: {original_text} -> {filtered_text}")
        
        return filtered_text
    
    def handle_command(self, command: str, args: str):
        """Handle filter-related commands"""
        if command == "filter_stats":
            return f"Profanity filter has censored {self.filtered_count} message(s) this session."
        
        return None
    
    def on_load(self, manager):
        """Called when plugin is loaded"""
        context = self.context or {}
        if context.get("debug"):
            print(f"[DEBUG] Profanity filter loaded with {len(BAD_WORDS)} bad words")
    
    def on_unload(self, manager):
        """Called when plugin is unloaded"""
        context = self.context or {}
        if context.get("debug"):
            print(f"[DEBUG] Profanity filter unloaded (filtered {self.filtered_count} messages)")
