import googleapiclient.errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow


# Hello
class Auth:
    CLIENT_SECRETS_FILE = "client.json"
    SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

    def __init__(self):
        flow = InstalledAppFlow.from_client_secrets_file(self.CLIENT_SECRETS_FILE, self.SCOPES)
        self.credentials = flow.run_local_server(port=0)
        self.youtube = build('youtube', 'v3', credentials=self.credentials)

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
            else:
                raise
