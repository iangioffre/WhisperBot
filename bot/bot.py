import discord
from discord.ext import commands
import json
import os

TOKEN = 'OTA1MjQ1MDgzNDU1MDkwNjg4.YYHRLg.uIdheDkug0vnar8Fav3FStOgEaM'

bot = commands.Bot(command_prefix='$')

g_reactions = {}
files_path = 'files/'
reactions_file_name = files_path + 'reactions.json'

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await import_reactions()
    print('Reactions imported')
    print(g_reactions)

@bot.command()
async def test(ctx):
    await ctx.send('Message receieved')

@bot.command()
async def reactions(ctx):
    print(g_reactions)
    await ctx.send(g_reactions)

@bot.command()
async def role(ctx, *args):
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

    for role_reaction in role_map:
        await message.add_reaction(role_reaction[1])
        if g_reactions.get(message.guild.id) is None:
            g_reactions[message.guild.id] = {}
        if g_reactions[message.guild.id].get(message.id) is None:
            g_reactions[message.guild.id][message.id] = {}
        if g_reactions[message.guild.id][message.id].get(role_reaction[0]) is None:
            g_reactions[message.guild.id][message.id][role_reaction[0]] = role_reaction[1]
    
    # write g_reactions changes to file
    with open(reactions_file_name, 'w') as f_reactions:
        json.dump(g_reactions, f_reactions)

@bot.event
async def on_raw_reaction_add(payload):
    """payload: channel_id, emoji, event_type, guild_id, member, message_id, user_id
    """
    pass

@bot.event
async def on_raw_reaction_remove(payload):
    """payload: channel_id, emoji, event_type, guild_id, member, message_id, user_id
    """
    pass

async def import_reactions():
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

bot.run(TOKEN)
