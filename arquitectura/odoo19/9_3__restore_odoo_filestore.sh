# Dar permisos de ejecución
#chmod +x /home/simon/opt/odoo/odoo-from-13-to-18/arquitectura/odoo19/backup/restore.sh

# Restaurar último backup para integraia_19
#./restore.sh integraia_19

# Restaurar último backup para hoteljumpjibe_19
#./restore.sh hoteljumpjibe_19

# Restaurar e instalar módulos
./backup/restore.sh integraia_19 --install-modules

# Restaurar desde un archivo específico
#./restore.sh integraia_19 -f /ruta/al/backup.dump

# Listar backups disponibles
#./restore.sh --list