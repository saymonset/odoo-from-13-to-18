# para las pruebas desarrollo , siempre se hace con integraiadev_19

################################***PRODUCCION***################################
# PROXY_MODE EN EL .cfg SE CAMBIA A FALSE SI ESTÁ EN DEVELOPER, EN PRODUCCIÓN DEBE ESTAR EN TRUE
################################***FIN PRODUCCION***################################

###############################****HACER BACKUP****################################
# SIEMPRE QUE HAGAS BACKUP A PRODUCCIÓN COLOCA LA BANDERA proxy_mode = True en el archivo:
# arquitectura/odoo19/clientes/integraiadev_19/conf/odoo.cfg
# Solo debes abrir el archivo backup.sh y cambiar el nombre del cliente a respaldar y ejecutar:
# ./9_1_backup_bd.sh
###############################****FIN HACER BACKUP****################################

###############################****HACER RESTORE****################################
# Solo debes abrir el archivo 9_3__restore_odoo_filestore.sh y cambiar el nombre del cliente a restaurar y ejecutar:
# ./9_3__restore_odoo_filestore.sh
###############################****FIN HACER RESTORE****################################

# Para probar en remoto: https://integradev.integraia.lat

# Si vas a debuggear, en el archivo /home/odoo/odoo-from-13-to-18/.vscode/launch.json,
# cambiar el 18 por la versión que vas a debuguear. La carpeta integraiadev_19 es la default.

# Para debuguear, siempre en el SSH abrir los fuentes desde ODOO-13-19:
cd /home/odoo/odoo-from-13-to-18/arquitectura/odoo19

# En el archivo start_odoo.sh debes cambiar el nombre del cliente a correr.

# Buscar un módulo, ejemplo: _name = "stock.picking.type"

# Descripción: Esta es la arquitectura para implementar diferentes versiones de Odoo
# con sus respectivos clientes y extra-addons.

# ============================================================
# INSTALACIÓN DE LIBRERÍAS ESTÁNDAR (sistema)
# ============================================================
sudo apt install openssh-server fail2ban libxml2-dev libxslt1-dev zlib1g-dev libsasl2-dev libldap2-dev build-essential libssl-dev libffi-dev libmysqlclient-dev libpq-dev libjpeg8-dev liblcms2-dev libblas-dev libatlas-base-dev git curl fontconfig libxrender1 xfonts-75dpi xfonts-base -y

sudo apt install snapd
sudo snap install astral-uv --classic

# ============================================================
# BAJAR FUENTES DE ODOO 19
# ============================================================
git clone -b 19.0 --single-branch --depth 1 https://github.com/odoo/odoo.git odoo

# ============================================================
# INSTALAR PYTHON 3.12 Y LIBRERÍAS CON UV
# ============================================================
uv python install 3.12
uv venv --python 3.12
source .venv/bin/activate

# Instalar dependencias base de Odoo
uv pip install -r odoo/requirements.txt

# Instalar librerías adicionales necesarias para el proyecto
uv pip install viivakoodi
uv pip install python-barcode
uv pip install pandas
uv pip install xmltodict
uv pip install gtts
uv pip install lxml

# ---------- ⚠️ LIBRERÍA FALTANTE DETECTADA ----------
# El módulo chat_bot_n8n_ia necesita openai para funcionar (evita error 'NoneType' object is not callable)
uv pip install openai
# -----------------------------------------------------

# ============================================================
# CONFIGURACIÓN DE BASE DE DATOS (DOCKER)
# ============================================================
# 1. Crear usuario odoo19 dentro del contenedor PostgreSQL
docker exec -it odoo-db19-n8n bash
psql -U odoo -d postgres

CREATE ROLE odoo19 WITH LOGIN PASSWORD 'odoo' CREATEDB;
ALTER USER odoo19 WITH SUPERUSER;
\q
exit

# 2. Crear usuario y base de datos para el cliente integraiadev_19
docker exec -it odoo-db19-n8n bash
psql -U odoo19 -d postgres

CREATE USER integraiadev_19 WITH PASSWORD 'odoo';
ALTER USER integraiadev_19 WITH SUPERUSER;
CREATE DATABASE dbintegraiadev_19;
GRANT ALL PRIVILEGES ON DATABASE dbintegraiadev_19 TO integraiadev_19;
\q
exit

# Para listar roles y permisos:
\du

# ============================================================
# ABRIR PUERTO EN EL SERVIDOR (si es necesario)
# ============================================================
sudo ufw allow 8019/tcp

# ============================================================
# INICIALIZAR BASE DE DATOS POR PRIMERA VEZ
# ============================================================
# Ir a la ruta del proyecto
cd /home/simon/odoo-13-19/arquitectura/odoo19   # Ajusta según tu usuario real

# Activar entorno virtual si no lo está
source .venv/bin/activate

# Inicializar con módulo base
./odoo/odoo-bin -d dbintegraiadev_19 -i base -c clientes/integraiadev_19/conf/odoo.cfg

# ============================================================
# ARRANCAR ODOO DE MANERA REGULAR
# ============================================================
# Si el puerto está ocupado, matar proceso:
sudo lsof -i :8019
# (opcional kill -9 <PID>)

# Activar entorno virtual
source .venv/bin/activate

# Levantar Odoo
./odoo/odoo-bin -d dbintegraiadev_19 -c clientes/integraiadev_19/conf/odoo.cfg

# ============================================================
# ACCESO WEB
# ============================================================
# http://5.189.161.7:18069/   (ajustar IP y puerto según tu configuración)

# ============================================================
# CONEXIÓN DIRECTA A LA BASE DE DATOS (postgreSQL)
# ============================================================
psql -U panna19 -d dbintegraiadev_19
# password: odoo