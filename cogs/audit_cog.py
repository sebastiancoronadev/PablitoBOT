import discord
from discord.ext import commands
import sqlite3
import datetime

# Cog de auditoria
class AuditCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = bot.db_path
        self.log_channel_id = 0

    # Evento mensaje editado
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        await self.send_log(before.guild, f"Mensaje editado por {before.author.display_name}", f"Canal: {before.channel.mention}")

    # Evento mensaje borrado
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        await self.send_log(message.guild, f"Mensaje borrado por {message.author.display_name}", f"Canal: {message.channel.mention}")

    # Evento usuario entra
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.send_log(member.guild, f"{member.display_name} se unio", f"ID: {member.id}")

    # Evento usuario sale
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.send_log(member.guild, f"{member.display_name} salio", f"ID: {member.id}")

    # Enviar log al canal
    async def send_log(self, guild, title, description):
        if self.log_channel_id == 0:
            return
        channel = guild.get_channel(self.log_channel_id)
        if not channel:
            return
        embed = discord.Embed(title=title, description=description, color=discord.Color.gold())
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AuditCog(bot))
