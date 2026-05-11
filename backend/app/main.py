from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.database import Base, engine
from .routers import auth, locales, pedidos

# Crear todas las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ATuCasa API",
    description="API para la app de delivery ATuCasa — similar a PedidosYa",
    version="1.0.0",
)

# Configuración CORS (permite que el frontend se conecte)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, reemplazar con el dominio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(auth.router)
app.include_router(locales.router)
app.include_router(pedidos.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "¡Bienvenido a ATuCasa API! 🏠", "docs": "/docs"}
