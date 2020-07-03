FROM python:latest

WORKDIR /var/www

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
