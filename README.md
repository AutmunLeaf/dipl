# Mostootryad Diploma Project

## Запуск в Docker Compose (локально)

1. Скопируйте файл окружения:
   ```bash
   cp .env.example .env
   ```

2. Запустите контейнеры:
   ```bash
   docker-compose up --build
   ```

3. Приложение доступно по адресу: http://localhost:8000
4. Документация API: http://localhost:8000/docs

## Запуск в GitHub Codespaces

1. Откройте репозиторий в GitHub.
2. Нажмите кнопку **Code** -> **Codespaces** -> **Create codespace on main**.
3. Дождитесь создания среды. Контейнеры поднимутся автоматически согласно `.devcontainer/devcontainer.json`.
4. После завершения настройки (`postCreateCommand`) приложение будет доступно:
   - Нажмите на уведомление о проброшенном порте 8000 или перейдите во вкладку "Ports".
   - URL будет вида: `https://<random-name>-8000.app.github.dev`
5. База данных PostgreSQL доступна внутри сети контейнеров по хосту `db` (порт 5432).

## Структура проекта

- `app/` - основной код приложения
- `frontend/` - шаблоны и статика
- `migrations/` - миграции Alembic
- `docker-compose.yml` - конфигурация Docker
- `.devcontainer/` - настройка для Codespaces
