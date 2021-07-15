import discord
from discord.ext import commands
import datetime
import asyncio
import hashlib
import requests
import socket
import re

class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = bot.db_path

    @commands.command(name='help')
    async def help_command(self, ctx):
        embed = discord.Embed(title="Comandos de PablitoBOT", color=discord.Color.blue())
        embed.add_field(name="Avatar", value="!avatar, !banner", inline=True)
        embed.add_field(name="Voz", value="!voicestats, !voicetop", inline=True)
        embed.add_field(name="Canales temporales", value="!lock, !unlock, !limit", inline=True)
        embed.add_field(name="Utilidades", value="!poll, !remind, !ping, !serverinfo, !userinfo, !hash, !ip", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='ping')
    async def ping_command(self, ctx):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(title="Pong!", description=f"Latencia: **{latency}ms**", color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.command(name='poll')
    async def poll_command(self, ctx, *, poll_data: str):
        parts = [p.strip() for p in poll_data.split('|')]
        if len(parts) < 2:
            await ctx.send("Uso: !poll pregunta | opcion1 | opcion2 | ...")
            return
        question = parts[0]
        options = parts[1:]
        if len(options) > 10:
            await ctx.send("Maximo 10 opciones.")
            return
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        embed = discord.Embed(title=f"Encuesta: {question}", color=discord.Color.blue())
        description = []
        for i, option in enumerate(options):
            description.append(f"{emojis[i]} {option}")
        embed.description = "\n".join(description)
        message = await ctx.send(embed=embed)
        for i in range(len(options)):
            await message.add_reaction(emojis[i])

    @commands.command(name='serverinfo')
    async def serverinfo_command(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title=f"Informacion de {guild.name}", color=discord.Color.blue())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Miembros", value=guild.member_count, inline=True)
        embed.add_field(name="Creado", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Canales", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        await ctx.send(embed=embed)

    @commands.command(name='userinfo')
    async def userinfo_command(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        embed = discord.Embed(title=f"Informacion de {member.display_name}", color=member.color)
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Cuenta creada", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Ingreso", value=member.joined_at.strftime("%d/%m/%Y") if member.joined_at else "Desconocido", inline=True)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UtilityCog(bot))
