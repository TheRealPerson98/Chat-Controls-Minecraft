import sys
import json
import googleapiclient.errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from colorama import init, Fore, Back, Style
import pickle
import os
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent
from twitchio.ext import commands


class Auth:
    def __init__(self):
        pass

    def get_live_broadcast_id(self):
        raise NotImplementedError

    def get_live_chat_id_from_broadcast(self, broadcast_id):
        raise NotImplementedError

    def get_chat_messages(self, live_chat_id, page_token=None):
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
        except Exception as e:
            print(Fore.RED + "There was an issue with client.json. Please check the file and try again." + Fore.RESET)
            sys.exit(1)

    def get_live_broadcast_id(self):
        request = self.youtube.liveBroadcasts().list(
            part="id",
            broadcastType="all",
            mine=True,
            maxResults=1
        )
        response = request.execute()
        if response['items']:
            return response['items'][0]['id']
        return None

    def get_live_chat_id_from_broadcast(self, broadcast_id):
        request = self.youtube.liveBroadcasts().list(
            part="snippet",
            id=broadcast_id
        )
        response = request.execute()
        return response['items'][0]['snippet']['liveChatId']

    def get_chat_messages(self, live_chat_id, page_token=None):
        params = {
            "liveChatId": live_chat_id,
            "part": "snippet"
        }
        if page_token:
            params["pageToken"] = page_token

        try:
            request = self.youtube.liveChatMessages().list(**params)
            response = request.execute()
            return response
        except googleapiclient.errors.HttpError as e:
            if "liveChatEnded" in str(e):
                print("Live chat has ended.")
                return None
            elif YouTubeAuth.is_quota_error(e):
                print(Fore.RED + "YouTube API quota exceeded. Please try again later." + Fore.RESET)
                sys.exit(1)
            else:
                raise

    @staticmethod
    def is_quota_error(error):
        if not error.content:
            return False
        try:
            content = json.loads(error.content)
            if "errors" in content["error"]:
                for e in content["error"]["errors"]:
                    if e["reason"] == "quotaExceeded":
                        return True
        except ValueError:
            return False
        return False


class TikTokAuth(Auth):
    def __init__(self):
        self.details = load_auth_details('tiktok')
        if not self.details:
            self.username = input("Enter your TikTok username (e.g., @BetterPerson98): ")
            save_auth_details('tiktok', self.username)
            self.client = TikTokLiveClient(unique_id=self.username)
        else:
            self.username = self.details
            self.client = TikTokLiveClient(unique_id=self.username)

    def get_live_broadcast_id(self):
        # Since TikTokLive library already connects to the live room using username,
        # we can use the `room_id` attribute to represent the broadcast ID
        return self.client.room_id

    def get_live_chat_id_from_broadcast(self, broadcast_id):
        # In this context, the broadcast ID is equivalent to the chat ID for TikTok
        return broadcast_id

    def get_chat_messages(self, live_chat_id, page_token=None):
        messages = []

        @self.client.on("comment")
        async def on_comment(event: CommentEvent):
            messages.append(f"{event.user.nickname} -> {event.comment}")

        # Start listening for comments (this will block the thread until live ends)
        self.client.start()

        # Return collected messages (this could be adjusted to fit your needs)
        return messages


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

        # Initialize twitch bot (using twitchio's bot extension)
        self.bot = commands.Bot(
            irc_token=self.irc_token,
            client_id=self.client_id,
            nick=self.bot_nickname,
            prefix='!',
            initial_channels=[self.channel]
        )

        self.messages = []

        @self.bot.event
        async def event_message(ctx):
            # Print each message to console
            print(f'{ctx.author.name}: {ctx.content}')
            self.messages.append(f'{ctx.author.name}: {ctx.content}')

        # Run the bot (this will block)
        self.bot.run()

    def get_live_broadcast_id(self):
        # Fetch the live broadcast/stream ID from Twitch (for this use case, we'll use the channel name as the ID)
        return self.channel

    def get_live_chat_id_from_broadcast(self, broadcast_id):
        # For Twitch, chatrooms are tied to channels, so you might not need this method
        return broadcast_id  # Returning broadcast ID since it's the same as the chat ID for Twitch

    def get_chat_messages(self, live_chat_id, page_token=None):
        # Return stored messages
        return self.messages
