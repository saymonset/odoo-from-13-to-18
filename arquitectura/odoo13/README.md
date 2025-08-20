## Descripción

Este es la arquitectura para implementar diferentes versiones de odoo con sus respectios clientes y extra-addons

# Instalacion de algunas librerias standar

```bash

sudo apt install -y python3-pip build-essential wget python3-dev python3-venv \
libxslt-dev libzip-dev libldap2-dev libsasl2-dev python3-setuptools node-less \
libjpeg-dev zlib1g-dev libpq-dev libxml2-dev libxslt1-dev libldap2-dev \
libsasl2-dev libtiff5-dev libjpeg8-dev libopenjp2-7-dev liblcms2-dev \
libwebp-dev libharfbuzz-dev libfribidi-dev libxcb1-dev

```

sudo apt install build-essential
sudo apt install python3.8-dev
pip install cython
sudo apt install libev-dev
pip install gevent --only-binary :all:
sudo apt update
sudo apt install build-essential python3.8-dev libev-dev
pip install --upgrade pip setuptools wheel

```bash
 sudo apt install snapd
```

```bash
mkdir -p odoo13
```

# Bajar fuentes

```bash
  git clone -b 13.0 --single-branch --depth 1 https://github.com/odoo/odoo.git odoo
```

# Instalar version python con uv

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
```

```bash
sudo apt update
```

```bash
sudo apt install python3.8 python3.8-venv python3.8-dev
```

```bash
python3.8 -m venv .venv
```

# activarlo

```bash
source .venv/bin/activate
```

```bash
 pip install wheel
```

# Instalar los requirement

```bash
pip install -r odoo/requirements.txt
```

# En postgres creamos el usuario odoo

```bash
   psql -U postgres -d postgres
```

```bash
CREATE ROLE odoo15 WITH LOGIN PASSWORD 'odoo' CREATEDB;
```

# En postgres creamos el usuario odoo con super usuario

```bash
CREATE ROLE odoo15 WITH LOGIN PASSWORD 'odoo' CREATEDB SUPERUSER;
```

# Para listar los roles y permisos

```bash
\du
```

# Abrir el puertoen el server para que pueda escuchar

```bash
sudo ufw allow 8013/tcp
```

# Instalamos la base bd por primera vez

```bash
./odoo/odoo-bin -d dbodoo13 -i base -c clientes/cliente1/conf/odoo.cfg
```

# Arrancamos odoo de manera regular

# Si no esta activao el ambiente

```bash
source .venv/bin/activate
```

```bash
./odoo/odoo-bin -d dbodoo13 -c clientes/cliente1/conf/odoo.cfg
```
