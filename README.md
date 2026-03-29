# 🖼️ Wallpaper Daemon

Служба для автоматической смены обоев рабочего стола в зависимости от времени суток.

## 📋 Возможности

- 🌅 **Автоматическая смена обоев** — установка разных обоев для разных периодов дня
- 🎨 **Смена темы GNOME** — автоматическое переключение светлой/тёмной темы
- ⏰ **Гибкое расписание** — настройка времени смены обоев через JSON
- 🔧 **Systemd-служба** — интеграция с systemd для автоматического запуска
- 📝 **Логирование** — запись всех событий в лог

## 🚀 Требования

- Python 3.13+
- Linux с GNOME и systemd
- Установленные пакеты:

```bash
sudo apt install python3-pip python3-venv rsync
```

- Библиотеки Python (стандартные, установка не требуется):

```
subprocess, os, json, sys, signal, logging, datetime
```

## 📖 Использование

### Быстрый старт

**Однократная установка обоев:**

```bash
python wallpaper_handle.py
```

**Запуск демона (вручную):**

```bash
python wallpaper_daemon.py
```

### Управление через systemd

| Действие | Команда |
|----------|---------|
| Установка службы | `sudo ./install_service.sh` |
| Включение службы | `systemctl --user enable wallpaper-daemon.service` |
| Запуск службы | `systemctl --user start wallpaper-daemon.service` |
| Остановка службы | `systemctl --user stop wallpaper-daemon.service` |
| Проверка статуса | `systemctl --user status wallpaper-daemon.service` |
| Удаление службы | `sudo ./uninstall_service.sh` |

## ⏰ Расписание смены обоев

| Время суток | Период | Обои | Тема |
|-------------|--------|------|------|
| 🌙 Ночь | 00:00 - 07:59 | `night.jpg` | 🌑 Тёмная |
| 🌅 Утро | 08:00 - 11:59 | `morning.jpg` | ☀️ Светлая |
| ☀️ День | 12:00 - 15:59 | `day.jpg` | ☀️ Светлая |
| 🌆 Вечер | 16:00 - 19:59 | `evening.jpg` | ☀️ Светлая |
| 🌃 Перед ночью | 20:00 - 23:59 | `before_night.jpg` | 🌑 Тёмная |

## ⚙️ Настройки

Файл `settings.json` в корне проекта:

```json
{
    "night": {
        "time": ["0:0", "7:59"],
        "theme": "dark",
        "file": "night.jpg"
    },
    "morning": {
        "time": ["8:0", "11:59"],
        "theme": "light",
        "file": "morning.jpg"
    },
    "day": {
        "time": ["12:0", "15:59"],
        "theme": "light",
        "file": "day.jpg"
    },
    "evening": {
        "time": ["16:0", "19:59"],
        "theme": "light",
        "file": "evening.jpg"
    },
    "before_night": {
        "time": ["20:0", "23:59"],
        "theme": "dark",
        "file": "before_night.jpg"
    }
}
```

### Параметры

| Параметр | Описание |
|----------|----------|
| `time` | Период времени в формате `["часы:минуты", "часы:минуты"]` |
| `theme` | Тема GNOME: `light` или `dark` |
| `file` | Имя файла обоев в папке `wallpapers/` |

## 📂 Структура проекта

```
wallpaper-daemon/
├── wallpaper_daemon.py        # Основной демон (фоновый режим)
├── wallpaper_handle.py        # Однократная установка обоев
├── settings.json              # Конфигурация расписания
├── install_service.sh         # Скрипт установки systemd-службы
├── uninstall_service.sh       # Скрипт удаления systemd-службы
├── wallpaper-daemon.service   # Unit-файл systemd
├── README.md
├── LICENSE
├── .gitignore
└── wallpapers/
    ├── morning.jpg            # Утренние обои
    ├── day.jpg                # Дневные обои
    ├── evening.jpg            # Вечерние обои
    ├── before_night.jpg       # Обои перед ночью
    └── night.jpg              # Ночные обои
```

## 🔧 Установка службы

### Автоматическая установка

```bash
sudo ./install_service.sh
```

Скрипт:
1. Копирует файлы в `~/.local/share/wallpaper-daemon`
2. Устанавливает службу в `/etc/systemd/user`
3. Включает linger для пользователя

> **Примечание:** После установки службы нужно включить и запустить её от имени пользователя:
> ```bash
> systemctl --user enable wallpaper-daemon.service
> systemctl --user start wallpaper-daemon.service
> ```

### Переустановка

Если служба была установлена неправильно (например, в `/root/.local/...`):

```bash
# Удалить старую службу
sudo ./uninstall_service.sh

# Установить заново
sudo ./install_service.sh

# Включить и запустить
systemctl --user enable wallpaper-daemon.service
systemctl --user start wallpaper-daemon.service
```

### Ручная установка

```bash
# Создать директорию
mkdir -p ~/.local/share/wallpaper-daemon

# Скопировать файлы (без скриптов установки)
rsync -av --exclude='install_service.sh' --exclude='uninstall_service.sh' ./ ~/.local/share/wallpaper-daemon/

# Скопировать unit-файл
sudo cp wallpaper-daemon.service /etc/systemd/user/

# Перезагрузить демон
sudo systemctl daemon-reload

# Включить linger
loginctl enable-linger $USER

# Включить и запустить службу
systemctl --user enable wallpaper-daemon.service
systemctl --user start wallpaper-daemon.service
```

## 🛠️ Устранение неполадок

### Служба не запускается

**Проверьте статус:**

```bash
systemctl --user status wallpaper-daemon.service
```

**Посмотрите детальные логи:**

```bash
journalctl --user -u wallpaper-daemon.service -n 100 --no-pager
```

**Просмотр логов в реальном времени:**

```bash
journalctl --user -u wallpaper-daemon.service -f
```

### Обои не меняются

1. **Проверьте наличие файлов:**

```bash
ls -la ~/.local/share/wallpaper-daemon/wallpapers/
```

2. **Убедитесь, что GNOME активен:**

```bash
gsettings get org.gnome.desktop.background picture-uri
```

3. **Проверьте переменные окружения:**

```bash
echo $DISPLAY
echo $DBUS_SESSION_BUS_ADDRESS
```

### Ошибки в логах

| Ошибка | Решение |
|--------|---------|
| `Файл не найден` | Проверьте наличие обоев в папке `wallpapers/` |
| `gsettings: не удалось открыть` | Убедитесь, что GNOME запущен |
| `Permission denied` | Проверьте права доступа к файлам |

## 🎨 Добавление своих обоев

1. Поместите изображения в папку `wallpapers/`
2. Отредактируйте `settings.json`:
   - Измените `file` на имя вашего файла
   - Настройте `time` для нужного периода
   - Выберите `theme` (`light` или `dark`)
3. Перезапустите службу:

```bash
systemctl --user restart wallpaper-daemon.service
```

---

**сделано: s13bby**
