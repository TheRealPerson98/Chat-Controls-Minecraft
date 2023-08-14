# Chat-Controls-Minecraft

Control your Minecraft world with YouTube Live Chat! This tool allows you to interact with your Minecraft game using commands sent from a YouTube live chat. For example, you can spawn mobs, change the weather, or execute any other game command directly from the chat.

## How to Use

### Setup
Make sure you have Python installed on your system. If not, download and install Python.
Install the necessary Python packages:

```bash
pip install --upgrade google-api-python-client google-auth-oauthlib colorama
```
```bash
git clone https://github.com/your-username/Chat-Controls-Minecraft.git
cd Chat-Controls-Minecraft
```

### Configuration
You need to create a project on Google Developers Console, enable the YouTube API v3, and obtain the client.json file.
Place the client.json in the root directory of this project.

### Running
Start the script:
```bash
python main.py
```
Follow the instructions to authenticate your Google account.

Once authenticated, start your YouTube live stream. When viewers type commands into the live chat, they will be processed and sent to your Minecraft game.

### Security
Please ensure you only run commands from trusted sources. Be cautious about potential harmful commands that could be sent through the chat.

### Contribute
If you'd like to contribute, please fork the repository and make changes as you'd like. Pull requests are warmly welcome.