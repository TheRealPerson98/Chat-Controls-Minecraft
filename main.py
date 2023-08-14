import time
from auth import Auth
from controller import Controller

# Hello

class Main:
    def __init__(self):
        self.auth = Auth()
        self.controller = Controller()

    def listen_to_live_chat(self, live_chat_id):
        next_page_token = None
        while True:
            response = self.auth.get_chat_messages(live_chat_id, next_page_token)
            if response:
                for item in response['items']:
                    message = item['snippet']['textMessageDetails']['messageText']
                    print(f"Message: {message}")
                    if Controller.is_valid_message(message):
                        Controller.perform_action(message)
                next_page_token = response.get("nextPageToken")
                if next_page_token is None:
                    break
                time.sleep(5)

    def run(self):
        broadcast_id = self.auth.get_live_broadcast_id()
        if broadcast_id:
            live_chat_id = self.auth.get_live_chat_id_from_broadcast(broadcast_id)
            self.listen_to_live_chat(live_chat_id)
        else:
            print("No active livestream found for this channel.")


if __name__ == "__main__":
    main_app = Main()
    main_app.run()
