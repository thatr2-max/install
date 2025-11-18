#!/bin/bash
# scaffold-kde-install.sh
# Run as root after minimal AlmaLinux 9 install
# Installs KDE Plasma with SDDM + business applications

set -euo pipefail

echo "[1/6] Enabling required repositories..."
dnf install -y dnf-plugins-core
dnf config-manager --set-enabled crb
dnf install -y epel-release
dnf update -y

echo "[2/6] Installing KDE Plasma and SDDM..."
dnf groupinstall -y "KDE Plasma Workspaces"
dnf install -y sddm

echo "[3/6] Installing business applications..."
dnf install -y \
  libreoffice-writer libreoffice-calc libreoffice-impress \
  vlc \
  firefox \
  thunderbird \
  konsole \
  okular \
  plasma-nm \
  plasma-pa

echo "[4/6] Configuring firewall with essential rules..."
dnf install -y firewalld
systemctl enable --now firewalld
firewall-cmd --permanent --add-service=ssh
firewall-cmd --reload

echo "[5/6] Setting default boot target to GUI..."
systemctl set-default graphical.target
systemctl enable sddm

echo "[6/6] Cleaning package cache and rebooting..."
dnf clean all
journalctl --vacuum-time=1d
echo "Rebooting in 5 seconds... (Ctrl+C to cancel)"
sleep 5
reboot now
