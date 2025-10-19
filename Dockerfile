FROM python:3.11-slim

WORKDIR /app

# Copiar requirements.txt primero para aprovechar la caché de Docker
COPY backend/api/requirements.txt ./

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todos los módulos necesarios
COPY backend/analyzer ./analyzer
COPY backend/utils ./utils
COPY backend/views ./views
COPY backend/api/*.py ./

# Render expone el puerto 10000 por defecto
EXPOSE 10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]