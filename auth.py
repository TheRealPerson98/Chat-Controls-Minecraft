import sys
import googleapiclient.errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from colorama import init, Fore, Back, Style
import json


class Auth:
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

    @staticmethod
    def is_quota_error(error):
        """Check if an error is a quota error."""
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
            elif Auth.is_quota_error(e):
                print(Fore.RED + "YouTube API quota exceeded. Please try again later." + Fore.RESET)
                sys.exit(1)
            else:
                raise
