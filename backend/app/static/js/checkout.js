// =============================================
// checkout.js — Confirmación y envío del pedido
// =============================================

document.addEventListener('DOMContentLoaded', () => {
    const resumen = document.getElementById('resumen-checkout');
    const totalEl = document.getElementById('total-checkout');
    const btnConfirmar = document.getElementById('btn-confirmar');
    const usuarioDiv = document.getElementById('usuario-logueado');
    const nombreEl = document.getElementById('nombre-usuario');

    // Mostrar resumen del carrito
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];

    if (carrito.length === 0) {
        resumen.innerHTML = '<p class="text-muted">No hay productos en el carrito.</p>';
        if (btnConfirmar) btnConfirmar.disabled = true;
    } else {
        let total = 0;
        carrito.forEach(item => {
            const subtotal = item.precio * item.cantidad;
            total += subtotal;
            resumen.innerHTML += `
                <div class="d-flex justify-content-between mb-1">
                    <span>${item.cantidad}x ${item.nombre}</span>
                    <span>$${subtotal.toLocaleString('es-AR')}</span>
                </div>`;
        });
        totalEl.innerText = total.toLocaleString('es-AR');
    }

    // Mostrar estado de sesión
    const usuario = getUsuarioActual();
    if (usuario) {
        usuarioDiv.classList.remove('d-none');
        nombreEl.textContent = usuario.nombre;
    }

    // Confirmar pedido
    if (btnConfirmar) {
        btnConfirmar.addEventListener('click', async () => {
            const direccion = document.getElementById('input-direccion').value.trim();
            const mensajeDiv = document.getElementById('mensaje-pedido');
            const localId = parseInt(localStorage.getItem('local_id_actual'));

            if (!direccion) {
                mensajeDiv.innerHTML = '<div class="alert alert-warning">Por favor ingresá una dirección de entrega.</div>';
                return;
            }
            if (!localId) {
                mensajeDiv.innerHTML = '<div class="alert alert-danger">No se encontró el local. Volvé al menú.</div>';
                return;
            }

            const items = carrito.map(item => ({
                producto_id: item.id,
                cantidad: item.cantidad,
            }));

            btnConfirmar.disabled = true;
            btnConfirmar.textContent = 'Enviando pedido...';

            try {
                const pedido = await api.post('/pedidos', {
                    local_id: localId,
                    direccion_entrega: direccion,
                    items,
                });

                limpiarCarrito();
                mensajeDiv.innerHTML = `
                    <div class="alert alert-success">
                        ✅ <strong>¡Pedido confirmado!</strong> Número #${pedido.id}<br>
                        Estado: <span class="badge bg-warning text-dark">${pedido.estado}</span>
                    </div>`;
                btnConfirmar.textContent = '¡Pedido enviado!';

            } catch (error) {
                mensajeDiv.innerHTML = `<div class="alert alert-danger">${error.message || 'Error al confirmar el pedido.'}</div>`;
                btnConfirmar.disabled = false;
                btnConfirmar.textContent = 'Confirmar Pedido';
            }
        });
    }
});
