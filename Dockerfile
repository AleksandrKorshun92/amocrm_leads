# Используйте официальный образ Python в качестве базового
FROM python:3.10-slim

# Установите рабочую директорию
WORKDIR /app

# Копируйте файл зависимостей в контейнер
COPY requirements.txt .

# Установите зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируйте весь код приложения в контейнер
COPY . .

# Копируем .env файл в контейнер
COPY .env /app/.env

# Команда для запуска вашего скрипта
CMD ["python", "amocrm.py"]  