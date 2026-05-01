FROM python:3.12-slim
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . .
RUN pip install -e .
RUN playwright install chromium --with-deps
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
