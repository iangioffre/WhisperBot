import discord
import games
import random

TOKEN = 'OTA1MjQ1MDgzNDU1MDkwNjg4.YYHRLg.uIdheDkug0vnar8Fav3FStOgEaM'

class MyClient(discord.Client):
    async def on_ready(self):                               #prints a ready message to console
        print('Logged on as {0}!'.format(self.user))

    def on_message(self, message):                          #chat logging
        print('{0.author}: {0.content}'.format(message))

    async def on_message(self, message):
        if message.author == client.user:   #if message is from bot do nothing
            return

        if message.content.startswith('$test'):
            await message.channel.send("test worked")

      ## if message.content.startswith('$valorant'):
      ##      await create_voice_channel(test, 'test')
      ##     return test


client = MyClient()
client.run(TOKEN)
