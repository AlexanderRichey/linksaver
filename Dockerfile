FROM python:3.8-slim

WORKDIR /var/www

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD uvicorn sailbot:app --host 0.0.0.0 --port 8000
