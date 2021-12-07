import discord
from discord.ext import commands
from sqlite3 import connect
import time
import humanize
import datetime as dt
import os
import sanic



class Client(commands.Bot):
  def __init__(self):
    super().__init__("o!", intents=discord.Intents.all())
    self.conn = connect("last.db")
    self.conn.execute("""
      CREATE TABLE IF NOT EXISTS members(
        id integer UNIQUE,
        status text,
        change int
      )
    """)

  async def on_ready(self):
    print('Bot online')
    for i in self.users:
      if i.bot == True:
        pass
      else:
        if len(i.mutual_guilds) == 0:
          pass
        else:
          member = i.mutual_guilds[0].get_member(i.id)
          print(member)
          c = self.conn.execute('SELECT id FROM members')
          q = c.fetchall()
          ids = []
          for w in q:
            ids.append(w[0])
          if member.id in ids:
            print(time.time() * 1000)
            self.conn.execute(
              'UPDATE members SET status = ?, change = ? WHERE id = ?',
              [str(member.status), (time.time()*1000), member.id]
            )
            self.conn.commit()
          else:
            self.conn.execute(
              'INSERT INTO members(id,status,change) VALUES(?,?,?)',
              [member.id, str(member.status), (time.time()*1000)]
            )
            self.conn.commit()

  async def on_member_update(self, before, after):
    self.conn.execute(
      "UPDATE members SET id = ?, status = ?, change = ? WHERE id = ?",
      [after.id, str(after.status), (time.time()*1000), after.id]
    )
    self.conn.commit()

  async def on_member_join(self, member):
    if member.user.bot is True:
      pass
    else:
      c = self.conn.execute("SELECT id FROM members WHERE id = ?", [member.id])
      q = c.fetchone()
      if q is None:
        self.conn.execute(
          'INSERT INTO members(id,status,change) VALUES(?,?,?)',
          [member.id, str(member.status), (time.time()*1000)]
        )
        self.conn.commit()


client = Client()

@client.command()
async def member(ctx, member:discord.Member = None):
  async with ctx.channel.typing():
    mem = ctx.author if not member else member
    c = client.conn.execute('SELECT status,change FROM members WHERE id = ?', [mem.id])
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

client.run("TOKEN")
