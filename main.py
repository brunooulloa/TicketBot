from discord.ext.commands import CommandNotFound
from discord.ext import commands
from discord.utils import get
from classes import softFunctions
from datetime import datetime
from pytz import timezone
import mysql.connector, chat_exporter, asyncio, discord, json, os, io

""" Get current directory function """
def cwd(file: str):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), file)

""" Get config.json """
with open(cwd('config.json'), 'r') as config:
    data = json.load(config)
    token = data['token']
    owner_id = data['owner_id']
    guild_id = data['guild_id']
    staff_role = data['staff']['name']
    staff_role_id = data['staff']['id']
    database = data['database']
    muted_role = data['muted']['name']
    muted_role_id = data['muted']['id']
    purge_default = data['purge_default']
    if enable_logs := data['logs']['enabled']:
        log_channel_id = data['logs']['channel_id']

""" Intents """
intents = discord.Intents.all()
intents.members = True

""" Bot's presence """
async def presence():
	statuses = [ f'{bot.get_guild(guild_id).member_count} members! 👥', 'Soft 💻', 'with tickets! 🎫' ]
	while True:
		for status in statuses:
			if status == statuses[2]:
				await bot.change_presence(activity = discord.Game(name = status))
			else:
				await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = status))

			await asyncio.sleep(20)

""" Bot """
bot = commands.Bot(command_prefix = softFunctions.get_prefix, help_command = None, intents = intents, owner_id = owner_id)

""" Database """
connection = None

def init_db():
    return mysql.connector.connect(host = database['host'], user = database['user'], password = database['password'], database = database['db'])

def get_cursor():
    global connection
    try:
        connection.ping(reconnect = True, attempts = 3, delay = 5)
    except mysql.connector.Error as err:
        try:
            connection = init_db()
        except:
            softFunctions.restart_bot()
    return connection.cursor()

connection = init_db()
cursor = get_cursor()

""" Colours """
red = discord.Colour.from_rgb(255, 0, 0)

""" Owner variables """
soft_user = 'Soft#6666'
soft_avatar = 'https://images-ext-2.discordapp.net/external/p0KE48w9Lt_6PsiIu3hhU8zHgF-9LLEmk8tbUmNLPoU/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/293148087407476737/a_d0cbdc184155c678ea1ad107163a324b.gif'

""" Events """
@bot.event
async def on_ready():
    softFunctions.bot_print(bot, 'Logged in!')
    softFunctions.soft()
    bot.loop.create_task(presence())

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        softFunctions.owo_print(f'{ctx.author} tried to use unregistered command "{ctx.message.content.split(prefix)[1]}" at "{ctx.guild.name}" guild')
        return
    raise error

@bot.event
async def on_guild_join(guild):
    with open(cwd('prefixes.json'), 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = '!'

    with open(cwd('prefixes.json'), 'w') as f:
        json.dump(prefixes, f, indent = 4)

@bot.event
async def on_guild_remove(guild):
    with open(cwd('prefixes.json'), 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open(cwd('prefixes.json'), 'w') as f:
        json.dump(prefixes, f, indent = 4)

""" Ticket Commands """
@bot.command()
@commands.has_role(staff_role)
async def ticket(ctx):
    await ctx.message.delete()
    embed = discord.Embed(title = '🎫 Crea un Ticket!', description = '📩 Selecciona tu tipo de ticket abajo para contactarte con nosotros!', color = red)
    embed.set_footer(text = soft_user, icon_url = soft_avatar)
    await ctx.send(embed = embed, view = TicketView())
    global guild
    guild = ctx.guild
    if enable_logs:
        channel = bot.get_channel(log_channel_id)
        embed = discord.Embed(title = 'Panel creado', description = f'Panel creado por {ctx.author.mention} en {ctx.channel.mention}', color = red, timestamp = datetime.now(timezone('America/Argentina/Buenos_Aires')))
        await channel.send(embed = embed)

@bot.command()
@commands.has_role(staff_role)
async def rename(ctx, name: str):
    await ctx.message.delete()
    if 'ticket-' in ctx.channel.name:
        categories = [ 'Reporte', 'Dudas', 'Donacion', 'Otros' ]

        if ctx.channel.category.name in categories:
            await ctx.channel.edit(name = f'{name}-{ctx.channel.name.split("-")[-1]}')
            embed = discord.Embed(title = 'Canal renombrado!', description = f'Se ha renombrado el canal a "{name}"', color = red)
            embed.set_footer(text = soft_user, icon_url = soft_avatar)
            await ctx.send(embed = embed)

        if enable_logs:
            log_channel = bot.get_channel(log_channel_id)
            log = discord.Embed(title = 'Canal renombrado!', description = f'Se ha renombrado el canal {ctx.channel.name} a {name}-{ctx.channel.name.split("-")[-1]} por {ctx.author.mention}', color = red, timestamp = datetime.now(timezone('America/Argentina/Buenos_Aires')))
            await log_channel.send(embed = log)
    else:
        embed = discord.Embed(title = 'No puedes renombrar este canal!', description = 'Debes estar en un canal de ticket para poder renombrar un canal', color = red)
        await ctx.send(embed = embed)
        softFunctions.owo_print(f'{ctx.author} trato de renombrar el canal {ctx.channel.name} en la categoria {ctx.channel.category.name}')

@bot.command()
@commands.has_role(staff_role)
async def dm(ctx, user: discord.Member, msg: str):
    names = [ 'Reporte', 'Dudas', 'Donacion', 'Otros' ]
    if ctx.channel.category.name in names:
        await ctx.message.delete()
        await softFunctions.send_dm(user, embed = True, title = ctx.channel.name, description = f'{msg}', color = red, thumbnail = None, image = None, author = None, file = None)
    
            
@bot.command()
@commands.has_role(staff_role)
async def close(ctx):
    if 'ticket-' in ctx.channel.name:
        await ctx.message.delete()
        embed = discord.Embed(title = 'Cerrando...', description = 'Se esta cerrando el ticket', color = red)
        embed.set_footer(text = soft_user, icon_url = soft_avatar)
        await ctx.send(embed = embed)
        cursor.execute(f"UPDATE tickets SET closed = 1 WHERE ticket_id = {int(ctx.channel.name.split('-')[-1])}")
        connection.commit()
        if enable_logs:
            log_channel = bot.get_channel(log_channel_id)
            embed = discord.Embed(title = 'Ticket cerrado', description = f'{ctx.author.mention} cerro el ticket {ctx.channel.name}', color = red, timestamp = datetime.now(timezone('America/Argentina/Buenos_Aires')))
            cursor.execute(f"SELECT ticket_creator_id FROM tickets WHERE ticket_id = {int(ctx.channel.name.split('-')[-1])}")
            creator = str(cursor.fetchall())
            characters = [ '[', ']', '(', ')', ',' ]
            for character in characters:
                if character in creator:
                    creator = creator.replace(character, '')
            creator = ctx.guild.get_member(int(creator))
            transcript = await chat_exporter.export(ctx.channel)
            if transcript is None:
                return
            transcript_file = discord.File(io.BytesIO(transcript.encode()), filename = f'transcript-{ctx.channel.name}.html')
            await log_channel.send(embed = embed, file = transcript_file)
        
        transcript = await chat_exporter.export(ctx.channel)
        transcript_file = discord.File(io.BytesIO(transcript.encode()), filename = f'transcript-{ctx.channel.name}.html')
        await softFunctions.send_dm(creator, embed = True, title = ctx.channel.name, description = 'Aca esta tu transcript :)', color = red, thumbnail = None, image = None, author = None, file = transcript_file)

        await asyncio.sleep(5)
        await ctx.channel.delete()
    else:
        embed = discord.Embed(title = 'No puedes borrar este canal!', description = 'Debes estar en un canal de ticket para poder cerrar un canal', color = red)
        await ctx.send(embed = embed)
        softFunctions.owo_print(f'{ctx.author} trato de borrar el canal {ctx.channel.name} en la categoria {ctx.channel.category.name}')
    
@bot.command()
@commands.has_role(staff_role)
async def add(ctx, member: discord.Member):
    if 'ticket-' in ctx.channel.name:
        await ctx.message.delete()
        await ctx.channel.set_permissions(member, view_channel = True)
        embed = discord.Embed(title = 'Miembro agregado!', description = f'{member.mention} fue agregado a {ctx.channel.mention}', color = red)
        embed.set_footer(text = soft_user, icon_url = soft_avatar)
        await ctx.send(embed = embed)
        if enable_logs:
            log_channel = bot.get_channel(log_channel_id)
            log = discord.Embed(title = 'Miembro agregado!', description = f'{member.mention} fue agregado a {ctx.channel.mention}', color = red, timestamp = datetime.now(timezone('America/Argentina/Buenos_Aires')))
            await log_channel.send(embed = log)
    else:
        embed = discord.Embed(title = 'No puedes agregar a un usuario!', description = 'Debes estar en un canal de ticket para poder agregar a un usuario', color = red)
        await ctx.send(embed = embed)
        softFunctions.owo_print(f'{ctx.author} trato de agregar un usuario al canal {ctx.channel.name} en la categoria {ctx.channel.category.name}')
    
@bot.command()
@commands.has_role(staff_role)
async def remove(ctx, member: discord.Member):
    if 'ticket-' in ctx.channel.name:
        await ctx.message.delete()
        await ctx.channel.set_permissions(member, view_channel = False)
        embed = discord.Embed(title = 'Miembro removido!', description = f'{member.mention} fue removido de {ctx.channel.mention}', color = red)
        embed.set_footer(text = soft_user, icon_url = soft_avatar)
        await ctx.send(embed = embed)
        if enable_logs:
            log_channel = bot.get_channel(log_channel_id)
            log = discord.Embed(title = 'Miembro removido!', description = f'{member.mention} fue removido de {ctx.channel.mention}', color = red, timestamp = datetime.now(timezone('America/Argentina/Buenos_Aires')))
            await log_channel.send(embed = log)
    else:
        embed = discord.Embed(title = 'No puedes remover a un usuario!', description = 'Debes estar en un canal de ticket para poder remover a un usuario', color = red)
        await ctx.send(embed = embed)
        softFunctions.owo_print(f'{ctx.author} trato de remover a un usuario del canal {ctx.channel.name} en la categoria {ctx.channel.category.name}')

@bot.command()
@commands.has_role(staff_role)
async def claim(ctx):
    if 'ticket-' in ctx.channel.name:
        await ctx.message.delete()
        embed = discord.Embed(title = 'Ticket reclamado!', description = f'{ctx.author.mention} reclamo el ticket!', color = red)
        embed.set_footer(text = soft_user, icon_url = soft_avatar)
        await ctx.send(embed = embed)
        if enable_logs:
            log_channel = bot.get_channel(log_channel_id)
            log = discord.Embed(title = 'Ticket reclamado!', description = f'{ctx.author.mention} reclamo el {ctx.channel.name}', color = red, timestamp = datetime.now(timezone('America/Argentina/Buenos_Aires')))
            await log_channel.send(embed = log)
    else:
        embed = discord.Embed(title = 'No puedes reclamar este canal!', description = 'Debes estar en un canal de ticket para poder reclamar un canal', color = red)
        await ctx.send(embed = embed)
        softFunctions.owo_print(f'{ctx.author} trato de reclamar el canal {ctx.channel.name} en la categoria {ctx.channel.category.name}')

@bot.command()
@commands.has_role(staff_role)
async def unclaim(ctx):
    if 'ticket-' in ctx.channel.name:
        await ctx.message.delete()
        embed = discord.Embed(title = 'Ticket relevado!', description = f'{ctx.author.mention} relevo el ticket!', color = red)
        embed.set_footer(text = soft_user, icon_url = soft_avatar)
        await ctx.send(embed = embed)
        if enable_logs:
            log_channel = bot.get_channel(log_channel_id)
            log = discord.Embed(title = 'Ticket relevado!', description = f'{ctx.author.mention} relevo el {ctx.channel.name}', color = red, timestamp = datetime.now(timezone('America/Argentina/Buenos_Aires')))
            await log_channel.send(embed = log)
    else:
        embed = discord.Embed(title = 'No puedes relevar este canal!', description = 'Debes estar en un canal de ticket para poder relevar un canal', color = red)
        await ctx.send(embed = embed)
        softFunctions.owo_print(f'{ctx.author} trato de relevar el canal {ctx.channel.name} en la categoria {ctx.channel.category.name}')
        
@bot.command()
async def tickets(ctx):
    opened = sum('ticket-' in channel.name and channel.name != 'ticket-logs' for channel in ctx.guild.channels)
    if opened == 1:
        embed = discord.Embed(title = 'Tickets abiertos!', description = f'Hay {opened} ticket abierto', color = red)
    elif opened >= 1:
        embed = discord.Embed(title = 'Tickets abiertos!', description = f'Hay {opened} tickets abiertos', color = red)
    else:
        embed = discord.Embed(title = 'Tickets abiertos!', description = 'No hay tickets abiertos', color = red)
    
    embed.set_footer(text = soft_user, icon_url = soft_avatar)
    await ctx.send(embed = embed)
    
""" Bot commands """
@bot.command()
async def prefix(ctx, prefix = None):
    role = get(ctx.guild.roles, name = staff_role)
    if role in ctx.author.roles and prefix != None:
        with open(cwd('prefixes.json'), 'r') as f:
            prefixes = json.load(f)

        prefixes[str(ctx.guild.id)] = prefix

        with open(cwd('prefixes.json'), 'w') as f:
            json.dump(prefixes, f, indent = 4)

        await ctx.send(f'Prefix changed to: {prefix}')
    elif prefix is None:
        await ctx.send(f'{softFunctions.get_prefix(bot, ctx.message)}')
    
        
@bot.command()
async def help(ctx):
    embed = discord.Embed(title = 'Comandos', color = red, timestamp = datetime.now(timezone('America/Argentina/Buenos_Aires')))
    embed.add_field(name = '!ticket', value = '`Crear nuevo panel de tickets. (Dueño del bot)`', inline = True)
    embed.add_field(name = '!dm [@miembro] [mensaje]', value = '`Enviar un mensaje privado a algun miembro. (Administrador)`', inline = True)
    embed.add_field(name = '!close', value = '`Cerrar un ticket. (Administrador)`', inline = True)
    embed.add_field(name = '!add [@miembro]', value = '`Agregar a un miembro a un ticket. (Administrador)`', inline = True)
    embed.add_field(name = '!remove [@miembro]', value = '`Remover a un miembro de un ticket. (Administrador)`', inline = True)
    embed.add_field(name = '!claim', value = '`Reclamar un ticket. (Administrador)`', inline = True)
    embed.add_field(name = '!unclaim', value = '`Relevar un ticket. (Administrador)`', inline = True)
    embed.add_field(name = '!rename [nombre]', value = '`Renombrar un ticket. (Administrador)`', inline = True)
    embed.add_field(name = '!tickets', value = '`Ver cantidad de tickets abiertos.`', inline = True)
    embed.add_field(name = '!prefix [prefix]', value = '`Ver o cambiar  el prefijo del bot.`', inline = True)
    embed.add_field(name = '!help', value = '`Ver la lista de comandos.`', inline = True)
    embed.set_footer(text = soft_user, icon_url = soft_avatar)
    
    await ctx.send(embed = embed)

""" Modding commands """
@bot.command()
@commands.has_role(staff_role)
async def clear(ctx, amount: int = None):
    if amount is not None:
        await ctx.channel.purge(limit = amount + 1)
        embed = discord.Embed(title = 'Mensajes borrados!', description = f'{amount} mensajes fueron borrados por {ctx.author.mention}', color = red)
    else:
        embed = discord.Embed(title = 'Mensajes borrados!', description = f'{purge_default} mensajes fueron borrados por {ctx.author.mention}', color = red)
    embed.set_footer(text = soft_user, icon_url = soft_avatar)
    await ctx.send(embed = embed, delete_after = 5)

""" Views """
class TicketSelect(discord.ui.Select):
    def __init__(self):
        categories = {
            'labels': [ 'Reporte', 'Dudas', 'Donacion', 'Otros' ],
            'descriptions': [ 'Crea un ticket de Reporte!', 'Crea un ticket de Dudas!', 'Crea un ticket de Donaciones!', 'Crea un ticket de Otros!' ],
            'emojis': [ '<:redlock:934441253393793054>', '<:question_mark:934442243253755904>', '<:drawn_coin:934443133310234685>', '🎟️' ]
        }

        options = [ discord.SelectOption(label = x, description = categories['descriptions'][categories['labels'].index(x)], emoji = categories['emojis'][categories['labels'].index(x)]) for x in categories['labels'] ]
    
        super().__init__(placeholder = '🎫 Selecciona tu ticket!', min_values = 1, max_values = 1, options = options)
        
    async def callback(self, interaction: discord.Interaction):
        cursor.execute('SELECT MAX(ticket_id) AS ticket_id FROM tickets')
        result = cursor.fetchall()
        result = str(result)
        characters = [ '[', ']', '(', ')', ',' ]
        for character in characters:
            if character in result:
                result = result.replace(character, '')
        new_ticket = int(result) + 1
        channel = get(guild.text_channels, name = f'ticket-{new_ticket}')
        query = 'INSERT INTO tickets (ticket_creator, ticket_creator_id) VALUES (%s, %s)'
        values = (str(interaction.user), interaction.user.id)
        cursor.execute(query, values)
        connection.commit()
        if channel is None:
            if self.values[0] == 'Reporte':
                category = get(guild.categories, name = 'Reporte')
                channel = await guild.create_text_channel(f'ticket-{new_ticket}', category = category)
                connection.commit()
                await channel.set_permissions(interaction.user, view_channel = True)
            elif self.values[0] == 'Dudas':
                category = get(guild.categories, name = 'Dudas')
                channel = await guild.create_text_channel(f'ticket-{new_ticket}', category = category)
                await channel.set_permissions(interaction.user, view_channel = True)
            elif self.values[0] == 'Donacion':
                category = get(guild.categories, name = 'Donacion')
                channel = await guild.create_text_channel(f'ticket-{new_ticket}', category = category)
                await channel.set_permissions(interaction.user, view_channel = True)
            elif self.values[0] == 'Otros':
                category = get(guild.categories, name = 'Otros')
                channel = await guild.create_text_channel(f'ticket-{new_ticket}', category = category)
                await channel.set_permissions(interaction.user, view_channel = True)
            embed = discord.Embed(title = f'{self.values[0]}', description = f'Bienvenido, {interaction.user.mention}! Mientras esperas a que te conteste algun miembro de nuestro staff explicanos tu duda. :)', color = red)
            embed.set_footer(text = soft_user, icon_url = soft_avatar)
            await channel.send(embed = embed, view = TicketButtons())
        
        if enable_logs:
            log_channel = bot.get_channel(log_channel_id)
            log = discord.Embed(title = f'Ticket de {self.values[0]} creado', description = f'{interaction.user.mention} creo un ticket de {self.values[0]}', color = red, timestamp = datetime.now(timezone('America/Argentina/Buenos_Aires')))
            await log_channel.send(embed = log)

        await softFunctions.send_dm(interaction.user, embed = True, title = 'Tickets', description = f'Abriste un ticket de {self.values[0]} en {interaction.guild.name}!', color = red, thumbnail = None, image = None, author = None, file = None)
        await interaction.response.send_message(f'Se ha abierto tu ticket de {self.values[0]}', ephemeral = True)
        
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)
        self.add_item(TicketSelect())
        
class TicketButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)
        self.value = None
    
    @discord.ui.button(label = 'Reclamar', style = discord.ButtonStyle.blurple, emoji = '📌')
    async def claim(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name = staff_role)
        if role in interaction.user.roles:
            await interaction.response.send_message('Reclamando...', ephemeral = True)
            embed = discord.Embed(title = ' Ticket reclamado!', description = f'{interaction.user.mention} reclamo el ticket!', color = red)
            embed.set_footer(text = soft_user, icon_url = soft_avatar)
            await interaction.channel.send(embed = embed)
            if enable_logs:
                log_channel = bot.get_channel(log_channel_id)
                embed = discord.Embed(title = ' Ticket reclamado!', description = f'{interaction.user.mention} reclamo el {interaction.channel.name}!', color = red, timestamp = datetime.now(timezone('America/Argentina/Buenos_Aires')))
                await log_channel.send(embed = embed)
    
    @discord.ui.button(label = 'Cerrar', style = discord.ButtonStyle.red, emoji = '🔒')
    async def close(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = discord.Embed(title = 'Cerrando...', description = 'Se esta cerrando el ticket', color = red)
        embed.set_footer(text = soft_user, icon_url = soft_avatar)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        cursor.execute(f"UPDATE tickets SET closed = 1 WHERE ticket_id = {int(interaction.channel.name.split('-')[-1])}")
        connection.commit()
        if enable_logs:
            log_channel = bot.get_channel(log_channel_id)
            log = discord.Embed(title = 'Ticket cerrado', description = 'Se esta cerrando el ticket', color = red, timestamp = datetime.now(timezone('America/Argentina/Buenos_Aires')))
            cursor.execute(f"SELECT ticket_creator_id FROM tickets WHERE ticket_id = {int(interaction.channel.name.split('-')[-1])}")
            creator = str(cursor.fetchall())
            characters = [ '[', ']', '(', ')', ',' ]
            for character in characters:
                if character in creator:
                    creator = creator.replace(character, '')
            creator = interaction.guild.get_member(int(creator))
            transcript = await chat_exporter.export(interaction.channel)
            if transcript is None:
                return
            transcript_file = discord.File(io.BytesIO(transcript.encode()), filename = f'transcript-{interaction.channel.name}.html')
            await log_channel.send(embed = log, file = transcript_file)
            
        transcript = await chat_exporter.export(interaction.channel)
        transcript_file = discord.File(io.BytesIO(transcript.encode()), filename = f'transcript-{interaction.channel.name}.html')
        await softFunctions.send_dm(creator, embed = True, title = interaction.channel.name, description = 'Aca esta tu transcript :)', color = red, thumbnail = None, image = None, author = None, file = transcript_file)
        await interaction.channel.delete()
    
# Run bot
bot.run(token)