import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import get

import json
import os
import re
from dotenv import load_dotenv
from typing import Optional

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix = '$', intents = intents)

    async def setup_hook(self):
        await self.tree.sync() # global sync, for guild specific sync (faster), add parameter guild = discord.Object(id = [GUILD_ID])
        print(f"Synced slash commands for {self.user}.")

    async def on_command_error(self, ctx, error):
        print(error)
        await ctx.reply(error, ephemeral = True)

####################
#      GLOBAL      #
####################
bot = Bot()

g_reactions = {}
files_path = 'files/'
reactions_file_name = files_path + 'reactions.json'

###########################################
#            COMMANDS (*admin)            #
###########################################
# *ping - sends message back to say it's working
# *roles - prints reaction object
# *clear_roles - clears all role-reaction relationships
# *create_role - creates a message with role-reaction inputs
# *edit_role - edits a given message with role-reaction inputs
# *add_role - adds to given message with role-reaction inputs

@commands.has_permissions(administrator = True)
@bot.hybrid_command(name = 'ping', with_app_command = True, description = "For testing bot's connection")
async def ping(ctx: commands.Context):
    await ctx.defer(ephemeral = True)
    await ctx.reply("Pong!")

@commands.has_permissions(administrator=True)
@bot.hybrid_command(name = 'roles', with_app_command = True, description = "Shows the reaction object")
async def roles(ctx):
    await ctx.defer(ephemeral = True)
    print(g_reactions)
    await ctx.reply(g_reactions)

@commands.has_permissions(administrator=True)
@bot.hybrid_command(name = 'clear_roles', with_app_command = True, description = "Clears all role-reaction relationships")
async def clear_roles(ctx):
    global g_reactions
    await ctx.defer(ephemeral = True)
    print("Clearing all roles")
    g_reactions = {}
    write_reactions_to_file()
    await ctx.reply("All roles cleared")

@commands.has_permissions(administrator=True)
@bot.hybrid_command(name = 'create_role', with_app_command = True, description = "Creates a message with role-reaction inputs")
async def create_role(ctx, roles, channel: Optional[discord.TextChannel] = None):
    """Create a message and add reactions to the message
    Format: $create_role [optional:channel_id] [role1] [reaction1] [role2] [reaction2] ...
    """
    await ctx.defer(ephemeral = True)

    role_map = []
    send_message_context = ctx.channel

    if channel is not None: # channel_id to send message in
        send_message_context = channel

    # get message args into array of tuples
    roles = roles.split(",")
    for i in range(0, len(roles), 2):
        role_map.append((roles[i].strip(), roles[i + 1].strip()))

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

    await ctx.reply("Message created")

@commands.has_permissions(administrator=True)
@bot.hybrid_command(name = 'edit_role', with_app_command = True, description = "Edits a given message with role-reaction inputs")
async def edit_role(ctx, message_id, roles, channel: Optional[discord.TextChannel] = None):
    """Edit a message to include the new reactions given
    Format: $edit_role [message_id] [optional:channel_id] [role1] [reaction1] [role2] [reaction2] ...
    """
    role_map = []
    send_message_context = ctx.channel

    if channel is not None: # channel_id to edit message in
        send_message_context = channel

    # get message args into array of tuples
    roles = roles.split(",")
    for i in range(0, len(roles), 2):
        role_map.append((roles[i].strip(), roles[i + 1].strip()))

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

    await ctx.reply("Message edited")

@commands.has_permissions(administrator=True)
@bot.hybrid_command(name = 'add_role', with_app_command = True, description = "Adds to a given message with role-reaction inputs")
async def add_role(ctx, message_id, roles, channel: Optional[discord.TextChannel]):
    """Edit a message to include the new reactions given
    Format: $add_role [message_id] [optional:channel_id] [role1] [reaction1] [role2] [reaction2] ...
    """
    role_map = []
    send_message_context = ctx.channel

    if channel is not None: # channel_id to edit message in
        send_message_context = channel

    # get message args into array of tuples
    roles = roles.split(",")
    for i in range(0, len(roles), 2):
        role_map.append((roles[i].strip(), roles[i + 1].strip()))

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

    await ctx.reply("Message edited")

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

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
if TOKEN is None:
    print('You must pass have BOT_TOKEN defined in the environment.')
bot.run(TOKEN)