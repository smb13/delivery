# Демо проект к курсу "Domain Driven Design и Clean Architecture на языке Python"
📚 Подробнее о курсе: [microarch.ru/courses/ddd/languages/python](https://microarch.ru/courses/ddd/languages/python?utm_source=gitlab&utm_medium=repository)

---

## Условия использования

Вы можете использовать и модифицировать данный код **в образовательных целях**, при условии сохранения ссылки на курс и оригинального источника.

---

## Требования

- Python 3.11+
- PostgreSQL
- Kafka (опционально, для интеграционных событий)

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Запуск

```bash
delivery
# или
python -m microarch.delivery.main
```

Сервис поднимается на порту `8082` (переменная окружения `HTTP_PORT`).

## Миграции БД (Alembic)

Проект использует [Alembic](https://alembic.sqlalchemy.org/) для управления миграциями PostgreSQL.
URL подключения формируется из переменных окружения: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`.

### Применить миграции

```bash
alembic upgrade head
```

### Создать новую миграцию

```bash
alembic revision --autogenerate -m "описание изменений"
```

После генерации проверьте содержимое файла в `alembic/versions/` перед применением.

### Откатить последнюю миграцию

```bash
alembic downgrade -1
```

### Текущая версия БД

```bash
alembic current
```

### Режим offline

```bash
alembic upgrade head --sql > migration.sql
```

## Запросы к БД

```sql
SELECT * FROM public.assignments;
SELECT * FROM public.couriers;
SELECT * FROM public.orders;
SELECT * FROM public.outbox;
```

## Очистка БД (все кроме справочников)

```sql
DELETE FROM public.assignments;
DELETE FROM public.couriers;
DELETE FROM public.orders;
DELETE FROM public.outbox;
```

## Генерация gRPC-клиента из Protobuf

```bash
python -m grpc_tools.protoc \
  -I src/main/proto \
  --python_out=src/generated \
  --grpc_python_out=src/generated \
  src/main/proto/geo.proto
```

## Генерация интеграционных событий Kafka из Protobuf

```bash
python -m grpc_tools.protoc \
  -I src/main/proto \
  --python_out=src/generated \
  src/main/proto/basket_events.proto \
  src/main/proto/order_events.proto
```

## Структура проекта

```
src/
  libs/ddd/          # базовые DDD-примитивы (Aggregate, ValueObject, DomainEvent)
  libs/errs/         # Result, Guard, Error
  microarch/delivery/ # точка входа FastAPI, конфигурация, publishers
src/main/proto/      # Protobuf-контракты
config/application.yml # справочник переменных окружения
```

## Лицензия

Код распространяется под лицензией [MIT](./LICENSE).  
© 2025 microarch.ru
