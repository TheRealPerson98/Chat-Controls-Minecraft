import time
import pyautogui

# Hello

class Controller:
    ALLOWED_MESSAGES = [
        "w", "a", "s", "d", "space", "attack", "place", "mine",
        "e", "toggle sprint", "f3", "f2", "1", "2", "3", "4",
        "5", "6", "7", "8", "9", "turn left", "turn right", "turn up", "turn down", "open"
    ]

    @staticmethod
    def is_valid_message(message):
        return message in Controller.ALLOWED_MESSAGES

    @staticmethod
    def perform_action(command):
        print(f"Attempting to perform action: {command}")

        if command.startswith("turn"):
            Controller.turn_head(command)
            return

        if command not in Controller.ALLOWED_MESSAGES:
            print(f"Unknown or disallowed command: {command}")
            return

        key_mappings = {
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

        key = key_mappings.get(command)
        if key:
            pyautogui.keyDown(key)
            if command == "mine":
                time.sleep(1)
            else:
                time.sleep(0.3)
            pyautogui.keyUp(key)
            print(f"Pressed '{key}'")
        else:
            print(f"Unknown action: {command}")

    @staticmethod
    def turn_head(command):
        turn_mappings = {
            "turn left": (-100, 0),
            "turn right": (100, 0),
            "turn up": (0, -100),
            "turn down": (0, 100)
        }

        dx, dy = turn_mappings.get(command, (0, 0))
        pyautogui.moveRel(dx, dy, duration=0.2)
        print(f"Turned head {command.split(' ')[1]}")
