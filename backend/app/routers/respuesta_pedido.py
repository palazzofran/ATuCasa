"""Páginas que abren los botones del mail del local: confirmar y aplicar aceptar/rechazar.

GET muestra el pedido y pide confirmación (así un clic accidental o un antivirus que
abre los links del mail no responde el pedido). POST aplica la respuesta.
"""
from html import escape

from fastapi import APIRouter, BackgroundTasks, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.pedido import Pedido
from ..services.correos_pedidos import (
    ROJO, detalle_html, leer_token_respuesta, notificar_cliente, precio,
)

router = APIRouter(prefix="/respuesta-pedido", tags=["Respuesta de pedidos (mail)"])

ACCIONES = {
    "aceptar": {"estado": "enviado", "verbo": "Aceptar", "hecho": "Pedido aceptado",
                "detalle": "Le avisamos al cliente que su pedido está en camino."},
    "rechazar": {"estado": "cancelado", "verbo": "Rechazar", "hecho": "Pedido rechazado",
                 "detalle": "Le avisamos al cliente que su pedido no fue aceptado."},
}
NOMBRE_ESTADO = {"pendiente": "pendiente", "en_preparacion": "en preparación", "enviado": "en camino",
                 "entregado": "entregado", "cancelado": "cancelado"}


def _pagina(titulo: str, cuerpo: str, status: int = 200) -> HTMLResponse:
    html = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titulo)} · ATuCasa</title></head>
<body style="margin:0;padding:32px 16px;background:#f7f4f4;font-family:Arial,Helvetica,sans-serif;color:#1f1a1b">
  <div style="max-width:520px;margin:0 auto;background:#fff;border:1px solid #ece6e6;border-radius:14px">
    <div style="padding:18px 26px;border-bottom:1px solid #ece6e6;font-size:20px;font-weight:700">
      A<span style="color:{ROJO}">Tu</span>Casa</div>
    <div style="padding:26px">
      <h1 style="margin:0 0 14px;font-size:22px">{escape(titulo)}</h1>
      {cuerpo}
    </div>
  </div>
</body></html>"""
    return HTMLResponse(html, status_code=status)


def _resolver(token: str, accion: str, db: Session):
    """Devuelve (pedido, None) o (None, respuesta de error)."""
    if accion not in ACCIONES:
        return None, _pagina("Link inválido", "<p>La acción del link no es válida.</p>", 400)
    pedido_id = leer_token_respuesta(token)
    if pedido_id is None:
        return None, _pagina("Link vencido o inválido",
                             "<p>Este link ya no sirve. Gestioná el pedido desde la app.</p>", 400)
    pedido = db.get(Pedido, pedido_id)
    if not pedido:
        return None, _pagina("Pedido no encontrado", "<p>El pedido ya no existe.</p>", 404)
    if pedido.estado != "pendiente":
        estado = NOMBRE_ESTADO.get(pedido.estado, pedido.estado)
        return None, _pagina(f"El pedido #{pedido.id} ya fue respondido",
                             f"<p>Su estado actual es <strong>{estado}</strong>. No se hicieron cambios.</p>")
    return pedido, None


@router.get("", response_class=HTMLResponse)
def confirmar(token: str, accion: str, db: Session = Depends(get_db)):
    pedido, error = _resolver(token, accion, db)
    if error:
        return error
    a = ACCIONES[accion]
    color_boton = ROJO if accion == "aceptar" else "#5f5759"
    cuerpo = f"""
      <p style="margin:0 0 6px;color:#5f5759">Pedido <strong>#{pedido.id}</strong> para
        <strong>{escape(pedido.local.nombre)}</strong> · {precio(pedido.total)}</p>
      <p style="margin:0 0 18px;color:#5f5759">Entregar en: {escape(pedido.direccion_entrega)}</p>
      {detalle_html(pedido)}
      <form method="post" action="" style="margin-top:26px">
        <input type="hidden" name="token" value="{escape(token)}">
        <input type="hidden" name="accion" value="{accion}">
        <button type="submit" style="padding:12px 28px;border:0;border-radius:999px;background:{color_boton};
                color:#fff;font-weight:700;font-size:15px;cursor:pointer">{a['verbo']} pedido</button>
      </form>"""
    return _pagina(f"¿{a['verbo']} el pedido #{pedido.id}?", cuerpo)


@router.post("", response_class=HTMLResponse)
def responder(background: BackgroundTasks, token: str = Form(...), accion: str = Form(...),
              db: Session = Depends(get_db)):
    pedido, error = _resolver(token, accion, db)
    if error:
        return error
    a = ACCIONES[accion]
    pedido.estado = a["estado"]
    db.commit()
    background.add_task(notificar_cliente, pedido.id, accion == "aceptar")
    return _pagina(f"{a['hecho']} (#{pedido.id})", f"<p>{a['detalle']}</p>")
