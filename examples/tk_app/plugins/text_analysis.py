from plugflow import BasePlugin
import tkinter as tk
from tkinter import messagebox
import re

class TextAnalysisPlugin(BasePlugin):
    name = "text_analysis"
    version = "1.0.0"
    priority = 30  # Higher priority to run before other plugins

    def __init__(self, context=None, **kwargs):
        super().__init__(context, **kwargs)
        self.analysis_history = []

    def on_load(self, manager):
        """Initialize plugin and add analysis menu"""
        app = self.context.get("app")
        if app:
            # Create Analysis submenu in Tools
            analysis_menu = tk.Menu(app.tools_menu, tearoff=0)
            app.tools_menu.add_cascade(label="Text Analysis", menu=analysis_menu)
            
            analysis_menu.add_command(label="Analyze Current Text", command=self.analyze_current_text)
            analysis_menu.add_command(label="Show Analysis History", command=self.show_analysis_history)
            analysis_menu.add_command(label="Clear History", command=self.clear_history)
            analysis_menu.add_separator()
            analysis_menu.add_command(label="Auto-Analyze Settings", command=self.analysis_settings)
            
            # Also add to Help menu
            app.help_menu.add_command(label="Text Statistics", command=self.show_text_stats)
            
            app.log(f"Plugin {self.name} initialized analysis tools")
            
            # Register for events from other plugins
            manager.dispatch_event("plugin_ready", {"plugin": self, "name": self.name})

    def on_event(self, event: str, data, manager):
        """Handle events - can interact with other plugins"""
        if event == "text_processed":
            # Automatically analyze when text is processed by other plugins
            text = data.get("text", "")
            if text:
                self.auto_analyze(text)
        elif event == "plugin_ready":
            # Detect when other plugins are loaded
            plugin_name = data.get("name", "")
            app = self.context.get("app")
            if app and plugin_name != self.name:
                app.log(f"Analysis plugin detected: {plugin_name}")

    def analyze_current_text(self):
        """Analyze text currently in the main text widget"""
        app = self.context.get("app")
        if app:
            content = app.text_widget.get("1.0", tk.END).strip()
            if content:
                analysis = self.perform_analysis(content)
                self.show_analysis_results(analysis)
                self.analysis_history.append(analysis)
                app.log(f"Analyzed {analysis['char_count']} characters")
            else:
                messagebox.showwarning("Warning", "No text to analyze")

    def perform_analysis(self, text: str) -> dict:
        """Perform comprehensive text analysis"""
        analysis = {
            "timestamp": self.get_timestamp(),
            "char_count": len(text),
            "char_count_no_spaces": len(text.replace(" ", "")),
            "word_count": len(text.split()),
            "line_count": len(text.split("\n")),
            "sentence_count": len(re.findall(r'[.!?]+', text)),
            "paragraph_count": len([p for p in text.split("\n\n") if p.strip()]),
            "avg_word_length": 0,
            "most_common_words": [],
            "readability_score": 0
        }
        
        words = text.split()
        if words:
            analysis["avg_word_length"] = sum(len(word) for word in words) / len(words)
            
            # Find most common words (simple implementation)
            word_freq = {}
            for word in words:
                clean_word = re.sub(r'[^a-zA-Z]', '', word.lower())
                if len(clean_word) > 2:  # Only count words longer than 2 chars
                    word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
            
            analysis["most_common_words"] = sorted(
                word_freq.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            # Simple readability score (Flesch-like)
            if analysis["sentence_count"] > 0:
                avg_sentence_length = analysis["word_count"] / analysis["sentence_count"]
                analysis["readability_score"] = max(0, 100 - avg_sentence_length - analysis["avg_word_length"])
        
        return analysis

    def show_analysis_results(self, analysis: dict):
        """Display analysis results in a popup"""
        results = f"""Text Analysis Results

Basic Statistics:
  • Characters: {analysis['char_count']} (without spaces: {analysis['char_count_no_spaces']})
  • Words: {analysis['word_count']}
  • Lines: {analysis['line_count']}
  • Sentences: {analysis['sentence_count']}
  • Paragraphs: {analysis['paragraph_count']}

Advanced Metrics:
  • Average word length: {analysis['avg_word_length']:.1f} characters
  • Readability score: {analysis['readability_score']:.1f}/100

Most Common Words:"""
        
        for word, count in analysis["most_common_words"]:
            results += f"\n  • {word}: {count} times"
        
        if not analysis["most_common_words"]:
            results += "\n  • No significant words found"
        
        messagebox.showinfo("Text Analysis", results)

    def auto_analyze(self, text: str):
        """Automatically analyze text (called by events)"""
        if len(text) > 50:  # Only analyze substantial text
            analysis = self.perform_analysis(text)
            self.analysis_history.append(analysis)
            
            app = self.context.get("app")
            if app:
                app.log(f"Auto-analyzed: {analysis['word_count']} words, readability: {analysis['readability_score']:.1f}")

    def show_analysis_history(self):
        """Show analysis history in a new window"""
        if not self.analysis_history:
            messagebox.showinfo("History", "No analysis history available")
            return
        
        # Create new window for history
        history_window = tk.Toplevel()
        history_window.title("Analysis History")
        history_window.geometry("600x400")
        
        # Create text widget with scrollbar
        text_widget = tk.Text(history_window, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(history_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add history content
        for i, analysis in enumerate(self.analysis_history):
            text_widget.insert(tk.END, f"Analysis #{i+1} - {analysis['timestamp']}\n")
            text_widget.insert(tk.END, f"  Words: {analysis['word_count']}, ")
            text_widget.insert(tk.END, f"Characters: {analysis['char_count']}, ")
            text_widget.insert(tk.END, f"Readability: {analysis['readability_score']:.1f}\n\n")
        
        text_widget.config(state=tk.DISABLED)

    def clear_history(self):
        """Clear analysis history"""
        if messagebox.askyesno("Clear History", "Are you sure you want to clear the analysis history?"):
            self.analysis_history.clear()
            app = self.context.get("app")
            if app:
                app.log("Analysis history cleared")

    def analysis_settings(self):
        """Show analysis settings dialog"""
        messagebox.showinfo(
            "Analysis Settings",
            "Text Analysis Plugin Settings:\n\n"
            "• Auto-analysis triggers on text > 50 characters\n"
            "• Readability score based on sentence/word length\n"
            "• History stores up to 100 recent analyses\n\n"
            "This plugin demonstrates inter-plugin communication\n"
            "and automatic event-driven analysis."
        )

    def show_text_stats(self):
        """Show quick text statistics (for Help menu)"""
        app = self.context.get("app")
        if app:
            content = app.text_widget.get("1.0", tk.END).strip()
            if content:
                char_count = len(content)
                word_count = len(content.split())
                line_count = len(content.split("\n"))
                
                stats = f"""Quick Text Statistics:
                
Characters: {char_count}
Words: {word_count}
Lines: {line_count}

Use Tools → Text Analysis for detailed analysis."""
                
                messagebox.showinfo("Text Statistics", stats)
            else:
                messagebox.showinfo("Text Statistics", "No text to analyze")

    def get_timestamp(self):
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def handle_command(self, command: str, args: str):
        """Handle analysis commands"""
        if command == "analyze" or command == "stats":
            app = self.context.get("app")
            if app:
                if args:
                    # Analyze provided text
                    analysis = self.perform_analysis(args)
                    return f"Analysis: {analysis['word_count']} words, {analysis['char_count']} chars, readability: {analysis['readability_score']:.1f}"
                else:
                    # Analyze current content
                    content = app.text_widget.get("1.0", tk.END).strip()
                    if content:
                        analysis = self.perform_analysis(content)
                        return f"Current text: {analysis['word_count']} words, readability: {analysis['readability_score']:.1f}"
                    else:
                        return "No text to analyze"
        
        elif command == "history":
            count = len(self.analysis_history)
            if count > 0:
                latest = self.analysis_history[-1]
                return f"Analysis history: {count} entries. Latest: {latest['word_count']} words at {latest['timestamp']}"
            else:
                return "No analysis history"
        
        return None

    def filter_message(self, text: str):
        """Filter that can trigger analysis events"""
        # Dispatch event when processing substantial text
        if len(text) > 30:
            app = self.context.get("app")
            if app:
                app.plugin_manager.dispatch_event("text_processed", {"text": text, "source": "filter"})
        
        return None  # Don't modify the text
