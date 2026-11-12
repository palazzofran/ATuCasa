from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def agregar_columnas_faltantes():
    """create_all() crea tablas nuevas pero no agrega columnas a tablas que ya existen.
    Esto agrega las columnas nuevas (siempre opcionales) a una base existente.
    Es un parche hasta que el proyecto use migraciones de Alembic."""
    inspector = inspect(engine)
    tablas = set(inspector.get_table_names())
    with engine.begin() as conn:
        for tabla in Base.metadata.sorted_tables:
            if tabla.name not in tablas:
                continue
            existentes = {c["name"] for c in inspector.get_columns(tabla.name)}
            for col in tabla.columns:
                if col.name not in existentes and col.nullable:
                    tipo = col.type.compile(dialect=engine.dialect)
                    conn.execute(text(f'ALTER TABLE "{tabla.name}" ADD COLUMN "{col.name}" {tipo}'))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
