# Dar permisos de ejecución
chmod +x backup/restore.sh

# Listar backups disponibles
#./backup/restore.sh --list

# Restaurar último backup (solo datos)
#./backup/restore.sh integraia_19

# Restaurar último backup con módulos
./backup/restore.sh integraia_19 --install-modules

# Restaurar backup específico
#./backup/restore.sh integraia_19 -f 2026-04-11_14-59-52

# Restaurar backup específico con módulos
#./backup/restore.sh integraia_19 -f 2026-04-11_14-59-52 --install-modules

# Solo crear rol
#./backup/restore.sh integraia_19 --create-role

# Ayuda
#./backup/restore.sh --help