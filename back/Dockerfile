FROM python:3.14.0-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY start.sh .

CMD ["sh", "start.sh"]