import hashlib
import base64
import binascii
import sys
from pathlib import Path

# Add parent directory to path to import CLIPlugin
sys.path.append(str(Path(__file__).parent.parent))
from cli_plugin import CLIPlugin

class CryptoPlugin(CLIPlugin):
    name = "crypto"
    version = "1.0.0"
    priority = 50

    def get_cli_commands(self):
        return {
            'hash': {
                'description': 'Generate hash of input text',
                'usage': 'hash <algorithm> <text> [--no-newline]'
            },
            'encode': {
                'description': 'Encode text to base64',
                'usage': 'encode <text>'
            },
            'decode': {
                'description': 'Decode base64 text',
                'usage': 'decode <base64_text>'
            }
        }

    def execute_cli_command(self, command: str, args: list):
        if command == 'hash':
            return self._hash_command(args)
        elif command == 'encode':
            return self._encode_command(args)
        elif command == 'decode':
            return self._decode_command(args)
        return None

    def _hash_command(self, args: list):
        if len(args) < 2:
            print("Usage: hash <algorithm> <text> [--no-newline]")
            print("Supported algorithms: md5, sha1, sha256, sha512")
            print("Note: By default, adds newline like 'echo' command")
            print("Use --no-newline to hash text without newline")
            return False

        algorithm = args[0].lower()
        
        # Check for --no-newline flag
        no_newline = False
        text_args = args[1:]
        if '--no-newline' in text_args:
            no_newline = True
            text_args.remove('--no-newline')
        
        text = ' '.join(text_args)
        
        # Add newline by default to match 'echo "text" | md5sum' behavior
        if not no_newline:
            text += '\n'

        try:
            if algorithm == 'md5':
                result = hashlib.md5(text.encode()).hexdigest()
            elif algorithm == 'sha1':
                result = hashlib.sha1(text.encode()).hexdigest()
            elif algorithm == 'sha256':
                result = hashlib.sha256(text.encode()).hexdigest()
            elif algorithm == 'sha512':
                result = hashlib.sha512(text.encode()).hexdigest()
            else:
                print(f"Unsupported algorithm: {algorithm}")
                return False

            print(f"{algorithm.upper()}: {result}")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def _encode_command(self, args: list):
        if not args:
            print("Usage: encode <text>")
            return False

        text = ' '.join(args)
        try:
            encoded = base64.b64encode(text.encode()).decode()
            print(f"Base64: {encoded}")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def _decode_command(self, args: list):
        if not args:
            print("Usage: decode <base64_text>")
            return False

        encoded_text = ' '.join(args)
        try:
            decoded = base64.b64decode(encoded_text).decode()
            print(f"Decoded: {decoded}")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
