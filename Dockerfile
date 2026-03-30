FROM python:3.11-slim
WORKDIR /app

# Встановлюємо системні залежності
RUN apt-get update && apt-get install -y gcc python3-dev libpq-dev && rm -rf /var/lib/apt/lists/*

# Копіюємо requirements з кореня
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо ВСЕ (і .env, і папку backend_sp, і папку бота)
COPY . .

CMD ["sh", "-c", "python backend_sp/manage.py migrate && python backend_sp/manage.py runserver 0.0.0.0:8000"]
