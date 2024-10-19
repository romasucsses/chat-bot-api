FROM python:3.12.3-alpine3.19

WORKDIR /bot_service

COPY ./requirements/base.txt /bot_service/requirements.txt
COPY ./app /bot_service/app
COPY alembic.ini /bot_service/alembic.ini
COPY ./alembic /bot_service/alembic

RUN apk update
RUN pip install --no-cache-dir --upgrade -r /bot_service/requirements.txt


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]