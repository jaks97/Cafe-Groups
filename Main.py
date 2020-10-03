import os

import discord
from discord import User, Message, RawReactionActionEvent

from sheets import *

import random

TOKEN = os.getenv('TOKEN')

client = discord.Client()

event_msg_id: int


def garole():
    return next((role for role in guild.roles if role.name == "Giveaway!"), None)  # This is crap


def is_admin(user: User) -> bool:
    return any(role.name == "Moderator" for role in user.roles)  # TODO: Check this role


@client.event
async def on_message(message: Message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!startevent') and is_admin(message.author):
        msg: Message = await message.channel.send("Welcome to our 2nd giveaway! This time we do it a little "
                                                  "different, to participate you need to react to this message. Then "
                                                  "I will send you a link to solve a jigsaw puzzle that will reveal a "
                                                  "password when solved. Send back the password to me via DM and look "
                                                  "back in the discord to find a new channel at the top.")
        await msg.add_reaction("☕")
        global event_msg_id
        event_msg_id = msg.id
        print(event_msg_id)
        f = open('msg', 'wb')
        f.write(event_msg_id.to_bytes(8, 'little'))
        f.close()

    if isinstance(message.channel, discord.DMChannel):
        # Then we are on private message
        entry = sheet.get_entry_for_user(message.author.name)
        if entry is None:
            await message.channel.send("Sorry, I don't understand your message")
            return

        # If we are here, the player has an entry
        if entry.status is EntryStatus.SOLVED:
            # TODO: Check for the role
            await message.channel.send("You already solved the puzzle")
            return

        if message.content == entry.puzzle.password:
            sheet.update_entry_status(message.author.name, EntryStatus.SOLVED)
            await message.channel.send("Congratulations! You solved the puzzle!")
            await guild.get_member(message.author.id).add_roles(garole())
            return

        await message.channel.send("Sorry, the password is incorrect. Please check your message.")


@client.event
async def on_raw_reaction_add(payload: RawReactionActionEvent):
    global event_msg_id
    if payload.guild_id is None:
        return  # Reaction is on a private message
    if payload.message_id == event_msg_id:
        guild = client.get_guild(payload.guild_id)
        user: User = guild.get_member(payload.user_id)
        if user.bot:
            return
        # TODO: Check if user already has puzzle, by checking on the roles
        entry = sheet.get_entry_for_user(user.name)
        if entry is None:
            puzzle = random.choice(sheet.get_puzzles())
            sheet.add_entry(Entry(user.name, puzzle, EntryStatus.SOLVING))
            await user.send("Here's the link to the puzzle: " + puzzle.link)
            await user.send("When solved, a password will be revealed on that site. Reply to me with the password and "
                            "you will be participating")


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    global guild
    guild = client.get_guild(int(os.getenv('GUILD')))
    print("Guild: " + str(guild))
    try:
        f = open('msg', 'rb')
        global event_msg_id
        event_msg_id = int.from_bytes(f.read(), 'little')
        f.close()
    except FileNotFoundError:
        pass


sheet = Sheets()

client.run(TOKEN)
