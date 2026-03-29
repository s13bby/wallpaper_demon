#!/bin/bash

set -e

SERVICE_NAME="wallpaper-daemon"
SYSTEM_SERVICE_DIR="/etc/systemd/user"

# Используем домашнюю директорию реального пользователя, а не root
if [ "$EUID" -eq 0 ]; then
    REAL_USER="${SUDO_USER:-$(logname)}"
    INSTALL_DIR="/home/$REAL_USER/.local/share/wallpaper-daemon"
else
    INSTALL_DIR="$HOME/.local/share/wallpaper-daemon"
fi

if [ "$EUID" -ne 0 ]; then
  echo "Для удаления сервиса требуются права root. Запустите с sudo:"
  echo "  sudo $0"
  exit 1
fi

echo "Остановка сервисов у активных пользователей..."
for uid in $(loginctl list-users --no-legend | awk '{print $1}'); do
    user=$(id -un "$uid" 2>/dev/null)
    if [ -n "$user" ]; then
        echo "  - $user"
        runuser -u "$user" -- systemctl --user stop "$SERVICE_NAME.service" 2>/dev/null || true
        runuser -u "$user" -- systemctl --user disable "$SERVICE_NAME.service" 2>/dev/null || true
    fi
done

for uid in $(loginctl list-users --no-legend | awk '{print $1}'); do
    user=$(id -un "$uid" 2>/dev/null)
    if [ -n "$user" ]; then
        loginctl disable-linger "$user" 2>/dev/null || true
    fi
done

rm -f "$SYSTEM_SERVICE_DIR/$SERVICE_NAME.service"

systemctl daemon-reload

echo "Удаление файлов из $INSTALL_DIR..."
rm -rf "$INSTALL_DIR"

echo "Сервис удален"
