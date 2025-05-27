FROM python:3.10-slim

# Instala dependencias del sistema necesarias para tkinter y GUI
RUN apt-get update && apt-get install -y \
    python3-tk \
    tk \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . .

# Comando para ejecutar el simulador
CMD ["python3", "carro3.py"]
