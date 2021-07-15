import discord
from discord.ext import commands
import sqlite3
import datetime

class AvatarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = bot.db_path

    @commands.command(name='avatar')
    async def avatar_command(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        embed = discord.Embed(title=f"Avatar de {member.display_name}", color=member.color)
        embed.set_image(url=avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name='banner')
    async def banner_command(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        user_data = await self.bot.http.request(discord.http.Route('GET', '/users/{uid}', uid=member.id))
        banner_id = user_data.get('banner')
        if not banner_id:
            await ctx.send(f"{member.display_name} no tiene banner.")
            return
        banner_url = f"https://cdn.discordapp.com/banners/{member.id}/{banner_id}.png?size=1024"
        embed = discord.Embed(title=f"Banner de {member.display_name}", color=member.color)
        embed.set_image(url=banner_url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AvatarCog(bot))
