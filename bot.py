import os
import discord
from discord import utils
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.environ.get('DISCORD_OAUTH_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Plays a music file
@bot.command()
async def play(ctx):
    is_file = os.path.isfile("test.mp3")
    if not is_file:
        await ctx.send("File not found")
    else:
        voice_channel = utils.get(ctx.guild.voice_channels, name='General')
        await voice_channel.connect()
        voice = utils.get(bot.voice_clients, guild=ctx.guild)
        await voice.play(discord.FFmpegPCMAudio("test.mp3"))

# Leaves the voice channel
@bot.command()
async def leave(ctx):
    voice = utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()

bot.run(TOKEN)