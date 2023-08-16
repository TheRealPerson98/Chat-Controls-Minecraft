import asyncio
import os
import sys
import time

from colorama import init, Fore

from auth.MessageStore import MessageStore
from auth.TikTokAuth import TikTokAuth
from auth.YouTubeAuth import YouTubeAuth
from controller import Controller

init(autoreset=True)


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


def choose_platforms():
    print(Fore.CYAN + "Select the platforms you want to authenticate with (comma separated):")
    print(Fore.YELLOW + "1: YouTube")
    print(Fore.YELLOW + "2: TikTok")
    print(Fore.YELLOW + "3: Clear Auth")

    while True:  # Keep looping until valid input is received
        choices = input(Fore.GREEN + "Enter the numbers of your choices (e.g. '1,2' for YouTube and TikTok): ").split(
            ',')
        auth_methods = []
        invalid_choices = False  # Flag to check if any choice is invalid

        for choice in choices:
            choice = choice.strip()
            if choice == "1":
                auth_methods.append(YouTubeAuth())
            elif choice == "2":
                auth_methods.append(TikTokAuth())
            elif choice == "3":
                clear_auth()
            else:
                print(Fore.RED + f"Invalid choice: {choice}. Please enter valid choices.")
                invalid_choices = True
                break  # Break out of the for loop

        if not invalid_choices:  # If all choices are valid, break out of the while loop
            break

    return auth_methods


def clear_auth():
    print(Fore.CYAN + "Which platform's authentication would you like to clear?")
    print(Fore.YELLOW + "1: YouTube")
    print(Fore.YELLOW + "2: TikTok")

    choice = input(Fore.GREEN + "Enter the number of your choice: ").strip()

    if choice == "1":
        # Clear YouTube authentication by emptying the client.json file
        with open("client.json", "w") as file:
            file.write("{}")
        print(Fore.RED + "YouTube authentication cleared!")
    elif choice == "2":
        # Clear TikTok authentication by deleting the tiktok_auth.pkl file
        try:
            os.remove("tiktok_auth.pkl")
            print(Fore.RED + "TikTok authentication cleared!")
        except FileNotFoundError:
            print(Fore.RED + "TikTok authentication file not found!")
    else:
        print(Fore.RED + f"Invalid choice: {choice}. Please enter a valid choice.")


message_store = MessageStore()


class Main:
    def __init__(self):

        try:
            os.remove('message.txt')
        except FileNotFoundError:
            pass

        self.auths = choose_platforms()
        self.controller = Controller()

    async def listen_to_live_chat(self, auth):
        print(Fore.GREEN + "Listening to live chat...")

        while True:
            messages = message_store.get_messages()

            if messages:
                processed_count = 0  # Counter to keep track of processed messages
                for message_tuple in messages:
                    message_text = message_tuple[0]
                    print(f"[{message_text}]")
                    if self.controller.is_valid_message(message_text):
                        self.controller.perform_action(message_text)

                        processed_count += 1
                # Remove all the processed messages from the file
                message_store.remove_processed_messages(processed_count)
                await asyncio.sleep(5)  # wait for 5 seconds before the next poll
            else:
                await asyncio.sleep(5)

    async def run_platform_listener(self, auth):
        if isinstance(auth, TikTokAuth):
            await auth.start()  # Start TikTokAuth client
        elif isinstance(auth, YouTubeAuth):
            await auth.start()  # Start YouTubeAuth client (if you have such a method)

        await self.listen_to_live_chat(auth)

    async def run(self):
        listening_tasks = [self.run_platform_listener(auth) for auth in self.auths]
        await asyncio.gather(*listening_tasks)


if __name__ == "__main__":
    try:
        display_startup_message()
        check_configurations()
        print(Fore.GREEN)
        print("Loaded\n\n")
        print(Fore.RESET)

        main_app = Main()
        asyncio.run(main_app.run())
    except KeyboardInterrupt:
        print(Fore.RED + "\nThank you for using me. Have a good day!" + Fore.RESET)
