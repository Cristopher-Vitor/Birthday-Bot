import discord 
from discord.ext import commands
from discord.ext import tasks
from discord import Interaction
from datetime import datetime
from discord import File
from dotenv import load_dotenv
import os

load_dotenv()

#import do banco de dados
from db import Sessao_base, Aniversariantes

permissoes = discord.Intents.default()
permissoes.message_content = True
permissoes.members = True
bot = commands.Bot(command_prefix="!", intents=permissoes)

eventos = {}

#Adiciona um aniversariante no banco de dados
async def adicionar_aniversariante(nome: str, data: str):
  session = Sessao_base()
  aniversariante_existente = (session.query(Aniversariantes).filter(Aniversariantes.nome == nome, Aniversariantes.data == data).first())

  if aniversariante_existente:
    session.close()
    return False
  else:
    novo_aniversariante = Aniversariantes(nome=nome, data=data)
    session.add(novo_aniversariante)
    session.commit()
    session.close()
    return True

@bot.tree.command(description="Adiciona uma data de aniversário no formato dia/mes. Exemplo: 30/06")
async def set_date(interact:discord.Interaction, data:str):
  user = interact.user.name
  try:
    datetime.strptime(data, "%d/%m")
    aniversariante_adicionado = await adicionar_aniversariante(user,data) 
    if aniversariante_adicionado:
      await interact.response.send_message("Aniversariante adicionado!", ephemeral=True)
  except ValueError:
    await interact.response.send_message("Formato de data inválido! Use o formato Dia/Mês. Exemplo: 30/06", ephemeral=True)


async def listar_aniversariantes():
  session = Sessao_base()
  aniversariantes = session.query(Aniversariantes).all()
  session.close()
  return aniversariantes

@bot.tree.command(description="Mostra a lista de aniversariantes")
async def list(interact:discord.Interaction):
  aniversariantes = await listar_aniversariantes()
  if aniversariantes:
    aniversariantes_ordenados = sorted(aniversariantes, key=lambda aniv: datetime.strptime(aniv.data, "%d/%m"))
    lista = [f"{aniv.data}: {aniv.nome}" for aniv in aniversariantes_ordenados]      
    lista_str = "\n".join(lista)
    await interact.response.send_message(f"Lista de aniversariantes:\n{lista_str}", ephemeral=True)
  else:
    await interact.response.send_message("Não há aniversariantes registrados.", ephemeral=True)


async def buscar_aniversariantes_por_data(data: str):
  session = Sessao_base()
  aniversariantes = session.query(Aniversariantes).filter(Aniversariantes.data == data).all()
  session.close()
  return aniversariantes

def custom_message(nomes: str) -> discord.Embed:
  meu_embed = discord.Embed(title="Tem aniversariante na área! 👀",color=discord.Color.yellow(), description=f"Hoje é aniversário de: {nomes}! Parabéns! Feliz aniversário! 🥳🎉🎈")

  imagem_aniversario = discord.File("birthday.jpg", "imagem.jpg")
  meu_embed.set_image(url="attachment://imagem.jpg")

  return meu_embed, imagem_aniversario


async def editar_aniversario(nova_data: str, nome: str):
    session = Sessao_base()
    aniversariante = (session.query(Aniversariantes).filter(Aniversariantes.nome == nome).first())

    if aniversariante:
        aniversariante.data = nova_data
        session.commit()
        session.close()
        return True
    else:
        session.close()
        return False

@bot.tree.command(description="Edita a data de aniversário de um usuário.")
async def edit(interact: discord.Interaction, nova_data: str):
  user = interact.user.name
  try:
      datetime.strptime(nova_data, "%d/%m")
      sucesso = await editar_aniversario(nova_data, user)
      if sucesso:
          await interact.response.send_message(f"Aniversário de {user} editado para {nova_data}!", ephemeral=True)
      else:
          await interact.response.send_message(f"Não encontrei o aniversariante {user}.", ephemeral=True)
  except ValueError:
      await interact.response.send_message("Formato de data inválido! Use o formato Dia/Mês. Exemplo: 30/06", ephemeral=True)

#Verifica se tem algum aniversariante no dia atual
@tasks.loop(seconds=60)
async def verificar_data():
  agora = datetime.now()
  data_hoje = agora.strftime("%d/%m")
  horario_atual = agora.strftime("%H:%M")

  if horario_atual == "00:00":
    aniversariantes = await buscar_aniversariantes_por_data(data_hoje)
    if aniversariantes:
      canal = bot.get_channel(1320497553124491266)
      if canal:
        nomes = ", ".join(aniv.nome for aniv in aniversariantes)
        embed,imagem = custom_message(nomes)
        await canal.send("@everyone")
        await canal.send(embed=embed, file=imagem)
      
@bot.event
async def on_ready():
  await bot.tree.sync()
  verificar_data.start()

token = os.getenv("DISCORD_TOKEN")
bot.run(token)  