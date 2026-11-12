// =============================================
// checkout.js — Confirmación y envío del pedido
// =============================================

document.addEventListener('DOMContentLoaded', () => {
    const resumen = document.getElementById('resumen-checkout');
    const totalEl = document.getElementById('total-checkout');
    const btnConfirmar = document.getElementById('btn-confirmar');
    const usuarioDiv = document.getElementById('usuario-logueado');
    const nombreEl = document.getElementById('nombre-usuario');

    // Resumen del carrito, editable: −/+ cambia la cantidad y el tacho saca el producto.
    // Usa el `carrito` global de carrito.js, así lo que se confirma es lo que se ve.
    const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    const plata = n => '$' + n.toLocaleString('es-AR');

    function renderResumen() {
        if (carrito.length === 0) {
            resumen.innerHTML = `<p class="text-muted mb-0">No hay productos en el carrito.
                <a href="../index.html" class="form-link">Ver locales</a></p>`;
            totalEl.innerText = '0';
            if (btnConfirmar) btnConfirmar.disabled = true;
            return;
        }
        resumen.innerHTML = carrito.map(item => `
            <div class="checkout-item" data-id="${item.id}">
                <div class="checkout-item-info">
                    <div class="checkout-item-nombre">${esc(item.nombre)}</div>
                    <div class="checkout-item-unit">${plata(item.precio)} c/u</div>
                </div>
                <div class="qty-control">
                    <button type="button" class="qty-btn" data-accion="menos" aria-label="Quitar uno">−</button>
                    <span class="qty-num">${item.cantidad}</span>
                    <button type="button" class="qty-btn" data-accion="mas" aria-label="Agregar uno">+</button>
                </div>
                <div class="checkout-item-subtotal">${plata(item.precio * item.cantidad)}</div>
                <button type="button" class="btn-quitar-item" data-accion="eliminar"
                        aria-label="Sacar ${esc(item.nombre)} del pedido" title="Sacar del pedido">
                    <i class="fa-regular fa-trash-can"></i>
                </button>
            </div>`).join('');
        totalEl.innerText = getTotalCarrito().toLocaleString('es-AR');
        if (btnConfirmar && btnConfirmar.textContent !== '¡Pedido enviado!') btnConfirmar.disabled = false;
    }

    resumen.addEventListener('click', e => {
        const btn = e.target.closest('[data-accion]');
        if (!btn) return;
        const id = Number(btn.closest('.checkout-item').dataset.id);
        const item = carrito.find(i => i.id === id);
        if (!item) return;
        if (btn.dataset.accion === 'mas') {
            item.cantidad += 1;
            _guardarCarrito();
        } else if (btn.dataset.accion === 'menos') {
            quitarDelCarrito(id);
        } else {
            eliminarDelCarrito(id);
            _mostrarToast(`${item.nombre} se sacó del pedido`);
        }
        renderResumen();
    });

    renderResumen();

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
            const localId = parseInt(localStorage.getItem('atc_local_id'));

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
