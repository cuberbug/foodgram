#!/usr/bin/bash

# Определяет путь до этого скрипта
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Подключение оформления
source "${SCRIPT_DIR}/shell_config.sh"


# Сборка контейнера
echo -e "${BLUE_DECOR} Запуск сборки Docker-контейнера с бэкендом..."
if ! sudo docker build -t foodgram_backend ${SCRIPT_DIR}/../backend/; then
    echo -e "${BLUE_DECOR} ${D_DARK_RED}Не удалось собрать контейнер.${D_CANCEL}"
    exit 1
fi
echo -e "${BLUE_DECOR} ${D_GREEN}Docker-контейнер успешно собран.${D_CANCEL}"