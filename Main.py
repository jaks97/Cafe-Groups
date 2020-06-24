import os
from typing import List, Optional

import discord
from discord import User, Guild, Message, Role, Reaction

TOKEN = os.getenv('TOKEN')

client = discord.Client()


def get_groups(roles: List[Role]) -> List[Role]:
    return list(filter(lambda role: role.name.startswith("Group "), roles))[::-1]


def user_group(user: User) -> Optional[Role]:
    return next(iter(get_groups(user.roles)), None)


def next_group(guild: Guild) -> Role:
    groups = get_groups(guild.roles)
    return min(groups, key=lambda group: len(group.members))


def is_admin(user: User) -> bool:
    return any(role.name == "Moderator" for role in user.roles)


@client.event
async def on_message(message: Message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!test'):
        await message.channel.send("This is a test message")

    if message.content.startswith('!purge') and is_admin(message.author):
        for group in get_groups(message.guild.roles):
            for member in group.members:
                await member.remove_roles(group)
        await message.channel.send("All the groups have been cleaned")


@client.event
async def on_reaction_add(reaction: Reaction, user: User):
    if user_group(user) is not None:
        await reaction.message.channel.send(user.mention + " You already are part of " + user_group(user).name)
        return
    role = next_group(user.guild)
    await user.add_roles(role)
    await reaction.message.channel.send(user.mention + " You reacted to the test message and got added to " + role.name)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(TOKEN)
