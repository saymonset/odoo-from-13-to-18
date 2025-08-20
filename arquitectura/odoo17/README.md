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

```bash
mkdir -p odoo13 odoo14 odoo15 odoo16 odoo17 odoo18
```

# Bajar fuentes

```bash
  git clone -b 17.0 --single-branch --depth 1 https://github.com/odoo/odoo.git odoo
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

# Instalar los requirement

```bash
uv pip install -r odoo/requirements.txt
```

# En postgres creamos el usuario odoo17

```bash
   psql -U postgres -d postgres
```

```bash
CREATE ROLE odoo17 WITH LOGIN PASSWORD 'odoo' CREATEDB;
 ALTER USER odoo17 WITH SUPERUSER;
```

# En postgres creamos el usuario odoo17 con super usuario

```bash
CREATE ROLE odoo17 WITH LOGIN PASSWORD 'odoo' CREATEDB SUPERUSER;
```

# Para listar los roles y permisos

```bash
\du
```

# Abrir el puertoen el server para que pueda escuchar

```bash
sudo ufw allow 8017/tcp
```

# cambiar ruta del odoo.cfg

sustituir esta /opt/ic-tecnology/arquitectura/odoo17 por la actual

# Instalamo la base de odoo en bd por primera vez

```bash
./odoo/odoo-bin -d dbodoo17 -i base -c clientes/cliente1/conf/odoo.cfg
```

# Arrancamos odoo de manera regular

# Si no esta activao el ambiente

```bash
source .venv/bin/activate
```

```bash
./odoo/odoo-bin -d dbodoo17 -c clientes/cliente1/conf/odoo.cfg
```
