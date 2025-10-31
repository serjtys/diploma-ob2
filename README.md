# 🎯 ContentPlatform - Платформа платного контента

**Дипломный проект** - современная веб-платформа для монетизации контента через подписки.

## 🚀 Демо

**Живое демо:** http://84.201.167.150

**Тестовые данные для входа:**
- Логин: `+79990000000` 
- Пароль: `testpass123`
- **Тестовая карта:** `4242 4242 4242 4242`

## 📋 Функциональность

### ✅ Реализовано:
- **💰 Монетизация** - платный контент и подписки
- **🔐 Безопасность** - модерация контента, JWT аутентификация  
- **💬 Социальность** - комментарии, подписки на авторов
- **🔍 Поиск** - посты и пользователи
- **📱 API** - REST API с документацией Swagger
- **🎨 Современный UI** - glass-morphism дизайн

### 💳 Платежная система:
- Интеграция с **Stripe**
- Тестовые платежи (для демо)
- Webhook обработка
- Автоматическая активация подписки

## 🛠 Технологический стек

**Backend:**
- Django 4.2 + Django REST Framework
- PostgreSQL + Redis
- JWT аутентификация
- Stripe API

**Frontend:**
- HTML5 + CSS3 (Glass-morphism)
- JavaScript (Vanilla)
- Адаптивный дизайн

**Infrastructure:**
- Docker + Docker Compose
- Nginx + Gunicorn
- GitHub Actions CI/CD
- Yandex Cloud VM

## 🚀 Установка и запуск

### Локальная разработка:
```bash
git clone https://github.com/your-username/paid_content_platform.git
cd paid_content_platform
docker-compose up -d --build
```
## ⚙️ Настройка сервиса

### Системные требования
- **Минимальные**: 1 vCPU, 2 GB RAM, 10 GB SSD
- **Рекомендуемые**: 2 vCPU, 4 GB RAM, 20 GB SSD
- **ОС**: Ubuntu 22.04 LTS или выше

### Установка зависимостей
```bash
# Обновление пакетов
sudo apt update && sudo apt upgrade -y

# Установка Docker и Docker Compose
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker

# Дополнительные утилиты
sudo apt install -y curl wget htop net-tools
```
## ⚙️ Настройка сервиса
```bash
# Настройка фаервола
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable

# Проверка открытых портов
sudo ufw status
```
### 🐳 Конфигурация Docker
## Production Dockerfile
```bash
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN useradd -m -r appuser && chown -R appuser /app
USER appuser

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
```
## Production Dockerfile
```dockerfile
services:
  web:
    build: .
    command: >
      sh -c "python manage.py collectstatic --noinput &&
             python manage.py migrate &&
             gunicorn --bind 0.0.0.0:8000 --workers 3 config.wsgi:application"
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db:5432/diploma_db
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=0
      - REDIS_URL=redis://redis:6379/1
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_DB=diploma_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d diploma_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/app/static
      - media_volume:/app/media
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
  static_volume:
  media_volume:
```
### 🔧 Конфигурация Nginx
## nginx/nginx.conf
```bash
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /app/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```
### 🔒 Настройка безопасности
## Переменные окружения (.env)
```bash
# Django
SECRET_KEY=your-super-secure-secret-key
DEBUG=0
ALLOWED_HOSTS=your-domain.com,localhost,127.0.0.1,51.250.20.114

# Database
DATABASE_URL=postgres://postgres:postgres@db:5432/diploma_db

# Redis
REDIS_URL=redis://redis:6379/1

```
## Безопасность Django
```bash
# config/settings.py - production settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = False  # Set to True with HTTPS
SESSION_COOKIE_SECURE = False  # Set to True with HTTPS
CSRF_COOKIE_SECURE = False  # Set to True with HTTPS
```
### 📊 Мониторинг и логи
## Команды для мониторинга
```bash
# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats

# Просмотр логов
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f db

# Проверка здоровья
docker-compose exec db pg_isready -U postgres
docker-compose exec redis redis-cli ping
```
## Логи приложения
```bash
# Django логи
docker-compose exec web tail -f /app/logs/django.log

# Nginx логи
docker-compose exec nginx tail -f /var/log/nginx/access.log
docker-compose exec nginx tail -f /var/log/nginx/error.log
```

## 🧪 Тестирование

- **Покрытие тестами:** 78%
- **Автоматическая проверка** через GitHub Actions
- **Code quality:** black, isort, flake8

```bash
# Запуск тестов
python manage.py test
coverage run --source='.' manage.py test
```

### 4. **Фикс форматирования в конце**
```markdown
---
**Текущий статус сервиса**: ✅ Активен  
**Демо-доступ**: http://84.201.167.150