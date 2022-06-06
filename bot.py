import os
import discord
from discord import utils
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.environ.get('DISCORD_OAUTH_TOKEN')

bot = commands.Bot(command_prefix='!')
# Scan file names in the 'knallis' subdirectory
audio_files = [f for f in os.listdir('knallis') if f.endswith('.mp3')]

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Plays a music file
@bot.command()
async def play(ctx, name):
    # Find the matching audio file name
    audio_file = [f for f in audio_files if f.__contains__(name)]
    if len(audio_file) == 0:
        await ctx.send('No matching audio file found.')
    elif len(audio_file) > 1:
        await ctx.send('Multiple matching audio files found: ' + ', '.join(audio_file))
    else:
        is_file = os.path.isfile(f'knallis/{audio_file[0]}')
        if not is_file:
            await ctx.send("File not found")
        else:
            # Check if there is already a voice channel
            if ctx.voice_client is not None:
                # Disconnect from the voice channel
                await ctx.voice_client.disconnect()
            voice_channel = utils.get(ctx.guild.voice_channels, name='General')
            await voice_channel.connect()
            voice = utils.get(bot.voice_clients, guild=ctx.guild)
            await voice.play(discord.FFmpegPCMAudio(f'knallis/{audio_file[0]}'))

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

bot.run(TOKEN)