FROM python:3.10-slim

WORKDIR /app

# Əlavə paketlər (ssl və s. üçün)
RUN apt-get update && apt-get install -y gcc libffi-dev libssl-dev

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]

