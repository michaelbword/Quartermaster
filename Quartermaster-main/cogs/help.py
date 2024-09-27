import discord
from discord.ext import commands
from discord.ui import Button, View


class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        """Displays all available cogs and their commands."""
        user = self.context.author
        is_admin = user.guild_permissions.administrator

        embed = discord.Embed(title="Bot Commands", description="Here are the available commands:",
                              color=discord.Color.blue())

        # Iterate through all cogs and their commands
        for cog, command_list in mapping.items():
            # Filter commands based on is_admin attribute
            filtered_commands = [command for command in command_list if
                                 not getattr(command, 'is_admin', False) or is_admin]

            if cog and filtered_commands:
                # Join the list of commands with their docstring help or "No description"
                commands_desc = "\n".join(
                    [f"`{command.name}`: {command.help or 'No description'}" for command in filtered_commands]
                )
                if commands_desc:
                    embed.add_field(name=f"**{cog.qualified_name}**", value=commands_desc, inline=False)

        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        """Displays all commands for a specific cog."""
        user = self.context.author
        is_admin = user.guild_permissions.administrator

        embed = discord.Embed(title=f"{cog.qualified_name} Commands", description=cog.description or "No description",
                              color=discord.Color.green())

        # Filter commands based on is_admin attribute
        for command in cog.get_commands():
            if not getattr(command, 'is_admin', False) or is_admin:
                embed.add_field(name=f"`{command.name}`", value=command.help or "No description", inline=False)

        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        """Displays help for a single command."""
        embed = discord.Embed(title=f"Command: {command.name}", description=command.help or "No description",
                              color=discord.Color.purple())
        embed.add_field(name="**Usage**", value=f"`{command.usage}`" if command.usage else "No usage specified",
                        inline=False)

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        """Displays help for a command group."""
        embed = discord.Embed(title=f"Group: {group.name}", description=group.help or "No description",
                              color=discord.Color.orange())
        embed.add_field(name="**Usage**", value=f"`{group.usage}`" if group.usage else "No usage specified",
                        inline=False)

        for command in group.commands:
            embed.add_field(name=f"`{command.name}`", value=command.help or "No description", inline=False)

        await self.get_destination().send(embed=embed)


class HelpCog(commands.Cog):
    """Cog for the custom help command."""

    def __init__(self, bot):
        self._bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = CustomHelpCommand()
        bot.help_command.cog = self

    async def cog_unload(self):
        """Restores the original help command when this cog is unloaded."""
        self._bot.help_command = self._original_help_command


async def setup(bot):
    """Loads the HelpCog."""
    await bot.add_cog(HelpCog(bot))
