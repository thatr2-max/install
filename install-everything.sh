#!/bin/bash
# X1 Carbon Ultimate Server - FULL INSTALLATION
# Installs EVERYTHING with no questions asked

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }

if [ "$EUID" -eq 0 ]; then 
    print_error "Do not run as root!"
    exit 1
fi

# CONFIGURATION (Change these if you want)
HOSTNAME="x1-server"
TIMEZONE="America/New_York"
SERVER_USER="$USER"

print_header "X1 Carbon Ultimate Server - Full Install"
echo "Installing EVERYTHING..."
sleep 2

# ==========================================
# SYSTEM SETUP
# ==========================================
print_header "System Updates"
sudo dnf update -y

print_header "Installing Base Packages"
sudo dnf install -y \
    cockpit cockpit-storaged cockpit-networkmanager cockpit-podman \
    openssh-server avahi avahi-tools nss-mdns \
    tmux htop ncdu curl wget git nano vim tar unzip \
    lm_sensors smartmontools rsync screen \
    docker docker-compose \
    samba samba-client cifs-utils \
    dnf-automatic \
    tailscale

print_success "Base packages installed"

# ==========================================
# HOSTNAME & TIMEZONE
# ==========================================
print_header "Configuring System"
sudo hostnamectl set-hostname $HOSTNAME
sudo timedatectl set-timezone $TIMEZONE
sudo systemctl enable --now avahi-daemon
print_success "Hostname: $HOSTNAME.local"

# ==========================================
# DISABLE LID CLOSE
# ==========================================
print_header "Laptop Configuration"
sudo mkdir -p /etc/systemd/logind.conf.d/
sudo tee /etc/systemd/logind.conf.d/no-suspend.conf > /dev/null <<EOF
[Login]
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
EOF
sudo systemctl restart systemd-logind
print_success "Lid close disabled"

# ==========================================
# COCKPIT
# ==========================================
print_header "Enabling Cockpit"
sudo systemctl enable --now cockpit.socket
sudo firewall-cmd --permanent --add-service=cockpit 2>/dev/null || true
sudo firewall-cmd --reload 2>/dev/null || true
print_success "Cockpit enabled"

# ==========================================
# SSH HARDENING
# ==========================================
print_header "Hardening SSH"
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup 2>/dev/null || true
sudo tee /etc/ssh/sshd_config.d/hardening.conf > /dev/null <<EOF
PermitRootLogin no
PasswordAuthentication yes
PubkeyAuthentication yes
MaxAuthTries 3
MaxSessions 2
ClientAliveInterval 300
ClientAliveCountMax 2
EOF
sudo systemctl enable --now sshd
sudo systemctl restart sshd
sudo firewall-cmd --permanent --add-service=ssh 2>/dev/null || true
sudo firewall-cmd --reload 2>/dev/null || true
print_success "SSH hardened"

# ==========================================
# AUTO UPDATES
# ==========================================
print_header "Enabling Auto Updates"
sudo sed -i 's/^apply_updates = .*/apply_updates = yes/' /etc/dnf/automatic.conf
sudo sed -i 's/^upgrade_type = .*/upgrade_type = security/' /etc/dnf/automatic.conf
sudo systemctl enable --now dnf-automatic.timer
print_success "Automatic security updates enabled"

# ==========================================
# LOG ROTATION
# ==========================================
print_header "Configuring Log Rotation"
sudo tee /etc/logrotate.d/docker-containers > /dev/null <<EOF
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size 10M
    missingok
    delaycompress
    copytruncate
}
EOF
print_success "Log rotation configured"

# ==========================================
# DISK MONITORING
# ==========================================
print_header "Setting up Disk Monitoring"
cat > $HOME/disk-monitor.sh <<'EOF'
#!/bin/bash
THRESHOLD=90
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt $THRESHOLD ]; then
    echo "WARNING: Disk usage is at ${DISK_USAGE}%"
fi
EOF
chmod +x $HOME/disk-monitor.sh
(crontab -l 2>/dev/null; echo "0 9 * * * $HOME/disk-monitor.sh") | crontab -
print_success "Disk monitoring enabled"

# ==========================================
# SMART MONITORING
# ==========================================
print_header "Setting up SMART Monitoring"
sudo systemctl enable --now smartd
sudo tee /etc/smartmontools/smartd.conf > /dev/null <<EOF
DEVICESCAN -a -o on -S on -n standby,q -s (S/../.././02|L/../../6/03) -W 4,35,40
EOF
sudo systemctl restart smartd
print_success "SMART monitoring enabled"

# ==========================================
# SAMBA
# ==========================================
print_header "Setting up Samba"
sudo mkdir -p /srv/samba/{shared,media,downloads}
sudo chown -R $SERVER_USER:$SERVER_USER /srv/samba
sudo chmod -R 755 /srv/samba

sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.backup 2>/dev/null || true
sudo tee /etc/samba/smb.conf > /dev/null <<EOF
[global]
    workgroup = WORKGROUP
    server string = $HOSTNAME File Server
    security = user
    map to guest = Bad User
    dns proxy = no

[shared]
    path = /srv/samba/shared
    browseable = yes
    writable = yes
    guest ok = no
    valid users = $SERVER_USER
    create mask = 0644
    directory mask = 0755

[media]
    path = /srv/samba/media
    browseable = yes
    writable = yes
    guest ok = no
    valid users = $SERVER_USER
    create mask = 0644
    directory mask = 0755

[downloads]
    path = /srv/samba/downloads
    browseable = yes
    writable = yes
    guest ok = no
    valid users = $SERVER_USER
    create mask = 0644
    directory mask = 0755
EOF

echo -e "changeme\nchangeme" | sudo smbpasswd -a $SERVER_USER -s
sudo systemctl enable --now smb nmb
sudo firewall-cmd --permanent --add-service=samba 2>/dev/null || true
sudo firewall-cmd --reload 2>/dev/null || true
print_success "Samba configured (password: changeme - CHANGE THIS!)"

# ==========================================
# DOCKER
# ==========================================
print_header "Configuring Docker"
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
sudo systemctl enable --now docker
sudo usermod -aG docker $SERVER_USER
print_success "Docker configured"

# ==========================================
# SSL CERTIFICATES
# ==========================================
print_header "Generating SSL Certificates"
SSL_DIR="$HOME/ssl"
mkdir -p $SSL_DIR
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
    -keyout $SSL_DIR/server.key \
    -out $SSL_DIR/server.crt \
    -subj "/C=US/ST=State/L=City/O=Home/OU=Server/CN=$HOSTNAME.local" 2>/dev/null
chmod 600 $SSL_DIR/server.key
print_success "SSL certificates generated"

# ==========================================
# FIREWALL HARDENING
# ==========================================
print_header "Hardening Firewall"
sudo firewall-cmd --permanent --add-rich-rule='rule service name="ssh" limit value="10/m" accept'
sudo firewall-cmd --set-log-denied=all
print_success "Firewall hardened"

# ==========================================
# DOCKER SERVICES
# ==========================================
print_header "Setting up Docker Services"
DOCKER_DIR="$HOME/docker-services"
mkdir -p $DOCKER_DIR
cd $DOCKER_DIR

cat > docker-compose.yml <<EOF
version: '3.8'

services:
  homepage:
    image: ghcr.io/gethomepage/homepage:latest
    container_name: homepage
    ports:
      - 3000:3000
    volumes:
      - ./homepage/config:/app/config
      - /var/run/docker.sock:/var/run/docker.sock:ro
    restart: unless-stopped
    environment:
      - PUID=1000
      - PGID=1000

  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    ports:
      - 9000:9000
      - 9443:9443
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - portainer_data:/data
    restart: unless-stopped

  pihole:
    image: pihole/pihole:latest
    container_name: pihole
    ports:
      - "53:53/tcp"
      - "53:53/udp"
      - "8080:80/tcp"
    environment:
      - TZ=$TIMEZONE
      - WEBPASSWORD=changeme
    volumes:
      - ./pihole/etc-pihole:/etc/pihole
      - ./pihole/etc-dnsmasq.d:/etc/dnsmasq.d
    restart: unless-stopped
    cap_add:
      - NET_ADMIN

  uptime-kuma:
    image: louislam/uptime-kuma:latest
    container_name: uptime-kuma
    ports:
      - 3001:3001
    volumes:
      - uptime-kuma_data:/app/data
    restart: unless-stopped

  watchtower:
    image: containrrr/watchtower:latest
    container_name: watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_SCHEDULE=0 0 4 * * *
    restart: unless-stopped

  jellyfin:
    image: jellyfin/jellyfin:latest
    container_name: jellyfin
    ports:
      - 8096:8096
    volumes:
      - jellyfin_config:/config
      - jellyfin_cache:/cache
      - /srv/samba/media:/media
    restart: unless-stopped
    environment:
      - TZ=$TIMEZONE

  qbittorrent:
    image: lscr.io/linuxserver/qbittorrent:latest
    container_name: qbittorrent
    ports:
      - 8090:8090
      - 6881:6881
      - 6881:6881/udp
    volumes:
      - qbittorrent_config:/config
      - /srv/samba/downloads:/downloads
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=$TIMEZONE
      - WEBUI_PORT=8090
    restart: unless-stopped

  syncthing:
    image: lscr.io/linuxserver/syncthing:latest
    container_name: syncthing
    ports:
      - 8384:8384
      - 22000:22000/tcp
      - 22000:22000/udp
      - 21027:21027/udp
    volumes:
      - syncthing_config:/config
      - /srv/samba/shared:/data
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=$TIMEZONE
    restart: unless-stopped

  netdata:
    image: netdata/netdata:latest
    container_name: netdata
    ports:
      - 19999:19999
    volumes:
      - netdata_config:/etc/netdata
      - netdata_lib:/var/lib/netdata
      - netdata_cache:/var/cache/netdata
      - /etc/passwd:/host/etc/passwd:ro
      - /etc/group:/host/etc/group:ro
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      - TZ=$TIMEZONE
    cap_add:
      - SYS_PTRACE
    security_opt:
      - apparmor:unconfined
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - 9090:9090
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - 3003:3000
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - 9100:9100
    command:
      - '--path.rootfs=/host'
    volumes:
      - /:/host:ro,rslave
    restart: unless-stopped

  homeassistant:
    image: ghcr.io/home-assistant/home-assistant:stable
    container_name: homeassistant
    ports:
      - 8123:8123
    volumes:
      - homeassistant_config:/config
      - /etc/localtime:/etc/localtime:ro
    environment:
      - TZ=$TIMEZONE
    restart: unless-stopped
    privileged: true

volumes:
  portainer_data:
  uptime-kuma_data:
  jellyfin_config:
  jellyfin_cache:
  qbittorrent_config:
  syncthing_config:
  netdata_config:
  netdata_lib:
  netdata_cache:
  prometheus_data:
  grafana_data:
  homeassistant_config:
EOF

# Homepage config
mkdir -p homepage/config
cat > homepage/config/settings.yaml <<'EOF'
title: Home Server
background: https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920
cardBlur: md
theme: dark
headerStyle: boxed
layout:
  Services:
    style: row
    columns: 4
EOF

SERVER_IP=$(hostname -I | awk '{print $1}')
cat > homepage/config/services.yaml <<EOF
---
- Server Management:
    - Cockpit:
        icon: cockpit.png
        href: https://$HOSTNAME.local:9090
        description: System Management
    - Portainer:
        icon: portainer.png
        href: http://$HOSTNAME.local:9000
        description: Docker Management

- Network Services:
    - Pi-hole:
        icon: pi-hole.png
        href: http://$HOSTNAME.local:8080/admin
        description: Ad Blocking
    - Uptime Kuma:
        icon: uptime-kuma.png
        href: http://$HOSTNAME.local:3001
        description: Service Monitoring

- Media & Downloads:
    - Jellyfin:
        icon: jellyfin.png
        href: http://$HOSTNAME.local:8096
        description: Media Server
    - qBittorrent:
        icon: qbittorrent.png
        href: http://$HOSTNAME.local:8090
        description: Downloads
    - Syncthing:
        icon: syncthing.png
        href: http://$HOSTNAME.local:8384
        description: File Sync

- Monitoring:
    - Netdata:
        icon: netdata.png
        href: http://$HOSTNAME.local:19999
        description: Real-time Stats
    - Grafana:
        icon: grafana.png
        href: http://$HOSTNAME.local:3003
        description: Metrics Dashboard

- Smart Home:
    - Home Assistant:
        icon: home-assistant.png
        href: http://$HOSTNAME.local:8123
        description: Smart Home Hub

- File Access:
    - Samba Shares:
        icon: samba.png
        href: smb://$HOSTNAME.local/shared
        description: Network Files
EOF

cat > homepage/config/widgets.yaml <<'EOF'
---
- search:
    provider: duckduckgo
    target: _blank

- datetime:
    text_size: xl
    format:
      timeStyle: short
      dateStyle: short
      hour12: false

- resources:
    cpu: true
    memory: true
    disk: /
EOF

# Prometheus config
mkdir -p prometheus
cat > prometheus/prometheus.yml <<'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
EOF

print_success "Docker configs created"

# Open firewall ports
print_header "Opening Firewall Ports"
sudo firewall-cmd --permanent --add-port={3000,9000,8080,3001,8096,8090,6881,8384,22000,19999,3003,9090,8123}/tcp 2>/dev/null || true
sudo firewall-cmd --permanent --add-port={6881,22000,21027}/udp 2>/dev/null || true
sudo firewall-cmd --reload 2>/dev/null || true
print_success "Firewall configured"

# Start Docker services
print_header "Starting Docker Services"
sg docker -c "docker-compose up -d"
print_success "All services started!"

# ==========================================
# TAILSCALE
# ==========================================
print_header "Installing Tailscale"
sudo dnf config-manager --add-repo https://pkgs.tailscale.com/stable/fedora/tailscale.repo
sudo dnf install -y tailscale
sudo systemctl enable --now tailscaled
print_success "Tailscale installed (run 'sudo tailscale up' to connect)"

# ==========================================
# HELPER SCRIPTS
# ==========================================
print_header "Creating Helper Scripts"

cat > $HOME/start-server.sh <<'EOF'
#!/bin/bash
cd ~/docker-services && docker-compose up -d
echo "Server started!"
EOF

cat > $HOME/stop-server.sh <<'EOF'
#!/bin/bash
cd ~/docker-services && docker-compose down
echo "Server stopped!"
EOF

cat > $HOME/server-status.sh <<'EOF'
#!/bin/bash
echo "=== Server Status ==="
echo "Hostname: $(hostname)"
echo "IP: $(hostname -I | awk '{print $1}')"
echo "Uptime: $(uptime -p)"
echo ""
echo "=== Docker Services ==="
cd ~/docker-services && docker-compose ps
echo ""
echo "=== Resources ==="
free -h | grep "Mem:"
df -h / | tail -1
EOF

cat > $HOME/update-server.sh <<'EOF'
#!/bin/bash
sudo dnf update -y
cd ~/docker-services && docker-compose pull && docker-compose up -d
echo "Update complete!"
EOF

cat > $HOME/backup-server.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="$HOME/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/docker-$DATE.tar.gz ~/docker-services
sudo tar -czf $BACKUP_DIR/config-$DATE.tar.gz /etc/samba/smb.conf /etc/ssh/sshd_config 2>/dev/null || true
echo "Backup complete!"
EOF

chmod +x $HOME/*.sh
print_success "Helper scripts created"

# ==========================================
# DONE
# ==========================================
print_header "Installation Complete! 🎉"

echo -e "${GREEN}Everything is installed and running!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}Main Dashboard:${NC}"
echo "  http://$HOSTNAME.local:3000"
echo "  http://$SERVER_IP:3000"
echo ""
echo -e "${BLUE}Quick Access:${NC}"
echo "  Cockpit:        https://$HOSTNAME.local:9090"
echo "  Portainer:      http://$HOSTNAME.local:9000"
echo "  Pi-hole:        http://$HOSTNAME.local:8080/admin"
echo "  Jellyfin:       http://$HOSTNAME.local:8096"
echo "  qBittorrent:    http://$HOSTNAME.local:8090"
echo "  Syncthing:      http://$HOSTNAME.local:8384"
echo "  Netdata:        http://$HOSTNAME.local:19999"
echo "  Grafana:        http://$HOSTNAME.local:3003"
echo "  Home Assistant: http://$HOSTNAME.local:8123"
echo ""
echo -e "${BLUE}File Shares:${NC}"
echo "  \\\\$HOSTNAME.local\\shared"
echo "  \\\\$HOSTNAME.local\\media"
echo "  \\\\$HOSTNAME.local\\downloads"
echo ""
echo -e "${BLUE}Helper Commands:${NC}"
echo "  ~/start-server.sh"
echo "  ~/stop-server.sh"
echo "  ~/server-status.sh"
echo "  ~/update-server.sh"
echo "  ~/backup-server.sh"
echo ""
echo -e "${YELLOW}IMPORTANT:${NC}"
echo "  1. Change Samba password: sudo smbpasswd -a $USER"
echo "  2. Change Pi-hole password: docker exec -it pihole pihole -a -p"
echo "  3. Change Grafana password (default: admin/admin)"
echo "  4. Connect Tailscale: sudo tailscale up"
echo "  5. Log out and back in for Docker permissions"
echo ""
print_success "Enjoy your ultimate home server!"
