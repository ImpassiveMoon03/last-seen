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
  if member is None:
    c = conn.execute('SELECT status,change FROM members WHERE id = ?', [ctx.author.id])
    q = c.fetchone()
    delta = dt.timedelta(milliseconds = time.time()*1000 - q[1])
    if q[0] == 'offline':
      await ctx.send(F"Last seen {humanize.precisedelta(delta)} ago")
    elif q[0] == 'idle':
      await ctx.send(F"Idle for {humanize.precisedelta(delta)}")
    elif q[0] == 'dnd':
      await ctx.send(F"In do not disturb for {humanize.precisedelta(delta)}")
    elif q[0] == 'online':
      await ctx.send(F"Online for {humanize.precisedelta(delta)}")
  else:
    id = member.id
    c = conn.execute('SELECT status,change FROM members WHERE id = ?', [id])
    q = c.fetchone()
    delta = dt.timedelta(milliseconds = time.time()*1000 - q[1])
    if q[0] == 'offline':
      await ctx.send(F"Last seen {humanize.precisedelta(delta)} ago")
    elif q[0] == 'idle':
      await ctx.send(F"Idle for {humanize.precisedelta(delta)}")
    elif q[0] == 'dnd':
      await ctx.send(F"In do not disturb for {humanize.precisedelta(delta)}")
    elif q[0] == 'online':
      await ctx.send(F"Online for {humanize.precisedelta(delta)}")

client.run(os.environ.get('TOKEN'))