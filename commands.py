import discord 
from discord.ext import commands 
import tokens 
import requests 



bot = commands.Bot(command_prefix='/') 


@bot.command()
async def hello(context, *args):
    for arg in args: 
        await context.send(arg)



@bot.command()
async def numbers(context, arg): 
    api_string = 'http://numbersapi.com/' + str(arg) +'/math'
    response = requests.get(api_string) 
    await context.send(response.text)

token = tokens.Token
bot.run(token)