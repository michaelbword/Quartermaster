import os
import discord
from help import HelpCog

from admin_cog import AdminCogs
from COD_COG import CodCog
from discord_bot import setup_discord_bot
from role_assignment import assign_role
from web_scraper import get_attachment_names
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from the file
load_dotenv('environment.env')  # Adjust the filename if needed

# Get the bot token from an environment variable
bot_token = os.getenv('BOT_TOKEN')

# Set up the Discord bot
client = commands.Bot(command_prefix='!')
help_cog_instance = HelpCog(client)
client.help_command = help_cog_instance


# Event handlers
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

# Add cogs
client.remove_command('help')
client.add_cog(AdminCogs(client))
client.add_cog(CodCog(client))

# Run the bot
client.run(bot_token)
