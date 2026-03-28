FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-deps git+https://github.com/camel-ai/oasis.git
RUN pip install --no-deps camel-ai==0.2.90

COPY . .

ENV PYTHONPATH=/app

EXPOSE 8080

CMD ["python", "run.py"]
