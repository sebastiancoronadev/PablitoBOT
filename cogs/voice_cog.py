# ============================================================
# COG DE VOZ - PABLITOBOT 2021
# ============================================================

import discord
from discord.ext import commands
import sqlite3
import datetime
import asyncio
from collections import defaultdict

class VoiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = bot.db_path
        self.voice_sessions = {}  # {user_id: (guild_id, channel_id, join_time, is_muted, is_deafened, is_streaming)}
    
    #Aqui el evento de entrada a voz
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        \"\"\"Detectar cuando un usuario entra/sale de un canal de voz\"\"\"
        # Verificar si hay cambio de canal
        if before.channel != after.channel:
            # Salio de un canal
            if before.channel:
                await self.end_voice_session(member.id, before.channel.guild.id)
            
            # Entro a un canal
            if after.channel:
                await self.start_voice_session(
                    member.id,
                    after.channel.guild.id,
                    after.channel.id,
                    after.mute,
                    after.deaf,
                    after.self_stream
                )
        
        # Verificar cambios de estado (mute/deaf/stream)
        elif before.channel:
            key = member.id
            if key in self.voice_sessions:
                guild_id, channel_id, join_time, _, _, _ = self.voice_sessions[key]
                self.voice_sessions[key] = (guild_id, channel_id, join_time, after.mute, after.deaf, after.self_stream)
    
    async def start_voice_session(self, user_id, guild_id, channel_id, is_muted, is_deafened, is_streaming):
        \"\"\"Iniciar sesion de voz\"\"\"
        current_time = datetime.datetime.utcnow()
        self.voice_sessions[user_id] = (guild_id, channel_id, current_time, is_muted, is_deafened, is_streaming)
        
        # Actualizar stats en DB
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT OR IGNORE INTO voice_stats (user_id, guild_id, last_voice_join)
            VALUES (?, ?, ?)
        ''', (user_id, guild_id, current_time.isoformat()))
        
        c.execute('''
            UPDATE voice_stats
            SET last_voice_join = ?
            WHERE user_id = ? AND guild_id = ?
        ''', (current_time.isoformat(), user_id, guild_id))
        
        conn.commit()
        conn.close()
    
    async def end_voice_session(self, user_id, guild_id):
        \"\"\"Finalizar sesion de voz y calcular tiempo\"\"\"
        if user_id not in self.voice_sessions:
            return
        
        guild_id_temp, channel_id, join_time, is_muted, is_deafened, is_streaming = self.voice_sessions[user_id]
        current_time = datetime.datetime.utcnow()
        delta = (current_time - join_time).total_seconds()
        
        if delta < 1:  # Ignorar sesiones muy cortas
            del self.voice_sessions[user_id]
            return
        
        # Guardar en DB
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            UPDATE voice_stats
            SET total_seconds = total_seconds + ?,
                daily_seconds = daily_seconds + ?,
                weekly_seconds = weekly_seconds + ?,
                is_muted = is_muted + ?,
                is_deafened = is_deafened + ?,
                is_streaming = is_streaming + ?
            WHERE user_id = ? AND guild_id = ?
        ''', (
            int(delta), int(delta), int(delta),
            int(is_muted) * int(delta),
            int(is_deafened) * int(delta),
            int(is_streaming) * int(delta),
            user_id, guild_id
        ))
        
        conn.commit()
        conn.close()
        
        # Eliminar sesion
        del self.voice_sessions[user_id]
    
    #Aqui el comando estadisticas de voz
    @commands.command(name='voicestats', aliases=['vs'])
    async def voice_stats_command(self, ctx, member: discord.Member = None):
        \"\"\"Muestra estadisticas de tiempo en canales de voz\"\"\"
        if member is None:
            member = ctx.author
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT total_seconds, daily_seconds, weekly_seconds,
                   is_muted, is_deafened, is_streaming
            FROM voice_stats
            WHERE user_id = ? AND guild_id = ?
        ''', (member.id, ctx.guild.id))
        
        result = c.fetchone()
        conn.close()
        
        if not result:
            await ctx.send(f"{member.display_name} no tiene estadisticas de voz registradas.")
            return
        
        total_sec, daily_sec, weekly_sec, muted_sec, deaf_sec, stream_sec = result
        
        # Calcular tiempos
        total_time = self.seconds_to_string(total_sec)
        daily_time = self.seconds_to_string(daily_sec)
        weekly_time = self.seconds_to_string(weekly_sec)
        muted_time = self.seconds_to_string(muted_sec)
        deaf_time = self.seconds_to_string(deaf_sec)
        stream_time = self.seconds_to_string(stream_sec)
        
        # Estado actual
        is_in_voice = member.voice and member.voice.channel
        current_channel = member.voice.channel.name if is_in_voice else "No conectado"
        
        embed = discord.Embed(
            title=f"Estadisticas de voz - {member.display_name}",
            color=member.color,
            timestamp=datetime.datetime.utcnow()
        )
        
        embed.add_field(name="Tiempo total", value=total_time, inline=True)
        embed.add_field(name="Tiempo diario", value=daily_time, inline=True)
        embed.add_field(name="Tiempo semanal", value=weekly_time, inline=True)
        embed.add_field(name="Estado actual", value=current_channel, inline=True)
        embed.add_field(name="Tiempo muteado", value=muted_time, inline=True)
        embed.add_field(name="Tiempo ensordecido", value=deaf_time, inline=True)
        embed.add_field(name="Tiempo en streaming", value=stream_time, inline=True)
        
        await ctx.send(embed=embed)
    
    #Aqui el comando leaderboard de voz
    @commands.command(name='voicetop', aliases=['vt'])
    async def voice_top_command(self, ctx, limit: int = 10):
        \"\"\"Muestra el ranking de usuarios mas activos en voz\"\"\"
        if limit > 20:
            limit = 20
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT user_id, total_seconds
            FROM voice_stats
            WHERE guild_id = ?
            ORDER BY total_seconds DESC
            LIMIT ?
        ''', (ctx.guild.id, limit))
        
        results = c.fetchall()
        conn.close()
        
        if not results:
            await ctx.send("No hay datos de actividad de voz en este servidor.")
            return
        
        embed = discord.Embed(
            title="Ranking de actividad en voz",
            description="Los usuarios mas activos en canales de voz",
            color=discord.Color.gold()
        )
        
        for i, (user_id, total_sec) in enumerate(results, 1):
            member = ctx.guild.get_member(user_id)
            if member:
                name = member.display_name
            else:
                name = f"Usuario {user_id}"
            
            time_str = self.seconds_to_string(total_sec)
            
            # Medallas
            medal = ""
            if i == 1:
                medal = "🥇 "
            elif i == 2:
                medal = "🥈 "
            elif i == 3:
                medal = "🥉 "
            
            embed.add_field(
                name=f"{medal}#{i} - {name}",
                value=f"Tiempo: {time_str}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    def seconds_to_string(self, seconds):
        \"\"\"Convertir segundos a formato legible\"\"\"
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        parts = []
        if days > 0:
            parts.append(f"{int(days)}d")
        if hours > 0:
            parts.append(f"{int(hours)}h")
        if minutes > 0:
            parts.append(f"{int(minutes)}m")
        if secs > 0 or not parts:
            parts.append(f"{int(secs)}s")
        
        return " ".join(parts)

async def setup(bot):
    await bot.add_cog(VoiceCog(bot))
