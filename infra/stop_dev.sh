#!/usr/bin/bash

# Определяет путь до этого скрипта
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Подключение оформления
source "${SCRIPT_DIR}/shell_config.sh"

# Остановка проекта
if confirm "Действительно остановить проект"; then
    echo -e "${BLUE_DECOR} Производится остановка проекта..."
    if ! sudo docker-compose -f ${SCRIPT_DIR}/docker-compose.yml down; then
        echo -e "${BLUE_DECOR} ${D_DARK_RED}Не удалось остановить проект.${D_CANCEL}"
        exit 1
    fi
    echo -e "${BLUE_DECOR} ${D_ORANGE}Проект успешно остановлен.${D_CANCEL}"
else
    echo -e "${BLUE_DECOR} ${D_ORANGE}Остановка проекта прервана.${D_CANCEL}"
fi