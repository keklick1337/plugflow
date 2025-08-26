import subprocess
import sys
import json
import re
from pathlib import Path

# Add parent directory to path to import CLIPlugin
sys.path.append(str(Path(__file__).parent.parent))
from cli_plugin import CLIPlugin

class DevToolsPlugin(CLIPlugin):
    name = "devtools"
    version = "1.0.0"
    priority = 50

    def get_cli_commands(self):
        return {
            'gitinfo': {
                'description': 'Show git repository information',
                'usage': 'gitinfo [path]'
            },
            'json-format': {
                'description': 'Format/validate JSON string or file',
                'usage': 'json-format <json_string_or_file>'
            },
            'count-lines': {
                'description': 'Count lines of code in project',
                'usage': 'count-lines [directory] [--ext=.py,.js]'
            },
            'gen-readme': {
                'description': 'Generate basic README.md template',
                'usage': 'gen-readme [project_name]'
            }
        }

    def execute_cli_command(self, command: str, args: list):
        if command == 'gitinfo':
            return self._gitinfo_command(args)
        elif command == 'json-format':
            return self._json_format_command(args)
        elif command == 'count-lines':
            return self._count_lines_command(args)
        elif command == 'gen-readme':
            return self._gen_readme_command(args)
        return None

    def _gitinfo_command(self, args: list):
        path = Path(args[0]) if args else Path('.')
        
        if not (path / '.git').exists():
            print("Not a git repository")
            return False

        try:
            # Get current branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, cwd=path)
            branch = result.stdout.strip() if result.returncode == 0 else "unknown"

            # Get remote URL
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                  capture_output=True, text=True, cwd=path)
            remote = result.stdout.strip() if result.returncode == 0 else "no remote"

            # Get last commit
            result = subprocess.run(['git', 'log', '-1', '--oneline'], 
                                  capture_output=True, text=True, cwd=path)
            last_commit = result.stdout.strip() if result.returncode == 0 else "no commits"

            # Get status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=path)
            status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            print(f"Git Repository Info:")
            print(f"  Branch: {branch}")
            print(f"  Remote: {remote}")
            print(f"  Last commit: {last_commit}")
            print(f"  Status: {'Clean' if not status_lines or status_lines == [''] else f'{len(status_lines)} changes'}")
            
            return True
        except Exception as e:
            print(f"Error getting git info: {e}")
            return False

    def _json_format_command(self, args: list):
        if not args:
            print("Usage: json-format <json_string_or_file>")
            return False

        input_data = ' '.join(args)
        
        try:
            # Try to parse as file first
            if Path(input_data).exists():
                with open(input_data, 'r') as f:
                    data = json.load(f)
                print("JSON file is valid!")
            else:
                # Parse as JSON string
                data = json.loads(input_data)
            
            # Pretty print
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            print("Formatted JSON:")
            print(formatted)
            return True
            
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    def _count_lines_command(self, args: list):
        directory = Path(args[0]) if args else Path('.')
        extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h']
        
        # Parse extension filter
        for arg in args:
            if arg.startswith('--ext='):
                extensions = arg[6:].split(',')
                break

        if not directory.exists():
            print(f"Directory does not exist: {directory}")
            return False

        try:
            file_counts = {}
            total_lines = 0
            total_files = 0

            for ext in extensions:
                files = list(directory.rglob(f'*{ext}'))
                if not files:
                    continue
                    
                ext_lines = 0
                for file in files:
                    try:
                        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = len(f.readlines())
                            ext_lines += lines
                    except:
                        continue
                
                file_counts[ext] = {'files': len(files), 'lines': ext_lines}
                total_lines += ext_lines
                total_files += len(files)

            print("Lines of Code Summary:")
            print(f"{'Extension':<10} {'Files':<8} {'Lines':<10}")
            print("-" * 30)
            
            for ext, data in file_counts.items():
                print(f"{ext:<10} {data['files']:<8} {data['lines']:<10}")
            
            print("-" * 30)
            print(f"{'Total':<10} {total_files:<8} {total_lines:<10}")
            
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def _gen_readme_command(self, args: list):
        project_name = args[0] if args else "My Project"
        
        readme_template = f"""# {project_name}

## Description

A brief description of what this project does and who it's for.

## Installation

```bash
# Installation instructions
pip install {project_name.lower().replace(' ', '-')}
```

## Usage

```python
# Basic usage example
from {project_name.lower().replace(' ', '_')} import main

main()
```

## Features

- Feature 1
- Feature 2
- Feature 3

## Contributing

Contributions are always welcome!

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Project Link: [https://github.com/username/{project_name.lower().replace(' ', '-')}](https://github.com/username/{project_name.lower().replace(' ', '-')})
"""

        try:
            readme_path = Path('README.md')
            if readme_path.exists():
                response = input("README.md already exists. Overwrite? (y/N): ")
                if response.lower() != 'y':
                    print("Cancelled")
                    return True

            with open(readme_path, 'w') as f:
                f.write(readme_template)
            
            print(f"Generated README.md for '{project_name}'")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
