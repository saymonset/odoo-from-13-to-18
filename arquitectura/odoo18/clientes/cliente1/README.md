## Ubicate en esta ruta para instalar los fuentes de odoo y el ambiente virtual enviroment .venv

/home/simon/odoo-13-18/arquitectura/odoo18
sudo apt install tree
tree -L 2 .
cat /etc/os-release
ps aux | grep odoo-bin

## Configurar en ubuntu locale para venezuela. Correr en la terminal

```bash
sudo locale-gen es_VE.UTF-8
sudo update-locale
```
# MULTI LENGUAJE
# Creamos lenguaje multiple con i18n
# 1 -) Crear el directorio i18n en tu módulo:
# Asegúrate de que tu módulo evolution-api tenga un directorio i18n en su estructura.

 # 2-) Generar el archivo de traducción base (.pot):
 # Usa el comando de Odoo para exportar las cadenas traducibles de tu módulo a un archivo .pot
```bash
./odoo/odoo-bin --addons-path=/root/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra -d dbcontabo18 --i18n-export=clientes/cliente1/extra-addons/extra/evolution-api/i18n/evolution_api.pot --modules=evolution-api -c clientes/cliente1/conf/odoo.cfg
```
# 3-) Crear archivos de traducción para los idiomas deseados:
  # Copia el archivo evolution_api.pot a un archivo .po para cada idioma que desees soportar. Por ejemplo, para español:

  
# Repite este paso para otros idiomas (por ejemplo, en.po para inglés).
# Cargar las traducciones en Odoo:
# 4-) Actualiza tu módulo para cargar las traducciones:
./odoo/odoo-bin --addons-path=/root/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra -d dbcontabo18 -u evolution-api -c clientes/cliente1/
conf/odoo.cfg
# FIN MULTI LENGUAJE

# -----------------------------------
## Descripción

Este es la arquitectura para implementar diferentes versiones de odoo con sus respectios clientes y extra-addons

# Instalacion de algunas librerias standar

```bash
sudo apt install openssh-server fail2ban libxml2-dev libxslt1-dev zlib1g-dev libsasl2-dev libldap2-dev build-essential libssl-dev libffi-dev libmysqlclient-dev libpq-dev libjpeg8-dev liblcms2-dev libblas-dev libatlas-base-dev git curl   fontconfig libxrender1 xfonts-75dpi xfonts-base -y

```

```bash
 sudo apt install snapd
 sudo apt-get install ffmpeg -y
```

```bash
sudo snap install astral-uv --classic
```

# Bajar fuentes

```bash
  git clone -b 18.0 --single-branch --depth 1 https://github.com/odoo/odoo.git odoo
```

# Instalar version python con uv

```bash
uv python install 3.11
```

# colocar el enviroment

```bash
uv venv --python 3.11
```

# activarlo

```bash
source .venv/bin/activate
```

````bash
    uv pip install pandas
    uv  pip install xmltodict
    uv    pip install gtts
    # para debugg
    uv pip install ptvsd
    uv pip install inotify
    uv pip install watchdog
    uv pip install openai
    uv pip install lxml
    uv pip install pydantic
    uv pip install pycryptodome
    uv pip install pydub

     ``
# Instalar los requirement
```bash
uv pip install -r odoo/requirements.txt
````

# En postgres creamos el usuario odoo18

```bash
   psql -U postgres -d postgres
```

```bash
CREATE ROLE odooia WITH LOGIN PASSWORD '123456' CREATEDB;
 ALTER USER odooia WITH SUPERUSER;
```
 
```

# En postgres creamos el usuario odoo18 con super usuario

```bash
CREATE ROLE odooia WITH LOGIN PASSWORD '123456' CREATEDB SUPERUSER;
```
```bash
\q
\exit
 psql -U odooia -d postgres
 CREATE DATABASE dbcontabo18;
 ```

# Para listar los roles y permisos

```bash
\du
```

# Abrir el puertoen el server para que pueda escuchar

```bash
sudo ufw allow 8020/tcp
```

# Abrir puerto para debugguear

```bash
sudo ufw allow 49003/tcp
```

# Abrir puerto para debugguear

```bash
sudo ufw allow 42091/tcp
```

# Abrir puerto para debugguear

```bash
sudo ufw allow 8888/tcp
```
# Ir a la ruta or path
```bash
/home/simon/odoo-13-18/arquitectura/odoo18
```
# Instalamo la base de odoo en bd por primera vez

# Si no esta activao el ambiente

```bash
source .venv/bin/activate
```

```bash
./odoo/odoo-bin -d dbcontabo18 -i base -c clientes/cliente1/conf/odoo.cfg
```

# Arrancamos odoo de manera regular

# Si no esta activao el ambiente

```bash
source .venv/bin/activate
```

```bash
 ./odoo/odoo-bin -d dbcontabo18 -c clientes/cliente1/conf/odoo.cfg --dev=all
```
# Accedemos
```bash
http://5.189.161.7:8020/
```

# Coloca lo que haga en los fuentes a los addons de docker
```bash
cd /root/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra
```
```bash
cp -r evolution-api /root/odoo/n8n-evolution-ap
i-odoo-18/v18/addons
```
 