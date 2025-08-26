"""
CLI Plugin base class for PlugFlow CLI tools.

This module provides the CLIPlugin base class that extends BasePlugin
with CLI-specific functionality and proper type hints.
"""

from typing import Dict, List, Optional
from abc import abstractmethod
from plugflow import BasePlugin


class CLIPlugin(BasePlugin):
    """
    Base class for CLI plugins with typed methods.
    
    This class extends BasePlugin with CLI-specific functionality,
    providing proper type hints and abstract methods for CLI commands.
    """
    
    @abstractmethod
    def get_cli_commands(self) -> Dict[str, Dict[str, str]]:
        """
        Return dictionary of commands this plugin provides.
        
        Returns:
            Dict mapping command names to their info:
            {
                'command_name': {
                    'description': 'Command description',
                    'usage': 'command_name <args>'
                }
            }
        """
        pass
    
    @abstractmethod
    def execute_cli_command(self, command: str, args: List[str]) -> Optional[bool]:
        """
        Execute a CLI command.
        
        Args:
            command: The command name
            args: List of command arguments
            
        Returns:
            True if command executed successfully
            False if command failed
            None if command not handled by this plugin
        """
        pass
