import discord
from discord.ext import commands
from role_assignment import assign_role

class CodCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def handle_build_command(self, parts, message):
        if len(parts) >= 2:
            gun_name = ' '.join(parts[1:])
            print(f"Requested gun name: {gun_name}")
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
        else:
            await message.channel.send('Usage: !build <gun_name>')

    @commands.command()
    async def build(self, ctx, *, gun_name):
        print(f"Requested gun name: {gun_name}")
        await self.handle_build_command(gun_name.split(' '), ctx.message)

def setup(client):
    client.add_cog(CodCog(client))