import discord
import tokens
bot = discord.Client()

@bot.event
async def on_ready():
    print("Bot is ready")

@bot.event
async def on_message(message):
    msg = message.content.lower()
    if(message.author == bot.user):
        return
    else:
        if(msg.startswith("hello") or msg.startswith("hi") ):
            await message.channel.send('Hi! ' + str(message.author))
        if(msg.startswith("how are you?")):
            await message.channel.send('Awesome! ')

token = tokens.Token
bot.run(token)
