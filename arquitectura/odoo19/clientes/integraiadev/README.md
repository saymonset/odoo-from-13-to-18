
## Para ./start_odoo.sh y start el odoo con la nueva  bd , debes abrir el scripts y apuntar a la nueva bd

## Ubicate en esta ruta para instalar los fuentes de odoo y el ambiente virtual enviroment .venv
```bash
/home/simon/odoo-13-18/arquitectura/odoo19
```
## Bjar los puertos , cambia el nombre del proyecto o modulo a tumbar por ejemplo: integraiadev en los start_odoo.sh
```bash
odoo@vmi2870902:~/odoo-from-13-to-18/arquitectura/odoo19$ ls
README.md  clientes  odoo  start_odoo.sh  stop_odoo_puertos.sh  tasa_bcv.py
odoo@vmi2870902:~/odoo-from-13-to-18/arquitectura/odoo19$ ./stop_odoo_puertos.sh 
```

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
  git clone -b 19.0 --single-branch --depth 1 https://github.com/odoo/odoo.git odoo
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

# En postgres creamos el usuario odoo19

```bash
   psql -U postgres -d postgres
```
# Si estas en docker la bd postgres
```bash
 docker exec -it odoo-db18-n8n bash
 psql -U odoo -d postgres
 ```

```bash
CREATE ROLE integraiadev WITH LOGIN PASSWORD '123456' CREATEDB;
 ALTER USER integraiadev WITH SUPERUSER;
```
 

# En postgres creamos el usuario odoo19 con super usuario

```bash
CREATE ROLE integraiadev WITH LOGIN PASSWORD '123456' CREATEDB SUPERUSER;
```
```bash
\q
\exit
# Dentro de odoo-db18-n8n   ( docker exec -it odoo-db18-n8n bash )
docker exec -it odoo-db18-n8n bash
 psql -U integraiadev -d postgres
 CREATE DATABASE dbintegraiadev;
 ```

# Para listar los roles y permisos

```bash
\du
```

# Abrir el puerto en el server para que pueda escuchar

```bash
sudo ufw allow 38069/tcp
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
/home/simon/odoo-13-18/arquitectura/odoo19
```
# Instalamo la base de odoo en bd por primera vez

# Si no esta activao el ambiente

```bash
source .venv/bin/activate
```
# Inicializamos BD
```bash
./odoo/odoo-bin -d dbintegraiadev -i base -c clientes/integraiadev/conf/odoo.cfg
```

# Arrancamos odoo de manera regular

# Si no esta activao el ambiente

```bash
source .venv/bin/activate
```

```bash
 ./odoo/odoo-bin -d dbintegraiadev -c clientes/integraiadev/conf/odoo.cfg --dev=all
```
# actualizar modulo
```bash
 ./odoo/odoo-bin -d dbintegraiadev -c clientes/integraiadev/conf/odoo.cfg -u all
 ./odoo/odoo-bin -d dbintegraiadev -c clientes/integraiadev/conf/odoo.cfg --dev=all -u web -u website --stop-after-init
```
# Accedemos
```bash
http://5.189.161.7:18069/
```

```bash
 ./odoo/odoo-bin --test-enable --stop-after-init  -d dbintegraiadev -i a_hospital_19 -c clientes/integraiadev/conf/odoo.cfg 
 ```
# Coloca lo que haga en los fuentes a los addons de docker
```bash
cd /root/odoo/odoo-from-13-to-18/arquitectura/odoo19/clientes/integraiadev/extra-addons/extra
```
```bash
cp -r evolution-api /root/odoo/n8n-evolution-ap
i-odoo-19/v19/addons
```
 