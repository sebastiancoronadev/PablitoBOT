import discord
from discord.ext import commands
import sqlite3
import datetime

# Cog para estadisticas de voz
class VoiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = bot.db_path
        self.voice_sessions = {}

    # Evento para detectar entrada/salida de canales de voz
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            if before.channel:
                await self.end_voice_session(member.id, before.channel.guild.id)
            if after.channel:
                await self.start_voice_session(member.id, after.channel.guild.id, after.channel.id)

    # Iniciar sesion de voz
    async def start_voice_session(self, user_id, guild_id, channel_id):
        current_time = datetime.datetime.utcnow()
        self.voice_sessions[user_id] = (guild_id, channel_id, current_time)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO voice_stats (user_id, guild_id, last_voice_join) VALUES (?, ?, ?)', (user_id, guild_id, current_time.isoformat()))
        c.execute('UPDATE voice_stats SET last_voice_join = ? WHERE user_id = ? AND guild_id = ?', (current_time.isoformat(), user_id, guild_id))
        conn.commit()
        conn.close()

    # Terminar sesion de voz
    async def end_voice_session(self, user_id, guild_id):
        if user_id not in self.voice_sessions:
            return
        guild_id_temp, channel_id, join_time = self.voice_sessions[user_id]
        current_time = datetime.datetime.utcnow()
        delta = (current_time - join_time).total_seconds()
        if delta < 1:
            del self.voice_sessions[user_id]
            return
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('UPDATE voice_stats SET total_seconds = total_seconds + ?, daily_seconds = daily_seconds + ?, weekly_seconds = weekly_seconds + ? WHERE user_id = ? AND guild_id = ?', (int(delta), int(delta), int(delta), user_id, guild_id))
        conn.commit()
        conn.close()
        del self.voice_sessions[user_id]

    # Ver estadisticas de voz de un usuario
    @commands.command(name='voicestats')
    async def voice_stats_command(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT total_seconds, daily_seconds, weekly_seconds FROM voice_stats WHERE user_id = ? AND guild_id = ?', (member.id, ctx.guild.id))
        result = c.fetchone()
        conn.close()
        if not result:
            await ctx.send(f"{member.display_name} no tiene estadisticas.")
            return
        total_sec, daily_sec, weekly_sec = result
        embed = discord.Embed(title=f"Estadisticas de voz - {member.display_name}", color=member.color)
        embed.add_field(name="Total", value=f"{int(total_sec)}s", inline=True)
        embed.add_field(name="Diario", value=f"{int(daily_sec)}s", inline=True)
        embed.add_field(name="Semanal", value=f"{int(weekly_sec)}s", inline=True)
        await ctx.send(embed=embed)

    # Ranking de actividad en voz
    @commands.command(name='voicetop')
    async def voice_top_command(self, ctx, limit: int = 10):
        if limit > 20:
            limit = 20
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT user_id, total_seconds FROM voice_stats WHERE guild_id = ? ORDER BY total_seconds DESC LIMIT ?', (ctx.guild.id, limit))
        results = c.fetchall()
        conn.close()
        if not results:
            await ctx.send("No hay datos.")
            return
        embed = discord.Embed(title="Ranking de actividad en voz", color=discord.Color.gold())
        for i, (user_id, total_sec) in enumerate(results, 1):
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else f"Usuario {user_id}"
            embed.add_field(name=f"#{i} - {name}", value=f"{int(total_sec)}s", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(VoiceCog(bot))
