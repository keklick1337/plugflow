from plugflow import BasePlugin

class ReverseWebPlugin(BasePlugin):
    name = "web_reverse"
    priority = 50

    def handles(self, event: str) -> bool:
        return event == "web_request_reverse"

    def on_event(self, event: str, data, manager):
        if event == "web_request_reverse":
            message = data.get("data", {}).get("message", "")
            return {"reversed": message[::-1], "plugin": self.name}
        return None
