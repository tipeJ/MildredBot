import os
import discord
from discord import utils
from dotenv import load_dotenv
from discord.ext import commands
import random

load_dotenv()
TOKEN = os.environ.get('DISCORD_OAUTH_TOKEN')
KNALLIS_DIRECTORY = os.environ.get('KNALLIS_DIRECTORY')

bot = commands.Bot(command_prefix='!')
# Scan file names in the directory
audio_files = [f[:-4] for f in os.listdir(KNALLIS_DIRECTORY) if f.endswith('.mp3')]
audio_files.sort()

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

async def _playFile(ctx, file):
    path = f'{KNALLIS_DIRECTORY}/{file}.mp3'
    is_file = os.path.isfile(path)
    if not is_file:
        await ctx.send("File not found")
    else:
        # Check if there is already a voice channel
        if ctx.voice_client is not None:
            # Disconnect from the voice channel
            await ctx.voice_client.disconnect()
        # If user is in a voice channel, connect to it
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        # Otherwise, connect to General
        else:
            voice_channel = utils.get(ctx.guild.voice_channels, name='General')
            await voice_channel.connect()
        # Play the file 
        await ctx.send(f'Playing {file}')
        voice = utils.get(bot.voice_clients, guild=ctx.guild)
        await voice.play(discord.FFmpegPCMAudio(path))

# Plays a music file
@bot.command()
async def play(ctx, name):
    # Find the matching audio file name. Non-case-sensitive
    audio_file = [f for f in audio_files if name.lower() in f.lower()]
    if len(audio_file) == 0:
        await ctx.send('No matching audio file found.')
    elif len(audio_file) > 1:
        await ctx.send('Multiple matching audio files found: ' + ', '.join(audio_file))
    else:
        await _playFile(ctx, audio_file[0])

@bot.command()
async def rand(ctx):
    # Select random audio file
    audio_file = audio_files[int(len(audio_files) * random.random())]
    await _playFile(ctx, audio_file)

# Pause the music
@bot.command()
async def pause(ctx):
    voice = utils.get(bot.voice_clients, guild=ctx.guild)
    voice.pause()

# Resume the music
@bot.command()
async def resume(ctx):
    voice = utils.get(bot.voice_clients, guild=ctx.guild)
    voice.resume()

# Leaves the voice channel
@bot.command()
async def leave(ctx):
    voice = utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()

# Lists the audio files
@bot.command()
async def list(ctx):
    await ctx.send('\n'.join(audio_files))

bot.run(TOKEN)