
FROM python:3.12.11-slim

WORKDIR /app

COPY requirements.txt .

# --no-cache-dir to disable keeping downloaded packages
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
