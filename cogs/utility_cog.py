# ============================================================
# COG DE UTILIDADES - PABLITOBOT 2021
# ============================================================

import discord
from discord.ext import commands
import sqlite3
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
    
    #Aqui el comando help
    @commands.command(name='help')
    async def help_command(self, ctx):
        \"\"\"Muestra todos los comandos disponibles\"\"\"
        embed = discord.Embed(
            title="PablitoBOT - Ayuda",
            description="Lista de todos los comandos disponibles",
            color=discord.Color.blue()
        )
        
        # Comandos de avatar
        embed.add_field(
            name="Comandos de avatar",
            value="!avatar [@usuario] - Ver avatar\n"
                  "!banner [@usuario] - Ver banner\n"
                  "!avatarhistory [@usuario] - Historial de avatares",
            inline=False
        )
        
        # Comandos de voz
        embed.add_field(
            name="Comandos de voz",
            value="!voicestats [@usuario] - Estadisticas de voz\n"
                  "!voicetop [cantidad] - Ranking de actividad",
            inline=False
        )
        
        # Comandos de canales temporales
        embed.add_field(
            name="Comandos de canales temporales",
            value="!lock - Bloquear canal\n"
                  "!unlock - Desbloquear canal\n"
                  "!limit [numero] - Cambiar limite\n"
                  "!kick [@usuario] - Expulsar usuario\n"
                  "!allow [@usuario] - Permitir acceso",
            inline=False
        )
        
        # Utilidades
        embed.add_field(
            name="Utilidades",
            value="!poll [pregunta] | opcion1 | opcion2 | ... - Crear encuesta\n"
                  "!remind [tiempo] [mensaje] - Crear recordatorio\n"
                  "!ping - Ver latencia del bot\n"
                  "!serverinfo - Informacion del servidor\n"
                  "!userinfo [@usuario] - Informacion del usuario\n"
                  "!hash [texto] - Calcular hash\n"
                  "!ip [dominio] - Informacion de IP",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    #Aqui el comando ping
    @commands.command(name='ping')
    async def ping_command(self, ctx):
        \"\"\"Muestra la latencia del bot\"\"\"
        latency = round(self.bot.latency * 1000)
        
        if latency < 100:
            status = "Excelente"
            color = discord.Color.green()
        elif latency < 200:
            status = "Buena"
            color = discord.Color.gold()
        elif latency < 300:
            status = "Regular"
            color = discord.Color.orange()
        else:
            status = "Mala"
            color = discord.Color.red()
        
        embed = discord.Embed(
            title="PablitoBOT - Ping",
            description=f"Latencia: **{latency}ms**\nEstado: **{status}**",
            color=color
        )
        embed.set_footer(text=f"Uptime: {self.get_uptime()}")
        
        await ctx.send(embed=embed)
    
    def get_uptime(self):
        \"\"\"Calcular uptime del bot\"\"\"
        delta = datetime.datetime.utcnow() - self.bot.start_time
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        
        return " ".join(parts) if parts else "Menos de 1 minuto"
    
    #Aqui el comando poll
    @commands.command(name='poll')
    async def poll_command(self, ctx, *, poll_data: str):
        \"\"\"Crear una encuesta\"\"\"
        # Parsear: pregunta | opcion1 | opcion2 | ...
        parts = [p.strip() for p in poll_data.split('|')]
        
        if len(parts) < 2:
            await ctx.send("Uso: !poll pregunta | opcion1 | opcion2 | ...")
            return
        
        question = parts[0]
        options = parts[1:]
        
        if len(options) > 10:
            await ctx.send("Maximo 10 opciones permitidas.")
            return
        
        if len(options) < 2:
            await ctx.send("Minimo 2 opciones para una encuesta.")
            return
        
        # Crear embed
        embed = discord.Embed(
            title=f"Encuesta: {question}",
            color=discord.Color.blue()
        )
        
        # Agregar opciones con emojis
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        description = []
        
        for i, option in enumerate(options):
            description.append(f"{emojis[i]} {option}")
        
        embed.description = "\n".join(description)
        embed.set_footer(text=f"Encuesta creada por {ctx.author.display_name} | Vota con las reacciones")
        
        # Enviar mensaje
        message = await ctx.send(embed=embed)
        
        # Agregar reacciones
        for i in range(len(options)):
            await message.add_reaction(emojis[i])
    
    #Aqui el comando remind
    @commands.command(name='remind')
    async def remind_command(self, ctx, time_str: str, *, message: str):
        \"\"\"Crear un recordatorio\"\"\"
        # Parsear tiempo (ej: "10m", "2h", "30s")
        time_seconds = self.parse_time(time_str)
        
        if time_seconds is None:
            await ctx.send("Formato de tiempo invalido. Usa: 10s, 5m, 2h, 1d")
            return
        
        if time_seconds > 604800:  # Maximo 7 dias
            await ctx.send("El recordatorio no puede ser mayor a 7 dias.")
            return
        
        # Guardar en DB
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        remind_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=time_seconds)
        
        c.execute('''
            INSERT INTO reminders (user_id, channel_id, message, remind_time)
            VALUES (?, ?, ?, ?)
        ''', (ctx.author.id, ctx.channel.id, message, remind_time.isoformat()))
        
        conn.commit()
        conn.close()
        
        # Responder
        await ctx.send(f"Recordatorio programado para {time_str}. Te recordare: \"{message}\"")
        
        # Programar tarea asincrona
        asyncio.create_task(self.process_reminder(ctx.author.id, ctx.channel.id, message, time_seconds))
    
    def parse_time(self, time_str):
        \"\"\"Parsear string de tiempo a segundos\"\"\"
        time_str = time_str.lower()
        
        match = re.match(r'^(\d+)([smhd])$', time_str)
        if not match:
            return None
        
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit == 's':
            return value
        elif unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 3600
        elif unit == 'd':
            return value * 86400
        
        return None
    
    async def process_reminder(self, user_id, channel_id, message, seconds):
        \"\"\"Procesar el recordatorio\"\"\"
        await asyncio.sleep(seconds)
        
        # Obtener canal
        channel = self.bot.get_channel(channel_id)
        if channel:
            user = self.bot.get_user(user_id)
            if user:
                await channel.send(f"{user.mention} Recuerda: {message}")
            else:
                await channel.send(f"Recordatorio para usuario {user_id}: {message}")
    
    #Aqui el comando serverinfo
    @commands.command(name='serverinfo', aliases=['si'])
    async def serverinfo_command(self, ctx):
        \"\"\"Muestra informacion del servidor\"\"\"
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"Informacion de {guild.name}",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Informacion basica
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Miembros", value=guild.member_count, inline=True)
        embed.add_field(name="Creado", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
        
        # Canales
        total_channels = len(guild.channels)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed.add_field(name="Canales totales", value=total_channels, inline=True)
        embed.add_field(name="Canales de texto", value=text_channels, inline=True)
        embed.add_field(name="Canales de voz", value=voice_channels, inline=True)
        embed.add_field(name="Categorias", value=categories, inline=True)
        
        # Roles
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        
        # Boosts
        if guild.premium_tier > 0:
            embed.add_field(name="Boosts", value=f"Nivel {guild.premium_tier} ({guild.premium_subscription_count} boosts)", inline=True)
        else:
            embed.add_field(name="Boosts", value="Sin boosts", inline=True)
        
        await ctx.send(embed=embed)
    
    #Aqui el comando userinfo
    @commands.command(name='userinfo', aliases=['ui'])
    async def userinfo_command(self, ctx, member: discord.Member = None):
        \"\"\"Muestra informacion de un usuario\"\"\"
        if member is None:
            member = ctx.author
        
        embed = discord.Embed(
            title=f"Informacion de {member.display_name}",
            color=member.color,
            timestamp=datetime.datetime.utcnow()
        )
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        # Informacion basica
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Nombre", value=member.name, inline=True)
        embed.add_field(name="Apodo", value=member.display_name, inline=True)
        
        embed.add_field(name="Cuenta creada", value=member.created_at.strftime("%d/%m/%Y %H:%M"), inline=True)
        embed.add_field(name="Fecha de ingreso", value=member.joined_at.strftime("%d/%m/%Y %H:%M") if member.joined_at else "Desconocido", inline=True)
        
        # Estado
        status = str(member.status).capitalize()
        if member.activity:
            activity = f"{member.activity.type.name.capitalize()} {member.activity.name}"
            embed.add_field(name="Actividad", value=activity, inline=True)
        embed.add_field(name="Estado", value=status, inline=True)
        
        # Roles
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        if roles:
            embed.add_field(name=f"Roles ({len(roles)})", value=" ".join(roles[:5]) + ("..." if len(roles) > 5 else ""), inline=False)
        
        await ctx.send(embed=embed)
    
    #Aqui el comando hash
    @commands.command(name='hash')
    async def hash_command(self, ctx, *, text: str):
        \"\"\"Calcula el hash de un texto\"\"\"
        md5_hash = hashlib.md5(text.encode()).hexdigest()
        sha1_hash = hashlib.sha1(text.encode()).hexdigest()
        sha256_hash = hashlib.sha256(text.encode()).hexdigest()
        
        embed = discord.Embed(
            title="Hashes calculados",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="MD5", value=f"{md5_hash}", inline=False)
        embed.add_field(name="SHA1", value=f"{sha1_hash}", inline=False)
        embed.add_field(name="SHA256", value=f"{sha256_hash}", inline=False)
        
        await ctx.send(embed=embed)
    
    #Aqui el comando ip
    @commands.command(name='ip')
    async def ip_command(self, ctx, domain: str):
        \"\"\"Obtiene informacion de una IP o dominio\"\"\"
        try:
            # Resolver dominio
            ip = socket.gethostbyname(domain)
            
            # Obtener informacion de IP (usando ipapi.co)
            response = requests.get(f"https://ipapi.co/{ip}/json/")
            data = response.json()
            
            if data.get('error'):
                await ctx.send(f"No se pudo obtener informacion de {domain}.")
                return
            
            embed = discord.Embed(
                title=f"Informacion de {domain}",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="IP", value=ip, inline=True)
            embed.add_field(name="Pais", value=data.get('country_name', 'Desconocido'), inline=True)
            embed.add_field(name="Ciudad", value=data.get('city', 'Desconocida'), inline=True)
            embed.add_field(name="Region", value=data.get('region', 'Desconocida'), inline=True)
            embed.add_field(name="ISP", value=data.get('org', 'Desconocido'), inline=True)
            embed.add_field(name="Coordenadas", value=f"{data.get('latitude', 'N/A')}, {data.get('longitude', 'N/A')}", inline=True)
            
            await ctx.send(embed=embed)
            
        except socket.gaierror:
            await ctx.send(f"No se pudo resolver el dominio {domain}.")
        except Exception as e:
            await ctx.send(f"Error al obtener informacion: {str(e)}")

async def setup(bot):
    await bot.add_cog(UtilityCog(bot))
