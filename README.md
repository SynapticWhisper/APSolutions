# Тестовое задание Python

**Структура БД:**

- `id` - уникальный для каждого документа;
- `rubrics` - массив рубрик;
- `text` - текст документа;
- `created_date` - дата создания документа.

**Структура Индекса:**

- `id` - id из базы;
- `text` - текст из структуры БД.

## Инструкция по запуску

1. **Измените директорию на проектную**

```bash
cd apsolutions_testTask
```

2. **Создайте Docker-сеть**

```bash
docker network create mynetwork
```

3. **Получите `Gateway` сети**

```bash
docker network inspect mynetwork
```
Найдите и сохраните `Gateway` сети, например:
```json
"Gateway": "172.29.0.1"
```

4. **Создайте файл .env**

```bash
nano .env
```

Пример содержимого .env файла:

```makefile
DB_HOST=<network geteway>
DB_PORT=5432
DB_USER=admin
DB_PWD=12345
DB_NAME=TestTaskDB
ES_HOST=<network geteway>
ES_PORT=9200
```

5. **Запустите контейнер PostgreSQL**
*Используйте данные указанные в .env файле*
```bash
docker run --name TestTaskDB -p 5432:5432 -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=12345 -e POSTGRES_DB=TestTaskDB -d postgres:16.4
```


6. **Запустите контейнер Elasticsearch**

```bash
docker run -d --name TestTaskES --net mynetwork -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -e "xpack.security.enabled=false" elasticsearch:8.15.0
```


7. **Постройте Docker-образ для проекта**

```bash
docker build -t apsolutions_task ./
```

8. **Запустите контейнер приложения**

```bash
docker run -d --name TestTaskFA -p 8000:8000 apsolutions_task
```