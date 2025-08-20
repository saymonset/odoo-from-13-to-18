## En este patch corre:

odoo18simon@simon:~/odoo-13-18/arquitectura/odoo18$ ./odoo/odoo-bin -d dbtestclient18 -i base -c clientes/testclient/conf/odoo.cfg

## Para debuguear , siempre en el ssh abrir los fuentes desde ODOO-13-18

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
     ``
# Instalar los requirement
```bash
uv pip install -r odoo/requirements.txt
````

# En postgres creamos el usuario testclient

```bash
   psql -U postgres -d postgres
```

```bash
CREATE ROLE testclient WITH LOGIN PASSWORD 'odoo' CREATEDB;
 ALTER USER testclient WITH SUPERUSER;
```

# En postgres creamos el usuario testclient con super usuario

```bash
CREATE ROLE testclient WITH LOGIN PASSWORD 'odoo' CREATEDB SUPERUSER;
```

# Para listar los roles y permisos

```bash
\du
```

# Abrir el puertoen el server para que pueda escuchar

```bash
sudo ufw allow 8018/tcp
```

# Instalamo la base de odoo en bd por primera vez

# Si no esta activao el ambiente

```bash
source .venv/bin/activate
```

```bash
./odoo/odoo-bin -d dbtestclient18 -i base -c clientes/testclient/conf/odoo.cfg
```

# Arrancamos odoo de manera regular

# Si no esta activao el ambiente

```bash
source .venv/bin/activate
```

```bash
./odoo/odoo-bin -d dbcliente1_18 -c clientes/cliente1/conf/odoo.cfg
```
