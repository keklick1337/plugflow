from plugflow import BasePlugin

class EchoWebPlugin(BasePlugin):
    name = "web_echo"
    priority = 50

    def handles(self, event: str) -> bool:
        return event == "web_request_echo"

    def on_event(self, event: str, data, manager):
        if event == "web_request_echo":
            message = data.get("data", {}).get("message", "")
            return {"echo": message, "plugin": self.name}
        return None
