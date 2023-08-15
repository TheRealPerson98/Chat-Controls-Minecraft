import asyncio
import sys
import json

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from colorama import Fore
from auth.Auth import Auth
from auth.MessageStore import MessageStore


class YouTubeAuth(Auth):
    CLIENT_SECRETS_FILE = "client.json"
    SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
    ALLOWED_MESSAGES = [
        "w", "a", "s", "d", "space", "attack", "place", "mine",
        "e", "toggle sprint", "f3", "f2", "1", "2", "3", "4",
        "5", "6", "7", "8", "9", "turn left", "turn right", "turn up",
        "turn down", "open", "dance"
    ]

    def __init__(self):
        try:
            flow = InstalledAppFlow.from_client_secrets_file(self.CLIENT_SECRETS_FILE, self.SCOPES)
            self.credentials = flow.run_local_server(port=0)
            self.youtube = build('youtube', 'v3', credentials=self.credentials)
            self.seen_message_ids = set()  # Initialize the set to store seen message IDs
        except Exception:
            print(Fore.RED + "There was an issue with client.json. Please check the file and try again." + Fore.RESET)
            sys.exit(1)

    def get_live_broadcast_id(self):
        request = self.youtube.liveBroadcasts().list(part="id", broadcastType="all", mine=True, maxResults=1)
        response = request.execute()
        if response['items']:
            return response['items'][0]['id']
        return None

    async def get_chat_messages(self):
        broadcast_id = self.get_live_broadcast_id()
        if not broadcast_id:
            return
        live_chat_id = self.get_live_chat_id_from_broadcast(broadcast_id)
        params = {
            "liveChatId": live_chat_id,
            "part": "snippet"
        }
        try:
            request = self.youtube.liveChatMessages().list(**params)
            response = request.execute()
            for item in response.get('items', []):
                message_id = item['id']  # Get the unique message ID

                # Check if the message has been seen before
                if message_id in self.seen_message_ids:
                    continue  # Skip this message

                # If not, process the message and add its ID to the set
                self.seen_message_ids.add(message_id)

                user = item['snippet']['displayMessage']
                message = item['snippet']['textMessageDetails']['messageText']

                # Only store the message if it's in the ALLOWED_MESSAGES list
                if message.lower() in self.ALLOWED_MESSAGES:
                    store = MessageStore()
                    store.add_message(message)

        except HttpError as e:
            if "liveChatEnded" in str(e):
                print("Live chat has ended.")
            elif YouTubeAuth.is_quota_error(e):
                print(Fore.RED + "YouTube API quota exceeded. Please try again later." + Fore.RESET)
                sys.exit(1)

    def get_live_chat_id_from_broadcast(self, broadcast_id):
        request = self.youtube.liveBroadcasts().list(part="snippet", id=broadcast_id)
        response = request.execute()
        return response['items'][0]['snippet']['liveChatId']

    @staticmethod
    def is_quota_error(error):
        if not error.content:
            return False
        content = json.loads(error.content)
        for e in content["error"].get("errors", []):
            if e["reason"] == "quotaExceeded":
                return True
        return False

    async def start(self):
        """Start listening to YouTube live chat messages."""
        while True:
            await self.get_chat_messages()
            await asyncio.sleep(10)  # Poll every 10 seconds
