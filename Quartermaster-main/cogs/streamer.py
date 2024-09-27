import asyncio
import json
import os

import aiohttp
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../config/environment.env')

class StreamersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client_id = os.getenv('client_id')
        self.client_secret = os.getenv('client_secret')
        self.streamers = self.load_streamers()
        self.oauth_token = None
        self.notified_streams = set()  # Set to keep track of notified streams



    def load_streamers(self):
        # Load streamers from a JSON file
        try:
            with open('../config/streamers.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    async def get_oauth_token(self):
        token_url = 'https://id.twitch.tv/oauth2/token'
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        print("Requesting OAuth token...")  # Logging
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, params=params) as response:
                print(f"Response Status: {response.status}")  # Logging
                if response.status == 200:
                    data = await response.json()
                    self.oauth_token = data['access_token']
                    print(f"Obtained OAuth token: {self.oauth_token}")
                else:
                    response_text = await response.text()
                    print(f"Failed to obtain OAuth token: {response_text}")
                    return None

    async def is_stream_live(self, twitch_url):
        # Extract the username from the Twitch URL
        if 'twitch.tv/' in twitch_url:
            twitch_username = twitch_url.split('twitch.tv/')[-1]
        else:
            # Handle cases where the URL does not follow the expected format
            print(f"Invalid Twitch URL format: {twitch_url}")
            return False

        twitch_username = twitch_username.lower()

        url = 'https://api.twitch.tv/helix/streams'
        params = {'user_login': twitch_username}
        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.oauth_token}',
            'Content-Type': 'application/json',
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"API Response for {twitch_username}: {data}")  # Logging
                    return len(data['data']) > 0
                else:
                    print(f"Failed to check stream status for {twitch_username}: {await response.text()}")
                    return False

    async def notify_stream_status(self, channel, twitch_username):
        message = f'@everyone {twitch_username} is now live on Twitch! Check it out: https://www.twitch.tv/{twitch_username}'
        await channel.send(message)

    async def check_stream_status(self, channel):
        while True:
            for twitch_url in self.streamers.values():
                # Ensure twitch_url is a string
                twitch_url = twitch_url[0] if isinstance(twitch_url, list) else twitch_url
                twitch_username = twitch_url.split('/')[-1].lower()

                if await self.is_stream_live(twitch_url):
                    if twitch_username not in self.notified_streams:
                        await self.notify_stream_status(channel, twitch_username)
                        self.notified_streams.add(twitch_username)
                else:
                    if twitch_username in self.notified_streams:
                        # Streamer goes offline, remove from notified_streams to reset notification
                        self.notified_streams.remove(twitch_username)

            await asyncio.sleep(60)  # Check every 60 seconds

    @commands.command()
    async def addstreamer(self, ctx, twitch_url):
        discord_user_id = str(ctx.author.id)

        if discord_user_id in self.streamers:
            await ctx.send(f'You have already stored a streamer: {self.streamers[discord_user_id]}')
        else:
            self.streamers[discord_user_id] = twitch_url  # Storing as a string
            with open('../config/streamers.json', 'w') as file:
                json.dump(self.streamers, file)
            await ctx.send(f'Streamer {twitch_url} added.')

    @commands.command()
    async def removestreamer(self, ctx, twitch_username):
        if twitch_username in self.streamers:
            del self.streamers[twitch_username]
            with open('../config/streamers.json', 'w') as file:
                json.dump(self.streamers, file)
            await ctx.send(f'Streamer {twitch_username} removed.')
        else:
            await ctx.send(f'Streamer {twitch_username} not found.')

async def setup(client):
    await client.add_cog(StreamersCog(client))