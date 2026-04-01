# Guía de Despliegue con Docker y Portainer

Sigue estos pasos para publicar tu aplicación y desplegarla en tu servidor.

## 1. Preparación local (Build y Push)

Desde tu terminal en la carpeta del proyecto:

1. **Construir la imagen (para Intel/AMD/AMD64)**:
   Si estás en un Mac moderno (M1/M2/M3), necesitas forzar la plataforma del servidor (Intel/AMD):
   ```bash
   docker build --platform linux/amd64 -t rallue/gestion_fichajes:latest .
   ```

2. **Login en Docker Hub**:
   ```bash
   docker login
   ```

3. **Subir la imagen**:
   ```bash
   docker push rallue/gestion_fichajes:latest
   ```

## 2. Despliegue en el Servidor (Portainer)

1. **Preparar el entorno**:
   En tu servidor (VPS/NAS), crea una carpeta para la aplicación (ej: `/opt/gestion_fichajes`).
   
2. **Copiar base de datos**:
   Sube tu archivo `reflex.db` actual a esa carpeta en el servidor. Esto mantendrá todos tus usuarios y fichajes.

3. **Configurar Stacks**:
   - Ve a **Portainer** -> **Stacks** -> **Add Stack**.
   - Ponle un nombre (ej: `gestion-fichajes`).
   - Copia el contenido de `docker-compose.yml` en el editor web.
   - **IMPORTANTE**: Asegúrate de que la ruta del volumen sea la correcta (si has puesto el archivo en `/opt/gestion_fichajes`, cambia el volumen a `/opt/gestion_fichajes/reflex.db:/app/reflex.db`).

4. **Desplegar**:
   Pulsa en **Deploy the stack**.

## 3. Acceso

La aplicación estará disponible en:
- **Frontend**: `http://tu-vps-ip:3004`
- **Backend (API)**: `http://tu-vps-ip:8004`

> [!TIP]
> Si vas a usar un dominio (ej: `fichajes.tudominio.com`), lo ideal es usar un **Reverse Proxy** (como Nginx Proxy Manager o Traefik) apuntando al puerto `3000` (interno) o `3004` (externo).
