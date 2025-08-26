from plugflow import BasePlugin

class UppercaseWebPlugin(BasePlugin):
    name = "web_uppercase"
    priority = 50

    def handles(self, event: str) -> bool:
        return event == "web_request_uppercase"

    def on_event(self, event: str, data, manager):
        if event == "web_request_uppercase":
            message = data.get("data", {}).get("message", "")
            return {"uppercase": message.upper(), "plugin": self.name}
        return None
