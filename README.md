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

0. **Скопируйте репозиторий**

```bash
git clone https://github.com/SynapticWhisper/apsolutions_testTask.git
```

1. **Измените директорию на проектную**

```bash
cd apsolutions_testTask
```

2. **Создайте файл .env**

```bash
nano .env
```

Пример содержимого .env файла:

```makefile
DB_HOST=postgres  # Используется имя сервися из docker-compose.yaml
DB_PORT=5432
DB_USER=admin
DB_PWD=12345
DB_NAME=TestTaskDB
ES_HOST=elasticsearch  # Используется имя сервися из docker-compose.yaml
ES_PORT=9200
```

3. **Постройте Docker-образ для проекта**

```bash
docker build -t apsolutions_task ./
```

4. **Добавление необходимых прав доступа**

```bash
mkdir ./esdata && sudo chown -R 1000:1000 ./esdata
```

8. **Запустите контейнер приложения**

```bash
docker-compose up
```