# Establece la imagen base (Python en este caso)
FROM python:3.12.0

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos necesarios al directorio de trabajo del contenedor
COPY BackendPython/ /app/
COPY requirements.txt /app

# Instala las dependencias especificadas en el archivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto que utilizar� el servidor FastAPI dentro del contenedor
EXPOSE 8000

# Comando para ejecutar el servidor FastAPI dentro del contenedor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
