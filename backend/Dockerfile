FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --upgrade pip --root-user-action=ignore
RUN pip install -r requirements.txt --no-cache-dir --root-user-action=ignore

# Копирует скрипт wait-for-it
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh

# Запуск сервера gunicorn только после того, как будет получен ответ от db PostgreSQL
CMD ["./wait-for-it.sh", "db:5432", "--", "gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi"]