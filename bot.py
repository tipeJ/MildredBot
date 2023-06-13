import os
from typing import Type
import discord
import time
from discord import utils
from dotenv import load_dotenv
from discord.ext import commands
import random
import requests

load_dotenv()
TOKEN = os.environ.get('DISCORD_OAUTH_TOKEN')
KNALLIS_DIRECTORY = os.environ.get('KNALLIS_DIRECTORY')
FILES_LOCATION = os.environ.get('FILES_LOCATION')

playback_started_millis = None
playback_ended_millis = None
playback_file = None
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
# Scan file names in the directory
audio_files = [f[:-4] for f in os.listdir(KNALLIS_DIRECTORY) if f.lower().endswith('.mp3')]
audio_files.sort()

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

async def _playFile(ctx, file, start_time=None):
    path = f'{KNALLIS_DIRECTORY}/{file}.mp3'
    is_file = os.path.isfile(path)
    if not is_file:
        await ctx.send("ERROR: File not found")
    else:
        # Check if there is already a voice channel
        if ctx.voice_client is not None:
            # Disconnect from the voice channel
            await ctx.voice_client.disconnect()
        # If user is in a voice channel, connect to it
        # Check if author is User or not
        if not isinstance(ctx.author, discord.User):
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            # Otherwise, connect to General
            else:
                voice_channel = utils.get(ctx.guild.voice_channels, name='General')
                await voice_channel.connect()
            # Play the file 
            await ctx.send(f'Playing {file}')
            voice = utils.get(bot.voice_clients, guild=ctx.guild)
            if start_time is not None:
                before_options = f'-ss {start_time}'
            else:
                before_options = None
            global playback_started_millis
            global playback_file
            playback_started_millis = int(round(time.time() * 1000))
            playback_file = file
            voice.play(discord.FFmpegPCMAudio(path, before_options=before_options))
        else:
            await ctx.send("ERROR: You are not in a voice channel")

# Plays a music file
@bot.command()
async def play(ctx, name):
    # Find the matching audio file name. Non-case-sensitive
    audio_file = [f for f in audio_files if name.lower() in f.lower()]
    if len(audio_file) == 0:
        await ctx.send('No matching episode found.')
    elif len(audio_file) > 1:
        await ctx.send('Multiple matching episodes found:\n' + ',\n'.join(audio_file))
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
    try:
        voice.pause()
    except AttributeError:
        await ctx.send("ERROR: Nothing is playing")

# Resume the music
@bot.command()
async def resume(ctx):
    voice = utils.get(bot.voice_clients, guild=ctx.guild)
    try:
        voice.resume()
    except AttributeError:
        await ctx.send("ERROR: Nothing is playing")

# Leaves the voice channel
@bot.command()
async def leave(ctx):
    voice = utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()
        global playback_file
        playback_file = None

# Joins the current voice channel
@bot.command()
async def join(ctx):
    # Check if playing or not
    if playback_file is None:
        await ctx.send("ERROR: No last played file available")
    else:
        # Leave
        voice = utils.get(bot.voice_clients, guild=ctx.guild)
        start_time = None
        if voice and voice.is_connected():
            await voice.disconnect()
            playback_ended_millis = int(round(time.time() * 1000))
            start_time = (playback_ended_millis - playback_started_millis) / 1000
        # Join
        await _playFile(ctx, playback_file, start_time)

# Lists the audio files
@bot.command()
async def list(ctx):
    # Send txt file 'files.txt' to the chat as an attachment
    file = discord.File(FILES_LOCATION)
    await ctx.send(file=file)

# Sends the given file to the user
# TODO: Find alternative way of sending, as audio files exceed the maximum allowed by discord.
@bot.command()
async def download(ctx, name):
    # Find the matching audio file name. Non-case-sensitive
    audio_file = [f for f in audio_files if name.lower() in f.lower()]
    if len(audio_file) == 0:
        await ctx.send('No matching episode found.')
    elif len(audio_file) > 1:
        await ctx.send('Multiple matching episodes found:\n' + ',\n'.join(audio_file))
    else:
        # ! Discord API limit: File size is limited to 8MB, which is not enough to cover k&s episodes, as they range from 30 to 50MB.
        # Upload the file to file.io
        path = f'{KNALLIS_DIRECTORY}/{audio_file[0]}.mp3'
        is_file = os.path.isfile(path)
        if is_file:
            # Make a POST request to file.io
            upload_url = 'https://file.io'
            data = {
                'file': open(path, 'rb'),
            }
            response = requests.post(upload_url, files=data)
            res = response.json()
            if res['success']:
                await ctx.author.send(f'Here is your file: {res["link"]}')
            else:
                await ctx.send('ERROR: File upload failed!')

# Lists commands and what they do
@bot.command()
async def commands(ctx):
    await ctx.send('List of commands:\n' + '\n'.join([
        '!play [name] - Plays the given episode',
        '!rand - Plays a random episode',
        '!pause - Pauses the playback',
        '!resume - Resumes the playback',
        '!leave - Leaves the voice channel, stopping playback',
        '!join - Joins the current voice channel, resuming playback',
        '!list - Lists all episodes',
        '!download [name] - Sends the given episode to the user'
    ]))

bot.run(TOKEN)