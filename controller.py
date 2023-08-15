import time
import pyautogui
from colorama import init, Fore, Back, Style
import pygetwindow as gw


class Controller:
    ALLOWED_MESSAGES = [
        "w", "a", "s", "d", "space", "attack", "place", "mine",
        "e", "toggle sprint", "f3", "f2", "1", "2", "3", "4",
        "5", "6", "7", "8", "9", "turn left", "turn right", "turn up", "turn down", "open",
        "dance"
    ]

    KEY_MAPPINGS = {
        "w": 'w',
        "a": 'a',
        "s": 's',
        "d": 'd',
        "space": 'space',
        "attack": ',',
        "open": '.',
        "place": '.',
        "mine": ',',
        "e": 'e',
        "toggle sprint": 'shift',
        "f3": 'f3',
        "f2": 'f2',
        "1": '1',
        "2": '2',
        "3": '3',
        "4": '4',
        "5": '5',
        "6": '6',
        "7": '7',
        "8": '8',
        "9": '9'
    }

    TURN_MAPPINGS = {
        "turn left": (-100, 0),
        "turn right": (100, 0),
        "turn up": (0, -100),
        "turn down": (0, 100)
    }

    @staticmethod
    def is_valid_message(message):
        return message.strip() in Controller.ALLOWED_MESSAGES

    @staticmethod
    def is_minecraft_active():
        try:
            active_win = gw.getActiveWindow()
            if active_win and "Minecraft" in active_win.title:
                return True
            else:
                return False
        except Exception:
            return False

    @staticmethod
    def perform_action(command):
        if not Controller.is_minecraft_active():
            print(f"{Fore.RED}Minecraft is not the active window. No action performed.{Fore.RESET}")
            return

        if command == "dance":
            for _ in range(5):  # Repeat 5 times
                pyautogui.keyDown('shift')  # Shift
                time.sleep(0.3)
                pyautogui.keyUp('shift')

                pyautogui.keyDown(',')  # Attack
                time.sleep(0.3)
                pyautogui.keyUp(',')

                pyautogui.moveRel(0, -100, duration=0.2)  # Turn up
            print(f"{Fore.GREEN}Performed dance sequence!{Fore.RESET}")
            return

        if command.startswith("turn"):
            Controller.turn_head(command)
            return

        if command not in Controller.ALLOWED_MESSAGES:
            print(f"{Fore.RED}Unknown or disallowed command: {command}{Fore.RESET}")
            return

        key = Controller.KEY_MAPPINGS.get(command)
        if key:
            pyautogui.keyDown(key)
            if command == "mine":
                time.sleep(1)
            else:
                time.sleep(0.3)
            pyautogui.keyUp(key)
            print(f"{Fore.GREEN}Player Clicked '{key}'{Fore.RESET}")
        else:
            print(f"{Fore.RED}Unknown action: {command}{Fore.RESET}")

    @staticmethod
    def turn_head(command):
        dx, dy = Controller.TURN_MAPPINGS.get(command, (0, 0))
        pyautogui.moveRel(dx, dy, duration=0.2)
        print(f"{Fore.YELLOW}Turned head {command.split(' ')[1]}{Fore.RESET}")
