## Ubicate en esta ruta para instalar los fuentes de odoo y el ambiente virtual enviroment .venv

/home/simon/odoo-13-18/arquitectura/odoo18
sudo apt install tree
tree -L 2 .
cat /etc/os-release
ps aux | grep odoo-bin

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
http://192.168.4.109:8020/
```