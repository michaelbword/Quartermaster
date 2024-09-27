import discord
import random
from discord.ext import commands
from discord.ui import Button, View

class RockPaperScissors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rps", help="Play a game of rock paper scissors with !rps")
    async def rps(self, ctx):
        """
        Starts a Rock-Paper-Scissors game with interactive buttons.
        """
        # Create buttons for Rock, Paper, and Scissors
        button_rock = Button(label="🪨 Rock", style=discord.ButtonStyle.primary, custom_id="rock")
        button_paper = Button(label="📜 Paper", style=discord.ButtonStyle.primary, custom_id="paper")
        button_scissors = Button(label="✂️ Scissors", style=discord.ButtonStyle.primary, custom_id="scissors")

        # Assign callback functions to buttons
        button_rock.callback = lambda interaction: self.play_game(interaction, "rock")
        button_paper.callback = lambda interaction: self.play_game(interaction, "paper")
        button_scissors.callback = lambda interaction: self.play_game(interaction, "scissors")

        # Create a view and add buttons
        view = View()
        view.add_item(button_rock)
        view.add_item(button_paper)
        view.add_item(button_scissors)

        # Send an embed with game instructions
        embed = discord.Embed(title="Rock-Paper-Scissors", description="Click one of the buttons below to play!", color=discord.Color.green())
        await ctx.send(embed=embed, view=view)

    async def play_game(self, interaction: discord.Interaction, player_choice: str):
        """
        Play the Rock-Paper-Scissors game with the user's choice and the bot's random choice.
        """
        bot_choice = random.choice(["rock", "paper", "scissors"])

        # Determine the result of the game
        if player_choice == bot_choice:
            result = "It's a tie!"
            color = discord.Color.yellow()
        elif (player_choice == "rock" and bot_choice == "scissors") or \
             (player_choice == "paper" and bot_choice == "rock") or \
             (player_choice == "scissors" and bot_choice == "paper"):
            result = "You win!"
            color = discord.Color.green()
        else:
            result = "You lose!"
            color = discord.Color.red()

        # Create a result embed
        embed = discord.Embed(title="Rock-Paper-Scissors", color=color)
        embed.add_field(name="Your Choice", value=f"**{self.get_choice_emoji(player_choice)}**", inline=True)
        embed.add_field(name="Bot's Choice", value=f"**{self.get_choice_emoji(bot_choice)}**", inline=True)
        embed.add_field(name="Result", value=result, inline=False)

        # Respond to the interaction with the result
        await interaction.response.send_message(embed=embed, ephemeral=True)

    def get_choice_emoji(self, choice):
        """
        Return the corresponding emoji for rock, paper, or scissors.
        """
        emojis = {
            "rock": "🪨",
            "paper": "📜",
            "scissors": "✂️"
        }
        return emojis.get(choice, "")


async def setup(bot):
    await bot.add_cog(RockPaperScissors(bot))
