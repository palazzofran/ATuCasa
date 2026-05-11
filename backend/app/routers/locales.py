from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..core.security import get_current_user, require_comercio
from ..models.local import Local, Producto
from ..models.usuario import Usuario
from ..schemas.local import LocalCreate, LocalUpdate, LocalResponse, LocalConProductos, ProductoCreate, ProductoUpdate, ProductoResponse

router = APIRouter(prefix="/locales", tags=["Locales"])


@router.get("/", response_model=List[LocalResponse])
def listar_locales(categoria: str = None, db: Session = Depends(get_db)):
    """Lista todos los locales activos. Se puede filtrar por categoría."""
    query = db.query(Local).filter(Local.activo == True)
    if categoria:
        query = query.filter(Local.categoria == categoria)
    return query.all()


@router.get("/{local_id}", response_model=LocalConProductos)
def obtener_local(local_id: int, db: Session = Depends(get_db)):
    """Detalle de un local con todos sus productos."""
    local = db.query(Local).filter(Local.id == local_id, Local.activo == True).first()
    if not local:
        raise HTTPException(status_code=404, detail="Local no encontrado")
    return local


@router.post("/", response_model=LocalResponse, status_code=status.HTTP_201_CREATED)
def crear_local(
    data: LocalCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_comercio),
):
    """Crea un nuevo local. Solo para usuarios con rol 'comercio'."""
    nuevo_local = Local(**data.model_dump(), propietario_id=current_user.id)
    db.add(nuevo_local)
    db.commit()
    db.refresh(nuevo_local)
    return nuevo_local


@router.put("/{local_id}", response_model=LocalResponse)
def actualizar_local(
    local_id: int,
    data: LocalUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_comercio),
):
    """Actualiza los datos de un local. Solo el propietario puede editarlo."""
    local = db.query(Local).filter(Local.id == local_id).first()
    if not local:
        raise HTTPException(status_code=404, detail="Local no encontrado")
    if local.propietario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tenés permisos para editar este local")

    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(local, campo, valor)
    db.commit()
    db.refresh(local)
    return local


# --- Productos de un local ---

@router.get("/{local_id}/productos", response_model=List[ProductoResponse])
def listar_productos(local_id: int, db: Session = Depends(get_db)):
    """Lista los productos disponibles de un local."""
    return db.query(Producto).filter(Producto.local_id == local_id, Producto.disponible == True).all()


@router.post("/{local_id}/productos", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def agregar_producto(
    local_id: int,
    data: ProductoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_comercio),
):
    """Agrega un producto a un local. Solo el propietario puede hacerlo."""
    local = db.query(Local).filter(Local.id == local_id).first()
    if not local or local.propietario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tenés permisos para agregar productos a este local")

    producto = Producto(**data.model_dump(), local_id=local_id)
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


@router.put("/productos/{producto_id}", response_model=ProductoResponse)
def actualizar_producto(
    producto_id: int,
    data: ProductoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_comercio),
):
    """Edita un producto. Solo el dueño del local puede hacerlo."""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if producto.local.propietario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tenés permisos para editar este producto")

    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(producto, campo, valor)
    db.commit()
    db.refresh(producto)
    return producto


@router.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_comercio),
):
    """Elimina un producto. Solo el dueño del local puede hacerlo."""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if producto.local.propietario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tenés permisos para eliminar este producto")

    db.delete(producto)
    db.commit()
