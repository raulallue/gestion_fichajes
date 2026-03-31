# Imagen base de Python 3.12
FROM python:3.12-slim

# Evitar que Python genere archivos .pyc y asegurar que los logs se emitan inmediatamente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema y Node.js para las herramientas de Reflex
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los requerimientos e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Inicializar Reflex y exportar el frontend (optimización opcional para producción)
# Esto asegura que todas las dependencias de Node se instalen durante el build
RUN reflex init

# Exponer los puertos específicos (Frontend: 3004, Backend: 8004)
EXPOSE 3004
EXPOSE 8004

# Comando para arrancar la aplicación (Migrar DB y luego Correr)
CMD ["sh", "-c", "reflex db migrate && reflex run --env prod --frontend-port 3004 --backend-port 8004"]

# Añadir Healthcheck con el endpoint oficial de Reflex /ping
# Nota: Usamos 8004 porque es el puerto backend que hemos configurado para esta App
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8004/ping || exit 1
