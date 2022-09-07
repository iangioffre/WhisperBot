import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import get

import json
import os
import re
from dotenv import load_dotenv

###########################################
#            COMMANDS (*admin)            #
###########################################
# *test - sends message back to say it's working
# *roles - prints reaction object
# *clear_roles - clears all role-reaction relationships
# *create_role - creates a message with role-reaction inputs
# *edit_role - edits a given message with role-reaction inputs
# *add_role - adds to given message with role-reaction inputs

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

intents = discord.Intents.default()  # Allow the use of custom intents
intents.members = True
# intents.messages = True
# intents.reactions = True

####################
#      GLOBAL      #
####################
bot = commands.Bot(command_prefix='$', intents=intents)

g_reactions = {}
files_path = 'files/'
reactions_file_name = files_path + 'reactions.json'

####################
#     COMMANDS     #
####################

@commands.has_permissions(administrator=True)
@bot.command()
async def test(ctx):
    await ctx.send('Message receieved')

@commands.has_permissions(administrator=True)
@bot.command()
async def roles(ctx):
    print(g_reactions)
    await ctx.send(g_reactions)

@commands.has_permissions(administrator=True)
@bot.command()
async def clear_roles(ctx):
    global g_reactions
    print("Clearing all roles")
    g_reactions = {}
    write_reactions_to_file()
    await ctx.send("All roles cleared")

@commands.has_permissions(administrator=True)
@bot.command()
async def create_role(ctx, *args):
    """Create a message and add reactions to the message
    Format: $create_role [optional:channel_id] [role1] [reaction1] [role2] [reaction2] ...
    """
    role_map = []
    send_message_context = ctx

    start = 0
    if args[0].isnumeric(): # channel_id to send message in
        start = 1
        send_message_context = ctx.guild.get_channel(int(args[0]))

    # get message args into array of tuples
    for i in range(start, len(args), 2):
        role_map.append((args[i], args[i + 1]))

    message_text = ''
    is_first = True
    for role_reaction in role_map:
        if not is_first:
            message_text += '\n'
        is_first = False
        # if not discord.utils.get(ctx.guild.roles, name=role_reaction[0]):
        #     await ctx.guild.create_role(name=role_reaction[0])
        message_text += role_reaction[0] + ' - ' + role_reaction[1]

    message = await send_message_context.send(message_text)
    """message:
    id, channel(id, name, position, nsfw, news, category_id), type, author(id, name, discriminator, bot, nick, guild(id, name, shard_id, chunked, member_count)), flags
    """
    guild_id = str(message.guild.id)
    message_id = str(message.id)

    if g_reactions.get(guild_id) is None:
        g_reactions[guild_id] = {}
    if g_reactions[guild_id].get(message_id) is None:
        g_reactions[guild_id][message_id] = {}

    for role_reaction in role_map:
        await message.add_reaction(role_reaction[1])
        if g_reactions[guild_id][message_id].get(role_reaction[1]) is None:
            g_reactions[guild_id][message_id][role_reaction[1]] = role_reaction[0]
    
    write_reactions_to_file()

    # remove command message if it's in the same channel
    if not args[0].isnumeric(): # channel_id to send message in
        await ctx.message.delete()
    else: # give checkmark reaction to command
        await ctx.message.add_reaction('✅')

@commands.has_permissions(administrator=True)
@bot.command()
async def edit_role(ctx, *args):
    """Edit a message to include the new reactions given
    Format: $edit_role [message_id] [optional:channel_id] [role1] [reaction1] [role2] [reaction2] ...
    """
    role_map = []
    message_id = args[0]
    send_message_context = ctx

    start = 1
    if args[1].isnumeric(): # channel_id to send message in
        start = 2
        send_message_context = ctx.guild.get_channel(int(args[1]))

    # get message args into array of tuples
    for i in range(start, len(args), 2):
        role_map.append((args[i], args[i + 1]))

    message_text = ''
    is_first = True
    for role_reaction in role_map:
        if not is_first:
            message_text += '\n'
        is_first = False
        # if not discord.utils.get(ctx.guild.roles, name=role_reaction[0]):
        #     await ctx.guild.create_role(name=role_reaction[0])
        message_text += role_reaction[0] + ' - ' + role_reaction[1]

    message = await send_message_context.fetch_message(message_id)
    await message.edit(content=message_text)
    """message:
    id, channel(id, name, position, nsfw, news, category_id), type, author(id, name, discriminator, bot, nick, guild(id, name, shard_id, chunked, member_count)), flags
    """
    guild_id = str(message.guild.id)
    message_id = str(message.id)

    if g_reactions.get(guild_id) is None:
        g_reactions[guild_id] = {}
    g_reactions[guild_id][message_id] = {}

    await message.clear_reactions()

    for role_reaction in role_map:
        await message.add_reaction(role_reaction[1])
        if g_reactions[guild_id][message_id].get(role_reaction[1]) is None:
            g_reactions[guild_id][message_id][role_reaction[1]] = role_reaction[0]
    
    write_reactions_to_file()

    # remove command message if it's in the same channel
    if not args[1].isnumeric(): # channel_id to send message in
        await ctx.message.delete()
    else: # give checkmark reaction to command
        await ctx.message.add_reaction('✅')

@commands.has_permissions(administrator=True)
@bot.command()
async def add_role(ctx, *args):
    """Edit a message to include the new reactions given
    Format: $add_role [message_id] [optional:channel_id] [role1] [reaction1] [role2] [reaction2] ...
    """
    role_map = []
    message_id = args[0]
    send_message_context = ctx

    start = 1
    if args[1].isnumeric(): # channel_id to send message in
        start = 2
        send_message_context = ctx.guild.get_channel(int(args[1]))

    # get message args into array of tuples
    for i in range(start, len(args), 2):
        role_map.append((args[i], args[i + 1]))

    message_text = ''
    for role_reaction in role_map:
        message_text += '\n'
        # if not discord.utils.get(ctx.guild.roles, name=role_reaction[0]):
        #     await ctx.guild.create_role(name=role_reaction[0])
        message_text += role_reaction[0] + ' - ' + role_reaction[1]

    message = await send_message_context.fetch_message(message_id)
    await message.edit(content=message.content + message_text)
    """message:
    id, channel(id, name, position, nsfw, news, category_id), type, author(id, name, discriminator, bot, nick, guild(id, name, shard_id, chunked, member_count)), flags
    """
    guild_id = str(message.guild.id)
    message_id = str(message.id)

    if g_reactions.get(guild_id) is None:
        g_reactions[guild_id] = {}
    if g_reactions[guild_id].get(message_id) is None:
        g_reactions[guild_id][message_id] = {}

    for role_reaction in role_map:
        await message.add_reaction(role_reaction[1])
        if g_reactions[guild_id][message_id].get(role_reaction[1]) is None:
            g_reactions[guild_id][message_id][role_reaction[1]] = role_reaction[0]
    
    write_reactions_to_file()

    # remove command message if it's in the same channel
    if not args[1].isnumeric(): # channel_id to send message in
        await ctx.message.delete()
    else: # give checkmark reaction to command
        await ctx.message.add_reaction('✅')

####################
#      EVENTS      #
####################

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await import_reactions()
    print('Reactions imported')
    print(g_reactions)

@bot.event
async def on_raw_reaction_add(payload):
    """payload: channel_id, emoji, event_type, guild_id, member, message_id, user_id
    """
    guild_id = str(payload.guild_id)
    message_id = str(payload.message_id)
    reaction = str(payload.emoji.name)
    reaction_key = reaction
    pattern = re.compile(':(.*):')
    member = payload.member
    
    if member.bot:
        return
    if g_reactions.get(guild_id) is None:
        return
    if g_reactions[guild_id].get(message_id) is None:
        return 
    if g_reactions[guild_id][message_id].get(reaction) is None:
        for key in g_reactions[guild_id][message_id].keys():
            if pattern.search(key):
                reaction_key = key
                break
        else:
            return 

    role = g_reactions[guild_id][message_id][reaction_key]

    try:
        await member.add_roles(discord.utils.get(member.guild.roles, name=role))
    except Exception as e:
        print(e)
        print('bot.py: error giving role to member')
    else:
        pass # print('role added')

@bot.event
async def on_raw_reaction_remove(payload):
    """payload: channel_id, emoji, event_type, guild_id, member, message_id, user_id
    """
    guild_id = str(payload.guild_id)
    message_id = str(payload.message_id)
    reaction = str(payload.emoji.name)
    reaction_key = reaction
    pattern = re.compile(':(.*):')
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    
    if member.bot:
        return
    if g_reactions.get(guild_id) is None:
        return
    if g_reactions[guild_id].get(message_id) is None:
        return 
    if g_reactions[guild_id][message_id].get(reaction) is None:
        for key in g_reactions[guild_id][message_id].keys():
            if pattern.search(key):
                reaction_key = key
                break
        else:
            return

    role = g_reactions[guild_id][message_id][reaction_key]

    try:
        await member.remove_roles(discord.utils.get(member.guild.roles, name=role))
    except Exception as e:
        print(e)
        print('bot.py: error removing role from member')
    else:
        pass # print('role removed')

@bot.event
async def on_raw_message_delete(payload):
    """payload: cached_message, channel_id, guild_id, message_id
    """
    guild_id = str(payload.guild_id)
    message_id = str(payload.message_id)
    
    if g_reactions.get(guild_id) is None:
        return
    if g_reactions[guild_id].get(message_id) is None:
        return

    del g_reactions[guild_id][message_id]
    if len(g_reactions[guild_id]) == 0:
        del g_reactions[guild_id]
    write_reactions_to_file()
    

####################
# HELPER FUNCTIONS #
####################

async def import_reactions():
    """Imports reactions from json file
    reactions_file_name
    """
    global g_reactions
    try:
        os.makedirs(files_path, exist_ok=True)
    except:
        print('Failed to create files directory')
    with open(reactions_file_name, 'a+') as f_reactions:
        try:
            f_reactions.seek(0, 0)
            g_reactions = json.load(f_reactions)
        except:
            print('Reactions file empty, malformed, or failed to open.')
            g_reactions = {}
    return g_reactions

def write_reactions_to_file():
    with open(reactions_file_name, 'w') as f_reactions:
        json.dump(g_reactions, f_reactions)

bot.run(TOKEN)