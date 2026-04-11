#cd /home/odoo/odoo19-skeleton/postiz-n8n-chatwoot-pgadmin-odoo_19

# Dar permisos de ejecución
#chmod +x backup.sh

# Backup completo para integraia_19
./backup/backup.sh integraia_19

# Backup sin filestore (solo base de datos y addons)
#./backup/backup.sh integraia_19 --no-filestore

# Backup para otro cliente
#./backup/backup.sh hoteljumpjibe_19

# Ver ayuda
#./backup/backup.sh --help