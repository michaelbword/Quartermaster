import discord


async def assign_role(member, role_name):
    # Implement your logic to assign a role to a member based on role_name
    # Fetch the guild
    guild = member.guild

    # Find the role by name
    role = discord.utils.get(guild.roles, name=role_name)
    if role:
        await member.add_roles(role)
        await member.send(f"You now have the {role_name} role.")
    else:
        await member.send(f"Role {role_name} not found.")


