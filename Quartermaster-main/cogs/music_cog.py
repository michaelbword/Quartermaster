import asyncio
import logging
import os
import random
from asyncio import Lock

import discord
import googleapiclient.discovery
import yt_dlp
from discord.ext import commands
from dotenv import load_dotenv

# Basic logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv('../config/environment.env')
google_api = os.getenv("google_api")


def in_channel_or_admin(channel_id):
    def predicate(ctx):
        return ctx.channel.id == channel_id or ctx.author.guild_permissions.administrator
    return commands.check(predicate)


class MusicCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.voice_clients = {}
        self.queues = {}
        self.loop = asyncio.get_event_loop()
        self.file_lock = Lock()  # Add a lock for file operations

    async def ensure_voice(self, ctx):
        guild_id = ctx.guild.id
        if guild_id not in self.voice_clients or not self.voice_clients[guild_id].is_connected():
            if ctx.author.voice:
                voice_client = await ctx.author.voice.channel.connect()
                self.voice_clients[guild_id] = voice_client  # Ensure the client is saved
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        return self.voice_clients[guild_id]

    async def play_next(self, ctx):
        guild_id = ctx.guild.id
        if guild_id in self.queues and self.queues[guild_id]:
            if not self.queues[guild_id]:  # Check if queue is empty before popping
                await ctx.send("The queue is empty.")
                # Disconnect if the queue is empty
                voice_client = self.voice_clients.get(guild_id)
                if voice_client:
                    await voice_client.disconnect()
                    del self.voice_clients[guild_id]  # Remove the client after disconnecting
                return

            next_song = self.queues[guild_id].pop(0)
            await self.play_youtube(ctx, next_song)
        else:
            voice_client = self.voice_clients.get(guild_id)
            if voice_client:
                await voice_client.disconnect()
                del self.voice_clients[guild_id]  # Properly handle deletion after disconnect
            await ctx.send("The queue is empty and the bot has disconnected from the voice channel.")

    async def play_youtube(self, ctx, song):
        async with self.file_lock:  # Lock to ensure exclusive access to the file
            voice_client = await self.ensure_voice(ctx)
            if voice_client.is_playing():
                await ctx.send("Already playing audio. Please wait or use the queue command.")
                return  # Stop execution if something is already playing

            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'opus',
                    'preferredquality': '128',
                }],
                'outtmpl': f'audio_cache/{ctx.guild.id}.%(ext)s',
            }

            # Corrected file extension to match postprocessor output
            audio_path = f'audio_cache/{ctx.guild.id}.opus'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(song, download=True)  # Download the song

            try:
                def after_playback(error):
                    if error:
                        logger.error(f"Playback error: {error}")
                    try:
                        os.remove(audio_path)  # Try to delete the file after playback
                    except Exception as e:
                        logger.error(f"Failed to delete audio file: {e}")

                    asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.loop)

                # Play the downloaded file
                voice_client.play(discord.FFmpegPCMAudio(audio_path), after=after_playback)
                await ctx.send(f'Now playing: {info["title"]}')
            except Exception as e:
                logger.error(f"An error occurred in play_youtube: {e}")
                try:
                    os.remove(audio_path)  # Ensure file is deleted even if an error occurs
                except Exception as ex:
                    logger.error(f"Failed to delete audio file: {ex}")
                await self.play_next(ctx)

    def is_playlist_url(self, url: str) -> bool:
        return 'list=' in url

    async def handle_playlist(self, ctx, url):
        guild_id = ctx.guild.id
        if guild_id not in self.queues:
            self.queues[guild_id] = []  # Initialize the queue if it doesn't exist

        ydl_opts = {
            'quiet': True,
            'noplaylist': False,
            'extract_flat': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=False)
            if 'entries' in result:
                for entry in result['entries']:
                    if 'id' in entry:
                        video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                        self.queues[guild_id].append(video_url)
                if not self.queues[guild_id]:
                    await ctx.send("No songs found in the playlist.")
                else:
                    await ctx.send(f"Added {len(self.queues[guild_id])} songs to the queue.")
                    await self.play_next(ctx)
            else:
                await ctx.send("Failed to retrieve playlist information.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clearqueue(self, ctx):
        guild_id = ctx.guild.id
        if guild_id in self.queues:
            self.queues[guild_id].clear()
            await ctx.send("Queue cleared.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def skip(self, ctx):
        guild_id = ctx.guild.id
        if guild_id in self.voice_clients and self.voice_clients[guild_id].is_playing():
            self.voice_clients[guild_id].stop()
            await self.play_next(ctx)
        else:
            await ctx.send('No audio is playing.')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def pause(self, ctx):
        guild_id = ctx.guild.id
        if guild_id in self.voice_clients and self.voice_clients[guild_id].is_playing():
            self.voice_clients[guild_id].pause()
            await ctx.send("Audio paused.")
        else:
            await ctx.send("No audio is playing.")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def shuffle(self, ctx):
        """Shuffles the queue."""
        guild_id = ctx.guild.id
        if guild_id in self.queues and self.queues[guild_id]:
            random.shuffle(self.queues[guild_id])
            await ctx.send("Queue has been shuffled.")
        else:
            await ctx.send("The queue is empty.")
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def resume(self, ctx):
        guild_id = ctx.guild.id
        if guild_id in self.voice_clients and self.voice_clients[guild_id].is_paused():
            self.voice_clients[guild_id].resume()
            await ctx.send("Audio resumed.")
        else:
            await ctx.send("Audio is not paused or no audio is playing.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def stop(self, ctx):
        guild_id = ctx.guild.id
        if guild_id in self.voice_clients:
            self.voice_clients[guild_id].stop()
            if guild_id in self.queues:
                self.queues[guild_id].clear()
            await ctx.send("Playback stopped and queue cleared.")
        else:
            await ctx.send("No audio is playing.")

    @commands.command()
    @in_channel_or_admin(1163007525587796008)  # Replace with your specific channel ID
    async def play(self, ctx, *, url):
        guild_id = ctx.guild.id

        # Ensure the voice client exists and is connected; create/connect if necessary
        voice_client = await self.ensure_voice(ctx)
        if not voice_client:
            return  # Stop if we can't connect to a voice channel

        # Check if URL is a playlist
        if self.is_playlist_url(url):
            ydl_opts = {
                'quiet': True,
                'noplaylist': False,
                'extract_flat': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(url, download=False)
                if 'entries' in result:
                    track_count = len(result['entries'])
                    await ctx.send(
                        f"This playlist contains {track_count} tracks. Do you want to add all of them to the queue? (yes/no)")

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['yes',
                                                                                                             'no']

                    try:
                        reply = await self.client.wait_for('message', check=check, timeout=30.0)
                        if reply.content.lower() == 'yes':
                            await self.handle_playlist(ctx, url)
                        else:
                            await ctx.send("Playlist addition canceled.")
                    except asyncio.TimeoutError:
                        await ctx.send("You didn't reply in time. Playlist addition canceled.")
                else:
                    await ctx.send("Failed to retrieve playlist information.")
        else:
            if guild_id not in self.queues:
                self.queues[guild_id] = []
            self.queues[guild_id].append(url)

        # Only start playing if nothing is currently playing
        if not voice_client.is_playing() and not voice_client.is_paused():
            await ctx.send(f"Starting playback.")
            await self.play_next(ctx)
        else:
            await ctx.send(f"Added to queue. There are now {len(self.queues[guild_id])} track(s) in the queue.")

    @commands.command()
    async def showqueue(self, ctx):
        guild_id = ctx.guild.id
        if guild_id in self.queues and self.queues[guild_id]:
            queue_str = '\n'.join([f'{index + 1}. {song}' for index, song in enumerate(self.queues[guild_id])])
            await ctx.send(f"Current Queue:\n{queue_str}")
        else:
            await ctx.send("The queue is currently empty.")


    @commands.command(name='fix')
    @commands.has_permissions(administrator=True)  # Ensure only administrators can use this command for safety.
    async def fix(self, ctx):
        guild_id = ctx.guild.id
        voice_client = self.voice_clients.get(guild_id, None)

        # Check if the bot is connected to a voice channel.
        if voice_client is None or not voice_client.is_connected():
            await ctx.send("The bot is not connected to a voice channel. Attempting to connect...")
            await self.ensure_voice(ctx)  # Attempt to connect to the voice channel.

        # If something is already playing, try to resume it.
        if voice_client.is_paused():
            await ctx.send("Resuming paused audio...")
            voice_client.resume()
        elif not voice_client.is_playing() and guild_id in self.queues and len(self.queues[guild_id]) > 0:
            await ctx.send("Attempting to play the next song in the queue...")
            await self.play_next(ctx)
        else:
            await ctx.send("No audio is paused and the queue is empty. Nothing to fix.")

    @commands.command()
    async def search(self, ctx, *, query):
        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=google_api)
        request = youtube.search().list(q=query, part="snippet", type="video", maxResults=5)
        response = request.execute()

        results = [(video['id']['videoId'], video['snippet']['title']) for video in response['items']]
        search_results = '\n'.join([f'{index + 1}. {title}' for index, (videoId, title) in enumerate(results)])
        await ctx.send("Search results:\n" + search_results)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            reply = await self.client.wait_for('message', check=check, timeout=30.0)
            choice = int(reply.content) - 1
            selected_video_id = results[choice][0]
            selected_video_url = f"https://www.youtube.com/watch?v={selected_video_id}"
            if ctx.guild.id not in self.queues:
                self.queues[ctx.guild.id] = []
            self.queues[ctx.guild.id].append(selected_video_url)
            await ctx.send(f"Added to queue: {results[choice][1]}")
            if not ctx.voice_client or not ctx.voice_client.is_playing():
                await self.play_next(ctx)
        except asyncio.TimeoutError:
            await ctx.send("You didn't reply in time!")
        except (IndexError, ValueError):
            await ctx.send("Invalid selection.")


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            missing = [perm.replace('_', ' ').title() for perm in error.missing_permissions]
            missing_perms_str = ', '.join(missing)
            await ctx.send(
                f"You are missing the following permissions required to run this command: {missing_perms_str}")
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("You can't use this command in this channel or you lack the required permissions.")
        else:
            logger.error(f"Unhandled command error: {error}")


async def setup(client):
    await client.add_cog(MusicCog(client))
