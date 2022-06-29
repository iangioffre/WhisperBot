import discord
import random

TOKEN = 'OTA1MjQ1MDgzNDU1MDkwNjg4.YYHRLg.uIdheDkug0vnar8Fav3FStOgEaM'
client = discord.Client()


@client.event
async def on_ready():
    print('Whats up bitches im {0.user}'.format(client))



@client.event
async def on_message(message):
    if message.author == client.user:
        return

    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    print(f'{username}: {user_message} ({channel})')



client.run(TOKEN)
