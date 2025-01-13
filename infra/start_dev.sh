#!/usr/bin/bash

# Определяет путь до этого скрипта
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Подключает оформление и функции.
# confirm "str": Обёртка, которая запрашивает подтверждение выполняемых действий (по умолчанию "Y").
# refuse "str": Обёртка, аналогичная confirm, только со значением по умолчанию "N".
if ! source "${SCRIPT_DIR}/shell_config.sh"; then
    echo "Не удалось подключить shell_config.sh. Проверьте путь!" >&2
    exit 1
fi


# Запуск Docker
echo -e "${BLUE_DECOR} Запуск службы Docker..."
if ! sudo systemctl start docker.service; then
    echo -e "${BLUE_DECOR} ${D_DARK_RED}Не удалось запустить Docker.${D_CANCEL}"
    echo -e "${BLUE_DECOR} Возможно ${D_ORANGE}Docker${D_CANCEL} не установлен или не настроен его демон."
    exit 1
fi
echo -e "${BLUE_DECOR} ${D_GREEN}Docker успешно запущен.${D_CANCEL}"

# Проверяет, переданы ли опции: да - выводит оповещение об их использовании, нет - выводит подсказку
# --build: Заново сбилдить контейнеры из образов.
# --no-confirm: Автоматически согласиться со всеми запросами на прдтверждение.
if [[ $# -eq 0 ]]; then
    echo -e "${BLUE_DECOR} ${D_BOLD}Поддерживаются аргументы:${D_CANCEL}"
    echo -e "\t$0 [опции для ${D_ORANGE}docker-compose up -d${D_CANCEL}]"
else
    echo -e "\t${D_ORANGE}docker-compose up -d${D_CANCEL} выполнится со следующими опциями: ${D_ORANGE}$@${D_CANCEL}"
fi

# Запуск проекта
echo -e "${BLUE_DECOR} Запуск локальной сборки проекта в Docker-Compose..."
if ! sudo docker-compose -f ${SCRIPT_DIR}/docker-compose.yml up -d "$@"; then
    echo -e "${BLUE_DECOR} ${D_DARK_RED}Не удалось запустить проект.${D_CANCEL}"
    echo -e "${BLUE_DECOR} Возможно ${D_ORANGE}Docker-Compose${D_CANCEL} не установлен, проверьте его наличие в системе."
    exit 1
fi
echo -e "${BLUE_DECOR} ${D_GREEN}Проект успешно запущен.${D_CANCEL}"


# Создать миграции
if confirm "Создать миграции makemigrations"; then
    echo -e "${BLUE_DECOR} Выполнение makemigrations..."
    if ! sudo docker compose -f ${SCRIPT_DIR}/docker-compose.yml exec backend python manage.py makemigrations > /dev/null 2>&1; then
        echo -e "${BLUE_DECOR} ${D_DARK_RED}Не удалось выполнить миграции.${D_CANCEL}"
        exit 1
    fi
    echo -e "${BLUE_DECOR} ${D_GREEN}Миграции успешно созданы.${D_CANCEL}"
else
    echo -e "${BLUE_DECOR} ${D_ORANGE}Пропуск выполнения makemigrations.${D_CANCEL}"
fi


# Применить миграции
if confirm "Применить миграции"; then
    echo -e "${BLUE_DECOR} Выполнение migrate..."
    if ! sudo docker compose -f ${SCRIPT_DIR}/docker-compose.yml exec backend python manage.py migrate > /dev/null 2>&1; then
        echo -e "${BLUE_DECOR} ${D_DARK_RED}Не удалось выполнить миграции.${D_CANCEL}"
        exit 1
    fi
    echo -e "${BLUE_DECOR} ${D_GREEN}Миграции успешно выполнены.${D_CANCEL}"
else
    echo -e "${BLUE_DECOR} ${D_ORANGE}Пропуск выполнения миграций.${D_CANCEL}"
fi


# Сбор статических файлов
if confirm "Собрать статические файлы Django"; then
    echo -e "${BLUE_DECOR} Сбор статических файлов Django..."
    if ! sudo docker compose -f ${SCRIPT_DIR}/docker-compose.yml exec backend python manage.py collectstatic --no-input; then
        echo -e "${BLUE_DECOR} ${D_DARK_RED}Не удалось собрать статические файлы.${D_CANCEL}"
        exit 1
    fi
    echo -e "${BLUE_DECOR} ${D_GREEN}Статические файлы успешно собраны.${D_CANCEL}"
else
    echo -e "${BLUE_DECOR} ${D_ORANGE}Пропуск сбора статических файлов.${D_CANCEL}"
fi


# Создание стандартного суперпользователя
if refuse "Создать суперпользователя"; then
    echo -e "${BLUE_DECOR} Создание суперпользователя..."
    if ! sudo docker compose -f ${SCRIPT_DIR}/docker-compose.yml exec backend python manage.py create_superuser; then
        echo -e "${BLUE_DECOR} ${D_DARK_RED}Не удалось создать суперпользователя.${D_CANCEL}"
        exit 1
    fi
else
    echo -e "${BLUE_DECOR} ${D_ORANGE}Пропуск создания суперпользователя.${D_CANCEL}"
fi


# Загрузка ингридиентов из CSV-файла
if refuse "Загрузить ингредиенты в базу данных"; then
    echo -e "${BLUE_DECOR} Загрузка ингредиентов в базу данных..."
    if ! sudo docker compose -f ${SCRIPT_DIR}/docker-compose.yml exec backend python manage.py load_ingredients > /dev/null 2>&1; then
        echo -e "${BLUE_DECOR} ${D_DARK_RED}Не удалось загрузить ингредиенты.${D_CANCEL}"
        echo -e "${BLUE_DECOR} ${D_DARK_RED}Для получения отладочной информации запустите команду в ручном режиме:${D_CANCEL}"
        echo -e "${D_ORANGE}sudo docker compose -f ${SCRIPT_DIR}/docker-compose.yml exec backend python manage.py load_ingredients${D_CANCEL}"
        exit 1
    fi
    echo -e "${BLUE_DECOR} ${D_GREEN}Ингредиенты успешно загружены.${D_CANCEL}"
else
    echo -e "${BLUE_DECOR} ${D_ORANGE}Пропуск загрузки ингредиентов.${D_CANCEL}"
fi
