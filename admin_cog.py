import asyncio
import datetime
import discord
from discord.ext import commands
from help import HelpCog
from tabulate import tabulate
from discord_bot import client
from web_scraper import get_attachment_names

QUARTERMASTER_ID = 1157876931551842344


class AdminCogs(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.command_limits = {}  # Initialize the command_limits dictionary

    @commands.command()
    async def roles(self, ctx):
        print('Roles command triggered!')
        embed = discord.Embed(title="React with the corresponding emoji to get the role:")
        embed.add_field(name="🍆", value="NSFW 🍆", inline=False)
        embed.add_field(name="🎥", value="Streamer 🎥", inline=False)

        message = await ctx.send(embed=embed)
        await message.add_reaction("🍆")
        await message.add_reaction("🎥")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        if str(reaction.emoji) == "🍆":
            role = discord.utils.get(user.guild.roles, name="NSFW")
            await user.add_roles(role)
            await user.send("You have been assigned NSFW. Let's get frisky ;)")
        elif str(reaction.emoji) == "🎥":
            role = discord.utils.get(user.guild.roles, name="Streamer")
            await user.add_roles(role)
            await user.send("You have been assigned Streamer.")

    @commands.command()
    async def help(self, ctx):
        commands_data = [
            ("!roles", "AdminCogs", "<Name of role> ex: !Role NSFW - Assign roles using reactions or manually with "
                                    "chat\n"),
            ("!help", "AdminCogs", "Ask for help, obviously. The bot will spout all the helpful info it can\n"),
            ("!build", "CodCog", "<gun_name>: Get information about a specific gun's attachments \n")
        ]
        table = tabulate(commands_data, headers=["Command", "Cog", "Description"], tablefmt="fancy_grid")
        # Your help message goes here
        response = f"Here's some help for this bot:\n```\n{table}```"
        await ctx.send(response)

    async def check_command_limit(self, user):
        # Check if the user has exceeded the command limit
        user_id = user.id
        current_time = datetime.datetime.now()

        commands_info = self.command_limits.get(user_id, {'count': 0, 'start_time': current_time})

        # Check the command limit and time elapsed
        if commands_info['count'] >= 3 and (current_time - commands_info['start_time']).seconds < 900:
            # Apply a timeout
            await self.timeout_user(user)
        else:
            # Increment command count and update start time
            commands_info['count'] += 1
            commands_info['start_time'] = current_time
            self.command_limits[user_id] = commands_info

    async def timeout_user(self, user):
        guild = user.guild

        # Get the timeout role
        timeout_role = discord.utils.get(guild.roles, name="Timeout")

        # Add the timeout role to the user
        await user.add_roles(timeout_role)

        # Remove the spam commands from the user
        await self.remove_spam_commands(user)

        # Send a message to the user
        timeout_message = "Did you have a stroke and fall on your keyboard? Timeout for 30 minutes. Stop smelling " \
                          "toast. Only people with small dicks spam chat. "
        await user.send(timeout_message)
        # Send a message in the channel
        timeout_channel = discord.utils.get(guild.channels, name="testing")
        if timeout_channel:
            await timeout_channel.send(f"{user.mention}, did you have a stroke and fall on your keyboard? Timeout for "
                                       f"30 minutes. Stop smelling "
                                       "toast. Only people with small dicks spam chat.")

        # Remove the timeout role after the specified duration
        await asyncio.sleep(1800)  # 30 minutes
        await user.remove_roles(timeout_role)


    async def remove_spam_commands(self, user):
        print("Removing spam commands...")  # Debug print statement

        async for message in user.history(limit=15):
            if message.content.startswith('!'):
                await message.delete()
                print(f"Deleted message from user {user.id}: {message.content}")

        print("Finished removing spam commands.")  # Debug print statement

    @commands.Cog.listener()
    async def on_message(self, message):
        print("on_message event triggered!")
        print(f"Received message from {message.author}: {message.content}")

        if message.author.bot:
            return

        # Check if the message is from the user you want to timeout
        user_id = message.author.id
        if user_id == QUARTERMASTER_ID:
            await message.channel.send("This is a test message from the bot.")
            await message.delete()
            print(f"Deleted message from Quartermaster: {message.content}")

        else:
            print(f"Message is not from the Quartermaster.")

        # Update command usage for the user
        user_id = message.author.id
        await self.check_command_limit(message.author)
        self.command_limits[user_id]['count'] += 1


def setup(client):
    client.add_cog(AdminCogs(client))
    client.add_cog(HelpCog(client))
