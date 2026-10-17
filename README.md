# BoomNetwork Bot

Bot de Discord de **BoomNetwork** (Survival · Gens OP · Skyblock). Python + discord.py.

**Estado actual: Fase 1** — arranque, conexión, `/ping` e `/info`. Todo lo demás llega por fases (ver Roadmap).

## Requisitos
- Python **3.11+** (Debian 12 del Chromebook trae 3.11)
- Un bot **nuevo** creado en el [Discord Developer Portal](https://discord.com/developers/applications)

## 1. Crear / configurar el bot en Discord
1. *Developer Portal → tu aplicación → **Bot*** → **Reset Token** → copia el token (solo se muestra una vez).
2. En esa misma página deja **desactivados** los *Privileged Gateway Intents* (la Fase 1 no los necesita).
3. *OAuth2 → URL Generator*: scopes `bot` y `applications.commands`; **sin permisos** (los comandos slash no los requieren).
   Abre la URL generada e invita el bot a tu servidor de pruebas.
4. (Recomendado) En Discord activa *Ajustes → Avanzado → Modo desarrollador*, clic derecho en tu servidor → **Copiar ID del servidor**.

> Si el token llegó a pegarse en un chat, captura, repositorio o mensaje, **regéneralo** (Reset Token). Un token expuesto debe considerarse comprometido.

## 2. Instalación (Chromebook con Linux)
Activa Linux: *Ajustes → Avanzado → Desarrolladores → Entorno de desarrollo de Linux*. Luego, en la terminal:

```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git unzip
cd ~/boomnetwork-bot            # carpeta donde descomprimiste el proyecto
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt     # (en producción basta requirements.txt)
```

## 3. Configuración
```bash
cp .env.example .env
nano .env        # Ctrl+O guardar, Enter, Ctrl+X salir
```
Rellena `DISCORD_TOKEN` (sin comillas ni espacios) y, si quieres, `DISCORD_GUILD_ID`.
El `.env` está en `.gitignore`: **nunca se sube a Git**. En un hosting, define las mismas variables en su panel
en lugar de usar el archivo (las variables reales tienen prioridad sobre el `.env`).

## 4. Ejecutar
```bash
source .venv/bin/activate
python -m boombot
```
Salida esperada (aprox.): `Módulo cargado: boombot.cogs.core` → `Sincronizados 2 comandos...` → `Conectado como <TuBot>#... `.
Para detenerlo: `Ctrl+C`.

## 5. Probar
1. **Tests automáticos** (no necesitan token ni Internet): `python -m pytest -q`
2. **Sin token**: renombra temporalmente `.env` y ejecuta → debe mostrar un error claro y salir sin traceback.
3. **En Discord**: escribe `/ping` (respuesta con latencia) y `/info` (embed con versión, modalidades y rangos).
4. **Seguridad**: `git init && git check-ignore -v .env` debe confirmar que `.env` está ignorado.

## Estructura
```
boomnetwork-bot/
├── .env.example            # plantilla de variables (sin secretos)
├── .gitignore
├── pyproject.toml          # metadatos + configuración de pytest
├── requirements.txt        # dependencias de ejecución
├── requirements-dev.txt    # + pytest
├── README.md
├── boombot/
│   ├── __main__.py         # punto de entrada: python -m boombot
│   ├── bot.py              # clase BoomBot: intents, carga de módulos, sync, errores
│   ├── config.py           # Settings + validación de .env / variables de entorno
│   ├── constants.py        # marca, modalidades, rangos, lista de módulos
│   ├── logging_setup.py    # logs en consola + archivo rotativo, con redacción del token
│   ├── cogs/
│   │   └── core.py         # /ping, /info
│   └── utils/
│       └── embeds.py       # embeds con identidad de marca
└── tests/
```
**Añadir un módulo nuevo:** crea `boombot/cogs/<nombre>.py` con una función `async def setup(bot)` y añádelo a `EXTENSIONS` en `constants.py`.

## Seguridad (decisiones ya aplicadas)
- Token solo por variable de entorno / `.env`; nunca en el código, nunca impreso.
- `Settings.__repr__` oculta el token; los logs lo sustituyen por `[REDACTED]` si apareciera.
- Intents mínimos (solo `guilds`); `AllowedMentions` sin `@everyone` ni roles por defecto.
- Los errores internos se registran en el log y al usuario solo se le muestra un mensaje genérico.

## Hosting gratuito / recursos limitados
- El bot necesita un **proceso continuo** (conexión websocket): no encaja en funciones serverless.
- Muchos planes gratuitos duermen procesos, limitan RAM o tienen disco efímero, y sus condiciones cambian: verifica las actuales antes de elegir.
- Por eso: dependencias ligeras, logs rotativos de tamaño acotado, y (desde la Fase 2) la ruta de la base de datos será configurable con copias de seguridad exportables.
- Un Chromebook sirve para **desarrollar y probar**; si se suspende o pierde conexión, el bot se desconecta.

## Roadmap
| Fase | Contenido |
|---|---|
| 1 ✅ | Estructura, arranque, `/ping`, `/info`, logging, tests |
| 2 | SQLite (aiosqlite), configuración por servidor, sistema de permisos/roles staff, recarga de módulos |
| 3 | Logs de servidor y moderación (warn, timeout, kick, ban, casos) |
| 4 | Bienvenida y autorol (intent *members*) |
| 5 | Tickets con transcripciones HTML (vistas persistentes; intent *message content*) |
| 6 | Sorteos persistentes |
| 7 | Cumpleaños y niveles/XP |
| 8 | Valoración de integración con Minecraft y web |
