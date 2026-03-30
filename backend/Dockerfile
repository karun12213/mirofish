FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install torch CPU first (small version)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install camel-ai 0.2.90
RUN pip install --no-cache-dir camel-ai==0.2.90

# Install sentence-transformers
RUN pip install --no-cache-dir sentence-transformers

# Install oasis with all deps from source
RUN pip install --no-cache-dir git+https://github.com/camel-ai/oasis.git

COPY . .

ENV PYTHONPATH=/app

EXPOSE 8080

CMD ["python", "run.py"]
