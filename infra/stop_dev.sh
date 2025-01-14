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

# Запрос на удаление томов
echo -e "${BLUE_DECOR} ${D_BOLD}В системе присутствуют следующие тома:${D_CANCEL}"
if ! sudo docker volume ls; then
    echo -e "${BLUE_DECOR} ${D_DARK_RED}Возникла ошибка при работе с Docker.${D_CANCEL}"
    exit 1
fi
echo -e "${BLUE_DECOR} ${D_BOLD}Проекту принадлежат следующие тома:${D_CANCEL}"
echo -e "\t${D_ORANGE}infra_backend_volume ${D_CANCEL}"
echo -e "\t${D_ORANGE}infra_front_volume ${D_CANCEL}"
echo -e "\t${D_BOLD}infra_logs ${D_CANCEL}(не предлагается к удалению)"
echo -e "\t${D_ORANGE}infra_media ${D_CANCEL}"
echo -e "\t${D_ORANGE}infra_pg_data ${D_CANCEL}"
if refuse "Удалить созданные проектом тома"; then
    echo -e "${BLUE_DECOR} Производится удаление томов..."
    if ! sudo docker volume rm infra_backend_volume infra_front_volume infra_media infra_pg_data; then
        echo -e "${BLUE_DECOR} ${D_DARK_RED}Не удалось удалить тома.${D_CANCEL}"
        exit 1
    fi
    echo -e "${BLUE_DECOR} ${D_ORANGE}Тома проекта успешно удалены.${D_CANCEL}"
else
    echo -e "${BLUE_DECOR} ${D_ORANGE}Удаление томов отменено.${D_CANCEL}"
fi
