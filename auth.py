import sys
import json
import pickle
import asyncio
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from colorama import init, Fore
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, ConnectEvent
from twitchio.ext import commands


class Auth:
    """Base Authentication class."""

    def get_live_broadcast_id(self):
        raise NotImplementedError

    def get_chat_messages(self):
        raise NotImplementedError


def save_auth_details(platform, auth_details):
    with open(f"{platform}_auth.pkl", 'wb') as f:
        pickle.dump(auth_details, f)


def load_auth_details(platform):
    try:
        with open(f"{platform}_auth.pkl", 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None


class YouTubeAuth(Auth):
    CLIENT_SECRETS_FILE = "client.json"
    SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

    def __init__(self):
        try:
            flow = InstalledAppFlow.from_client_secrets_file(self.CLIENT_SECRETS_FILE, self.SCOPES)
            self.credentials = flow.run_local_server(port=0)
            self.youtube = build('youtube', 'v3', credentials=self.credentials)
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
                user = item['snippet']['displayMessage']
                message = item['snippet']['textMessageDetails']['messageText']
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
            print(Fore.GREEN + "Connected to Room ID:", self.client.room_id)

        self.client.add_listener("comment", self.on_comment)

    async def on_comment(self, event: CommentEvent):
        store = MessageStore()
        store.add_message(event.comment)

    async def get_chat_messages(self):
        messages_to_return = self.messages.copy()
        print(messages_to_return)
        self.messages.clear()
        return messages_to_return if messages_to_return else None

    async def start(self):
        await self.client.start()


class TwitchAuth(Auth):
    def __init__(self):
        self.details = load_auth_details('twitch')
        if not self.details:
            self.client_id = input("Enter your Twitch client ID: ")
            self.client_secret = input("Enter your Twitch client secret: ")
            self.channel = input("Enter the channel name: ")
            self.irc_token = input("Enter your Twitch IRC token (OAuth token for bot): ")
            self.bot_nickname = input("Enter the nickname of your bot: ")
            save_auth_details('twitch', {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'channel': self.channel,
                'irc_token': self.irc_token,
                'bot_nickname': self.bot_nickname
            })
        else:
            self.client_id = self.details['client_id']
            self.client_secret = self.details['client_secret']
            self.channel = self.details['channel']
            self.irc_token = self.details['irc_token']
            self.bot_nickname = self.details['bot_nickname']

        self.bot = commands.Bot(
            irc_token=self.irc_token,
            client_id=self.client_id,
            nick=self.bot_nickname,
            prefix='!',
            initial_channels=[self.channel]
        )

        @self.bot.event
        async def event_message(ctx):
            user = ctx.author.name
            message = ctx.content
            store = MessageStore()
            store.add_message(message)

    def run(self):
        self.bot.run()


class MessageStore:

    def __init__(self, filename='message.txt'):
        self.filename = filename
        # Ensure the file exists
        open(self.filename, 'a').close()

    def add_message(self, message):
        with open(self.filename, 'a') as file:
            file.write(f"{message}\n")

    def get_messages(self):
        with open(self.filename, 'r') as file:
            lines = file.readlines()
        return [tuple(line.strip().split(',')) for line in lines]

    def remove_processed_messages(self, num_messages):
        with open(self.filename, 'r') as file:
            lines = file.readlines()

        # Remove the processed messages
        with open(self.filename, 'w') as file:
            file.writelines(lines[num_messages:])

