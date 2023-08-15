import os
import subprocess
import sys
import time
from colorama import init, Fore, Back, Style
import importlib
import asyncio

from auth import YouTubeAuth, TikTokAuth, TwitchAuth, MessageStore
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


message_store = MessageStore()


class Main:
    def __init__(self):
        self.auths = choose_platforms()
        self.controller = Controller()

    async def listen_to_live_chat(self, auth):
        print("Listening to live chat...")  # Debug line

        while True:
            messages = message_store.get_messages()
            print(f"Stored Messages: {messages}")

            if messages:
                processed_count = 0  # Counter to keep track of processed messages
                for platform, user, message in messages:
                    print(f"[{message}")
                    if self.controller.is_valid_message(message):  # Changed to instance method
                        self.controller.perform_action(message)  # Changed to instance method
                        processed_count += 1
                # Remove all the processed messages from the file
                message_store.remove_processed_messages(processed_count)
                await asyncio.sleep(5)  # wait for 5 seconds before the next poll
            else:
                print("No messages in the store right now.")  # Debug line
                await asyncio.sleep(5)

    async def run_platform_listener(self, auth):
        if isinstance(auth, TikTokAuth):
            await auth.start()  # Start TikTokAuth client (if you have such a method)
        await self.listen_to_live_chat(auth)

    async def run(self):
        listening_tasks = [self.run_platform_listener(auth) for auth in self.auths]
        await asyncio.gather(*listening_tasks)


if __name__ == "__main__":
    try:
        display_startup_message()
        install_required_packages()
        check_configurations()
        print(Fore.GREEN)
        print("Loaded\n\n")
        print(Fore.RESET)

        main_app = Main()
        asyncio.run(main_app.run())
    except KeyboardInterrupt:
        print(Fore.RED + "\nThank you for using me. Have a good day!" + Fore.RESET)
