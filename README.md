# Python Bot For Discord

 --- ENGLISH ---
Bot for playing music on discord made with python


The Librarys needed for use this on your pc:


<li>discord.py==3.2.1</li>
<li>asyncio</li>
<li>ffmpeg</li>
<li>yt-dlp</li>
<li>python-decouple</li>



<p>This is just an practice experimental bot made for myself and my friends to enjoy some music on discord channels. its free to use for any who wants to use or improve the code.
i will work on having this bot updated for work on discord.</p>

thanks and hope u enjoy the repository!

# HOW TO USE

This bot Has the next commands for use:

<li>/entrar - Joins the Channel</li>
<li>/Reproducir + url - Start Playing the song from the url</li>
<li>/skip - Skip to the next song if there any on queue</li>
<li>/stop - Stop the music and leave the Voice Channel</li>
<li>/pause - Stop the current playing song</li>
<li>/resume - Resume the last song paused</li>


<p>for running it just install the dependencies, make and .env archive and add as enviroment variables  your APP-TOKEN from discord then, copy the ID from the server that will the bot first connect when u start it.

then run the archive main with the next command:
python main.py</p>

Enjoy

 --- SPANISH ---
# Bot de Musica para Discord

Librerias necesarias para correr el bot:

<li>asyncio</li>
<li>ffmpeg (Instalar ffmpeg.exe ademas de la biblioteca e indicar en el codigo el path al ejecutable.)li>
<li>discord.py</li>
<li>yt-dlp</li>
<li>python-decouple</li>

Podes tambien ejecutar el siguiente comando para instalar todas las bibliotecas mencionadas:

<h3>pip install -r requirements.txt<h3>


<p> este bot es un proyecto personal de codigo abierto. hecho para disfrutar de musica con mis amigos en los canales de discord que frecuento. voy a trabajar en que el bot funcione incluso si discord es actualizado. </p>

# COMO USAR

el bot cuenta con los siguientes comandos:

<li>/entrar - Entra al canal de quien ingrese el comando.</li>
<li>/Reproducir + url - empieza a reproducir la canción indicada en el url de youtube.</li>
<li>/skip - salta a la siguiente canción en la playlist.</li>
<li>/stop - Para de reproducir musica y abandona el canal.</li>
<li>/pause - pausa la canción que esta sonando actualmente.</li>
<li>/resume - resume la ultima canción puesta.</li>


# PASO 1
Para poder utilizar este bot, es necesario crear una aplicación en la siguiente pagina de discord:
https://discord.com/developers/applications/

# PASO 2

crear un archivo .env dentro de la carpeta donde este el archivo main.py, crear una variable de entorno dentro del archivo .env con el siguiente nombre : DISCORD_TOKEN= (y tu api key)

# PASO 3

Generar un link de invitacion al canal desde OAuth2 en discord, con los permisos (bot, aplications.commands.permissions.update , view channels, connect, manage messages, view channels)

# PASO 4

invitar a tu canal de discord con el link generado desde el 0Auth2 con los permisos mencionados arriba.

# PASO 5

Disfruta del bot.


PD IMPORTANTE :

RECORDA DE INSTALAR PYTHON 3.12 Y AGREGAR AL .PATH (en la instalación) PARA PODER CORRER EL SCRIPT DESDE CONSOLA.
