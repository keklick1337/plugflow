from plugflow import BasePlugin
from flask import Blueprint, jsonify, Flask

echo_page = Blueprint("echo", __name__)


@echo_page.route("/echo")
def echo():
    return jsonify({"ping": "pong"})


class EchoWeb(BasePlugin):
    name = "echo"
    version = "0.0.1"

    def on_load(self, manager) -> None:
        echo_pl: Flask = self.context.get("app")
        echo_pl.register_blueprint(echo_page)
