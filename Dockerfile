FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Ensure upload folder exists
RUN mkdir -p /app/static/uploads/profiles

EXPOSE 5000

CMD ["python", "app.py"]