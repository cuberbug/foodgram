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

# Проверяет, переданы ли опции: да - выводит оповещение об их использовании, нет - выводит подсказку
if [[ $# -eq 0 ]]; then
    echo -e "${BLUE_DECOR} ${D_BOLD}Поддерживаются аргументы:${D_CANCEL}"
    echo -e "\t$0 [опции для ${D_ORANGE}docker-compose up -d${D_CANCEL}]"
else
    echo -e "${BLUE_DECOR} ${D_ORANGE}docker-compose up -d${D_CANCEL} выполнится со следующими опциями: ${D_ORANGE}$@${D_CANCEL}"
fi

# Запуск проекта
echo -e "${BLUE_DECOR} Запуск локальной сборки проекта в Docker-Compose..."
if ! sudo docker-compose -f ${SCRIPT_DIR}/docker-compose.yml up -d "$@"; then
    echo -e "${BLUE_DECOR} ${D_DARK_RED}Не удалось запустить проект.${D_CANCEL}"
    exit 1
fi
echo -e "${BLUE_DECOR} ${D_GREEN}Проект успешно запущен.${D_CANCEL}"


# Выполнение makemigrations
echo -e "${BLUE_DECOR} Выполнение makemigrations..."
if ! sudo docker compose -f ${SCRIPT_DIR}/docker-compose.yml exec backend python manage.py makemigrations; then
    echo -e "${BLUE_DECOR} ${D_DARK_RED}Не удалось выполнить миграции.${D_CANCEL}"
    exit 1
fi
echo -e "${BLUE_DECOR} ${D_GREEN}Миграции успешно созданы.${D_CANCEL}"

# Выполнение миграций
echo -e "${BLUE_DECOR} Выполнение миграций Django..."
if ! sudo docker compose -f ${SCRIPT_DIR}/docker-compose.yml exec backend python manage.py migrate; then
    echo -e "${BLUE_DECOR} ${D_DARK_RED}Не удалось выполнить миграции.${D_CANCEL}"
    exit 1
fi
echo -e "${BLUE_DECOR} ${D_GREEN}Миграции успешно выполнены.${D_CANCEL}"


# Сбор статических файлов
echo -e "${BLUE_DECOR} Сбор статических файлов Django..."
if ! sudo docker compose -f ${SCRIPT_DIR}/docker-compose.yml exec backend python manage.py collectstatic --no-input; then
    echo -e "${BLUE_DECOR} ${D_DARK_RED}Не удалось собрать статические файлы.${D_CANCEL}"
    exit 1
fi
echo -e "${BLUE_DECOR} ${D_GREEN}Статические файлы успешно собраны.${D_CANCEL}"

# Создание стандартного суперпользователя
echo -e "${BLUE_DECOR} Создание суперпользователя..."
if ! sudo docker compose -f ${SCRIPT_DIR}/docker-compose.yml exec backend python manage.py create_superuser; then
    echo -e "${BLUE_DECOR} ${D_DARK_RED}Не удалось выполнить миграции.${D_CANCEL}"
    exit 1
fi
echo -e "${BLUE_DECOR} ${D_GREEN}Суперпользователь успешно создан.${D_CANCEL}"
