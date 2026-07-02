import chatexchange
from ..settings import CHAT_HOST, SE_EMAIL, SE_PASSWORD, ROOM_ID


class ChatClient:
    def __init__(self):
        self.client = chatexchange.Client(CHAT_HOST)
        self.room = None

    def login(self):
        self.client.login(SE_EMAIL, SE_PASSWORD)
        self.room = self.client.get_room(ROOM_ID)
        self.room.join()
        return self.room

    def get_room(self):
        if self.room is None:
            return self.login()
        return self.room
