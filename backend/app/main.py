from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.database import Base, engine, agregar_columnas_faltantes
from .routers import auth, locales, pedidos, favoritos, respuesta_pedido

# Crear todas las tablas en la base de datos (y columnas nuevas en tablas existentes)
Base.metadata.create_all(bind=engine)
agregar_columnas_faltantes()

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
app.include_router(favoritos.router)
app.include_router(respuesta_pedido.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "¡Bienvenido a ATuCasa API! 🏠", "docs": "/docs"}
