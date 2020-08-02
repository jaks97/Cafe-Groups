import os
from typing import List, Optional

import discord
from discord import User, Guild, Message, Role, Reaction

from tabulate import tabulate

TOKEN = os.getenv('TOKEN')

client = discord.Client()

event_msg_id: int


def get_groups(roles: List[Role]) -> List[Role]:
    return list(filter(lambda role: role.name.startswith("Group "), roles))[::-1]


def user_group(user: User) -> Optional[Role]:
    return next(iter(get_groups(user.roles)), None)


def next_group(guild: Guild) -> Role:
    groups = get_groups(guild.roles)
    return min(groups, key=lambda group: len(group.members))


def is_admin(user: User) -> bool:
    return any(role.name == "Moderator" for role in user.roles)


def groups_state(guild: Guild) -> str:
    groups: List[Role] = get_groups(guild.roles)
    data = dict(list(map(lambda group: (group.name, group.members), groups)))
    tab = tabulate(data, headers="keys", tablefmt="fancy_grid", stralign="center")
    return tab


@client.event
async def on_message(message: Message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!test'):
        await message.channel.send("```This is a test message\n"
                                   "Many lines?\n"
                                   "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa```")

    if message.content.startswith('!startevent') and is_admin(message.author):
        msg: Message = await message.channel.send("React to this message to get added into a group")
        await msg.add_reaction("😃")
        global event_msg_id
        event_msg_id = msg.id

    if message.content.startswith('!status') and is_admin(message.author):
        msg: Message = await message.channel.send("```" + groups_state(message.guild) + "```")

    if message.content.startswith('!purge') and is_admin(message.author):
        for group in get_groups(message.guild.roles):
            for member in group.members:
                await member.remove_roles(group)
        await message.channel.send("All the groups have been cleaned")


@client.event
async def on_reaction_add(reaction: Reaction, user: User):
    global event_msg_id
    if not user.bot and reaction.message.id == event_msg_id:
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
