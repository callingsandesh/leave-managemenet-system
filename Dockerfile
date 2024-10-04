# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN apt-get update && \
    apt-get install -y cron && \
    apt-get install -y gcc python3-dev build-essential libpq-dev && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get remove -y gcc python3-dev build-essential && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code
COPY . /app/

# Set the default command to run both cron and the Django server
CMD ["sh", "-c", "python manage.py migrate && python manage.py crontab add && cron && python manage.py runserver 0.0.0.0:8000"]
