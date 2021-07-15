# ============================================================
# COG DE CANALES TEMPORALES - PABLITOBOT 2021
# ============================================================

import discord
from discord.ext import commands
import sqlite3
import datetime
import asyncio

class TempChannelsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = bot.db_path
        self.temp_channels = {}  # {channel_id: owner_id}
        self.load_temp_channels()
    
    def load_temp_channels(self):
        \"\"\"Cargar canales temporales desde DB\"\"\"
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT channel_id, owner_id FROM temp_channels')
        results = c.fetchall()
        conn.close()
        
        for channel_id, owner_id in results:
            self.temp_channels[channel_id] = owner_id
    
    #Aqui el evento de entrada a canal de voz
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        \"\"\"Crear canal temporal cuando alguien entra al canal creador\"\"\"
        # Verificar si entro al canal creador
        if after.channel:
            # Buscar el canal creador en la configuracion
            # Por simplicidad, usamos un canal especifico (se configura en el comando)
            creator_channel_id = 0  # Se configura con !setvoicecreator
            if after.channel.id == creator_channel_id:
                await self.create_temp_channel(member, after.channel.category)
        
        # Verificar si alguien abandono un canal temporal
        if before.channel and before.channel.id in self.temp_channels:
            if len(before.channel.members) == 0:
                await self.delete_temp_channel(before.channel)
    
    async def create_temp_channel(self, member, category):
        \"\"\"Crear un canal de voz temporal\"\"\"
        guild = member.guild
        
        # Crear canal
        channel_name = f"Sala de {member.display_name}"
        channel = await guild.create_voice_channel(
            channel_name,
            category=category,
            reason="Canal temporal creado por PablitoBOT"
        )
        
        # Guardar en DB
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT OR REPLACE INTO temp_channels (channel_id, owner_id, created_at)
            VALUES (?, ?, ?)
        ''', (channel.id, member.id, datetime.datetime.utcnow().isoformat()))
        
        conn.commit()
        conn.close()
        
        self.temp_channels[channel.id] = member.id
        
        # Mover al usuario al nuevo canal
        await member.move_to(channel)
        
        # Enviar mensaje de instrucciones
        embed = discord.Embed(
            title="Canal temporal creado",
            description=f"Bienvenido a tu sala privada, {member.display_name}.",
            color=discord.Color.green()
        )
        embed.add_field(name="Comandos disponibles", value="""
        !lock - Bloquear el canal
        !unlock - Desbloquear el canal
        !limit [numero] - Cambiar limite de usuarios
        !kick [usuario] - Expulsar a alguien
        !allow [usuario] - Permitir acceso a alguien
        """, inline=False)
        
        await channel.send(embed=embed)
    
    async def delete_temp_channel(self, channel):
        \"\"\"Eliminar un canal temporal\"\"\"
        channel_id = channel.id
        
        # Eliminar de DB
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('DELETE FROM temp_channels WHERE channel_id = ?', (channel_id,))
        conn.commit()
        conn.close()
        
        if channel_id in self.temp_channels:
            del self.temp_channels[channel_id]
        
        await channel.delete(reason="Canal temporal vacio")
    
    #Aqui el comando lock
    @commands.command(name='lock')
    async def lock_command(self, ctx):
        \"\"\"Bloquear un canal temporal\"\"\"
        channel = ctx.author.voice.channel if ctx.author.voice else None
        if not channel:
            await ctx.send("Debes estar en un canal de voz.")
            return
        
        if channel.id not in self.temp_channels:
            await ctx.send("Este no es un canal temporal.")
            return
        
        if self.temp_channels[channel.id] != ctx.author.id:
            await ctx.send("Solo el creador del canal puede usar este comando.")
            return
        
        # Bloquear canal
        overwrite = discord.PermissionOverwrite()
        overwrite.connect = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        
        await ctx.send(f"Canal {channel.name} bloqueado correctamente.")
    
    #Aqui el comando unlock
    @commands.command(name='unlock')
    async def unlock_command(self, ctx):
        \"\"\"Desbloquear un canal temporal\"\"\"
        channel = ctx.author.voice.channel if ctx.author.voice else None
        if not channel:
            await ctx.send("Debes estar en un canal de voz.")
            return
        
        if channel.id not in self.temp_channels:
            await ctx.send("Este no es un canal temporal.")
            return
        
        if self.temp_channels[channel.id] != ctx.author.id:
            await ctx.send("Solo el creador del canal puede usar este comando.")
            return
        
        # Desbloquear canal
        overwrite = discord.PermissionOverwrite()
        overwrite.connect = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        
        await ctx.send(f"Canal {channel.name} desbloqueado correctamente.")
    
    #Aqui el comando limit
    @commands.command(name='limit')
    async def limit_command(self, ctx, limit: int):
        \"\"\"Cambiar limite de usuarios del canal\"\"\"
        channel = ctx.author.voice.channel if ctx.author.voice else None
        if not channel:
            await ctx.send("Debes estar en un canal de voz.")
            return
        
        if channel.id not in self.temp_channels:
            await ctx.send("Este no es un canal temporal.")
            return
        
        if self.temp_channels[channel.id] != ctx.author.id:
            await ctx.send("Solo el creador del canal puede usar este comando.")
            return
        
        if limit < 1 or limit > 99:
            await ctx.send("El limite debe ser entre 1 y 99.")
            return
        
        await channel.edit(user_limit=limit)
        await ctx.send(f"Limite del canal {channel.name} cambiado a {limit} usuarios.")
    
    #Aqui el comando kick
    @commands.command(name='kick')
    async def kick_command(self, ctx, member: discord.Member):
        \"\"\"Expulsar a alguien del canal temporal\"\"\"
        channel = ctx.author.voice.channel if ctx.author.voice else None
        if not channel:
            await ctx.send("Debes estar en un canal de voz.")
            return
        
        if channel.id not in self.temp_channels:
            await ctx.send("Este no es un canal temporal.")
            return
        
        if self.temp_channels[channel.id] != ctx.author.id:
            await ctx.send("Solo el creador del canal puede usar este comando.")
            return
        
        if member not in channel.members:
            await ctx.send(f"{member.display_name} no esta en este canal.")
            return
        
        await member.move_to(None)
        await ctx.send(f"{member.display_name} ha sido expulsado del canal.")
    
    #Aqui el comando allow
    @commands.command(name='allow')
    async def allow_command(self, ctx, member: discord.Member):
        \"\"\"Permitir acceso a alguien al canal temporal\"\"\"
        channel = ctx.author.voice.channel if ctx.author.voice else None
        if not channel:
            await ctx.send("Debes estar en un canal de voz.")
            return
        
        if channel.id not in self.temp_channels:
            await ctx.send("Este no es un canal temporal.")
            return
        
        if self.temp_channels[channel.id] != ctx.author.id:
            await ctx.send("Solo el creador del canal puede usar este comando.")
            return
        
        # Dar permisos especificos
        overwrite = discord.PermissionOverwrite()
        overwrite.connect = True
        await channel.set_permissions(member, overwrite=overwrite)
        
        await ctx.send(f"{member.display_name} ahora puede unirse al canal {channel.name}.")

async def setup(bot):
    await bot.add_cog(TempChannelsCog(bot))
