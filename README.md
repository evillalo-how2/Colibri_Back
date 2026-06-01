
# Psicomichi API

Backend base para el proyecto Psicomichi.
## Stack inicial

- FastAPI
- PostgreSQL (local)
- SQLAlchemy
- Alembic
- Pydantic Settings

## Requisitos previos

- Python 3.9+
- PostgreSQL instalado y corriendo localmente
- pip o poetry

## Configuración del entorno

### 1. Crear base de datos PostgreSQL

Accede a PostgreSQL y crea la base de datos:

```bash
sudo -u postgres psql
CREATE DATABASE psicomichi_db;
```
O desde la línea de comandos:

```bash
createdb -U postgres psicomichi_db
```

### 2. Configurar variables de entorno
Copiar el archivo de ejemplo:

```bash
cp .env.example .env
```
Editar el archivo .env con tu configuración local de PostgreSQL:

```bash
APP_NAME=Psicomichi API
APP_ENV=development
DEBUG=true

API_V1_PREFIX=/api/v1

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=psicomichi_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_contraseña_aqui

DATABASE_URL=postgresql+psycopg://postgres:tu_contraseña_aqui@localhost:5432/psicomichi_db
```
Importante: Reemplaza tu_contraseña_aqui con la contraseña real de tu usuario PostgreSQL.

### 3. Crear y activar entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```
O si usas Poetry:

```bash
poetry install
```

### Levantar el proyecto 
```bash
uvicorn app.main:app --reload --port 8000
```
La API estará disponible en:

```bash
http://localhost:8000
```
Swagger (Documentacion interactiva)

```bash
http://localhost:8000/docs
```
Healthcheck

```bash
http://localhost:8000/api/v1/health
```
## Migraciónes con Alembic
Inicializar Alembic (Solo la primera vez):
```bash
alembic init migrations
```
Crear una nueva migración: 
```bash
alembic revision --autogenerate -m "initial migration"
```
Ejecutar migraciones:
```bash
alembic upgrade head
```
Ver estado de las migraciones:
```bash
alembic current
```
Rollback a migración anterior:
```bash
alembic downgrade -1
```
## Pruebas manuales
### 1. Verificar que PostgreSQL esté corriendo
```bash
python -c "from app.db.session import engine; print('Conexión exitosa')"
```
Resultado esperado: Debe imprimir "Conexión exitosa" sin errores.

### 2. Probar endpoint raíz
```bash
curl http://localhost:8000/
```
Resultado esperado:

```bash
{
  "message": "Psicomichi API is running",
  "environment": "development",
  "docs_url": "/docs"
}
```

### 3. Probar healthcheck
```bash
curl http://localhost:8000/api/v1/health
```
Resultado esperado:

```bash
{
  "status": "ok",
  "app_name": "Psicomichi API",
  "environment": "development",
  "database": "ok"
}
```

### 4. Probar Swagger
```bash
http://localhost:8000/docs
```
Resultado esperado: Debe mostrarse Swagger con los endpoints:
* GET/
* GET /api/v1/health

### 5. Probar que las migraciones funcionan
```bash
alembic history
alembic current
```
Resultado esperado: Debe mostrar el historial y la versión actual de la migración.

## Estructura esperada del proyecto
```bash
psicomichi-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── deps.py
│   │       └── endpoints/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   ├── handlers.py
│   │   ├── password_policy.py
│   │   ├── rate_limit.py
│   │   ├── security.py
│   │   └── validators.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── base_class.py
│   │   └── session.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── refresh_token.py
│   │   └── user.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── refresh_token_repository.py
│   │   └── user_repository.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── common.py
│   │   ├── health.py
│   │   └── user.py
│   └── services/
│       └── __init__.py
├── migrations/
├── scripts/
├── venv/
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```