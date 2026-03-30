#!/usr/bin/env python3

from datetime import datetime, timedelta
import subprocess
import os
import json
import sys
import signal
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

RUNNING = True

def signal_handler(signum, frame):
    global RUNNING
    RUNNING = False
    logger.info("Получен сигнал остановки, завершаю работу...")

def get_base_dir():
    return os.path.dirname(os.path.abspath(__file__))

def get_settings():
    path = os.path.join(get_base_dir(), "settings.json")
    try:
        with open(path, "r", encoding="utf-8") as data:
            return json.load(data)
    except Exception as e:
        logger.error(f"Ошибка чтения {path}: {e}")
        sys.exit(1)

def get_current_time():
    now = datetime.now()
    return now.hour, now.minute, now.second

def parse_time(time_str):
    h, m = map(int, time_str.split(':'))
    return h * 60 + m

def choose_wallpaper(current_time, settings):
    current_hours, current_minutes, _ = current_time
    current_minutes_total = current_hours * 60 + current_minutes
    
    for phase_name, data in settings.items():
        start = parse_time(data["time"][0])
        end = parse_time(data["time"][1])
        
        if start <= end:
            if start <= current_minutes_total <= end:
                return data["file"], data["theme"], phase_name
        else:
            if current_minutes_total >= start or current_minutes_total <= end:
                return data["file"], data["theme"], phase_name
    
    return "night.jpg", "dark", "night"

def check_system_active():
    """Проверяет, активна ли система (не в процессе suspend/resume)"""
    try:
        result = subprocess.run(
            ["systemctl", "status", "sleep.target", "suspend.target", 
             "hibernate.target", "hybrid-sleep.target"],
            capture_output=True, text=True, timeout=2
        )
        # Если есть активные таргеты сна - ждём
        if result.returncode == 0:
            return False
    except Exception:
        pass
    return True

def set_wallpaper(image):
    wallpaper_path = os.path.join(get_base_dir(), "wallpapers", image)
    
    if not os.path.exists(wallpaper_path):
        logger.error(f"Файл не найден: {wallpaper_path}")
        return False
    
    uri = f"file://{wallpaper_path}"
    
    try:
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.background", "picture-options", "zoom"],
            check=True, capture_output=True
        )
    except subprocess.CalledProcessError as e:
        logger.warning(f"Ошибка picture-options: {e}")
    
    keys = [
        ("org.gnome.desktop.background", "picture-uri"),
        ("org.gnome.desktop.background", "picture-uri-dark"),
    ]
    
    success = True
    for schema, setting in keys:
        try:
            subprocess.run(
                ["gsettings", "set", schema, setting, f"'{uri}'"],
                check=True, capture_output=True
            )
        except subprocess.CalledProcessError as e:
            logger.warning(f"Ошибка {setting}: {e}")
            success = False
    
    return success

def switch_theme(theme):
    scheme = "prefer-dark" if theme == "dark" else "prefer-light"
    try:
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", scheme],
            check=True, capture_output=True
        )
    except subprocess.CalledProcessError as e:
        logger.warning(f"Ошибка смены темы: {e}")

def main():
    global RUNNING

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    settings = get_settings()
    last_applied = None
    was_inactive = False

    logger.info("Демон обоев запущен. Ожидание переключений...")

    while RUNNING:
        current_time = get_current_time()
        image, theme, phase = choose_wallpaper(current_time, settings)
        current_key = f"{image}_{theme}"

        # Проверяем активность системы
        system_active = check_system_active()
        
        # Если система только что вернулась из сна - применяем обои принудительно
        if was_inactive and system_active:
            logger.info("Система вернулась из сна, применяю обои...")
            switch_theme(theme)
            if set_wallpaper(image):
                last_applied = current_key
            was_inactive = False
        elif current_key != last_applied:
            logger.info(f"Переключение: {phase} -> {image} (тема: {theme})")
            switch_theme(theme)
            if set_wallpaper(image):
                last_applied = current_key
        else:
            logger.debug(f"Без изменений: {phase} -> {image}")

        if not system_active:
            was_inactive = True
            logger.debug("Система неактивна (сон/приостановка)")

        # Короткий интервал опроса для быстрой реакции после сна
        # Используем interruptible sleep для корректной обработки сигналов
        sleep_seconds = 30
        
        logger.debug(f"Сон на {sleep_seconds} сек")

        # Прерываемый сон - проверяем RUNNING каждые 0.5 сек
        import time
        for _ in range(sleep_seconds * 2):
            if not RUNNING:
                break
            time.sleep(0.5)

    logger.info("Демон остановлен")

if __name__ == "__main__":
    main()
