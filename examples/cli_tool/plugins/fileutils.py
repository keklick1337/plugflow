import os
import json
import shutil
import sys
from pathlib import Path

# Add parent directory to path to import CLIPlugin
sys.path.append(str(Path(__file__).parent.parent))
from cli_plugin import CLIPlugin

class FileUtilsPlugin(CLIPlugin):
    name = "fileutils"
    version = "1.0.0"
    priority = 50

    def get_cli_commands(self):
        return {
            'size': {
                'description': 'Get file or directory size',
                'usage': 'size <path>'
            },
            'tree': {
                'description': 'Show directory tree structure',
                'usage': 'tree [path] [max_depth]'
            },
            'find': {
                'description': 'Find files by pattern',
                'usage': 'find <pattern> [directory]'
            },
            'backup': {
                'description': 'Create backup of file/directory',
                'usage': 'backup <source> [destination]'
            }
        }

    def execute_cli_command(self, command: str, args: list):
        if command == 'size':
            return self._size_command(args)
        elif command == 'tree':
            return self._tree_command(args)
        elif command == 'find':
            return self._find_command(args)
        elif command == 'backup':
            return self._backup_command(args)
        return None

    def _size_command(self, args: list):
        if not args:
            print("Usage: size <path>")
            return False

        path = Path(args[0])
        if not path.exists():
            print(f"Path does not exist: {path}")
            return False

        try:
            if path.is_file():
                size = path.stat().st_size
                print(f"File size: {self._format_size(size)}")
            else:
                size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                file_count = len([f for f in path.rglob('*') if f.is_file()])
                dir_count = len([f for f in path.rglob('*') if f.is_dir()])
                print(f"Directory size: {self._format_size(size)}")
                print(f"Files: {file_count}, Directories: {dir_count}")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def _tree_command(self, args: list):
        path = Path(args[0]) if args else Path('.')
        max_depth = int(args[1]) if len(args) > 1 else 3

        if not path.exists():
            print(f"Path does not exist: {path}")
            return False

        try:
            self._print_tree(path, max_depth=max_depth)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def _find_command(self, args: list):
        if not args:
            print("Usage: find <pattern> [directory]")
            return False

        pattern = args[0]
        directory = Path(args[1]) if len(args) > 1 else Path('.')

        if not directory.exists():
            print(f"Directory does not exist: {directory}")
            return False

        try:
            matches = list(directory.rglob(pattern))
            if matches:
                print(f"Found {len(matches)} matches:")
                for match in matches:
                    print(f"  {match}")
            else:
                print("No matches found")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def _backup_command(self, args: list):
        if not args:
            print("Usage: backup <source> [destination]")
            return False

        source = Path(args[0])
        if not source.exists():
            print(f"Source does not exist: {source}")
            return False

        if len(args) > 1:
            destination = Path(args[1])
        else:
            destination = source.parent / f"{source.name}.backup"

        try:
            if source.is_file():
                shutil.copy2(source, destination)
                print(f"File backed up to: {destination}")
            else:
                shutil.copytree(source, destination)
                print(f"Directory backed up to: {destination}")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def _format_size(self, size_bytes: int) -> str:
        """Format size in human readable format"""
        size = float(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def _print_tree(self, path: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0):
        """Print directory tree structure"""
        if current_depth >= max_depth:
            return

        if current_depth == 0:
            print(str(path))

        items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir() and current_depth < max_depth - 1:
                next_prefix = prefix + ("    " if is_last else "│   ")
                self._print_tree(item, next_prefix, max_depth, current_depth + 1)
