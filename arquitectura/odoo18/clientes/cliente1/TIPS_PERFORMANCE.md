 # Crear archivo de swap (2GB)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Hacerlo permanente
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Fix ¿por qué el error "No space left on device"?
# Ejecutar instruccion
sudo sysctl fs.inotify.max_user_watches=524288
# Para hacerlo permanente, agrega esta línea a /etc/sysctl.conf:
vi /etc/sysctl.conf:
fs.inotify.max_user_watches=524288
# luego ejecuta 
sudo sysctl -p.
