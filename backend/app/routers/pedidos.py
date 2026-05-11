from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..core.security import get_current_user, require_comercio
from ..models.pedido import Pedido, ItemPedido
from ..models.local import Producto, Local
from ..models.usuario import Usuario
from ..schemas.pedido import PedidoCreate, PedidoResponse, PedidoEstadoUpdate

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

ESTADOS_VALIDOS = ["pendiente", "en_preparacion", "enviado", "entregado", "cancelado"]


@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def crear_pedido(
    data: PedidoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea un pedido a partir del carrito del cliente."""
    # Validar que el local existe
    local = db.query(Local).filter(Local.id == data.local_id, Local.activo == True).first()
    if not local:
        raise HTTPException(status_code=404, detail="Local no encontrado")

    # Construir los items y calcular el total
    total = 0.0
    items_db = []
    for item in data.items:
        producto = db.query(Producto).filter(
            Producto.id == item.producto_id,
            Producto.local_id == data.local_id,
            Producto.disponible == True,
        ).first()
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {item.producto_id} no disponible")

        subtotal = producto.precio * item.cantidad
        total += subtotal
        items_db.append(ItemPedido(
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            precio_unitario=producto.precio,
        ))

    # Crear el pedido
    pedido = Pedido(
        cliente_id=current_user.id,
        local_id=data.local_id,
        direccion_entrega=data.direccion_entrega,
        total=total,
        estado="pendiente",
    )
    db.add(pedido)
    db.flush()  # para obtener el id del pedido

    for item in items_db:
        item.pedido_id = pedido.id
        db.add(item)

    db.commit()
    db.refresh(pedido)
    return pedido


@router.get("/mis-pedidos", response_model=List[PedidoResponse])
def mis_pedidos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Historial de pedidos del cliente autenticado."""
    return db.query(Pedido).filter(Pedido.cliente_id == current_user.id).order_by(Pedido.created_at.desc()).all()


@router.get("/comercio/entrantes", response_model=List[PedidoResponse])
def pedidos_entrantes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_comercio),
):
    """Pedidos recibidos en los locales del comercio autenticado."""
    locales_ids = [local.id for local in current_user.locales]
    return (
        db.query(Pedido)
        .filter(Pedido.local_id.in_(locales_ids))
        .order_by(Pedido.created_at.desc())
        .all()
    )


@router.get("/{pedido_id}", response_model=PedidoResponse)
def obtener_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Detalle de un pedido. Solo el cliente o el comercio involucrado pueden verlo."""
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    es_cliente = pedido.cliente_id == current_user.id
    es_comercio = current_user.rol == "comercio" and pedido.local.propietario_id == current_user.id
    if not es_cliente and not es_comercio:
        raise HTTPException(status_code=403, detail="No tenés acceso a este pedido")

    return pedido


@router.patch("/{pedido_id}/estado", response_model=PedidoResponse)
def cambiar_estado(
    pedido_id: int,
    data: PedidoEstadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza el estado de un pedido. El comercio avanza el estado; el cliente puede cancelar."""
    if data.estado not in ESTADOS_VALIDOS:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Opciones: {ESTADOS_VALIDOS}")

    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    es_comercio = current_user.rol == "comercio" and pedido.local.propietario_id == current_user.id
    es_cliente = pedido.cliente_id == current_user.id

    if not es_comercio and not es_cliente:
        raise HTTPException(status_code=403, detail="No tenés permisos para modificar este pedido")

    # El cliente solo puede cancelar
    if es_cliente and not es_comercio and data.estado != "cancelado":
        raise HTTPException(status_code=403, detail="Como cliente solo podés cancelar el pedido")

    pedido.estado = data.estado
    db.commit()
    db.refresh(pedido)
    return pedido
