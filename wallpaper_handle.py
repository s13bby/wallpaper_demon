from datetime import datetime
import subprocess
import os
import json
import sys

def get_settings():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "settings.json")
    try:
        with open(path, "r", encoding="utf-8") as data:
            return json.load(data)
    except Exception:
        print(f"Ошибка: Не удалось прочитать {path}")
        sys.exit()

def get_current_time():
    return [datetime.now().hour, datetime.now().minute]

def switch_theme(theme):
    scheme = "prefer-dark" if theme == "dark" else "prefer-light"
    cmd = ["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", scheme]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при смене темы: {e}")

def choose_wallpaper(current_time, settings):
    current_hours, current_minutes = current_time
    for phase_name, data in settings.items():
        start_hours, start_minutes = map(int, data["time"][0].split(':'))
        end_hours, end_minutes = map(int, data["time"][1].split(':'))
        if (start_hours, start_minutes) <= (current_hours, current_minutes) \
            <= (end_hours, end_minutes):
            return data["file"], data["theme"]
    return "night.jpg", "dark"

def main():
    settings = get_settings()
    current_time = get_current_time()
    image, theme = choose_wallpaper(current_time, settings)
    switch_theme(theme)
    set_wallpaper(image)      


def set_wallpaper(image):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    wallpaper_path = os.path.join(base_dir, "wallpapers", image)

    if not os.path.exists(wallpaper_path):
        print(f"ОШИБКА: Файл не найден: {wallpaper_path}")
        return
    uri = f"file://{wallpaper_path}"
    try:
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.background", "picture-options", "zoom"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при установке picture-options: {e}")

    keys = [
        ("org.gnome.desktop.background", "picture-uri"),
        ("org.gnome.desktop.background", "picture-uri-dark"),
        ("org.gnome.desktop.screensaver", "picture-uri")
    ]

    for schema, setting in keys:
        command = ["gsettings", "set", schema, setting, f"'{uri}'"]
        try:
            subprocess.run(command, check=True)
            print(f"Успешно: {setting} -> {image}")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка: {e}")
    try:
        subprocess.run([
            "gdbus", "call", "--session",
            "--dest", "org.gnome.Shell",
            "--object-path", "/org/gnome/Shell",
            "--method", "org.gnome.Shell.Eval",
            "imports.gi.Meta.BackgroundActor.get_for_screen(global.display.get_screen()).force_redraw()"
        ], check=False, capture_output=True)
    except Exception:
        pass



if __name__ == "__main__":
    main()