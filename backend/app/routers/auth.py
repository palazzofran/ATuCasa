from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import hash_password, verify_password, create_access_token
from ..models.usuario import Usuario
from ..schemas.auth import UsuarioRegistro, UsuarioLogin, TokenResponse, UsuarioResponse
from ..core.security import get_current_user


router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/registro", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def registro(data: UsuarioRegistro, db: Session = Depends(get_db)):
    existente = db.query(Usuario).filter(Usuario.email == data.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    nuevo_usuario = Usuario(
        nombre=data.nombre,
        email=data.email,
        password_hash=hash_password(data.password),
        telefono=data.telefono,
        rol=data.rol,
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    token = create_access_token({"sub": str(nuevo_usuario.id), "rol": nuevo_usuario.rol})
    return {"access_token": token, "usuario": nuevo_usuario}

@router.post("/login", response_model=TokenResponse)
def login(data: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == data.email).first()
    if not usuario or not verify_password(data.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    token = create_access_token({"sub": str(usuario.id), "rol": usuario.rol})
    return {"access_token": token, "usuario": usuario}

@router.get("/me", response_model=UsuarioResponse)
def perfil_actual(current_user: Usuario = Depends(get_current_user)):
    """Devuelve los datos del usuario autenticado."""
    return current_user
