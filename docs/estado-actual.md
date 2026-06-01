# Módulo 7.0 — Estado actual y frontera del módulo

## 0. Tipo de trabajo

**Área:** Docs / Arquitectura / Producto / Seguridad  
**Repositorio:** `psicomichi-docs`  
**Prioridad:** Alta  
**Estado:** En proceso  

---

## 1. Objetivo

Documentar el estado actual del proyecto Psicomichi antes de comenzar a definir dominio, roles, permisos, módulos de negocio y mapa funcional.

Este submódulo sirve como punto de partida para evitar reescribir lo ya construido y para continuar el desarrollo de forma modular, ordenada y segura.

---

## 2. Alcance

### Incluye

- Estado actual del backend.
- Estado actual del frontend.
- Decisiones técnicas ya tomadas.
- Frontera de lo que este módulo va a definir.
- Criterios para no romper lo existente.

### No incluye todavía

- Nuevos modelos de base de datos.
- Nuevos endpoints.
- Nuevas pantallas.
- Integración con pagos.
- Bot de pre-contención.
- Expediente clínico completo.

---

## 3. Estado actual del backend

**Repositorio:** `psicomichi-api`

El backend ya cuenta con una base funcional y robusta construida con FastAPI.

Actualmente incluye:

- FastAPI configurado.
- PostgreSQL local.
- SQLAlchemy.
- Alembic.
- Configuración mediante variables de entorno.
- Healthcheck.
- Manejo estándar de errores.
- Modelo base de usuarios.
- Administración de usuarios.
- Autenticación robusta.
- JWT access tokens.
- Refresh tokens persistidos.
- Refresh tokens almacenados como hash.
- Cookies HttpOnly para refresh token.
- Logout y logout all.
- Cambio de contraseña.
- Política robusta de contraseñas.
- Validaciones defensivas.
- Rate limit básico en memoria.
- CORS con credentials.
- Seeders de usuarios iniciales.

---

## 4. Estado actual del frontend

**Repositorio:** `psicomichi-web`

El frontend ya cuenta con una base funcional construida con React, TypeScript y Vite.

Actualmente incluye:

- React + TypeScript.
- Vite.
- TailwindCSS.
- React Router.
- Axios.
- Zustand.
- React Hook Form.
- Zod.
- React Hot Toast.
- Login visual.
- Login conectado al backend.
- Refresh automático.
- Access token en memoria.
- Refresh token en cookie HttpOnly.
- Layout privado.
- Dashboard inicial.
- Sidebar privado.
- Header móvil.
- Componentes UI base.
- Ruta `/users`.
- Service de usuarios.
- Types de usuarios.
- Pantalla inicial del módulo de usuarios.

---

## 5. Decisiones técnicas ya tomadas

### Seguridad de sesión

- El refresh token no se guarda en localStorage.
- El refresh token vive en cookie HttpOnly.
- El access token vive en memoria del frontend.
- El backend es responsable de revocar sesiones.
- El frontend solo conserva sesión activa mientras pueda refrescarla contra backend.

### Arquitectura backend

- Endpoints delgados.
- Services para lógica de negocio.
- Repositories para acceso a datos.
- Schemas para validación.
- Models para base de datos.
- Core para seguridad, configuración, errores y utilidades.
- Migraciones con Alembic.
- No crear tablas manualmente.

### Arquitectura frontend

- No meter lógica pesada en componentes.
- Centralizar llamadas HTTP en services.
- Centralizar rutas API en `endpoints.ts`.
- Centralizar variables de entorno en `env.ts`.
- Usar stores para estado global.
- Usar componentes UI reutilizables.

---

## 6. Frontera del Módulo 7

El Módulo 7 **no busca programar funcionalidad nueva todavía**.

Busca definir:

- Módulos funcionales reales.
- Roles del sistema.
- Matriz de permisos.
- Datos sensibles.
- Entidades principales.
- Pantallas futuras.
- Endpoints futuros.
- Reglas de seguridad.
- Roadmap técnico priorizado.

---

## 7. Módulos de negocio que se evaluarán

Los módulos candidatos son:

- Administración.
- Usuarios.
- Pacientes.
- Agenda.
- Citas.
- Notas terapéuticas.
- Servicios.
- Tienda.
- Productos.
- Cursos.
- Talleres.
- Retiros.
- Órdenes.
- Pagos.
- Bot de pre-contención.
- Conversaciones del bot.
- Reportes.
- Configuración.

---

## 8. Reglas para continuar sin romper lo existente

- No reescribir autenticación.
- No cambiar el flujo de tokens salvo que sea una mejora puntual.
- No mezclar pacientes con clientes comerciales sin definirlo.
- No crear expediente clínico completo sin matriz de permisos.
- No integrar Stripe sin órdenes internas.
- No confiar en datos enviados desde frontend para pagos.
- No guardar información clínica sensible sin permisos claros.
- No construir pantallas sin endpoint o contrato definido.
- No crear endpoints sin definir quién puede usarlos.

---

## 9. Resultado esperado de este submódulo

Al cerrar este submódulo debe quedar claro:

- Qué existe actualmente.
- Qué se conserva.
- Qué no se va a tocar por ahora.
- Qué se definirá en los siguientes submódulos del Módulo 7.