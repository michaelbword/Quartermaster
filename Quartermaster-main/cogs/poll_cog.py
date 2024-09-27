import discord
from discord.ext import commands
from discord.ui import Button, View


class PollView(View):
    def __init__(self, options):
        super().__init__(timeout=None)
        self.poll_options = {option: 0 for option in options}
        self.voters = set()
        for option in options:
            button = Button(label=option, style=discord.ButtonStyle.primary)
            button.callback = self.make_callback(option)
            self.add_item(button)

    def make_callback(self, option):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id in self.voters:
                await interaction.response.send_message("You have already voted.", ephemeral=True)
            else:
                self.poll_options[option] += 1
                self.voters.add(interaction.user.id)
                await interaction.response.send_message(f"You voted for **{option}**.", ephemeral=True)

        return callback


class PollCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_polls = {}

    @commands.command()
    async def poll(self, ctx, question: str, *options):
        """Create a poll with up to five options.
        Usage: !poll "Question" "Option1" "Option2" ..."""
        if len(options) < 2:
            await ctx.send("You need at least two options to create a poll.")
            return
        if len(options) > 5:
            await ctx.send("You can have a maximum of five options.")
            return

        view = PollView(options)
        embed = discord.Embed(
            title="📊 " + question,
            description="\n".join([f"{i + 1}. {option}" for i, option in enumerate(options)]),
            color=0x00FF00
        )
        message = await ctx.send(embed=embed, view=view)
        self.active_polls[message.id] = view

    @commands.command()
    async def poll_results(self, ctx, message_id: int):
        """Display the results of a poll.
        Usage: !poll_results message_id"""
        if message_id not in self.active_polls:
            await ctx.send("Poll not found or has expired.")
            return
        view = self.active_polls[message_id]
        results = "\n".join([f"**{option}**: {count} vote(s)" for option, count in view.poll_options.items()])
        await ctx.send(f"**Poll Results:**\n{results}")


async def setup(client):
    await client.add_cog(PollCog(client))
