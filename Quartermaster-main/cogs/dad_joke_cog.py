import requests
from discord.ext import commands


class DadJokeCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def dadjoke(self, ctx):
        joke = self.get_dad_joke()
        await ctx.send(joke)

    def get_dad_joke(self):
        url = "https://icanhazdadjoke.com/"
        response = requests.get(url, headers={"Accept": "text/plain"})
        if response.status_code == 200:
            return response.text
        else:
            return "Sorry, I couldn't fetch a dad joke right now. Please try again later."


async def setup(client):
    await client.add_cog(DadJokeCog(client))
