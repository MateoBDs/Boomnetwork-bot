"""Constantes de marca y de dominio compartidas por todos los módulos.

Se mantienen aquí (y no repartidas por los cogs) para tener un único sitio
que cambiar. En fases posteriores, lo que deba ser editable en caliente
(rangos, canales, roles) pasará a base de datos o a configuración por servidor.
"""

from __future__ import annotations

NETWORK_NAME = "BoomNetwork"

# Color de marca provisional (naranja fuego). Cámbialo cuando tengas tu paleta.
BRAND_COLOR = 0xE8590C

# Modalidades y rangos, en el orden indicado en el diseño de la network.
GAME_MODES: tuple[str, ...] = ("Survival", "Gens OP", "Skyblock")
RANKS: tuple[str, ...] = ("Arena", "Pólvora", "Fuego", "Boom")

# Extensiones (cogs) que se cargan al arrancar. Lista explícita a propósito:
# es predecible y evita cargar archivos inesperados. Añade aquí cada módulo nuevo.
EXTENSIONS: tuple[str, ...] = ("boombot.cogs.core",)
