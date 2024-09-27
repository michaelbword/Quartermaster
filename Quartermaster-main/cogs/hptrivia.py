import discord
from discord.ext import commands
from discord.ui import Button, View
import random
import os
import json
import logging

# Set up logging for better debugging
logging.basicConfig(level=logging.INFO)

# File paths for questions and scores
config_folder = os.path.join(os.path.dirname(__file__), '..', 'config')
questions_file_path = os.path.join(config_folder, 'questions.json')
scores_file_path = os.path.join(config_folder, 'hpscores.json')

# Load trivia questions from JSON with proper UTF-8 encoding
with open(questions_file_path, 'r', encoding='utf-8') as f:
    trivia_data = json.load(f)

# Load existing scores from the scores file or initialize an empty dictionary if the file doesn't exist or is empty
if os.path.exists(scores_file_path):
    try:
        with open(scores_file_path, 'r', encoding='utf-8') as f:
            player_scores = json.load(f)
            if not isinstance(player_scores, dict):
                player_scores = {}
    except json.JSONDecodeError:
        logging.error("hpscores.json is empty or invalid. Initializing a new score dictionary.")
        player_scores = {}
else:
    player_scores = {}

# Helper function to save scores to the JSON file
def save_scores():
    with open(scores_file_path, 'w', encoding='utf-8') as f:
        json.dump(player_scores, f, indent=4)
    logging.info("Scores have been saved to hpscores.json")

# Button class for each trivia answer
class TriviaButton(Button):
    def __init__(self, label, correct_answer, player):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.correct_answer = correct_answer
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        logging.info(f"Button pressed: {self.label}, correct answer: {self.correct_answer}")

        if interaction.user != self.player:
            await interaction.response.send_message("This trivia isn't for you!", ephemeral=True)
            logging.info(f"Interaction from wrong user: {interaction.user}. Expected: {self.player}")
            return

        if self.label == self.correct_answer:
            response = "Correct! 🎉"
            player_scores[self.player.id] = player_scores.get(self.player.id, 0) + 1
            save_scores()  # Save updated score to the JSON file
            logging.info(f"Correct answer. {self.player.name}'s new score: {player_scores[self.player.id]}")
        else:
            response = f"Incorrect. The correct answer was **{self.correct_answer}**."
            logging.info(f"Incorrect answer. {self.player.name} answered: {self.label}")

        # Disable all buttons after interaction
        for item in self.view.children:
            item.disabled = True

        # Respond to the interaction with the result
        if not interaction.response.is_done():
            await interaction.response.send_message(response, ephemeral=True)
        else:
            # Fallback in case the interaction has already been responded to
            await interaction.followup.send(response, ephemeral=True)

        # Announce the player's current score publicly
        await self.view.ctx.send(f"**{self.player.name}** now has {player_scores[self.player.id]} points!")


# View class that holds all buttons for a trivia question
class TriviaView(View):
    def __init__(self, ctx, question, player):
        super().__init__(timeout=30)  # Timeout for interaction
        self.ctx = ctx
        self.player = player

        # Get the correct answer and shuffle answers for display
        answers = trivia_data[question]
        correct_answer = answers[0]  # First one is always the correct answer

        random.shuffle(answers)  # Shuffle for random button order
        logging.info(f"Question: {question}, shuffled answers: {answers}")

        # Create buttons for each answer, and add them to the view
        for answer in answers:
            button = TriviaButton(label=answer, correct_answer=correct_answer, player=player)
            self.add_item(button)
        logging.info(f"Created buttons for question: {question}")


# Button to refresh the leaderboard using an emoji
class RefreshButton(Button):
    def __init__(self, leaderboard_embed, ctx):
        super().__init__(emoji="🔄", style=discord.ButtonStyle.secondary)
        self.leaderboard_embed = leaderboard_embed
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        # Rebuild the leaderboard message
        self.update_leaderboard_embed()

        # Edit the original message to update the embed
        await interaction.message.edit(embed=self.leaderboard_embed)

        # Optionally, acknowledge the interaction
        await interaction.response.send_message("Leaderboard updated!", ephemeral=True)

    def update_leaderboard_embed(self):
        """Update the leaderboard embed content."""
        sorted_leaderboard = sorted(player_scores.items(), key=lambda x: x[1], reverse=True)
        leaderboard_content = "\n".join([f"<@{player_id}>: {score} points" for player_id, score in sorted_leaderboard])

        if not leaderboard_content:
            leaderboard_content = "No scores yet!"

        # Update the embed fields
        self.leaderboard_embed.clear_fields()
        self.leaderboard_embed.add_field(name="Trivia Leaderboard", value=leaderboard_content)


# View class to hold the refresh button
class LeaderboardView(View):
    def __init__(self, leaderboard_embed, ctx):
        super().__init__(timeout=None)  # The view doesn't time out
        # Add the refresh emoji button
        self.add_item(RefreshButton(leaderboard_embed, ctx))


# The trivia cog containing the trivia commands
class TriviaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="trivia", help="Starts a Harry Potter trivia game.")
    async def trivia(self, ctx):
        """Starts a Harry Potter trivia game for the player."""
        try:
            logging.info("Trivia command triggered.")
            player = ctx.author
            question = random.choice(list(trivia_data.keys()))
            logging.info(f"Selected question: {question} for player: {player}")

            # Send the trivia question with buttons for answers
            view = TriviaView(ctx, question, player)
            await ctx.send(f"**{player.name}**, here’s your trivia question:\n\n**{question}**", view=view)
        except Exception as e:
            logging.error(f"Error in trivia command: {e}")
            await ctx.send("Something went wrong with the trivia game. Please try again.")

    @commands.command(name="score", help="Check your or another player's trivia score.")
    async def score(self, ctx, member: discord.Member = None):
        """Check your or another player's trivia score."""
        member = member or ctx.author
        score = player_scores.get(member.id, 0)
        logging.info(f"Score check for {member}: {score}")
        await ctx.send(f"**{member.name}**'s current score is: **{score}**")

    @commands.command(name="leaderboard", help="Displays the trivia leaderboard.")
    async def leaderboard(self, ctx):
        """Displays the trivia leaderboard."""
        logging.info("Leaderboard command triggered.")

        # Generate the initial leaderboard content
        sorted_leaderboard = sorted(player_scores.items(), key=lambda x: x[1], reverse=True)
        leaderboard_content = "\n".join([f"<@{player_id}>: {score} points" for player_id, score in sorted_leaderboard])

        if not leaderboard_content:
            leaderboard_content = "No scores yet!"

        # Create an embed for the leaderboard
        leaderboard_embed = discord.Embed(
            title="Trivia Leaderboard",
            description=leaderboard_content,
            color=discord.Color.blue()
        )

        # Create a view that includes the refresh button
        view = LeaderboardView(leaderboard_embed, ctx)

        # Send the embed and the refresh button
        await ctx.send(embed=leaderboard_embed, view=view)


# Register the cog with the bot
async def setup(bot):
    await bot.add_cog(TriviaCog(bot))
