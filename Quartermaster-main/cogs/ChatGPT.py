import os
from discord.ext import commands
from openai import OpenAI

class ChatGPTCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.contexts = {}  # Dictionary to store conversation contexts for each channel

    def update_context(self, channel_id, message):
        """Update the conversation context for a specific channel."""
        if channel_id not in self.contexts:
            self.contexts[channel_id] = []
        self.contexts[channel_id].append(message)
        self.contexts[channel_id] = self.contexts[channel_id][-5:]  # Keep only the last 5 messages

    async def process_query(self, channel, prompt):
        """Process a query using OpenAI and send the response to the channel."""
        channel_id = channel.id
        self.update_context(channel_id, {"role": "user", "content": prompt})

        messages = self.contexts.get(channel_id, [])
        try:
            response = self.openai_client.chat.completions.create(
                messages=messages,
                model="gpt-4-turbo"
            )
            reply = response.choices[0].message.content

            self.update_context(channel_id, {"role": "assistant", "content": reply})

            if len(reply) > 2000:
                reply = reply[:1997] + '...'

            await channel.send(reply)
        except Exception as e:
            await channel.send(f"An error occurred: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen to messages and process them if they start with 'Quartermaster,'."""
        if message.author == self.client.user or message.content.startswith(self.client.command_prefix):
            return

        if message.content.lower().startswith('quartermaster,'):
            prompt = message.content[len('Quartermaster,'):].strip()
            await self.process_query(message.channel, prompt)

# Ensure this method exists in each cog
async def setup(client):
    await client.add_cog(ChatGPTCog(client))
