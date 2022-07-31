import discord
from discord.ext import commands

TOKEN = 'OTA1MjQ1MDgzNDU1MDkwNjg4.YYHRLg.uIdheDkug0vnar8Fav3FStOgEaM'

bot = commands.Bot(command_prefix='$')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def test(ctx):
    await ctx.send('Message receieved')

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

    for role_reaction in role_map:
        await message.add_reaction(role_reaction[1])

bot.run(TOKEN)
