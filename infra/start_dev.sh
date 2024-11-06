#!/usr/bin/bash

# Определяет путь до этого скрипта
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Подключение оформления
source "${SCRIPT_DIR}/shell_config.sh"


# Запуск Docker
echo -e "${BLUE_DECOR} Запуск службы Docker..."
if ! sudo systemctl start docker.service; then
    echo -e "${BLUE_DECOR} ${D_DARK_RED}Не удалось запустить Docker.${D_CANCEL}"
    exit 1
fi
echo -e "${BLUE_DECOR} ${D_GREEN}Docker успешно запущен.${D_CANCEL}"

# Запуск проекта
echo -e "${BLUE_DECOR} Запуск локальной сборки проекта в Docker-Compose..."
if ! sudo docker-compose -f ${SCRIPT_DIR}/docker-compose.yml up -d; then
    echo -e "${BLUE_DECOR} ${D_DARK_RED}Не удалось запустить проект.${D_CANCEL}"
    exit 1
fi
echo -e "${BLUE_DECOR} ${D_GREEN}Проект успешно запущен.${D_CANCEL}"