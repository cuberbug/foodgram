#!/usr/bin/bash

# === Работа с текстом ===

# Оформление (D - декор)
BOLD_DARK_BLUE="\e[1;94m"
BOLD_ORANGE="\e[1;33m"

D_GREEN="\e[92m"
D_DARK_RED="\e[31m"
D_ORANGE="\e[33m"
D_BOLD="\e[1m"
D_CANCEL="\e[0m"

BLUE_DECOR="${BOLD_DARK_BLUE}::${D_CANCEL}"
ORANGE_DECOR="${BOLD_ORANGE}::${D_CANCEL}"

# === Функции ===

# Запрашивает подтверждение выполнения действий, обёрнутых этой функцией.
# Принимает строку, которая является запросом на подтверждение.
confirm() {
    local message=$1
    echo -en "${BLUE_DECOR} ${D_BOLD}${message}?${D_CANCEL} [Y/n]: "
    read -r response
    case "$response" in
        [Yy]* | "") return 0 ;;  # По умолчанию — "да"
        [Nn]* ) return 1 ;;      # "Нет" — не выполнять
        *) 
            echo -e "${BLUE_DECOR} ${D_ORANGE}Неверный ввод, попробуйте снова.${D_CANCEL}"
            confirm "$message"   # Рекурсия до правильного ввода
        ;;
    esac
}

# Запрашивает подтверждение на выполнение действия, как и confirm,
# но по умолчанию установлен вариант "N", то есть отказ.
refuse() {
    local message=$1
    echo -en "${ORANGE_DECOR} ${BOLD_ORANGE}${message}?${D_CANCEL} [y/N]: "
    read -r response
    case "$response" in
        [Yy]* ) return 0 ;;
        [Nn]* | "") return 1 ;;  # "Нет" — не выполнять (по умолчанию)
        *) 
            echo -e "${BLUE_DECOR} ${D_ORANGE}Неверный ввод, попробуйте снова.${D_CANCEL}"
            refuse "$message"    # Рекурсия до правильного ввода
        ;;
    esac
}
