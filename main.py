import os
import subprocess
import sys
import time
from colorama import init, Fore, Back, Style
import importlib

from auth import Auth
from controller import Controller

init()


def display_startup_message():
    print(Fore.GREEN)

    print("$$\      $$\  $$$$$$\  $$\                  $$\      $$$$$$\    $$\               $$\ ")
    print("$$$\    $$$ |$$  __$$\ $$ |                 $$ |    $$  __$$\   $$ |              $$ |")
    print("$$$$\  $$$$ |$$ /  \__|$$$$$$$\   $$$$$$\ $$$$$$\   $$ /  \__|$$$$$$\    $$$$$$\  $$ |")
    print("$$\$$\$$ $$ |$$ |      $$  __$$\  \____$$\\_$$  _|  $$ |      \_$$  _|  $$  __$$\ $$ |")
    print("$$ \$$$  $$ |$$ |      $$ |  $$ | $$$$$$$ | $$ |    $$ |        $$ |    $$ |  \__|$$ |")
    print("$$ |\$  /$$ |$$ |  $$\ $$ |  $$ |$$  __$$ | $$ |$$\ $$ |  $$\   $$ |$$\ $$ |      $$ |")
    print("$$ | \_/ $$ |\$$$$$$  |$$ |  $$ |\$$$$$$$ | \$$$$  |\$$$$$$  |  \$$$$  |$$ |      $$ |")
    print("\__|     \__| \______/ \__|  \__| \_______|  \____/  \______/    \____/ \__|      \__|")
    print(Fore.YELLOW)
    print("Made By Person98")
    print("Discord Person98")
    print(Fore.RED)

    print("Loading", end='', flush=True)
    for _ in range(5):
        print('.', end='', flush=True)
        time.sleep(0.5)
    print()


def check_configurations():
    # Check if client.json exists
    if not os.path.exists("client.json"):
        print("ERROR: client.json file missing!")
        sys.exit(1)


def install_required_packages():
    # Correct package names for pip installation
    packages = {
        'googleapiclient': 'google-api-python-client',
        'google_auth_oauthlib': 'google-auth-oauthlib',
        'pyautogui': 'pyautogui',
        'colorama': 'colorama',
    }
    for module_name, package_name in packages.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            print(f"{package_name} not found!")
            proceed = input(f"Do you want to install {package_name}? (y/n): ")
            if proceed.lower() == 'y':
                print(f"Installing {package_name}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
                print(f"{package_name} installed successfully!")



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
            else:
                # This section is added to handle the "Live chat has ended" scenario
                print("Live chat has ended.")
                time.sleep(60)  # wait for 1 minute before trying again
                continue

    def run(self):
        broadcast_id = self.auth.get_live_broadcast_id()
        if broadcast_id:
            live_chat_id = self.auth.get_live_chat_id_from_broadcast(broadcast_id)
            self.listen_to_live_chat(live_chat_id)
        else:
            print("No active livestream found for this channel.")


if __name__ == "__main__":
    display_startup_message()
    install_required_packages()
    check_configurations()
    print(Fore.GREEN)
    print("Loaded\n\n")  # "Loaded" message after installing packages and checking configurations
    print(Fore.RESET)

    main_app = Main()
    main_app.run()
