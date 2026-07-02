class ChatAdapter:
    def __init__(self, room):
        self.room = room

    def send_message(self, text):
        if not self.room:
            raise RuntimeError("Chat room is not available")
        if hasattr(self.room, "send_message"):
            return self.room.send_message(text)
        raise RuntimeError("Chat room does not support send_message")
