from flask import Flask
from plugflow import PluginManager

from pathlib import Path

PLUGINS_DIR = Path(__file__).parent / "plugins"

if __name__ == "__main__":
    app = Flask(__name__)
    manager = PluginManager(
        [PLUGINS_DIR], context={"app": app}, hot_reload=True, poll_interval=1.0
    )
    manager.load_all()

    app.run(host="0.0.0.0", port=3000)
