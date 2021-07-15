# ============================================================
# MAIN.PY - PABLITOBOT 2021
# ============================================================

import discord
from discord.ext import commands
import asyncio
import json
import sqlite3
import datetime
import logging
import os
from config_template import TOKEN, PREFIX, DB_PATH, ADMIN_IDS, LOG_CHANNEL_ID

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pablito.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('PablitoBOT')

# ============================================================
# CLASE PRINCIPAL DEL BOT
# ============================================================

class PablitoBOT(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.voice_states = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        
        self.start_time = datetime.datetime.utcnow()
        self.db_path = DB_PATH
        self.init_database()
        
        # Cargar cogs
        self.load_extension('cogs.avatar_cog')
        self.load_extension('cogs.voice_cog')
        self.load_extension('cogs.temp_channels_cog')
        self.load_extension('cogs.utility_cog')
        self.load_extension('cogs.audit_cog')
        
        logger.info("PablitoBOT inicializado correctamente")
    
    def init_database(self):
        \"\"\"Inicializar base de datos SQLite\"\"\"
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Tabla para estadisticas de voz
        c.execute('''
            CREATE TABLE IF NOT EXISTS voice_stats (
                user_id INTEGER,
                guild_id INTEGER,
                total_seconds INTEGER DEFAULT 0,
                daily_seconds INTEGER DEFAULT 0,
                weekly_seconds INTEGER DEFAULT 0,
                last_update TEXT,
                last_voice_join TEXT,
                is_muted INTEGER DEFAULT 0,
                is_deafened INTEGER DEFAULT 0,
                is_streaming INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, guild_id)
            )
        ''')
        
        # Tabla para historial de avatares
        c.execute('''
            CREATE TABLE IF NOT EXISTS avatar_history (
                user_id INTEGER,
                avatar_hash TEXT,
                avatar_url TEXT,
                change_date TEXT,
                PRIMARY KEY (user_id, avatar_hash)
            )
        ''')
        
        # Tabla para recordatorios
        c.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                channel_id INTEGER,
                message TEXT,
                remind_time TEXT,
                is_completed INTEGER DEFAULT 0
            )
        ''')
        
        # Tabla para canales temporales
        c.execute('''
            CREATE TABLE IF NOT EXISTS temp_channels (
                channel_id INTEGER PRIMARY KEY,
                owner_id INTEGER,
                created_at TEXT
            )
        ''')
        
        # Tabla para auditoria de mensajes
        c.execute('''
            CREATE TABLE IF NOT EXISTS message_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                channel_id INTEGER,
                user_id INTEGER,
                content TEXT,
                action_type TEXT,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Base de datos inicializada correctamente")
    
    async def on_ready(self):
        logger.info(f'PablitoBOT conectado como {self.user.name}')
        logger.info(f'ID: {self.user.id}')
        logger.info(f'Servidores: {len(self.guilds)}')
        
        # Sincronizar comandos slash
        await self.tree.sync()
        logger.info("Comandos slash sincronizados")
        
        # Actividad
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{len(self.guilds)} servidores | !help"
            )
        )

# ============================================================
# EVENTOS GLOBALES
# ============================================================

bot = PablitoBOT()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Espera {round(error.retry_after, 2)} segundos antes de usar este comando.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("No tienes permisos para usar este comando.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Argumento invalido. Usa !help para ver la sintaxis correcta.")
    else:
        logger.error(f"Error: {error}")
        await ctx.send(f"Ocurrio un error: {str(error)}")

# ============================================================
# EJECUTAR BOT
# ============================================================

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        logger.error("Error: Token invalido. Revisa config_template.py")
    except Exception as e:
        logger.error(f"Error al iniciar el bot: {e}")
