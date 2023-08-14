import os
import subprocess
import sys
import time
from colorama import init, Fore, Back, Style
import importlib
import asyncio

from auth import YouTubeAuth, TikTokAuth, TwitchAuth
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
    if not os.path.exists("client.json"):
        print("ERROR: client.json file missing!")
        sys.exit(1)


def install_required_packages():
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


def choose_platforms():
    print("Select the platforms you want to authenticate with (comma separated):")
    print("1: YouTube")
    print("2: TikTok")
    print("3: Twitch")

    choices = input("Enter the numbers of your choices (e.g. '1,2' for YouTube and TikTok): ").split(',')
    auth_methods = []
    for choice in choices:
        choice = choice.strip()
        if choice == "1":
            auth_methods.append(YouTubeAuth())
        elif choice == "2":
            auth_methods.append(TikTokAuth())  # Uncomment when you've defined TikTokAuth
        elif choice == "3":
            auth_methods.append(TwitchAuth())  # Uncomment when you've defined TwitchAuth
        else:
            print(f"Invalid choice: {choice}")
            sys.exit(1)
    return auth_methods


class Main:
    def __init__(self):
        self.auths = choose_platforms()
        self.controller = Controller()

    async def listen_to_live_chat(self, auth, live_chat_id):
        while True:
            response = auth.get_chat_messages(live_chat_id)
            if response:
                for item in response.get('items', []):  # make sure 'items' exists
                    message = item['snippet']['textMessageDetails']['messageText']
                    print(f"Message: {message}")
                    if Controller.is_valid_message(message):
                        Controller.perform_action(message)
                await asyncio.sleep(5)  # wait for 5 seconds before next poll
            else:
                print("Live chat has ended.")
                await asyncio.sleep(60)  # wait for 60 seconds before checking again

    async def run_platform_listener(self, auth):
        broadcast_id = auth.get_live_broadcast_id()
        if broadcast_id:
            live_chat_id = auth.get_live_chat_id_from_broadcast(broadcast_id)
            await self.listen_to_live_chat(auth, live_chat_id)
        else:
            print(f"No active livestream found for {type(auth).__name__}.")

    def run(self):
        loop = asyncio.get_event_loop()
        tasks = [self.run_platform_listener(auth) for auth in self.auths]
        loop.run_until_complete(asyncio.gather(*tasks))


if __name__ == "__main__":
    try:
        display_startup_message()
        install_required_packages()
        check_configurations()
        print(Fore.GREEN)
        print("Loaded\n\n")
        print(Fore.RESET)

        main_app = Main()
        main_app.run()
    except KeyboardInterrupt:
        print(Fore.RED + "\nThank you for using me. Have a good day!" + Fore.RESET)
