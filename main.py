from decouple import Config, RepositoryEnv
import discord
from discord import app_commands
import os
import yt_dlp
import asyncio


DOTENV_FILE = '.env'
env_config = Config(RepositoryEnv(DOTENV_FILE))


TOKENBOT = env_config.get('DISCORD_TOKEN')
MY_GUILD = discord.Object(id=int(env_config.get('GUILD')))

# Setup Youtube DL library
ytdl_options = {
    'format': 'bestaudio/best',
    'yesplaylist': True,  # Enable playlist support
    'noplaylist': None,  # Allow playlist parsing
    'playlist_items': '1-30',  # Stream items 1 to 10 from the playlist
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'ource_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

#setup FFmpeg
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
}

ytdl = yt_dlp.YoutubeDL(ytdl_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
        # Extract all songs from the playlist
            songs = data['entries']
            for song in songs:
                filename = song['url'] if stream else ytdl.prepare_filename(song)
                player = cls(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=filename, **ffmpeg_options), data=song)
                client.queue.append(player)
            return player
        else:
            filename = data['url'] if stream else ytdl.prepare_filename(data)
            return cls(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=filename, **ffmpeg_options), data=data)
    
class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.current_voice_channel = None
        self.queue = []

    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        await self.tree.sync()

    async def play_next(self, interaction, skipped=False):
        if self.queue:
            player = self.queue.pop(0)
            guild = interaction.guild
            guild.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(interaction, skipped=True), self.loop))
            if not skipped:
                await interaction.followup.send(f"Playing {player.title}")
        else:
            await interaction.followup.send("No more songs in queue")

intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.tree.command()
async def entrar(interaction: discord.Interaction):
    """ Joins the current voice channel"""
    if(interaction.user.voice):
        await interaction.response.send_message(f"Joining....")
        client.current_voice_channel = await interaction.user.voice.channel.connect()
    else:
        await interaction.response.send_message("You must be in a voice channel to use this command")


@app_commands.describe(
    url="URL to play"
)
@client.tree.command()
async def reproducir(interaction: discord.Interaction, url: str):
    """ plays a url """
    await interaction.response.defer()
    player = await YTDLSource.from_url(url, stream=True)
    client.queue.append(player)
    if not client.current_voice_channel.is_playing():
        await client.play_next(interaction, interaction.response)
    await interaction.followup.send(f"Attempting to play {url}")
    await interaction.followup.send(f"Playing {player.title}")

@client.tree.command()
async def pause(interaction: discord.Interaction):
    """ Pauses the current audio """
    if(client.current_voice_channel):
        if(client.current_voice_channel.is_paused()):
            await interaction.response.send_message(f"Audio is already paused")
            return
        client.current_voice_channel.pause()
        await interaction.response.send_message(f"Audio paused")
    else:
        await interaction.response.send_message("Not currently in a voice channel")
        
@client.tree.command()
async def resume(interaction: discord.Interaction):
    """ Resumes the current audio """
    if(client.current_voice_channel):
        if(client.current_voice_channel.is_paused()):
            await interaction.response.send_message(f"Resuming audio")
            client.current_voice_channel.resume()
        else:
            await interaction.response.send_message(f"Audio is not currently paused")
    else:
        await interaction.response.send_message("Not currently in a voice channel")

@client.tree.command()
async def stop(interaction: discord.Interaction):
    """ Leaves the current voice channel"""
    if(client.current_voice_channel):
        await client.current_voice_channel.disconnect()
        await interaction.response.send_message("Bye bye")
        client.current_voice_channel = None
    else:
        await interaction.response.send_message("Not currently in a voice channel")

@client.tree.command()
async def skip(interaction: discord.Interaction):
    if client.current_voice_channel and client.current_voice_channel.is_playing():
        client.current_voice_channel.stop()
        if client.queue:
            await client.play_next(interaction, skipped=True)
            await interaction.response.send_message("Skipped to the next song!")
        else:
            await interaction.response.send_message("No more songs in queue. Stopping music.")
    else:
        await interaction.response.send_message("No hay canción actualmente en reproducción")


client.run(TOKENBOT)