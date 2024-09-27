import random

from discord.ext import commands


class InitiativeCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def roll(self, ctx):
        # Simulate rolling a 20-sided die for initiative
        initiative_roll = random.randint(1, 20)
        await ctx.send(f"You rolled a {initiative_roll}!")


async def setup(client):
    await client.add_cog(InitiativeCog(client))
