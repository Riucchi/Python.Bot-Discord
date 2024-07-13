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
    'playlist_items': '1-11',  # Stream items 1 to 10 from the playlist
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
        self.entries = []  # Almacenar todas las canciones de la playlist

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # Almacenar todas las canciones de la playlist
            entries = data['entries']
            for entry in entries:
                filename = entry['url'] if stream else ytdl.prepare_filename(entry)
                source = discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=filename, **ffmpeg_options)
                ytdl_source = cls(source, data=entry)
                ytdl_source.entries = entries  # Asignar la lista de canciones a cada objeto YTDLSource
                yield ytdl_source
        else:
            filename = data['url'] if stream else ytdl.prepare_filename(data)
            yield cls(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=filename, **ffmpeg_options), data=data)
    
class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.current_voice_channel = None
        self.queue = []
        self.voice_connections = {}  # Inicializa el diccionario voice_connections

    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        await self.tree.sync()

    async def play_next(self, interaction, voice_channel, skipped=False, message=None):
        if client.voice_connections[voice_channel]['queue']:
            player = client.voice_connections[voice_channel]['queue'].pop(0)
            client.voice_connections[voice_channel]['connection'].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(interaction, voice_channel, skipped=True), self.loop))
            if not skipped:
                if message:
                    await message.edit(content=f"Playing {player.title}")
                else:
                    await interaction.followup.send(f"Playing {player.title}")
        else:
            if message:
                await message.edit(content="No more songs in queue")
            else:
                await interaction.followup.send("No more songs in queue")

intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.tree.command()
async def entrar(interaction: discord.Interaction):
    """ Joins the current voice channel"""
    if interaction.user.voice:
        voice_channel = interaction.user.voice.channel
        if voice_channel not in client.voice_connections:
            client.voice_connections[voice_channel] = {
                'connection': await voice_channel.connect(),
                'queue': []
            }
        await interaction.response.send_message(f"Joining....")
    else:
        await interaction.response.send_message("You must be in a voice channel to use this command")


@client.tree.command()
@app_commands.describe(
    url="URL to play"
)
async def reproducir(interaction: discord.Interaction, url: str):
    """ plays a url """
    await interaction.response.defer()
    voice_channel = interaction.user.voice.channel
    if voice_channel in client.voice_connections:
        async for player in YTDLSource.from_url(url, stream=True):
            client.voice_connections[voice_channel]['queue'].append(player)
        if not client.voice_connections[voice_channel]['connection'].is_playing():
            await client.play_next(interaction, voice_channel)
    await interaction.followup.send(f"Attempting to play {url}")

@client.tree.command()
async def pause(interaction: discord.Interaction):
    """ Pauses the current audio """
    voice_channel = interaction.user.voice.channel
    if voice_channel in client.voice_connections:
        client.voice_connections[voice_channel]['connection'].pause()
        await interaction.response.send_message(f"Audio paused")
    else:
        await interaction.response.send_message("Not currently in a voice channel")
        

@client.tree.command()
async def resume(interaction: discord.Interaction):
    """ Resumes the current audio """
    voice_channel = interaction.user.voice.channel
    if voice_channel in client.voice_connections:
        client.voice_connections[voice_channel]['connection'].resume()
        await interaction.response.send_message(f"Resuming audio")
    else:
        await interaction.response.send_message("Not currently in a voice channel")

@client.tree.command()
async def stop(interaction: discord.Interaction):
    """ Leaves the current voice channel"""
    voice_channel = interaction.user.voice.channel
    if voice_channel in client.voice_connections:
        await client.voice_connections[voice_channel]['connection'].disconnect()
        del client.voice_connections[voice_channel]
        await interaction.response.send_message("Bye bye")
    else:
        await interaction.response.send_message("Not currently in a voice channel")

@client.tree.command()
async def skip(interaction: discord.Interaction):
    """ Skips the current song """
    voice_channel = interaction.user.voice.channel
    if voice_channel in client.voice_connections:
        if client.voice_connections[voice_channel]['connection'].is_playing():
            client.voice_connections[voice_channel]['connection'].stop()
            await interaction.response.defer()
            message = await interaction.followup.send("Skipping song...")
            await client.play_next(interaction, voice_channel, skipped=True, message=message)
        else:
            await interaction.response.send_message("No hay canción actualmente en reproducción")
    else:
        await interaction.response.send_message("Not currently in a voice channel")


client.run(TOKENBOT)