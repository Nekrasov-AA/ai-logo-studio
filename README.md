# AI Logo Studio 🎨

**AI Logo Studio** — генератор фирменного стиля для малого бизнеса.
Введи название и тип бизнеса — получи 4 варианта логотипа в SVG за
несколько секунд.

## ✨ Что делает приложение

- Генерирует 4 варианта логотипа (centered, horizontal, badge)
- Подбирает иконку по типу бизнеса из библиотеки Phosphor Icons (MIT)
- Формирует цветовую палитру по правилам цветовой теории (HSL)
- Подбирает шрифтовую пару из 8 curated Google Fonts комбинаций
- Экспортирует SVG с текстом в контурах — файл работает офлайн,
  в Illustrator, Figma и любом векторном редакторе без потери шрифтов
- Детерминированная генерация: одинаковые входные данные всегда
  дают одинаковый результат

## 🏗️ Стек

### Backend
- **FastAPI** — REST API
- **PostgreSQL** — хранение jobs и вариантов логотипов
- **SQLAlchemy** — ORM с async/await
- **Alembic** — миграции БД
- **fontTools + brotli** — конвертация текста в SVG-контуры
- **Phosphor Icons** — библиотека filled SVG иконок (MIT)

### Frontend
- **Next.js 15** — React фреймворк
- **TypeScript** — типизация
- **Tailwind CSS** — стили

### DevOps
- **Docker + Docker Compose** — 3 сервиса: backend, frontend, db

## 🚀 Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Frontend     │────│   Backend API   │────│   PostgreSQL    │
│   (Next.js)     │    │   (FastAPI)     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │   logo_generator    │
                   │  (синхронный,       │
                   │   без внешних API)  │
                   └─────────────────────┘
```

Генерация происходит синхронно внутри backend — никаких очередей,
никаких внешних AI API. Время генерации < 1 секунды.

## ⚙️ Как работает генерация

```
1. POST /api/generate {business_name, business_type, style}
        ↓
2. Определение индустрии по ключевым словам
   ("coffee shop" → food, "startup" → tech, ...)
        ↓
3. Seed = MD5(business_name) → детерминированный выбор:
   - иконка из Phosphor Icons (filled, MIT)
   - шрифтовая пара из 8 curated комбинаций Google Fonts
   - цветовая палитра по HSL-алгебре
        ↓
4. Сборка SVG для 4 layout'ов (centered / horizontal / badge / centered2)
   - текст конвертируется в <path> через fontTools (без <text>, без @import)
   - иконка вставляется как filled SVG path (без stroke)
        ↓
5. Варианты сохраняются в PostgreSQL
6. GET /api/result/{job_id} возвращает 4 варианта
7. GET /api/svg/{job_id}/{index} отдаёт SVG файл
```

## 🛠️ Установка

### Требования

- Docker >= 20.0
- Docker Compose >= 2.0

### Запуск

```bash
git clone https://github.com/Nekrasov-AA/ai-logo-studio.git
cd ai-logo-studio

# Собрать и запустить (3 контейнера: backend, frontend, db)
docker-compose up --build -d

# Применить миграции БД
docker-compose exec backend alembic upgrade head
```

### Доступ

- Веб-приложение: http://localhost:3000
- API документация: http://localhost:8000/docs

## 🧪 Тестирование API

```bash
# Проверка health
curl http://localhost:8000/health

# Генерация логотипа
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "coffee shop",
    "prefs": {
      "business_name": "Brew & Co",
      "style": "modern"
    }
  }'

# Ответ:
# {"job_id": "...", "status": "processing"}

# Получить результат
curl http://localhost:8000/api/result/{job_id}

# Скачать SVG
curl http://localhost:8000/api/svg/{job_id}/0 -o logo.svg
```

## 📋 Сервисы и порты

| Сервис | Порт | Описание |
|--------|------|----------|
| Frontend | 3000 | Next.js приложение |
| Backend | 8000 | FastAPI REST API |
| PostgreSQL | 5432 | База данных |

## 🔧 Разработка

```bash
# Остановить
docker-compose down

# Пересобрать конкретный сервис
docker-compose build backend
docker-compose up backend -d

# Логи
docker-compose logs -f backend

# Создать миграцию
docker-compose exec backend alembic revision \
  --autogenerate -m "description"
docker-compose exec backend alembic upgrade head
```

## 📁 Структура проекта

```
ai-logo-studio/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI endpoints
│   │   ├── core/         # DB, настройки
│   │   ├── models/       # SQLAlchemy модели
│   │   ├── schemas/      # Pydantic схемы
│   │   ├── services/
│   │   │   └── logo_generator.py  # Движок генерации
│   │   └── assets/
│   │       ├── fonts/    # woff2 шрифты (OFL)
│   │       └── icons/    # Phosphor filled SVG (MIT)
│   ├── alembic/          # Миграции БД
│   └── tests/            # pytest тесты
├── frontend/
│   ├── src/app/          # Next.js App Router
│   └── Dockerfile
└── docker-compose.yml
```

## 🛡️ Переменные окружения

Настраиваются в `docker-compose.yml`:

- `DATABASE_URL` — подключение к PostgreSQL

## 📝 Лицензия

MIT — см. [LICENSE](LICENSE)

## 🔗 Использованные библиотеки

- [Phosphor Icons](https://phosphoricons.com/) — MIT
- [Google Fonts](https://fonts.google.com/) — OFL (Open Font License)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/docs)

---

Made with ❤️ by [Nekrasov-AA](https://github.com/Nekrasov-AA)