import discord
from discord.ext import commands
import sqlite3
import datetime

class TempChannelsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = bot.db_path
        self.temp_channels = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel:
            creator_channel_id = 0
            if after.channel.id == creator_channel_id:
                await self.create_temp_channel(member, after.channel.category)
        if before.channel and before.channel.id in self.temp_channels:
            if len(before.channel.members) == 0:
                await self.delete_temp_channel(before.channel)

    async def create_temp_channel(self, member, category):
        channel_name = f"Sala de {member.display_name}"
        channel = await member.guild.create_voice_channel(channel_name, category=category)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO temp_channels (channel_id, owner_id, created_at) VALUES (?, ?, ?)', (channel.id, member.id, datetime.datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
        self.temp_channels[channel.id] = member.id
        await member.move_to(channel)

    async def delete_temp_channel(self, channel):
        channel_id = channel.id
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('DELETE FROM temp_channels WHERE channel_id = ?', (channel_id,))
        conn.commit()
        conn.close()
        if channel_id in self.temp_channels:
            del self.temp_channels[channel_id]
        await channel.delete()

    @commands.command(name='lock')
    async def lock_command(self, ctx):
        channel = ctx.author.voice.channel if ctx.author.voice else None
        if not channel:
            await ctx.send("Debes estar en un canal de voz.")
            return
        if channel.id not in self.temp_channels:
            await ctx.send("No es un canal temporal.")
            return
        if self.temp_channels[channel.id] != ctx.author.id:
            await ctx.send("No eres el creador.")
            return
        overwrite = discord.PermissionOverwrite()
        overwrite.connect = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(f"Canal {channel.name} bloqueado.")

    @commands.command(name='unlock')
    async def unlock_command(self, ctx):
        channel = ctx.author.voice.channel if ctx.author.voice else None
        if not channel:
            await ctx.send("Debes estar en un canal de voz.")
            return
        if channel.id not in self.temp_channels:
            await ctx.send("No es un canal temporal.")
            return
        if self.temp_channels[channel.id] != ctx.author.id:
            await ctx.send("No eres el creador.")
            return
        overwrite = discord.PermissionOverwrite()
        overwrite.connect = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(f"Canal {channel.name} desbloqueado.")

    @commands.command(name='limit')
    async def limit_command(self, ctx, limit: int):
        channel = ctx.author.voice.channel if ctx.author.voice else None
        if not channel:
            await ctx.send("Debes estar en un canal de voz.")
            return
        if channel.id not in self.temp_channels:
            await ctx.send("No es un canal temporal.")
            return
        if self.temp_channels[channel.id] != ctx.author.id:
            await ctx.send("No eres el creador.")
            return
        if limit < 1 or limit > 99:
            await ctx.send("Limite entre 1 y 99.")
            return
        await channel.edit(user_limit=limit)
        await ctx.send(f"Limite cambiado a {limit}.")

async def setup(bot):
    await bot.add_cog(TempChannelsCog(bot))
