# ============================================================
# CONFIGURACION DE PABLITOBOT - 2021
# ============================================================

# Keys del bot (cambiar antes de ejecutar)
TOKEN = "AquiVaLaKeyDelBot"  # Reemplazar con token real
PREFIX = "!"

# Database config
DB_PATH = "data/pablito.db"

# Admin IDs (lista de IDs de administradores)
ADMIN_IDS = []  # Agregar IDs de admins aqui

# Canales de logs
LOG_CHANNEL_ID = 0  # ID del canal para logs de auditoria

# Configuracion de canales de voz temporales
VOICE_CATEGORY_ID = 0  # Categoria donde se crearan canales temporales
VOICE_CREATOR_ID = 0   # ID del canal "Crear Sala"

# Emojis para encuestas
POLL_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

# Configuracion de cache (Redis no usado en version 2021)
CACHE_ENABLED = False

# Rate limiting
COMMAND_COOLDOWN = 3  # Segundos de cooldown por comando
