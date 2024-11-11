FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --upgrade pip --root-user-action=ignore
RUN pip install -r requirements.txt --no-cache-dir --root-user-action=ignore

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi"]