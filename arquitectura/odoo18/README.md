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
  ls
  
  
```

# Instalar version python con uv

```bash
uv python install 3.12
```

# colocar el enviroment

```bash
uv venv --python 3.12
```

# activarlo

```bash
cd /home/odoo/odoo-from-13-to-18/arquitectura/odoo18
source .venv/bin/activate
```

````bash
    uv pip install pandas
    uv  pip install xmltodict
    uv    pip install gtts
     uv pip install lxml
    uv pip install gevent psycogreen
    uv pip install  greenlet
    uv pip install websocket-client
    uv pip install websocket-client
    uv pip install "pydantic>=2.0,<3.0" "httpx>=0.27.0" 
    uv pip install pypdfmake



     ``
# Instalar los requirement
```bash
uv pip install -r odoo/requirements.txt
````

# En postgres creamos el usuario odoo18

```bash
   docker exec -it odoo-db18 bash
   psql -U odoo -d postgres
```

```bash
CREATE ROLE odoo18 WITH LOGIN PASSWORD 'odoo' CREATEDB;
 ALTER USER odoo18 WITH SUPERUSER;
```

# En postgres creamos el usuario odoo18 con super usuario

```bash
CREATE ROLE odoo18 WITH LOGIN PASSWORD 'odoo' CREATEDB SUPERUSER;
```

# Para listar los roles y permisos

```bash
\du
```

# Abrir el puertoen el server para que pueda escuchar

```bash
#sudo ufw allow 8018/tcp
```
```bash
   docker exec -it odoo-db18 bash
   psql -U odoo18 -d postgres
   CREATE DATABASE dbcliente1_18;
```
# Instalamo la base de odoo en bd por primera vez

# Ir a la ruta or path
```bash
/home/simon/odoo-13-18/arquitectura/odoo18
```


# Si no esta activao el ambiente

```bash
source .venv/bin/activate
```
# SE obtiene la ip de ls bd de docker y se configura en el odoo.cfg, tambien se
# coloca el puerto 18069 ue es el puertoq eu tiene nginx abierto para escucharlop a travez del 80

```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' odoo-db18
```
# Solo se corre para inicializar la base de datos y se apaga con ctrl + c
```bash
./odoo/odoo-bin -d dbcliente1_18 -i base -c clientes/cliente1/conf/odoo.cfg
```

# Arrancamos odoo de manera regular
# Si no esta activao el ambiente

```bash
source .venv/bin/activate
```
# Rn naturalmente
```bash
# Corre normal
 
./odoo/odoo-bin -d dbcliente1_18 -c clientes/cliente1/conf/odoo.cfg 
./odoo/odoo-bin -d dbcliente1_18 -c clientes/cliente1/conf/odoo.cfg -u all --dev=assets
./odoo/odoo-bin -d dbcliente1_18  -u chatter_voice_note -c clientes/cliente1/conf/odoo.cfg
./odoo/odoo-bin  python -m debugpy --listen 5679 --wait-for-client ./odoo/odoo-bin -d dbcliente1_18 -c clientes/cliente1/conf/odoo.cfg



# actualizqar un modulo
./odoo/odoo-bin -d dbcliente1_18 -c clientes/cliente1/conf/odoo.cfg -u a_hospital

#Entrar al shell
./odoo/odoo-bin shell -d dbcliente1_18 -c clientes/cliente1/conf/odoo.cfg
./odoo/odoo-bin shell -d dbcliente1_18 -c clientes/cliente1/conf/odoo.cfg < clientes/cliente1/tmp/bus.py

# Desinstala un modulo por shell
# Antes, entrar a la shell '#Entrar al shell'
1-) ./odoo/odoo-bin shell -d dbcliente1_18 -c clientes/cliente1/conf/odoo.cfg
2-) env['ir.module.module'].search([('name', '=', 'chatter_voice_note')]).button_immediate_uninstall()

# en tu navegador por console, limpiar cache
localStorage.clear();
sessionStorage.clear();
indexedDB.deleteDatabase('odoo');
caches.keys().then(names => names.forEach(name => caches.delete(name)));
```
# Accedemos
```bash
https://jumpjibe.com
```

 source .venv/bin/activate
  uv pip install debugpy
  python -m debugpy --version
  python -m debugpy --listen 5679 --wait-for-client ./odoo/odoo-bin -d dbcliente1_18 -c clientes/cliente1/conf/odoo.cfg
   python -m debugpy --listen 5679 ./odoo/odoo-bin -d dbcliente1_18 -c clientes/cliente1/conf/odoo.cfg

   # Matar puertos
    _handleAudioResponse(ev) {
        console.log('🎯 _handleAudioResponse EJECUTADO', ev);
        
        const message = ev.detail;
        console.log('📨 Mensaje recibido en _handleAudioResponse:', message);
        
        if (message && message.type === 'new_response') {
            console.log('✅ Mensaje new_response detectado en _handleAudioResponse');
            
            // ✅ ACTUALIZACIÓN DIRECTA DEL STATE
            this.state.final_message = message.final_message || '';
            this.state.answer_ia = message.answer_ia || '';
            this.state.loading_response = false;
            
            console.log('🔄 Estado actualizado:', {
                final_message: this.state.final_message,
                answer_ia: this.state.answer_ia,
                loading_response: this.state.loading_response
            });
            
            // ✅ FORZAR ACTUALIZACIÓN
            this.render();
            
            this.notification.add("✅ Respuesta de IA recibida", { 
                type: "success", 
                sticky: false 
            });
        } else {
            console.log('❌ Mensaje no reconocido:', message);
        }
    }
   netstat -tlnp | grep 8072  # Debe mostrar un proceso de Python/Odoo



   ###############################EJECUTAR SCRIPT EN ODOO##############
   ./odoo/odoo-bin shell -d dbcliente1_18 -c clientes/cliente1/conf/odoo.cfg --shell-interface=python <<'EOF'
print("=== INSPECCIONANDO EL MÉTODO REAL ===")

from odoo.addons.bus.controllers.main import BusController
import inspect

# Ver la firma real del método
method = getattr(BusController, 'has_missed_notifications', None)
if method:
    print(f"Firma del método: {inspect.signature(method)}")
    print(f"Código fuente: {inspect.getsource(method) if hasattr(method, '__code__') else 'No disponible'}")
else:
    print("Método no encontrado")

# Verificar decoradores
if hasattr(method, 'routing'):
    print(f"Decorador routing: {method.routing}")
EOF

   
