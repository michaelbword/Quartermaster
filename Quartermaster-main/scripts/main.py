import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../config/environment.env')

discord_channel_id = int(os.getenv("main_channel_id"))

async def main():
    # Load environment variables
    load_dotenv('../config/environment.env')

    # Get the bot token from an environment variable
    bot_token = os.getenv('BOT_TOKEN')

    # Define all intents
    intents = discord.Intents.all()

    client = commands.Bot(command_prefix='!', intents=intents, help_command=None)

    # Load all the cogs as extensions
    await client.load_extension("cogs.help")
    await client.load_extension("cogs.ChatGPT")
    await client.load_extension("cogs.EasterEggCog")
    await client.load_extension("cogs.admin_cog")
    await client.load_extension("cogs.d20_cog")
    await client.load_extension("cogs.dad_joke_cog")
    await client.load_extension("cogs.music_cog")
    await client.load_extension("cogs.streamer")
    await client.load_extension("cogs.welcome_cog")
    await client.load_extension("cogs.poll_cog")
    await client.load_extension("cogs.rps")
    await client.load_extension("cogs.hptrivia")


    @client.event
    async def on_ready():
        print(f'{client.user} has connected to Discord!')

        # Load message_id and channel_id for role assignment
        channel = client.get_channel(discord_channel_id)
        if channel:
            client.get_cog('AdminCogs').load_role_message_data()
        else:
            print(f"Channel with ID {discord_channel_id} not found.")

    await client.start(bot_token)

if __name__ == '__main__':
    asyncio.run(main())
