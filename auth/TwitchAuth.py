from twitchio.ext import commands
from auth.Auth import Auth
from auth.MessageStore import MessageStore


class TwitchAuth(Auth):

    def __init__(self):
        self.irc_token = input("Enter your Twitch IRC token (OAuth token for bot): ")
        self.channel = input("Enter the channel name: ")
        self.bot = self.create_bot()

    def create_bot(self):
        bot = commands.Bot(
            token=self.irc_token,
            prefix="!",
            initial_channels=[self.channel]
        )

        @bot.event
        async def event_ready():
            print(f'Logged in as | {bot.nick}')

        @bot.event
        async def event_message(message):
            if message.echo:
                return

            print(f"{message.author.name}: {message.content}")
            await bot.handle_commands(message)

        @commands.command(name="hello")
        async def hello_command(ctx: commands.Context):
            await ctx.send(f'Hello {ctx.author.name}!')

        bot.add_command(hello_command)

        return bot

    async def start(self):
        await self.bot.start()
