import json

import discord
from discord.ext import commands


class WelcomeCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(help="Set a new welcome message to the server: Admin only",
                      usage="!set_welcome_message [message]")
    async def set_welcome_message(self, ctx, *, message: str):
        print("Set_welcome_message called!")
        """Set a new welcome message to the server: Admin only
        Usage: !poll_results message_id"""
        # Check if the user has administrator permissions
        if ctx.author.guild_permissions.administrator:
            # Update the welcome message template in the configuration file
            # Save 'message' to the configuration file (e.g., config.json)
            config = {}
            config['welcome_message'] = message
            with open('../config/config.json', 'w') as config_file:
                json.dump(config, config_file)
            await ctx.send('Welcome message updated successfully.')
        else:
            await ctx.send('You do not have the necessary permissions to use this command.')

    @commands.command(help="Shows current welcome message: Admin only",
                      usage="!get_welcome_message")
    async def get_welcome_message(self, ctx):
        if ctx.author.guild_permissions.administrator:
            """Show current welcome message
            Usage: !get_welcome_message"""
            with open('../config/config.json', 'r') as config_file:
                config = json.load(config_file)
            message = config.get('welcome_message', 'Welcome to the server!')
            await ctx.send(f'Current welcome message: {message}')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Read the welcome message template from the configuration file
        with open('../config/config.json', 'r') as config_file:
            config = json.load(config_file)
            message = config.get('welcome_message', 'Welcome to the server!')

        # Find the channel named "da-hoes" in the guild
        channel = discord.utils.get(member.guild.channels, name='da-hoes')

        # Send the welcome message to the channel if found
        if channel:
            await channel.send(message)
        else:
            print('Channel "da-hoes" not found.')


async def setup(client):
    await client.add_cog(WelcomeCog(client))
