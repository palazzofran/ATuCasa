"""Mails de pedidos: aviso al local con links para aceptar/rechazar, y respuesta al cliente.

Las funciones notificar_* se ejecutan como BackgroundTasks (después de responder al
navegador), por eso abren su propia sesión de base de datos.
"""
from datetime import datetime, timedelta
from html import escape
from urllib.parse import urlencode

from jose import JWTError, jwt

from ..core.config import settings
from ..core.database import SessionLocal
from ..core.email import enviar_correo
from ..models.pedido import Pedido

ROJO = "#a51c30"
_TIPO_TOKEN = "respuesta_pedido"


# ── Links firmados ──
def crear_token_respuesta(pedido_id: int) -> str:
    """Token firmado que permite responder un pedido sin iniciar sesión (desde el mail)."""
    exp = datetime.utcnow() + timedelta(hours=settings.RESPUESTA_PEDIDO_EXPIRE_HOURS)
    return jwt.encode({"pid": pedido_id, "tipo": _TIPO_TOKEN, "exp": exp},
                      settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def leer_token_respuesta(token: str) -> int | None:
    """Devuelve el id del pedido, o None si el token es inválido o venció."""
    try:
        datos = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
    if datos.get("tipo") != _TIPO_TOKEN or not isinstance(datos.get("pid"), int):
        return None
    return datos["pid"]


def link_respuesta(pedido_id: int, accion: str) -> str:
    token = crear_token_respuesta(pedido_id)
    return f"{settings.APP_URL.rstrip('/')}/respuesta-pedido?{urlencode({'token': token, 'accion': accion})}"


# ── Formato ──
def precio(valor: float) -> str:
    return "$" + f"{valor:,.0f}".replace(",", ".")


def detalle_html(pedido: Pedido) -> str:
    filas = "".join(
        f"""<tr>
              <td style="padding:8px 0;border-bottom:1px solid #eee">{i.cantidad}× {escape(i.producto.nombre)}</td>
              <td style="padding:8px 0;border-bottom:1px solid #eee;text-align:right">{precio(i.precio_unitario * i.cantidad)}</td>
            </tr>"""
        for i in pedido.items
    )
    return f"""
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="font-size:15px;color:#1f1a1b">
        {filas}
        <tr>
          <td style="padding:12px 0 0;font-weight:700">Total</td>
          <td style="padding:12px 0 0;font-weight:700;text-align:right;color:{ROJO}">{precio(pedido.total)}</td>
        </tr>
      </table>"""


def detalle_texto(pedido: Pedido) -> str:
    lineas = [f"  {i.cantidad}x {i.producto.nombre} — {precio(i.precio_unitario * i.cantidad)}" for i in pedido.items]
    return "\n".join(lineas) + f"\n  Total: {precio(pedido.total)}"


def plantilla(titulo: str, cuerpo: str) -> str:
    """Envoltorio común de los mails (estilos en línea para que se vean bien en Gmail)."""
    return f"""<!doctype html>
<html lang="es"><body style="margin:0;padding:24px 12px;background:#f7f4f4;font-family:Arial,Helvetica,sans-serif">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
           style="max-width:520px;background:#ffffff;border-radius:14px;border:1px solid #ece6e6">
      <tr><td style="padding:20px 28px;border-bottom:1px solid #ece6e6;font-size:20px;font-weight:700;color:#1f1a1b">
        A<span style="color:{ROJO}">Tu</span>Casa
      </td></tr>
      <tr><td style="padding:28px">
        <h1 style="margin:0 0 16px;font-size:22px;color:#1f1a1b">{titulo}</h1>
        {cuerpo}
      </td></tr>
    </table>
  </td></tr></table>
</body></html>"""


def _boton(texto: str, url: str, fondo: str, color: str = "#ffffff", borde: str | None = None) -> str:
    borde = borde or fondo
    return (f'<a href="{escape(url)}" style="display:inline-block;padding:12px 26px;margin:0 6px 8px 0;'
            f'border-radius:999px;background:{fondo};color:{color};border:2px solid {borde};'
            f'font-weight:700;font-size:15px;text-decoration:none">{texto}</a>')


# ── Mails ──
def notificar_nuevo_pedido(pedido_id: int) -> None:
    """Mail al local con el pedido y botones para aceptarlo o rechazarlo."""
    db = SessionLocal()
    try:
        pedido = db.get(Pedido, pedido_id)
        if not pedido or not pedido.local.email:
            return
        cliente = pedido.cliente
        datos_cliente = f"{escape(cliente.nombre)} · {escape(cliente.email)}"
        if cliente.telefono:
            datos_cliente += f" · {escape(cliente.telefono)}"

        cuerpo = f"""
          <p style="margin:0 0 6px;color:#5f5759;font-size:15px">
            Pedido <strong>#{pedido.id}</strong> para <strong>{escape(pedido.local.nombre)}</strong>
          </p>
          <p style="margin:0 0 4px;color:#5f5759;font-size:14px">Cliente: {datos_cliente}</p>
          <p style="margin:0 0 20px;color:#5f5759;font-size:14px">Entregar en: <strong>{escape(pedido.direccion_entrega)}</strong></p>
          {detalle_html(pedido)}
          <p style="margin:28px 0 12px;font-size:15px;color:#1f1a1b">¿Aceptás el pedido?</p>
          {_boton("Aceptar pedido", link_respuesta(pedido.id, "aceptar"), ROJO)}
          {_boton("Rechazar", link_respuesta(pedido.id, "rechazar"), "#ffffff", "#5f5759", "#dcd2d3")}
          <p style="margin:16px 0 0;font-size:12px;color:#8c8385">
            Los botones abren una página para confirmar. Vencen en {settings.RESPUESTA_PEDIDO_EXPIRE_HOURS} horas.
          </p>"""
        texto = (f"Nuevo pedido #{pedido.id} para {pedido.local.nombre}\n"
                 f"Cliente: {cliente.nombre} ({cliente.email})\n"
                 f"Entregar en: {pedido.direccion_entrega}\n\n{detalle_texto(pedido)}\n\n"
                 f"Aceptar: {link_respuesta(pedido.id, 'aceptar')}\n"
                 f"Rechazar: {link_respuesta(pedido.id, 'rechazar')}\n")
        enviar_correo(pedido.local.email, f"Nuevo pedido #{pedido.id} — {precio(pedido.total)}",
                      plantilla("¡Tenés un pedido nuevo!", cuerpo), texto)
    finally:
        db.close()


def notificar_cliente(pedido_id: int, aceptado: bool) -> None:
    """Mail al cliente: pedido en camino, o pedido no aceptado."""
    db = SessionLocal()
    try:
        pedido = db.get(Pedido, pedido_id)
        if not pedido:
            return
        local = escape(pedido.local.nombre)
        nombre = escape(pedido.cliente.nombre.split(" ")[0])
        if aceptado:
            titulo = "¡Tu pedido está en camino! 🛵"
            intro = (f"Hola {nombre}, <strong>{local}</strong> aceptó tu pedido <strong>#{pedido.id}</strong> "
                     f"y ya está en camino a <strong>{escape(pedido.direccion_entrega)}</strong>.")
            asunto = f"Tu pedido #{pedido.id} está en camino"
            texto_intro = f"{pedido.local.nombre} aceptó tu pedido #{pedido.id} y ya está en camino."
        else:
            titulo = "Tu pedido no fue aceptado"
            intro = (f"Hola {nombre}, lamentablemente <strong>{local}</strong> no pudo aceptar tu pedido "
                     f"<strong>#{pedido.id}</strong>. No se te va a cobrar nada. "
                     f"Podés intentar de nuevo más tarde o pedir en otro local.")
            asunto = f"Tu pedido #{pedido.id} no fue aceptado"
            texto_intro = f"{pedido.local.nombre} no pudo aceptar tu pedido #{pedido.id}."

        cuerpo = f"""<p style="margin:0 0 20px;font-size:15px;line-height:1.5;color:#1f1a1b">{intro}</p>
                     {detalle_html(pedido)}"""
        enviar_correo(pedido.cliente.email, asunto, plantilla(titulo, cuerpo),
                      f"{texto_intro}\n\n{detalle_texto(pedido)}\n")
    finally:
        db.close()
