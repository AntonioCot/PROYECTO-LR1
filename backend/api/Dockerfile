FROM python:3.11-slim

WORKDIR /app

# Copiar requirements.txt primero para aprovechar la caché de Docker
COPY requirements.txt /app/

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la API
COPY . /app/

# Agregar el directorio padre al PYTHONPATH
ENV PYTHONPATH=/app/..

# Render expone el puerto 10000 por defecto
EXPOSE 10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
