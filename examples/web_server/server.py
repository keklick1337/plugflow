#!/usr/bin/env python3
"""
Simple HTTP server with plugin system using PlugFlow.
Demonstrates how to use dynamic plugin loading in a web application.
"""

import http.server
import socketserver
import json
import argparse
import logging
from pathlib import Path
from typing import Optional
from plugflow import PluginManager

PLUGINS_DIR = Path(__file__).parent / "plugins"

class PluginHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    plugin_manager: Optional[PluginManager] = None  # Will be set by the server

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_index_html().encode())
        elif self.path == '/api/plugins':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            if self.plugin_manager:
                plugins = self.plugin_manager.list_plugins()
            else:
                plugins = []
            self.wfile.write(json.dumps({"plugins": plugins}).encode())
        elif self.path.startswith('/api/handle/'):
            endpoint = self.path[12:]  # Remove '/api/handle/'
            self.handle_plugin_endpoint(endpoint, {})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path.startswith('/api/handle/'):
            endpoint = self.path[12:]  # Remove '/api/handle/'
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode())
            except:
                data = {}
            self.handle_plugin_endpoint(endpoint, data)
        else:
            self.send_response(404)
            self.end_headers()

    def handle_plugin_endpoint(self, endpoint, data):
        """Handle plugin endpoints through event system"""
        if self.plugin_manager:
            results = self.plugin_manager.dispatch_event(f"web_request_{endpoint}", {
                "method": self.command,
                "data": data,
                "path": self.path
            })
        else:
            results = []
        
        response = {"results": results}
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def get_index_html(self):
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>PlugFlow Web Server Example</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .plugin { border: 1px solid #ccc; margin: 10px 0; padding: 10px; }
        button { margin: 5px; padding: 5px 10px; }
        input[type="text"] { width: 200px; margin: 5px; }
        .result { background: #f0f0f0; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>PlugFlow Web Server Example</h1>
    <p>This server dynamically loads plugins. Try adding new plugins to the plugins/ folder!</p>
    
    <div>
        <button onclick="loadPlugins()">Refresh Plugins</button>
        <div id="plugins"></div>
    </div>
    
    <div>
        <h3>Test Endpoints:</h3>
        <div>
            <input type="text" id="message" placeholder="Enter message" value="Hello World">
            <button onclick="testEcho()">Test Echo</button>
            <button onclick="testReverse()">Test Reverse</button>
            <button onclick="testUppercase()">Test Uppercase</button>
        </div>
        <div id="results"></div>
    </div>

    <script>
        async function loadPlugins() {
            const response = await fetch('/api/plugins');
            const data = await response.json();
            document.getElementById('plugins').innerHTML = 
                '<h3>Loaded Plugins:</h3><ul>' + 
                data.plugins.map(p => '<li>' + p + '</li>').join('') + 
                '</ul>';
        }
        
        async function testEndpoint(endpoint) {
            const message = document.getElementById('message').value;
            const response = await fetch('/api/handle/' + endpoint, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: message})
            });
            const data = await response.json();
            document.getElementById('results').innerHTML = 
                '<div class="result"><strong>' + endpoint + ':</strong> ' + 
                JSON.stringify(data.results) + '</div>' +
                document.getElementById('results').innerHTML;
        }
        
        function testEcho() { testEndpoint('echo'); }
        function testReverse() { testEndpoint('reverse'); }
        function testUppercase() { testEndpoint('uppercase'); }
        
        // Load plugins on page load
        loadPlugins();
    </script>
</body>
</html>
        '''

class PluginHTTPServer:
    def __init__(self, port=8080):
        self.port = port
        self.plugin_manager = PluginManager(
            plugins_paths=[str(PLUGINS_DIR)],
            context={"server": self},
            hot_reload=True,
            poll_interval=2.0,
        )
        self.plugin_manager.load_all()
        print(f"Loaded plugins: {self.plugin_manager.list_plugins()}")

    def run(self):
        # Set the plugin manager as a class attribute
        PluginHTTPRequestHandler.plugin_manager = self.plugin_manager
        
        with socketserver.TCPServer(("", self.port), PluginHTTPRequestHandler) as httpd:
            print(f"Server running on http://localhost:{self.port}")
            print("Press Ctrl+C to stop")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nShutting down server...")
                self.plugin_manager.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PlugFlow Web Server")
    parser.add_argument("--debug", "-d", action="store_true", 
                       help="Enable debug mode with verbose logging")
    parser.add_argument("--port", "-p", type=int, default=8080,
                       help="Port to run server on (default: 8080)")
    args = parser.parse_args()
    
    # Configure logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(name)s: %(message)s')
        # Enable PlugFlow debug logging explicitly
        logging.getLogger('plugflow').setLevel(logging.DEBUG)
        print("Debug mode enabled - showing all plugin logs")
    else:
        # In production mode, suppress PlugFlow logs completely
        logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
        # PlugFlow will default to WARNING level
    
    server = PluginHTTPServer(port=args.port)
    server.run()
