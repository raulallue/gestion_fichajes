# Gestión de Fichajes ATR - Sistema de Presencia Inteligente

Este proyecto es una aplicación web moderna construida con **Reflex** (Python) para la gestión automatizada y manual de fichajes en el sistema ATR. Está diseñada para ofrecer una experiencia de usuario fluida, proactiva y realista.

## 🚀 Características Principales

### 1. Panel de Control (Dashboard) Real-Time
- **Estadísticas Globales:** Visualización inmediata de usuarios trabajando, en vacaciones o inactivos.
- **Últimos Fichajes:** Registro en vivo de las acciones realizadas por todos los empleados.
- **Próximos Turnos Proactivos:** Sección dinámica que muestra los siguientes fichajes programados en un rango de 1h, 3h o 5h.
- **Auto-Actualización:** El dashboard se refresca automáticamente cada 5 minutos.

### 2. Motor de Fichajes Inteligente (Automation Engine)
- **Humanización/Realismo:** El sistema no ficha a la hora exacta para evitar patrones artificiales. Utiliza un **margen de aleatoriedad configurable** (ej. 0-10 min) que genera un desvío único cada día por usuario y por turno.
- **Precisión de Segundos:** Todos los fichajes automáticos se registran con **00 segundos** para una apariencia profesional y limpia en ATR.
- **Jornada Partida y Completa:** Soporta hasta 2 turnos diarios (4 acciones) por usuario.
- **Prevención de Bucles:** Sistema robusto basado en base de datos que garantiza que cada entrada/salida solo se procese una vez al día.

### 3. Gestión de Usuarios y Roles
- **Control de Acceso (RBAC):** Diferenciación entre administradores (acceso total) y usuarios (gestión de perfil propio).
- **Extracción Automática de Person ID:** Al añadir un usuario, el sistema se conecta a ATR para recuperar automáticamente su ID único.
- **Calendario de Vacaciones:** Gestión granular de días libres y respeto a los **Festivos Nacionales** configurados.

### 4. Configuración Global
- **Márgenes de Jitter:** Ajuste dinámico del tiempo de aleatoriedad desde la interfaz.
- **Modo Intensivo:** Opción para activar rápidamente la jornada intensiva por usuario.

---

## 🛠️ Funcionamiento Técnico

### El Motor (Engine)
El motor de fichajes (`engine.py`) corre como un daemon en segundo plano:
1. Cada minuto, evalúa quién debe fichar.
2. Calcula la `Hora Programada + Offset Aleatorio`.
3. Si la hora actual coincide con la hora objetivo y no se ha fichado hoy, ejecuta la acción en ATR.
4. Las entradas se realizan mediante `POST` y las salidas mediante `PUT`, manteniendo la sesión de ATR abierta correctamente.

### Integración con ATR
La comunicación se realiza a través de `ATRService`, que gestiona:
- Autenticación segura.
- Obtención del historial de fichajes.
- Creación y actualización de registros (fichajes parciales y completos).

---

## 📦 Instalación y Despliegue

### Requisitos
- Python 3.12+
- Reflex (`pip install reflex`)

### Ejecución
```bash
# Inicializar la base de datos (si es necesario)
reflex db migrate

# Ejecutar en modo desarrollo
reflex run
```

---

## 🛡️ Seguridad
- Las credenciales se almacenan localmente en la base de datos SQLModel.
- Las validaciones de horario impiden errores humanos (ej: horas de salida anteriores a las de entrada).
- El sistema utiliza la zona horaria `Europe/Madrid`.

---
*Desarrollado con ❤️ para optimizar la gestión de presencia de forma inteligente.*
