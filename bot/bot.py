import discord
from discord.ext import commands
import random

TOKEN = 'OTA1MjQ1MDgzNDU1MDkwNjg4.YYHRLg.uIdheDkug0vnar8Fav3FStOgEaM'

bot = commands.Bot(command_prefix='$')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def role(ctx):

    message = await ctx.send("Role Selector")

    reaction_X = '❌'

    await ctx.add_reaction(reaction_X)

bot.run(TOKEN)
