### ENGLISH
# PablitoBOT Discord

**Version:** 1.0  
**Date:** July 15, 2021  
**Author:** sebastiancoronadev  
**Repository:** https://github.com/sebastiancoronadev/PablitoBOT

---

## Description

PablitoBOT is an all-in-one Discord bot designed to provide useful tools for both administrators and regular members. Built with discord.py and SQLite, it is lightweight, fast, and easy to configure.

With PablitoBOT you can:
- View avatars and banners in high resolution.
- Track voice channel activity statistics.
- Create temporary voice rooms with management commands.
- Create polls, reminders, IP lookups, hashes, and more.
- Keep audit logs of messages and member events.

---

## Features

| Module               | Functionality                                                                 |
|----------------------|-------------------------------------------------------------------------------|
| Avatars & Banner     | `!avatar`, `!banner` – Display profile picture or banner of any user.         |
| Voice Statistics     | `!voicestats`, `!voicetop` – Time spent in voice channels and leaderboard.   |
| Temporary Channels   | `!lock`, `!unlock`, `!limit` – Create on-demand private voice rooms.          |
| Utilities            | `!poll`, `!remind`, `!ping`, `!serverinfo`, `!userinfo`, `!hash`, `!ip`      |
| Audit Logs           | Track edits, deletions, joins, and leaves.                                   |

---

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/sebastiancoronadev/PablitoBOT.git
cd PablitoBOT
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure the bot token
Edit `config_template.py` and rename it to `config.py` (or modify variables directly).  
Replace `TOKEN` with your bot's token.

```python
TOKEN = "YourBotTokenHere"
```

### 4. Run the bot
```bash
python main.py
```

---

## Available Commands

| Command                      | Description                                                                 |
|------------------------------|-----------------------------------------------------------------------------|
| `!avatar [@user]`            | Shows avatar in maximum resolution.                                        |
| `!banner [@user]`            | Shows banner (requires Nitro).                                             |
| `!voicestats [@user]`        | Voice channel time statistics.                                             |
| `!voicetop [amount]`         | Leaderboard of most active voice users.                                    |
| `!lock`                      | Locks current temporary channel (owner only).                              |
| `!unlock`                    | Unlocks the temporary channel.                                             |
| `!limit [number]`            | Changes user limit of the channel (1-99).                                  |
| `!poll question | op1 | op2` | Creates a poll with up to 10 options.                                     |
| `!remind [time] [message]`   | Schedules a reminder (e.g., `!remind 10m Drink water`).                    |
| `!ping`                      | Shows bot latency.                                                         |
| `!serverinfo`                | Shows current server information.                                          |
| `!userinfo [@user]`          | Shows detailed user information.                                           |
| `!hash [text]`               | Calculates MD5, SHA1, and SHA256 hashes.                                   |
| `!ip [domain]`               | Shows geolocation information of an IP or domain.                          |
| `!help`                      | Shows this help message.                                                   |

---

## Project Structure

```
PablitoBOT/
├── cogs/
│   ├── avatar_cog.py
│   ├── voice_cog.py
│   ├── temp_channels_cog.py
│   ├── utility_cog.py
│   └── audit_cog.py
├── data/               (SQLite database)
├── logs/               (log files)
├── main.py
├── config_template.py
├── requirements.txt
└── .gitignore
```

---

## Technologies Used

- Python 3.8+
- discord.py (1.7.3)
- SQLite3 (local storage)
- requests, Pillow (image handling)
- asyncio (asynchronous programming)

---

## License

This project is distributed under the MIT License.  
You may use, modify, and distribute it freely.

---

## Credits

Developed with ❤️ by Sebastian Corona  
GitHub: sebastiancoronadev  
Don't forget to leave a ⭐ on the repository!

---

*Last updated: July 15, 2021*

---
### ESPAÑOL

# PablitoBOT Discord

**Versión:** 1.0  
**Fecha:** 15 de julio de 2021  
**Autor:** sebastiancoronadev  
**Repositorio:** https://github.com/sebastiancoronadev/PablitoBOT

---

## Descripción

PablitoBOT es un bot de Discord todo-en-uno diseñado para ofrecer herramientas útiles tanto para administradores como para miembros comunes. Fue desarrollado con discord.py y SQLite, pensado para ser ligero, rápido y fácil de configurar.

Con PablitoBOT podrás:
- Ver avatares y banners en alta resolución.
- Llevar estadísticas de tiempo en canales de voz.
- Crear salas de voz temporales con comandos de gestión.
- Realizar encuestas, recordatorios, consultas de IP, hashes y más.
- Mantener un registro de auditoría de mensajes y eventos.

---

## Características

| Módulo               | Funcionalidad                                                                 |
|----------------------|-------------------------------------------------------------------------------|
| Avatares y Banner    | `!avatar`, `!banner` – Muestra la imagen de perfil o banner de cualquier usuario. |
| Estadísticas de Voz  | `!voicestats`, `!voicetop` – Tiempo acumulado en canales de voz y ranking.   |
| Canales Temporales   | `!lock`, `!unlock`, `!limit` – Crea salas privadas bajo demanda.              |
| Utilidades           | `!poll`, `!remind`, `!ping`, `!serverinfo`, `!userinfo`, `!hash`, `!ip`      |
| Registros de Auditoría | Seguimiento de ediciones, borrados, entradas y salidas.                      |

---

## Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/sebastiancoronadev/PablitoBOT.git
cd PablitoBOT
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar el token del bot
Edita el archivo `config_template.py` y renómbralo a `config.py` (o modifica las variables directamente).  
Cambia la variable `TOKEN` por el token de tu bot de Discord.

```python
TOKEN = "TuTokenAqui"
```

### 4. Iniciar el bot
```bash
python main.py
```

---

## Comandos Disponibles

| Comando                      | Descripción                                                                 |
|------------------------------|-----------------------------------------------------------------------------|
| `!avatar [@usuario]`         | Muestra el avatar en máxima resolución.                                     |
| `!banner [@usuario]`         | Muestra el banner (requiere Nitro).                                         |
| `!voicestats [@usuario]`     | Estadísticas de tiempo en canales de voz.                                   |
| `!voicetop [cantidad]`       | Ranking de los usuarios más activos en voz.                                 |
| `!lock`                      | Bloquea el canal temporal actual (solo dueño).                              |
| `!unlock`                    | Desbloquea el canal temporal.                                               |
| `!limit [número]`            | Cambia el límite de usuarios del canal (1-99).                              |
| `!poll pregunta | op1 | op2` | Crea una encuesta con hasta 10 opciones.                                    |
| `!remind [tiempo] [mensaje]` | Programa un recordatorio (ej: `!remind 10m Tomar agua`).                    |
| `!ping`                      | Muestra la latencia del bot.                                                |
| `!serverinfo`                | Muestra información del servidor actual.                                    |
| `!userinfo [@usuario]`       | Muestra información detallada del usuario.                                  |
| `!hash [texto]`              | Calcula MD5, SHA1 y SHA256 del texto.                                       |
| `!ip [dominio]`              | Muestra información de geolocalización de una IP o dominio.                 |
| `!help`                      | Muestra este mensaje de ayuda.                                              |

---

## Estructura del Proyecto

```
PablitoBOT/
├── cogs/
│   ├── avatar_cog.py
│   ├── voice_cog.py
│   ├── temp_channels_cog.py
│   ├── utility_cog.py
│   └── audit_cog.py
├── data/               (base de datos SQLite)
├── logs/               (archivos de log)
├── main.py
├── config_template.py
├── requirements.txt
└── .gitignore
```

---

## Tecnologías Utilizadas

- Python 3.8+
- discord.py (1.7.3)
- SQLite3 (almacenamiento local)
- requests, Pillow (manejo de imágenes)
- asyncio (programación asíncrona)

---

## Licencia

Este proyecto se distribuye bajo la licencia MIT.  
Puedes usarlo, modificarlo y distribuirlo libremente.

---

## Créditos

Desarrollado con ❤️ por Sebastian Corona  
GitHub: sebastiancoronadev  
¡No olvides dejar una ⭐ en el repositorio!

---

*Última actualización: 15 de julio de 2021*
