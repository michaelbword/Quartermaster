import discord
from discord.ext import commands
from tabulate import tabulate
from discord_bot import client


class HelpCog(commands.Cog, commands.HelpCommand):
    def __init__(self, client):
        super().__init__()
        self.client = client

    async def send_bot_help(self, mapping):
        # Your custom bot help implementation here
        commands_data = [
            ("!roles", "AdminCogs", "<Name of role> ex: !Role NSFW - Assign roles using reactions or manually with "
                                    "chat\n"),
            ("!help", "AdminCogs", "Ask for help, obviously. The bot will spout all the helpful info it can\n"),
            ("!build", "CodCog", "<gun_name>: Get information about a specific gun's attachments \n")
        ]
        ascii_art = [
            "    /~\\",
            "   |oo )",
            "   _\\=/_",
            "  /  _  \\",
            " //|/.\\|\\\\",
            "||  \\_/  ||"
        ]

        # Combine ASCII art with the commands_data
        for i, command_data in enumerate(commands_data):
            command_data = list(command_data)
            command_data.append(ascii_art[i])
            commands_data[i] = tuple(command_data)

        table = tabulate(commands_data, headers=["Command", "Cog", "Description"], tablefmt="simple")
        response = f"Here's some help for this bot:\n```\n{table}```"
        await self.get_destination().send(response)

    async def send_cog_help(self, cog):
        # Your custom cog help implementation here
        pass

    async def send_command_help(self, command):
        # Your custom command help implementation here
        pass

# Set the help command to your custom HelpCog
help_cog_instance = HelpCog(client)
client.help_command = help_cog_instance
