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


def next_group(guild: Guild):
    groups = get_groups(guild.roles)
    return min(groups, key=lambda group: len(group.members))


@client.event
async def on_message(message: Message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!test'):
        await message.channel.send("This is a test message")


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
