FROM python:3.10-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/src
COPY ./migrations /code/migrations
COPY ./alembic.ini /code/alembic.ini
COPY ./.env /code/.env

RUN pip install alembic

RUN alembic upgrade head

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
