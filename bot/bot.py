import discord
from discord.ext import commands
from discord.utils import get

import json
import os
from dotenv import load_dotenv

###########################################
#            COMMANDS (*admin)            #
###########################################
# *test - sends message back to say it's working
# *reactions - prints reaction object
# *clear_roles - clears all role-reaction relationships
# *create_role - creates a message with role-reaction inputs
# *edit_role - edits a given message with role-reaction inputs

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
async def reactions(ctx):
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
    Format: $role [role1] [reaction1] [role2] [reaction2] ...
    """
    role_map = []

    # get message args into array of tuples
    for i in range(0, len(args), 2):
        role_map.append((args[i], args[i + 1]))

    message_text = ''
    is_first = True
    for role_reaction in role_map:
        if not is_first:
            message_text += '\n'
        is_first = False
        message_text += role_reaction[0] + ' - ' + role_reaction[1]

    message = await ctx.send(message_text)
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

    # remove command message
    await ctx.message.delete()

@commands.has_permissions(administrator=True)
@bot.command()
async def edit_role(ctx, *args):
    """Edit a message to include the new reactions given
    Format: $role [role1] [reaction1] [role2] [reaction2] ...
    """
    role_map = []
    message_id = args[0]

    # get message args into array of tuples
    for i in range(1, len(args), 2):
        role_map.append((args[i], args[i + 1]))

    message_text = ''
    is_first = True
    for role_reaction in role_map:
        if not is_first:
            message_text += '\n'
        is_first = False
        message_text += role_reaction[0] + ' - ' + role_reaction[1]

    message = await ctx.fetch_message(message_id)
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
    # for reaction in message.reactions:
    #     await message.clear_reaction(reaction)

    for role_reaction in role_map:
        await message.add_reaction(role_reaction[1])
        if g_reactions[guild_id][message_id].get(role_reaction[1]) is None:
            g_reactions[guild_id][message_id][role_reaction[1]] = role_reaction[0]
    
    write_reactions_to_file()

    # remove command message
    await ctx.message.delete()

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
    member = payload.member
    
    if g_reactions.get(guild_id) is None:
        return
    if g_reactions[guild_id].get(message_id) is None:
        return 
    if g_reactions[guild_id][message_id].get(reaction) is None:
        return 

    role = g_reactions[guild_id][message_id][reaction]

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
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    
    if g_reactions.get(guild_id) is None:
        return
    if g_reactions[guild_id].get(message_id) is None:
        return 
    if g_reactions[guild_id][message_id].get(reaction) is None:
        return 

    role = g_reactions[guild_id][message_id][reaction]

    try:
        await member.remove_roles(discord.utils.get(member.guild.roles, name=role))
    except Exception as e:
        print(e)
        print('bot.py: error removing role from member')
    else:
        pass # print('role removed')

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