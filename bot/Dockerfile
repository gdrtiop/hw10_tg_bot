FROM python:3.12-slim

WORKDIR /bot
COPY . /bot/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "-m", "app.bot"]