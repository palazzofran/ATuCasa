from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # URL pública del backend: se usa para armar los links de los mails
    APP_URL: str = "http://localhost:8000"

    # Envío de mails (SMTP). Si SMTP_HOST está vacío, los mails no se envían:
    # se guardan como archivos .html en la carpeta CORREOS_DIR para poder revisarlos.
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""          # por defecto, SMTP_USER
    CORREOS_DIR: str = "correos_salientes"

    # Validez de los links de aceptar/rechazar pedidos
    RESPUESTA_PEDIDO_EXPIRE_HOURS: int = 48

    class Config:
        env_file = ".env"

settings = Settings()
