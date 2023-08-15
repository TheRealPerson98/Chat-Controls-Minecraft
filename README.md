# Chat-Controls-Minecraft

Control your Minecraft game using chat messages from YouTube and TikTok live streams.

## How to Use

### Setup

1. Ensure you have Python installed on your system. If not, download and install Python.
2. Clone the repository and navigate to its directory:
```bash
git clone https://github.com/TheRealPerson98/Chat-Controls-Minecraft
cd Chat-Controls-Minecraft
```
3. Install the necessary Python packages:
```bash
python setup.py
```

### Configuration

#### YouTube:
1. Create a project on the [Google Developers Console](https://console.developers.google.com/).
2. Enable the YouTube API v3.
3. Obtain the `client.json` file and place it in the root directory of this project.

#### TikTok:
1. Ensure you have your TikTok username ready.

### Running

Start the script:
```bash
python main.py
```

Follow the instructions to authenticate your Google account for YouTube and/or input your TikTok username.

Once authenticated, start your YouTube or TikTok live stream. When viewers type commands into the live chat, they will be processed and sent to your Minecraft game.

### Security

Please ensure you only run commands from trusted sources. Be cautious about potential harmful commands that could be sent through the chat.

### Contribute

If you'd like to contribute, please fork the repository and make changes as you'd like. Pull requests are warmly welcome.
