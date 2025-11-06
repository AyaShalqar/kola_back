# 1. Базовый образ
FROM python:3.11-slim

# 2. Устанавливаем зависимости
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Копируем всё приложение
COPY . .

# 4. Запуск
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
