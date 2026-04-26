#!/bin/bash

# ==============================================================================
# MANUAL DE BACKUP (Para ejecutar, descomenta la línea que necesites)
# ==============================================================================

# Dar permisos de ejecución al script principal (solo se hace una vez)
chmod +x backup/backup.sh

# ------------------------------------------------------------------------------
# 1. BACKUP COMPLETO (Base de datos + Filestore + Addons)
# ------------------------------------------------------------------------------
#./backup/backup.sh integraia_19
./backup/backup.sh integraiadev_19
# ./backup/backup.sh hoteljumpjibe_19

# ------------------------------------------------------------------------------
# 2. BACKUP PARCIAL (Solo Base de datos y Addons, omitir filestore)
# Útil cuando el filestore es muy grande y solo quieres respaldar datos rápidos
# ------------------------------------------------------------------------------
# ./backup/backup.sh integraia_19 --no-filestore

# ------------------------------------------------------------------------------
# 3. VER AYUDA COMPLETA
# ------------------------------------------------------------------------------
# ./backup/backup.sh --help