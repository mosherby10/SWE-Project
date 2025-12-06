FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir flask

EXPOSE 5000

RUN python init_db.py

CMD ["python", "app.py"]
