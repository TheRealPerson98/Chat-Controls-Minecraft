class MessageStore:

    def __init__(self, filename='message.txt'):
        self.filename = filename
        # Ensure the file exists
        open(self.filename, 'a').close()

    def add_message(self, message):
        with open(self.filename, 'a') as file:
            file.write(f"{message}\n")

    def get_messages(self):
        with open(self.filename, 'r') as file:
            lines = file.readlines()
        return [tuple(line.strip().split(',')) for line in lines]

    def remove_processed_messages(self, num_messages):
        with open(self.filename, 'r') as file:
            lines = file.readlines()

        # Remove the processed messages
        with open(self.filename, 'w') as file:
            file.writelines(lines[num_messages:])
