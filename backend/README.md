# ATuCasa API 🏠

API REST construida con **FastAPI** para la app de delivery ATuCasa.

## Estructura del proyecto

```
atucasa_api/
├── app/
│   ├── core/
│   │   ├── config.py       # Variables de entorno
│   │   ├── database.py     # Conexión a la DB
│   │   └── security.py     # JWT y hashing
│   ├── models/
│   │   ├── usuario.py      # Tabla usuarios
│   │   ├── local.py        # Tablas locales y productos
│   │   └── pedido.py       # Tablas pedidos e items
│   ├── routers/
│   │   ├── auth.py         # /auth/*
│   │   ├── locales.py      # /locales/*
│   │   └── pedidos.py      # /pedidos/*
│   ├── schemas/
│   │   ├── auth.py         # Schemas de autenticación
│   │   ├── local.py        # Schemas de locales/productos
│   │   └── pedido.py       # Schemas de pedidos
│   └── main.py             # Entry point
├── requirements.txt
└── .env.example
```

## Instalación

```bash
# 1. Clonar e instalar dependencias
pip install -r requirements.txt

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus datos de DB y secret key

# 3. Correr el servidor
uvicorn app.main:app --reload
```

## Documentación interactiva

Una vez corriendo, abrí en tu browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints principales

### 🔐 Autenticación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/auth/registro` | Registrar nuevo usuario |
| POST | `/auth/login` | Login, devuelve JWT |
| GET | `/auth/me` | Perfil del usuario autenticado |

### 🏪 Locales
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/locales` | Listar todos los locales |
| GET | `/locales/{id}` | Detalle de un local + productos |
| POST | `/locales` | Crear local (rol: comercio) |
| PUT | `/locales/{id}` | Editar local |
| GET | `/locales/{id}/productos` | Productos del local |
| POST | `/locales/{id}/productos` | Agregar producto |
| PUT | `/locales/productos/{id}` | Editar producto |
| DELETE | `/locales/productos/{id}` | Eliminar producto |

### 📦 Pedidos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/pedidos` | Crear pedido desde carrito |
| GET | `/pedidos/mis-pedidos` | Historial del cliente |
| GET | `/pedidos/comercio/entrantes` | Pedidos del comercio |
| GET | `/pedidos/{id}` | Detalle de un pedido |
| PATCH | `/pedidos/{id}/estado` | Cambiar estado del pedido |

## Estados de un pedido

`pendiente` → `en_preparacion` → `enviado` → `entregado`

El cliente puede cancelar en cualquier momento con estado `cancelado`.

## Base de datos

La API usa **PostgreSQL** por defecto. Para desarrollo local podés usar SQLite
reemplazando en `.env`:
```
DATABASE_URL=sqlite:///./atucasa.db
```
