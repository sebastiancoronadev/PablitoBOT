# ============================================================
# COG DE AVATARES - PABLITOBOT 2021
# ============================================================

import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import datetime
import hashlib
import aiohttp
from PIL import Image
import io

class AvatarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = bot.db_path
    
    #Aqui el comando avatar
    @commands.command(name='avatar', aliases=['av', 'pfp'])
    async def avatar_command(self, ctx, member: discord.Member = None):
        \"\"\"Muestra el avatar de un usuario en alta resolucion\"\"\"
        if member is None:
            member = ctx.author
        
        # Obtener URL del avatar en diferentes formatos
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        avatar_url_png = member.avatar.replace(format='png', size=1024).url if member.avatar else None
        avatar_url_jpg = member.avatar.replace(format='jpg', size=1024).url if member.avatar else None
        avatar_url_webp = member.avatar.replace(format='webp', size=1024).url if member.avatar else None
        
        # Guardar en historial
        if member.avatar:
            self.save_avatar_history(member.id, member.avatar.key, avatar_url)
        
        # Crear embed
        embed = discord.Embed(
            title=f"Avatar de {member.display_name}",
            color=member.color,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_image(url=avatar_url)
        embed.set_footer(text=f"Solicitado por {ctx.author.display_name}")
        
        # Agregar campos con metadatos
        embed.add_field(
            name="Insignias",
            value=self.get_badges(member),
            inline=True
        )
        embed.add_field(
            name="Cuenta creada",
            value=member.created_at.strftime("%d/%m/%Y %H:%M"),
            inline=True
        )
        embed.add_field(
            name="Fecha de ingreso",
            value=member.joined_at.strftime("%d/%m/%Y %H:%M") if member.joined_at else "Desconocido",
            inline=True
        )
        
        # Roles
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        if roles:
            embed.add_field(
                name=f"Roles ({len(roles)})",
                value=" ".join(roles[:5]) + ("..." if len(roles) > 5 else ""),
                inline=False
            )
        
        # Botones para descargar en diferentes formatos
        view = AvatarView(
            avatar_png=avatar_url_png,
            avatar_jpg=avatar_url_jpg,
            avatar_webp=avatar_url_webp,
            avatar_gif=avatar_url if avatar_url.endswith('.gif') else None
        )
        
        await ctx.send(embed=embed, view=view)
    
    def get_badges(self, member):
        \"\"\"Obtener insignias del usuario\"\"\"
        badges = []
        
        if member.public_flags.verified_bot_developer:
            badges.append("<:dev:123456> Bot Developer")
        if member.public_flags.discord_certified_moderator:
            badges.append("<:mod:123456> Certified Mod")
        if member.public_flags.hypesquad_balance:
            badges.append("<:hs_balance:123456> HypeSquad Balance")
        if member.public_flags.hypesquad_brilliance:
            badges.append("<:hs_brilliance:123456> HypeSquad Brilliance")
        if member.public_flags.hypesquad_bravery:
            badges.append("<:hs_bravery:123456> HypeSquad Bravery")
        if member.public_flags.staff:
            badges.append("<:staff:123456> Discord Staff")
        if member.public_flags.bug_hunter:
            badges.append("<:bughunter:123456> Bug Hunter")
        if member.public_flags.bug_hunter_level_2:
            badges.append("<:bughunter2:123456> Bug Hunter Level 2")
        if member.premium_since:
            badges.append("<:booster:123456> Booster")
        
        return ", ".join(badges) if badges else "Sin insignias especiales"
    
    def save_avatar_history(self, user_id, avatar_hash, avatar_url):
        \"\"\"Guardar historial de avatares\"\"\"
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT OR IGNORE INTO avatar_history (user_id, avatar_hash, avatar_url, change_date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, avatar_hash, avatar_url, datetime.datetime.utcnow().isoformat()))
        
        conn.commit()
        conn.close()
    
    #Aqui el comando banner
    @commands.command(name='banner')
    async def banner_command(self, ctx, member: discord.Member = None):
        \"\"\"Muestra el banner de un usuario (si tiene Nitro)\"\"\"
        if member is None:
            member = ctx.author
        
        # Obtener banner (requiere API)
        user_data = await self.bot.http.request(
            discord.http.Route('GET', '/users/{uid}', uid=member.id)
        )
        
        banner_id = user_data.get('banner')
        if not banner_id:
            await ctx.send(f"{member.display_name} no tiene banner (requiere Nitro).")
            return
        
        # Construir URL del banner
        banner_url = f"https://cdn.discordapp.com/banners/{member.id}/{banner_id}.png?size=1024"
        
        embed = discord.Embed(
            title=f"Banner de {member.display_name}",
            color=member.color
        )
        embed.set_image(url=banner_url)
        embed.set_footer(text="Los banners son exclusivos de Nitro")
        
        await ctx.send(embed=embed)
    
    #Aqui el comando historial de avatares
    @commands.command(name='avatarhistory', aliases=['avh'])
    async def avatar_history_command(self, ctx, member: discord.Member = None):
        \"\"\"Muestra el historial de avatares de un usuario\"\"\"
        if member is None:
            member = ctx.author
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT avatar_url, change_date FROM avatar_history
            WHERE user_id = ?
            ORDER BY change_date DESC
            LIMIT 5
        ''', (member.id,))
        
        results = c.fetchall()
        conn.close()
        
        if not results:
            await ctx.send(f"No hay historial de avatares para {member.display_name}.")
            return
        
        embed = discord.Embed(
            title=f"Historial de avatares - {member.display_name}",
            color=member.color
        )
        
        for i, (url, date) in enumerate(results):
            embed.add_field(
                name=f"Cambio {i+1}",
                value=f"Fecha: {date[:10]}\n[Ver avatar]({url})",
                inline=False
            )
        
        await ctx.send(embed=embed)

class AvatarView(discord.ui.View):
    def __init__(self, avatar_png, avatar_jpg, avatar_webp, avatar_gif):
        super().__init__(timeout=60)
        
        if avatar_png:
            self.add_item(discord.ui.Button(
                label="PNG",
                style=discord.ButtonStyle.primary,
                url=avatar_png
            ))
        if avatar_jpg:
            self.add_item(discord.ui.Button(
                label="JPG",
                style=discord.ButtonStyle.secondary,
                url=avatar_jpg
            ))
        if avatar_webp:
            self.add_item(discord.ui.Button(
                label="WebP",
                style=discord.ButtonStyle.success,
                url=avatar_webp
            ))
        if avatar_gif:
            self.add_item(discord.ui.Button(
                label="GIF",
                style=discord.ButtonStyle.danger,
                url=avatar_gif
            ))

async def setup(bot):
    await bot.add_cog(AvatarCog(bot))
