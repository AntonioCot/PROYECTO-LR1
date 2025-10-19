FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
# Render expone el puerto 10000 por defecto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
