import os
import json
import asyncio
import random
import time
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# Pega o token do bot a partir da variável de ambiente
TOKEN = os.getenv("DISCORD_TOKEN")

# Configura os intents do bot
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} está online!')

# Função para manter o bot ativo
async def keep_alive():
    while True:
        await asyncio.sleep(30)  # Mantém o bot ativo

# Configura o loop de eventos para manter o bot ativo
loop = asyncio.get_event_loop()
loop.create_task(keep_alive())

# Carrega as variáveis de ambiente
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Configurações do bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Necessário para acessar os cargos dos membros
bot = commands.Bot(command_prefix=["rpg!", "RPG!"], intents=intents)

# IDs dos cargos dos clãs
CLAS = {
    "1351416037454909471": {"nome": "Draconis 🐉", "emoji": "🐉", "cor": 0xFF0000, "foto": "https://exemplo.com/draconis.jpg"},
    "1351416382163652670": {"nome": "Tempus ⏳", "emoji": "⏳", "cor": 0x00FF00, "foto": "https://exemplo.com/tempus.jpg"},
    "1351416442636996751": {"nome": "Lunaris 🌙", "emoji": "🌙", "cor": 0x0000FF, "foto": "https://exemplo.com/lunaris.jpg"},
    "1351416527047622747": {"nome": "Solgarde 🔆", "emoji": "🔆", "cor": 0xFFFF00, "foto": "https://exemplo.com/solgarde.jpg"}
}

# Carrega os dados do arquivo JSON
def carregar_dados():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "clãs": {
                "1351416037454909471": {"nome": "Draconis 🐉", "pontos": 0, "membro_destaque": None, "foto": "https://exemplo.com/draconis.jpg"},
                "1351416382163652670": {"nome": "Tempus ⏳", "pontos": 0, "membro_destaque": None, "foto": "https://exemplo.com/tempus.jpg"},
                "1351416442636996751": {"nome": "Lunaris 🌙", "pontos": 0, "membro_destaque": None, "foto": "https://exemplo.com/lunaris.jpg"},
                "1351416527047622747": {"nome": "Solgarde 🔆", "pontos": 0, "membro_destaque": None, "foto": "https://exemplo.com/solgarde.jpg"}
            },
            "usuários": {},
            "último_uso": {}
        }

# Salva os dados no arquivo JSON
def salvar_dados(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

# Função para obter o clã do usuário com base nos cargos
def obter_clã(membro):
    for role in membro.roles:
        if str(role.id) in CLAS:
            return str(role.id)
    return None

# Comando: rpg!dado com cooldown de 35 segundos
@bot.command(name="dado")
@commands.cooldown(1, 35, commands.BucketType.user)  # Define o cooldown de 35 segundos para cada usuário
async def rolar_dado(ctx):
    try:
        # Aqui vem o código normal do comando
        data = carregar_dados()
        clã_id = obter_clã(ctx.author)

        if not clã_id:
            await ctx.send("Você não está em um clã!")
            return

        resultado = random.randint(1, 6)

        # Probabilidade de o dado cair da mesa (10% de chance)
        cair_da_mesa = random.random() < 0.1  # 10% de chance

        if cair_da_mesa:
            # Caso o dado caia da mesa, o clã perde pontos entre 20 a 60
            pontos_perdidos = random.randint(20, 60)
            data["clãs"][clã_id]["pontos"] = max(0, data["clãs"][clã_id]["pontos"] - pontos_perdidos)  # Evita que o clã fique com pontos negativos

            embed = discord.Embed(
                title="🎲 Dado Caiu da Mesa!",
                description=f"🫳🏽 O dado caiu da mesa! O clã **{CLAS[clã_id]['nome']}** perdeu **{pontos_perdidos} pontos**.",
                color=CLAS[clã_id]["cor"]
            )
            embed.set_thumbnail(url=CLAS[clã_id]["foto"])
            await ctx.send(embed=embed)
            return

        # Se o dado não cair da mesa, ele segue com a rolagem normal
        pontos = {
            1: 5,  # 1 → 5 pontos
            2: 9,  # 2 → 9 pontos
            3: 13,  # 3 → 13 pontos
            4: 19,  # 4 → 19 pontos
            5: 28,  # 5 → 28 pontos
            6: 40  # 6 → 40 pontos
        }.get(resultado)

        # Atualiza os pontos do clã
        data["clãs"][clã_id]["pontos"] += pontos
        salvar_dados(data)

        embed = discord.Embed(
            title="🎲 Resultado do Dado",
            description=f"🎲 Você rolou e o dado caiu no número **{resultado}**\n"
                        f"🍀 Seu ganho foi de **{pontos} pontos** para o clã **{CLAS[clã_id]['nome']}**!",
            color=CLAS[clã_id]["cor"]
        )
        embed.set_thumbnail(url=CLAS[clã_id]["foto"])
        await ctx.send(embed=embed)

    except Exception as e:
        # Tratar erros genéricos caso ocorram
        await ctx.send(f"Erro ao processar o comando: {str(e)}")

# Caso o comando esteja em cooldown, envia a mensagem
@rolar_dado.error
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        cooldown_time = round(error.retry_after, 1)
        await ctx.send(f"🕐 Lanças dados rapidos desgasta os dedos, espere **{cooldown_time} segundos** para jogar novamente.")

# Comando: rpg!benção
@bot.command(name="benção")
async def benção(ctx):
        jogadores = carregar_jogadores()  # Carrega as informações dos jogadores
        clã_id = obter_clã(ctx.author)

        if not clã_id:
            await ctx.send("🧔🏽Lucaido: Você não está em um clã!")
            return

        # Obtém as informações do jogador
        jogador = jogadores.get(str(ctx.author.id), {"ultimo_uso_bencao": 0})

        último_uso = jogador["ultimo_uso_bencao"]
        if time.time() - último_uso < 86400:  # 24 horas em segundos
            await ctx.send("🕐 Você só pode usar este comando uma vez a cada 24 horas!")
            return

        pontos = random.randint(40, 80)
        data = carregar_dados()  # Carrega os dados dos clãs
        data["clãs"][clã_id]["pontos"] += pontos

        # Atualiza a data do último uso da benção no arquivo jogadores.json
        jogador["ultimo_uso_bencao"] = time.time()
        jogadores[str(ctx.author.id)] = jogador
        salvar_jogadores(jogadores)
        salvar_dados(data)

        embed = discord.Embed(
            title="🙏 Benção Recebida",
            description=f"🍀 O clã **{CLAS[clã_id]['nome']}** recebeu uma benção de **{pontos} pontos**!",
            color=CLAS[clã_id]["cor"]
        )
        embed.set_thumbnail(url=CLAS[clã_id]["foto"])
        await ctx.send(embed=embed)

# Carrega os dados dos jogadores do arquivo JSON
def carregar_jogadores():
    try:
        with open("jogadores.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Salva os dados dos jogadores no arquivo JSON
def salvar_jogadores(jogadores):
    with open("jogadores.json", "w") as f:
        json.dump(jogadores, f, indent=4)

# Comando: rpg!perfil
@bot.command(name="perfil")
async def perfil(ctx):
    data = carregar_dados()
    clã_id = obter_clã(ctx.author)

    if not clã_id:
        await ctx.send("Você não está em um clã!")
        return

    clã = data["clãs"][clã_id]
    embed = discord.Embed(
        title=f"👤 Perfil do Jogador",
        description=f"Clã: **{clã['nome']}** {CLAS[clã_id]['emoji']}\n"
                    f"Pontos Atuais: **{clã['pontos']}**\n"
                    f"Membro Destaque: **{clã['membro_destaque'] or 'Nenhum'}**",
        color=CLAS[clã_id]["cor"]
    )
    embed.set_thumbnail(url=ctx.author.avatar.url)
    embed.set_image(url=CLAS[clã_id]["foto"])
    await ctx.send(embed=embed)

# Comando: rpg!rank
@bot.command(name="rank")
async def rank(ctx):
    data = carregar_dados()
    clãs_ordenados = sorted(data["clãs"].items(), key=lambda x: x[1]["pontos"], reverse=True)

    ranking = ""
    for i, (clã_id, clã) in enumerate(clãs_ordenados, start=1):
        emoji = "🏆" if i == 1 else "🔹"
        ranking += f"{emoji} **{i}º Lugar**: {clã['nome']} - **{clã['pontos']} pontos**\n"

    embed = discord.Embed(
        title="🏆 Ranking de Clãs",
        description=ranking,
        color=0x00FF00
    )
    await ctx.send(embed=embed)

# Comando: rpg!membros
@bot.command(name="membros")
async def membros(ctx):
    clã_id = obter_clã(ctx.author)

    if not clã_id:
        await ctx.send("Você não está em um clã!", ephemeral=True)
        return

    membros_clã = [membro.display_name for membro in ctx.guild.members if clã_id in [str(role.id) for role in membro.roles]]
    lista_membros = "\n".join(membros_clã) if membros_clã else "Nenhum membro encontrado."

    embed = discord.Embed(
        title=f"👥 Membros do Clã {CLAS[clã_id]['nome']}",
        description=lista_membros,
        color=CLAS[clã_id]["cor"]
    )
    await ctx.send(embed=embed, ephemeral=True)

# Comando: rpg!roubar
@bot.command(name="roubar")
async def roubar(ctx, cargo_alvo: discord.Role):
        data = carregar_dados()
        clã_id = obter_clã(ctx.author)

        if not clã_id:
            await ctx.send("❌ Você não está em um clã!")
            return

        # Verifica se o cargo mencionado é um clã válido
        if str(cargo_alvo.id) not in CLAS:
            await ctx.send("❌ Cargo inválido! O cargo mencionado não é um clã.")
            return

        clã_alvo_id = str(cargo_alvo.id)

        # Verifica se o clã alvo é o mesmo do usuário
        if clã_alvo_id == clã_id:
            await ctx.send("⚔️ Seria covardia roubar seu próprio clã! Não tente novamente.")
            return

        # Verifica se o clã alvo tem pontos para serem roubados
        if data["clãs"][clã_alvo_id]["pontos"] == 0:
            await ctx.send(f"❌ O clã **{CLAS[clã_alvo_id]['nome']}** não tem pontos para serem roubados! Eles ainda são pobres. Mas cuidado, o jogo pode virar!")
            return

        pontos_roubados = random.randint(10, 30)
        pontos_disponíveis = data["clãs"][clã_alvo_id]["pontos"]

        # Garante que o clã alvo nunca fique com pontos negativos
        pontos_roubados = min(pontos_roubados, pontos_disponíveis)

        sucesso = random.random() < 0.5  # 50% de chance de sucesso

        if sucesso:
            data["clãs"][clã_id]["pontos"] += pontos_roubados
            data["clãs"][clã_alvo_id]["pontos"] = max(0, data["clãs"][clã_alvo_id]["pontos"] - pontos_roubados)  # Evita que o clã alvo tenha pontos negativos
            mensagem = f"🕵️‍♂️ Você roubou **{pontos_roubados} pontos** do clã **{CLAS[clã_alvo_id]['nome']}**!"
        else:
            data["clãs"][clã_id]["pontos"] -= pontos_roubados
            mensagem = f"😄 Parece que você não serve para roubar! Seu clã perdeu **{pontos_roubados} pontos**."

        salvar_dados(data)

        embed = discord.Embed(
            title="🕵️‍♂️ Roubo de Pontos",
            description=mensagem,
            color=CLAS[clã_id]["cor"]
        )
        await ctx.send(embed=embed)


#Comandos para ver comandos

@bot.command(name="ajuda")
async def ajuda(ctx):
    embed = discord.Embed(
        title="🛠️ Comandos do ValoriaRPG",
        description="Aqui está a lista de todos os comandos disponíveis e como usá-los:",
        color=0x00FF00
    )

    # Comando: rpg!dado
    embed.add_field(
        name="🎲 **rpg!dado**",
        value="**O que faz?** Rola um dado e adiciona pontos ao seu clã com base no resultado.\n"
              "**Como usar?** Digite `rpg!dado`.\n"
              "**Exemplo:** `rpg!dado`",
        inline=False
    )

    # Comando: rpg!benção
    embed.add_field(
        name="🙏 **rpg!benção**",
        value="**O que faz?** Concede uma benção de 40 a 80 pontos ao seu clã. Disponível a cada 24 horas.\n"
              "**Como usar?** Digite `rpg!benção`.\n"
              "**Exemplo:** `rpg!benção`",
        inline=False
    )

    # Comando: rpg!perfil
    embed.add_field(
        name="👤 **rpg!perfil**",
        value="**O que faz?** Exibe o perfil do jogador, com informações sobre o clã, pontos e membro destaque.\n"
              "**Como usar?** Digite `rpg!perfil`.\n"
              "**Exemplo:** `rpg!perfil`",
        inline=False
    )

    # Comando: rpg!rank
    embed.add_field(
        name="🏆 **rpg!rank**",
        value="**O que faz?** Mostra o ranking dos clãs com base nos pontos acumulados.\n"
              "**Como usar?** Digite `rpg!rank`.\n"
              "**Exemplo:** `rpg!rank`",
        inline=False
    )

    # Comando: rpg!membros
    embed.add_field(
        name="👥 **rpg!membros**",
        value="**O que faz?** Lista todos os membros do seu clã. A mensagem é visível apenas para você.\n"
              "**Como usar?** Digite `rpg!membros`.\n"
              "**Exemplo:** `rpg!membros`",
        inline=False
    )

    # Comando: rpg!roubar
    embed.add_field(
        name="🕵️‍♂️ **rpg!roubar**",
        value="**O que faz?** Tenta roubar pontos de outro clã. Pode roubar entre 10 a 30 pontos, mas há risco de falha.\n"
              "**Como usar?** Digite `rpg!roubar @cargo_do_clã`.\n"
              "**Exemplo:** `rpg!roubar @Tempus ⏳`",
        inline=False
    )

    # Comando: rpg!ajuda
    embed.add_field(
        name="🛠️ **rpg!ajuda**",
        value="**O que faz?** Exibe esta mensagem de ajuda com todos os comandos disponíveis.\n"
              "**Como usar?** Digite `rpg!ajuda`.\n"
              "**Exemplo:** `rpg!ajuda`",
        inline=False
    )

    embed.set_footer(text="ValoriaRPG - Um bot para gerenciar clãs e diversão no Discord!")
    await ctx.send(embed=embed)


# Evento: Bot está pronto
@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} está online!')

# Inicia o bot
bot.run(TOKEN)