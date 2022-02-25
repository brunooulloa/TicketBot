from termcolor import colored
import discord, sys, os, json, mysql.connector

""" Get current directory function """
def cwd(file: str):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), file)

""" Get config.json """
with open(cwd('config.json'), 'r') as config: 
    data = json.load(config)
    owner_id = data['owner_id']
    guild_id = data['guild_id']
    staff_role = data['staff']['name']
    staff_role_id = data['staff']['id']
    database = data['database']
    if enable_logs := data['logs']['enabled']:
        log_channel_id = data['logs']['channel_id']
        
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

""" Classes """

class softFunctions:
    async def send_dm(member: discord.Member, **kwargs):
        channel = await member.create_dm()
        
        if kwargs['embed']:
            embed = discord.Embed(title = kwargs["title"], description = kwargs['description'], color = kwargs['color'])
            embed.set_footer(text = 'Made by Soft#6666', icon_url = 'https://images-ext-2.discordapp.net/external/p0KE48w9Lt_6PsiIu3hhU8zHgF-9LLEmk8tbUmNLPoU/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/293148087407476737/a_d0cbdc184155c678ea1ad107163a324b.gif')
            
            if kwargs['thumbnail'] is not None:
                embed.set_thumbnail(url = kwargs['thumbnail'])
                
            if kwargs['image'] is not None:
                embed.set_image(url = kwargs['image'])
                
            if kwargs['author'] is not None:
                embed.set_author(name = kwargs['author'].display_name, icon_url = kwargs['author'].avatar_url)
                
            if kwargs['file'] is not None:
                await channel.send(embed = embed, file = kwargs['file'])
            else:
                await channel.send(embed = embed)
        elif kwargs['file']:
            if kwargs['file_path'] is not None:
                await channel.send(file = kwargs['file_path'], content = kwargs['content'])
        else:
            await channel.send(kwargs['content'])
    
    def get_prefix(client, message):
        with open(cwd('prefixes.json'), 'r') as f:
            prefixes = json.load(f)
        return prefixes[str(message.guild.id)]
    
    def uwu_print(text: str):
        print(colored('[+]', 'red'), colored('[uwu]', 'magenta'), text)
    
    def owo_print(text: str):
        print(colored('[!]', 'green'), colored('[owo]', 'blue'), text)
    
    def bot_print(bot, text: str):
        print(colored('[-]', 'yellow'), colored(f'[{bot.user}]', 'cyan'), text)
    
    def restart_bot():
        python = sys.executable
        os.execl(python, python, * sys.argv)

    def soft():
        print(colored('''
   _____ ____  ____________
  / ___// __ \/ ____/_  __/
  \__ \/ / / / /_    / /   
 ___/ / /_/ / __/   / /    
/____/\____/_/     /_/ ''', 'cyan'))