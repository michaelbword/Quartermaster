import os
import discord
from dotenv import load_dotenv
from role_assignment import assign_role
from web_scraper import get_attachment_names

# Define the function to set up the Discord bot
def setup_discord_bot():
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)

    @client.event
    async def on_member_join(member):
        # Load environment variables from the file
        load_dotenv('environment.env')  # Adjust the filename if needed

        # Get the bot token from an environment variable
        channel_id = os.getenv('channel_id')
        channel = client.get_channel(channel_id)
        if channel:
            # Fetch the member you want to mention
            existing_member = discord.utils.get(member.guild.members, name='wordofkylar')

        if channel:
            welcome_message = f"Welcome to fun times, {member.mention}! {existing_member.mention} gets a blowey!"
            await channel.send(welcome_message)

    @client.event
    async def on_ready():
        print(f'Logged in as {client.user}')

    @client.event
    async def on_reaction_add(reaction, user):
        message = reaction.message
        if user.bot:
            return

        if message.author == client.user:  # Ensure the message is sent by the bot
            # Check the emoji and assign the role accordingly
            if str(reaction.emoji) == "1️⃣":
                role = discord.utils.get(user.guild.roles, name="NSFW")
                await user.add_roles(role)
                await user.send("You have been assigned NSFW. Let's get frisky ;)")
            elif str(reaction.emoji) == "2️⃣":
                role = discord.utils.get(user.guild.roles, name="Streamer")
                await user.add_roles(role)
                await user.send("You have been assigned Streamer.")

    @client.event
    async def on_message(message):
        if message.content.startswith('!meta'):
            gun_name = message.content[6:].strip()
            print(f"Requested gun name: {gun_name}")

            # Process gun name as needed (e.g., fetching attachments)
            attachment_info = await get_attachment_names(gun_name)
            if attachment_info:
                # Force everything to title case
                formatted_gun_name = gun_name.title()
                formatted_attachment_info = '\n'.join(
                    line.title() for line in attachment_info)  # Force everything to title case

                response_message = f"Attachments for {formatted_gun_name}:\n{formatted_attachment_info}"
                print(f"Response message: {response_message}")
                await message.channel.send(response_message)
            else:
                await message.channel.send(f"Gun information for {gun_name} not found.")


    @client.event
    async def on_message(message):
        if message.content.startswith('!'):
            command = message.content[1:]  # Remove the '!' prefix
            parts = command.split(' ')
            if parts[0] == 'role':
                # Check if the user wants to assign a role
                if len(parts) >= 2:
                    role_name = ' '.join(parts[1:])
                    await assign_role(message.author, role_name)
                else:
                    await message.channel.send('Usage: !role <role_name>')

    return client

# Run the setup function to get the client and set up the event handlers
client = setup_discord_bot()
