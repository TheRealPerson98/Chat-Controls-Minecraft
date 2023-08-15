from colorama import Fore
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, ConnectEvent

from auth.Auth import Auth
from auth.MessageStore import MessageStore
from auth.UtilityFunctions import load_auth_details, save_auth_details

ALLOWED_MESSAGES = [
    "w", "a", "s", "d", "space", "attack", "place", "mine",
    "e", "toggle sprint", "f3", "f2", "1", "2", "3", "4",
    "5", "6", "7", "8", "9", "turn left", "turn right", "turn up",
    "turn down", "open", "dance"
]


class TikTokAuth(Auth):
    def __init__(self):
        self.details = load_auth_details('tiktok')
        if not self.details:
            self.username = input("Enter your TikTok username (e.g., @BetterPerson98): ")
            save_auth_details('tiktok', self.username)
        else:
            self.username = self.details

        self.client = TikTokLiveClient(unique_id=self.username)
        self.messages = []

        @self.client.on("connect")
        async def on_connect(_: ConnectEvent):
            print(Fore.GREEN + " [TikTok] Connected to Room ID:", self.client.room_id)

        self.client.add_listener("comment", self.on_comment)

    async def on_comment(self, event: CommentEvent):
        message = event.comment.lower()  # Convert message to lowercase for consistent checking
        if message in ALLOWED_MESSAGES:
            store = MessageStore()
            store.add_message(message)  # Assuming event has a user attribute

    async def get_chat_messages(self):
        messages_to_return = self.messages.copy()
        print(messages_to_return)
        self.messages.clear()
        return messages_to_return if messages_to_return else None

    async def start(self):
        await self.client.start()
