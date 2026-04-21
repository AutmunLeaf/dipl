# Mostootryad Diploma - Система управления строительными актами

## Быстрый старт в GitHub Codespaces

### Инструкция для чайников (полная)

1. **Загрузи код на GitHub** (если еще не загружен):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/ТВОЙ_НИК/mostootryad-diploma.git
   git push -u origin main
   ```

2. **Создай Codespace**:
   - Зайди в свой репозиторий на GitHub
   - Нажми зеленую кнопку **<> Code**
   - Перейди на вкладку **Codespaces**
   - Нажми **Create codespace on main**

3. **Жди автоматической настройки** (1-3 минуты):
   - Codespace сам скачает Docker образы
   - Поднимет PostgreSQL
   - Установит все зависимости
   - Применит миграции базы данных
   
4. **Запусти приложение** (если не запустилось само):
   ```bash
   docker-compose up
   ```
   
5. **Открой приложение**:
   - Когда увидишь `INFO: Uvicorn running on http://0.0.0.0:8000`
   - Нажми всплывающую кнопку **Open in Browser**
   - Или добавь `/docs` к адресу для API документации

## Локальный запуск через Docker

```bash
# Копирование переменных окружения
cp .env.example .env

# Запуск всех сервисов
docker-compose up --build

# Остановка
docker-compose down
```

## Структура проекта

```
mostootryad-diploma/
├── app/                      # Основное приложение
│   ├── models/              # SQLAlchemy модели
│   ├── schemas/             # Pydantic схемы
│   ├── routers/             # API эндпоинты
│   ├── services/            # Бизнес-логика
│   ├── utils/               # Утилиты
│   └── tests/               # Тесты
├── frontend/                # HTML шаблоны
├── migrations/              # Alembic миграции
├── uploads/                 # Загруженные файлы
├── docker-compose.yml       # Docker конфигурация
├── Dockerfile              # Образ приложения
└── .devcontainer/          # Codespaces конфигурация
```

## Технологии

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: PostgreSQL 15
- **Auth**: JWT, passlib (bcrypt)
- **Documents**: docxtpl (КС-2, КС-3, АОСР)
- **Tests**: pytest

## API Документация

После запуска доступна по адресу: `http://localhost:8000/docs`

## Тесты

```bash
pytest app/tests -v
```