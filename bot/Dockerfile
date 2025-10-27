FROM python:3.12-slim

WORKDIR /bot
COPY . /bot/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["bash", "-c", "\
    alembic revision --autogenerate -m 'init tables' && \
    alembic upgrade head && \
    python -m app.bot \
"]