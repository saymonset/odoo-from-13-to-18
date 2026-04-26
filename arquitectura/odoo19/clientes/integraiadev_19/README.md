# Guía de Instalación - Arquitectura Odoo 19

Este repositorio contiene la arquitectura necesaria para implementar Odoo 19 con configuraciones específicas por cliente y módulos extra (IA, Chatbots, etc.).

---

## 1. Requisitos Previos del Sistema

Instala las dependencias de sistema necesarias para Odoo y las librerías de procesamiento de medios.

```bash
# Actualizar y librerías estándar
sudo apt update && sudo apt install -y \
    openssh-server fail2ban libxml2-dev libxslt1-dev zlib1g-dev \
    libsasl2-dev libldap2-dev build-essential libssl-dev libffi-dev \
    libmysqlclient-dev libpq-dev libjpeg8-dev liblcms2-dev libblas-dev \
    libatlas-base-dev git curl fontconfig libxrender1 xfonts-75dpi \
    xfonts-base ffmpeg libmagic1

# Instalar UV (Gestor de paquetes ultra rápido)
sudo apt install snapd -y
sudo snap install astral-uv --classic
```

---

## 2. Descarga de Fuentes y Entorno Python

Ubícate en la ruta de trabajo deseada (ej. `~/develop/odoo-from-13-to-18/arquitectura/odoo19`).

```bash
# Bajar fuentes de Odoo 19
git clone -b 19.0 --single-branch --depth 1 https://github.com/odoo/odoo.git odoo

# Configurar Python 3.11 y Entorno Virtual
uv python install 3.11
uv venv --python 3.11
source .venv/bin/activate
```

---

## 3. Instalación de Dependencias Python

Una vez activado el entorno virtual, instala todos los paquetes necesarios.

```bash
# Librerías base y utilitarios
uv pip install pandas xmltodict gtts lxml pycryptodome pydub python-magic

# Herramientas de desarrollo
uv pip install ptvsd inotify watchdog

# LIBRERÍAS CRÍTICAS PARA MÓDULOS DE IA
uv pip install "pydantic>=2.0" openai httpx python-dotenv

# Requisitos oficiales de Odoo
uv pip install -r odoo/requirements.txt
```

---

## 4. Configuración de Base de Datos (PostgreSQL)

### Opción A: En el Host
```bash
psql -U postgres -d postgres
# Crear rol de usuario
CREATE ROLE integraiadev_19 WITH LOGIN PASSWORD '123456' CREATEDB SUPERUSER;
```

### Opción B: En Docker
```bash
# Acceder al contenedor
docker exec -it odoo-db19-n8n bash
psql -U odoo -d postgres

# Crear base de datos y usuario
CREATE ROLE integraiadev_19 WITH LOGIN PASSWORD '123456' CREATEDB SUPERUSER;
CREATE DATABASE dbintegraiadev_19 OWNER integraiadev_19;
```

---

## 5. Configuración de Red y Firewall

Asegúrate de permitir el tráfico en los puertos necesarios.

```bash
# Odoo Web
sudo ufw allow 38069/tcp

# Puertos para Debugging
sudo ufw allow 49003/tcp
sudo ufw allow 42091/tcp
sudo ufw allow 8888/tcp
```

---

## 6. Ejecución e Inicialización

### Inicializar Base de Datos (Solo la primera vez)
```bash
./odoo/odoo-bin -d dbintegraiadev_19 -i base -c clientes/integraiadev_19/conf/odoo.cfg
```

### Ejecución Regular (Modo Desarrollo)
```bash
./odoo/odoo-bin -d dbintegraiadev_19 -c clientes/integraiadev_19/conf/odoo.cfg --dev=all
```

### Actualización de Módulos Específicos
```bash
# Actualizar módulos de IA
./odoo/odoo-bin -d dbintegraiadev_19 -c clientes/integraiadev_19/conf/odoo.cfg --dev=all -u chat_bot_n8n_ia,chat_bot_integra --stop-after-init
```

---

## 7. Acceso al Sistema

URL Local/Server: `http://5.189.161.7:38069/`

---

## Notas Adicionales
- **Logs**: Los logs están configurados en `clientes/integraiadev_19/log/odoo.log`. Puedes verlos en tiempo real con `tail -f`.
- **Scripts**: Usa `./stop_odoo_puertos.sh` para liberar los puertos antes de reiniciar.
