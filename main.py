import discord
from discord.ext import commands
from sqlite3 import connect
import time
import humanize
import datetime as dt
import os

conn = connect('last.db')

conn.execute("""
  CREATE TABLE IF NOT EXISTS members(
    id integer UNIQUE,
    status text,
    change int
  )
""")

intents = discord.Intents.default()
intents.members = True
intents.presences = True
client = commands.Bot(command_prefix="o!", intents=intents)

@client.event
async def on_ready():
  print('Bot online')
  for i in client.users:
    if i.bot == True:
      pass
    else:
      if len(i.mutual_guilds) == 0:
        pass
      else:
        member = i.mutual_guilds[0].get_member(i.id)
        print(member)
        c = conn.execute('SELECT id FROM members')
        q = c.fetchall()
        ids = []
        for w in q:
          ids.append(w[0])
        if member.id in ids:
          print(time.time() * 1000)
          conn.execute(
            'UPDATE members SET status = ?, change = ? WHERE id = ?',
            [str(member.status), (time.time()*1000), member.id]
          )
          conn.commit()
        else:
          conn.execute(
            'INSERT INTO members(id,status,change) VALUES(?,?,?)',
            [member.id, str(member.status), (time.time()*1000)]
          )
          conn.commit()

@client.event
async def on_member_update(before, after):
  print(str(after.status))
  conn.execute(
    "UPDATE members SET id = ?, status = ?, change = ? WHERE id = ?",
    [after.id, str(after.status), (time.time()*1000), after.id]
  )
  conn.commit()

@client.command()
async def member(ctx, member:discord.Member = None):
  async with ctx.channel.typing():
    mem = ctx.author if not member else member
    c = conn.execute('SELECT status,change FROM members WHERE id = ?', [mem.id])
    q = c.fetchone()
    delta = dt.timedelta(milliseconds = time.time()*1000 - q[1])
    createDelta = dt.timedelta(milliseconds = time.time()*1000 - mem.created_at.timestamp()*1000)
    creation = F"{mem.created_at.strftime('%B')} {mem.created_at.strftime('%d')}, {mem.created_at.strftime('%Y')}"
    if q[0] == 'offline':
      embed = discord.Embed(
        title = mem.name,
        description = F"**Account Creation:** {creation} - {humanize.precisedelta(createDelta, minimum_unit='months', format='%0.0f')}\nLast seen {humanize.precisedelta(delta)} ago"
      )
      await ctx.send(embed=embed)
    elif q[0] == 'idle':
      embed = discord.Embed(
        title = mem.name,
        description = F"**Account Creation:** {creation} - {humanize.precisedelta(createDelta, minimum_unit='months', format='%0.0f')}\nIdle for {humanize.precisedelta(delta)}"
      )
      await ctx.send(embed=embed)
    elif q[0] == 'dnd':
      embed = discord.Embed(
        title = mem.name,
        description = F"**Account Creation:** {creation} - {humanize.precisedelta(createDelta, minimum_unit='months', format='%0.0f')}\nIn do not disturb for {humanize.precisedelta(delta)}"
      )
      await ctx.send(embed=embed)
    elif q[0] == 'online':
      embed = discord.Embed(
        title = mem.name,
        description = F"**Account Creation:** {creation} - {humanize.precisedelta(createDelta, minimum_unit='months', format='%0.0f')}\nOnline for {humanize.precisedelta(delta)}"
      )
      await ctx.send(embed=embed)

client.run(os.environ.get('TOKEN'))