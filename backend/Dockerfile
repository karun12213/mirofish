FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install in stages to isolate failures
RUN pip install --no-cache-dir flask flask-cors openai pydantic python-dotenv charset-normalizer chardet PyMuPDF anthropic
RUN pip install --no-cache-dir zep-cloud==3.13.0
RUN pip install --no-cache-dir camel-ai==0.2.90
RUN pip install --no-cache-dir git+https://github.com/camel-ai/oasis.git

COPY . .

EXPOSE 8080

CMD ["python", "run.py"]
