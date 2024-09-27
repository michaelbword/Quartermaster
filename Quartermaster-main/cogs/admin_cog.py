import asyncio
import datetime
import os
import logging
import json

import discord
from discord.ext import commands
from dotenv import load_dotenv

from scripts.role_assignment import assign_role

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from the file
load_dotenv('../config/environment.env')

QUARTERMASTER_ID = os.getenv("QUARTERMASTER_ID")


class AdminCogs(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.command_limits = {}
        self.role_message_id = None
        self.role_channel_id = None

        # Load message_id and channel_id from the persistent storage
        self.load_role_message_data()

    def load_role_message_data(self):
        try:
            with open('role_message.json', 'r') as f:
                data = json.load(f)
                self.role_message_id = data['role_message_id']
                self.role_channel_id = data['role_channel_id']
                logging.info(f"Loaded role message ID: {self.role_message_id} and channel ID: {self.role_channel_id}")
        except FileNotFoundError:
            logging.warning("No previous role message found. You might need to resend the roles command.")
        except json.JSONDecodeError:
            logging.error("Error decoding role_message.json. Please check the file content.")

    def save_role_message_data(self):
        with open('role_message.json', 'w') as f:
            json.dump({'role_message_id': self.role_message_id, 'role_channel_id': self.role_channel_id}, f)
            logging.info(f"Saved role message ID: {self.role_message_id} and channel ID: {self.role_channel_id}")

    # Add the embed here with the value of the role name. Must match precisely.
    @commands.command()
    async def roles(self, ctx):
        logging.info('Roles command triggered!')
        embed = discord.Embed(title="React with the corresponding emoji to get the role:")
        embed.add_field(name="🍆", value="NSFW", inline=False)
        embed.add_field(name="🎥", value="Streamer", inline=False)
        embed.add_field(name="🩸", value="Dead By Daylight", inline=False)
        embed.add_field(name="🔫", value="Hunt", inline=False)
        embed.add_field(name="🌌", value="Destiny", inline=False)

        message = await ctx.send(embed=embed)
        await message.add_reaction("🍆")
        await message.add_reaction("🎥")
        await message.add_reaction("🩸")
        await message.add_reaction("🔫")
        await message.add_reaction("🌌")

        # Store the message ID and channel ID to identify reactions later
        self.role_message_id = message.id
        self.role_channel_id = message.channel.id
        self.save_role_message_data()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # Check if the message ID matches
        if payload.message_id != self.role_message_id:
            return

        guild = self.client.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        # Add role name and emojii for each channel you want to update
        role_name = None
        if payload.emoji.name == "🍆":
            role_name = "NSFW"
        elif payload.emoji.name == "🎥":
            role_name = "Streamer"
        elif payload.emoji.name == "🩸":
            role_name = "Dead By Daylight"
        elif payload.emoji.name == "🔫":
            role_name = "Hunt"
        elif payload.emoji.name == "🌌":
            role_name = "Destiny"

        if role_name:
            try:
                await assign_role(member, role_name)
                logging.info(f"Assigned {role_name} role to {member.display_name}.")
            except discord.Forbidden:
                logging.error(
                    f"Failed to assign {role_name} role to {member.display_name} due to insufficient permissions.")
            except discord.HTTPException as e:
                logging.error(f"Failed to assign {role_name} role to {member.display_name}. HTTPException: {e}")


    async def remove_spam_commands(self, user):
        logging.info("Removing spam commands...")

        async for message in user.history(limit=15):
            if message.content.startswith('!'):
                await message.delete()
                logging.info("Deleted message from user %s: %s", user.id, message.content)

        logging.info("Finished removing spam commands.")


async def setup(client):
    await client.add_cog(AdminCogs(client))
