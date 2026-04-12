
################################***PRODUCCION***################################
 PROXY_MODE EN EL .CG SE CAMBIO A FALSE SIE STA EN DEVELOPER, EN PRODUCCION DEBE ESTAR EN TRUE

################################***FIN PRODUCCION***################################

###############################****HACER BACKUP****################################
   SIEMPRE QUE HAGAS BACKUP A PRODUCCION COLOCA LA BANDERA proxy_mode = True en el arquitectura/odoo19/clientes/integraia_19/conf/odoo.cfg
  solo debes abrir el archivo backup.sh y cambiar el nombre del cliente a respaldar y ejecutarlo ./9_1_backup_bd.sh
  ###############################****FIN HACER BACKUP****################################

  ###############################****HACER RESTORE****################################
    solo debes abrir el archivo 9_3__restore_odoo_filestore.sh y cambiar el nombre del cliente a restaurar y ejecutarlo ./9_3__restore_odoo_filestore.sh
    ###############################****FIN HACER RESTORE****################################



## Si vas a debug , en el archivo, cambiar el 18 por la version que vas a debuguear y en la carpeta cliente1 es la default
'''bash
/home/odoo/odoo-from-13-to-18/.vscode/launch.json
```
## Para debuguear , siempre en el ssh abrir los fuentes desde ODOO-13-19
```bash
cd /home/odoo/odoo-from-13-to-18/arquitectura/odoo19
```

### En el archivo start_odoo.sh , debes cambiar el nombre del cliente a correr

## Buscar un modulo

## ejemplo , find con eso

\_name = "stock.picking.type"

## Descripción

Este es la arquitectura para implementar diferentes versiones de odoo con sus respectios clientes y extra-addons

# Instalacion de algunas librerias standar

```bash
sudo apt install openssh-server fail2ban libxml2-dev libxslt1-dev zlib1g-dev libsasl2-dev libldap2-dev build-essential libssl-dev libffi-dev libmysqlclient-dev libpq-dev libjpeg8-dev liblcms2-dev libblas-dev libatlas-base-dev git curl   fontconfig libxrender1 xfonts-75dpi xfonts-base -y

```

```bash
 sudo apt install snapd
```

```bash
sudo snap install astral-uv --classic
```

# Bajar fuentes

```bash
  git clone -b 19.0 --single-branch --depth 1 https://github.com/odoo/odoo.git odoo

  
```

# Instalar version python con uv

```bash
uv python install 3.12
```

#  Instalar viivakoodi para códigos de barras
```bash
uv pip install viivakoodi
uv pip install python-barcode
```

# colocar el enviroment

```bash
uv venv --python 3.12
```

# activarlo

```bash
source .venv/bin/activate
```

````bash
    uv pip install pandas
    uv  pip install xmltodict
    uv    pip install gtts
   uv pip install lxml

     ``
# Instalar los requirement
```bash
uv pip install -r odoo/requirements.txt
````

# En postgres creamos el usuario odoo19

```bash
 docker exec -it odoo-db19-n8n bash
   psql -U odoo -d postgres
```

```bash

CREATE ROLE odoo19 WITH LOGIN PASSWORD 'odoo' CREATEDB ;
 ALTER USER odoo19 WITH SUPERUSER;
```

# En postgres creamos el usuario odoo19 con super usuario

```bash
CREATE ROLE odoo19 WITH LOGIN PASSWORD 'odoo' CREATEDB SUPERUSER;
```
## Para docker
```bash
\q
docker exec -it odoo-db19-n8n bash
   psql -U odoo19 -d postgres
   CREATE USER integraia_19 WITH PASSWORD 'odoo';
   ALTER USER integraia_19 WITH SUPERUSER;

   \q
   docker exec -it odoo-db19-n8n bash
   psql -U integraia_19 -d postgres
   CREATE DATABASE dbintegraia_19;
   GRANT ALL PRIVILEGES ON DATABASE dbhoteljumpjibe_19 TO hoteljumpjibe_19;


```

# Para listar los roles y permisos

```bash
\du
```

# Abrir el puertoen el server para que pueda escuchar

```bash
sudo ufw allow 8019/tcp
```

# Instalamo la base de odoo en bd por primera vez

# Ir a la ruta or path
```bash
/home/simon/odoo-13-19/arquitectura/odoo19
```


# Si no esta activao el ambiente

```bash
source .venv/bin/activate
```

```bash
./odoo/odoo-bin -d dbintegraia_19 -i base -c clientes/cliente1/conf/odoo.cfg

```

# Arrancamos odoo de manera regular

# Si no esta activao el ambiente

```bash
source .venv/bin/activate
```
# si esta activo dl puero lo matamos
```bash
sudo lsof -i :8019
```

```bash
./odoo/odoo-bin -d dbintegraia_19 -c clientes/cliente1/conf/odoo.cfg
```
# Accedemos
```bash
http://5.189.161.7:18069/
```
# Base de datos
```bash
psql -U panna19 -d dbintegraia_19
password:odoo
```
