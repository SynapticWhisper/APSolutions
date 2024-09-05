FROM python:3.10-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/src

COPY ./.env /code/.env

RUN pip install alembic

ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV DB_USER=${DB_USER}
ENV DB_PWD=${DB_PWD}
ENV DB_NAME=${DB_NAME}
ENV ES_HOST=${ES_HOST}
ENV ES_PORT=${ES_PORT}

RUN alembic upgrade head

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
