#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="wallpaper-daemon"
SERVICE_FILE="$SCRIPT_DIR/wallpaper-daemon.service"
SYSTEM_SERVICE_DIR="/etc/systemd/user"

# Используем домашнюю директорию реального пользователя, а не root
if [ "$EUID" -eq 0 ]; then
    REAL_USER="${SUDO_USER:-$(logname)}"
    INSTALL_DIR="/home/$REAL_USER/.local/share/wallpaper-daemon"
else
    INSTALL_DIR="$HOME/.local/share/wallpaper-daemon"
fi

echo "Установка файлов в $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"

rsync -av --exclude='install_service.sh' --exclude='uninstall_service.sh' \
    "$SCRIPT_DIR/" "$INSTALL_DIR/" 2>/dev/null || cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"

if [ "$EUID" -ne 0 ]; then
  echo "Для установки сервиса требуются права root. Запустите с sudo:"
  echo "  sudo $0"
  exit 1
fi

mkdir -p "$SYSTEM_SERVICE_DIR"

cp "$SERVICE_FILE" "$SYSTEM_SERVICE_DIR/$SERVICE_NAME.service"

systemctl daemon-reload

loginctl enable-linger "$REAL_USER"

# Устанавливаем владельца файлов
chown -R "$REAL_USER:$REAL_USER" "$INSTALL_DIR"

echo "Сервис установлен в $SYSTEM_SERVICE_DIR"
echo "Файлы скопированы в $INSTALL_DIR"
echo ""
echo "Для запуска выполните:"
echo "  systemctl --user enable $SERVICE_NAME.service"
echo "  systemctl --user start $SERVICE_NAME.service"
echo ""
echo "Проверить статус:"
echo "  systemctl --user status $SERVICE_NAME.service"
echo "  journalctl --user -u $SERVICE_NAME.service -f"
