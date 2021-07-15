# ============================================================
# COG DE AUDITORIA - PABLITOBOT 2021
# ============================================================

import discord
from discord.ext import commands
import sqlite3
import datetime
import json

class AuditCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = bot.db_path
        
        # Configurar canal de logs (se configura en config)
        self.log_channel_id = 0  # Reemplazar con ID real
    
    #Aqui el evento de mensaje editado
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        \"\"\"Registrar mensajes editados\"\"\"
        if before.author.bot:
            return
        
        # Guardar en DB
        self.save_message_log(
            before.id,
            before.channel.id,
            before.author.id,
            f"Antes: {before.content}\nDespues: {after.content}",
            "editado",
            datetime.datetime.utcnow().isoformat()
        )
        
        # Enviar a canal de logs
        await self.send_log(
            before.guild,
            f"✏️ Mensaje editado por {before.author.display_name}",
            f"**Canal:** {before.channel.mention}\n"
            f"**Antes:** {before.content}\n"
            f"**Despues:** {after.content}"
        )
    
    #Aqui el evento de mensaje borrado
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        \"\"\"Registrar mensajes borrados\"\"\"
        if message.author.bot:
            return
        
        # Guardar en DB
        self.save_message_log(
            message.id,
            message.channel.id,
            message.author.id,
            message.content or "[Sin contenido]",
            "borrado",
            datetime.datetime.utcnow().isoformat()
        )
        
        # Enviar a canal de logs
        await self.send_log(
            message.guild,
            f"🗑️ Mensaje borrado por {message.author.display_name}",
            f"**Canal:** {message.channel.mention}\n"
            f"**Contenido:** {message.content or '[Sin contenido]'}"
        )
    
    #Aqui el evento de entrada de miembro
    @commands.Cog.listener()
    async def on_member_join(self, member):
        \"\"\"Registrar entrada de miembro\"\"\"
        await self.send_log(
            member.guild,
            f"🟢 {member.display_name} se unio al servidor",
            f"**ID:** {member.id}\n"
            f"**Cuenta creada:** {member.created_at.strftime('%d/%m/%Y %H:%M')}"
        )
    
    #Aqui el evento de salida de miembro
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        \"\"\"Registrar salida de miembro\"\"\"
        await self.send_log(
            member.guild,
            f"🔴 {member.display_name} salio del servidor",
            f"**ID:** {member.id}"
        )
    
    #Aqui el evento de cambio de nickname
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        \"\"\"Registrar cambios de perfil\"\"\"
        if before.nick != after.nick:
            old_name = before.nick or before.name
            new_name = after.nick or after.name
            
            await self.send_log(
                before.guild,
                f"📝 Cambio de nombre de {before.display_name}",
                f"**Antes:** {old_name}\n**Despues:** {new_name}"
            )
        
        if before.roles != after.roles:
            old_roles = [r.name for r in before.roles if r.name != "@everyone"]
            new_roles = [r.name for r in after.roles if r.name != "@everyone"]
            
            added = set(new_roles) - set(old_roles)
            removed = set(old_roles) - set(new_roles)
            
            message = ""
            if added:
                message += f"**Roles agregados:** {', '.join(added)}\n"
            if removed:
                message += f"**Roles removidos:** {', '.join(removed)}\n"
            
            if message:
                await self.send_log(
                    before.guild,
                    f"🔰 Cambio de roles de {before.display_name}",
                    message
                )
    
    def save_message_log(self, message_id, channel_id, user_id, content, action_type, timestamp):
        \"\"\"Guardar log de mensaje en DB\"\"\"
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO message_logs (message_id, channel_id, user_id, content, action_type, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (message_id, channel_id, user_id, content, action_type, timestamp))
        
        conn.commit()
        conn.close()
    
    async def send_log(self, guild, title, description):
        \"\"\"Enviar log al canal de auditoria\"\"\"
        if self.log_channel_id == 0:
            return
        
        channel = guild.get_channel(self.log_channel_id)
        if not channel:
            return
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.gold(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(text=f"ID del servidor: {guild.id}")
        
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AuditCog(bot))
