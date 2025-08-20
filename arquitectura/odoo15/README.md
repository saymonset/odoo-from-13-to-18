## Descripción

Este es la arquitectura para implementar diferentes versiones de odoo con sus respectios clientes y extra-addons

# Instalacion de algunas librerias standar

```bash
sudo apt install openssh-server fail2ban libxml2-dev libxslt1-dev zlib1g-dev libsasl2-dev libldap2-dev build-essential libssl-dev libffi-dev libmysqlclient-dev libpq-dev libjpeg8-dev liblcms2-dev libblas-dev libatlas-base-dev git curl   fontconfig libxrender1 xfonts-75dpi xfonts-base libjpeg-dev libevent-dev -y
```

```bash
 sudo apt install snapd
```

      sudo apt-get update

sudo add-apt-repository ppa:deadsnakes/ppa
pip install --upgrade pip setuptools wheel
sudo apt-get install -y build-essential libssl-dev libffi-dev python3-dev
sudo apt install python3.8 python3.8-venv
python3.8 -m venv .venv
sudo apt-get install -y python3-dev libldap2-dev libsasl2-dev libssl-dev build-essential

Editar el archivo requirements.txt:
Abre el archivo requirements.txt y reemplaza la línea:
javascript
gevent==20.9.0
por:
gevent>=21.1.2
pip install --upgrade cryptography

pip install cryptography --only-binary :all:
pip install --upgrade cryptography
in odoo/requirement.txt change
cryptography>=41.0.0

```bash
mkdir -p odoo15
```

# Bajar fuentes

```bash
  git clone -b 15.0 --single-branch --depth 1 https://github.com/odoo/odoo.git odoo
```

# activarlo

```bash
source .venv/bin/activate
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
 ALTER USER odoo15 WITH SUPERUSER;
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
sudo ufw allow 8015/tcp
```

# cambiar ruta del odoo.cfg

sustituir esta /opt/ic-tecnology/arquitectura/odoo15 por la actual

# Instalamos la base bd por primera vez

```bash
./odoo/odoo-bin -d dbodoo15 -i base -c clientes/cliente1/conf/odoo.cfg
```

# Arrancamos odoo de manera regular

# Si no esta activao el ambiente

```bash
source .venv/bin/activate
```

# Sin warnings

```bash
PYTHONWARNINGS="ignore" ./odoo/odoo-bin -d dbodoo15 -i base -c clientes/cliente1/conf/odoo.cfg
```

# Normal

```bash
./odoo/odoo-bin -d dbodoo15 -c clientes/cliente1/conf/odoo.cfg
```

# Ver puerto si esta en uso

```bash
lsof | grep :8015
```
