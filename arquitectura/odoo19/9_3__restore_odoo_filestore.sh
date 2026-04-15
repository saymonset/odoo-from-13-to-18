#!/bin/bash

# ==============================================================================
# MANUAL DE RESTAURACIÓN (Para ejecutar, descomenta la línea que necesites)
# ==============================================================================

# Dar permisos de ejecución al script principal (solo se hace una vez)
chmod +x backup/restore.sh

# ------------------------------------------------------------------------------
# 1. RESTAURAR EL ÚLTIMO BACKUP DISPONIBLE DE UN CLIENTE
# Busca automáticamente en la carpeta de backups el último que pertenezca a este cliente.
# ------------------------------------------------------------------------------
./backup/restore.sh integraia_19
# ./backup/restore.sh hoteljumpjibe_19


# ------------------------------------------------------------------------------
# 2. RESTAURAR UN BACKUP ESPECÍFICO DE UN CLIENTE
# Si quieres restaurar una fecha en particular, copia el nombre de la carpeta
# de backup y ponla como segundo argumento.
# ------------------------------------------------------------------------------
# ./backup/restore.sh integraia_19 backup_2026-04-14_10-00-00


# ------------------------------------------------------------------------------
# 3. VER AYUDA Y LISTA DE CLIENTES DISPONIBLES
# Si ejecutas el script sin parámetros, te mostrará cómo usarlo y los clientes.
# ------------------------------------------------------------------------------
# ./backup/restore.sh