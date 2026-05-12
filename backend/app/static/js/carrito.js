let carrito = JSON.parse(localStorage.getItem('atc_carrito')) || [];

function agregarAlCarrito(idProducto, nombre, precio) {
    const idx = carrito.findIndex(i => i.id === idProducto);
    if (idx !== -1) {
        carrito[idx].cantidad += 1;
    } else {
        carrito.push({ id: idProducto, nombre, precio, cantidad: 1 });
    }
    _guardarCarrito();
    _mostrarToast(`${nombre} agregado al pedido`);
}

function quitarDelCarrito(idProducto) {
    const idx = carrito.findIndex(i => i.id === idProducto);
    if (idx !== -1) {
        if (carrito[idx].cantidad > 1) {
            carrito[idx].cantidad -= 1;
        } else {
            carrito.splice(idx, 1);
        }
        _guardarCarrito();
    }
}

function eliminarDelCarrito(idProducto) {
    carrito = carrito.filter(i => i.id !== idProducto);
    _guardarCarrito();
}

function limpiarCarrito() {
    carrito = [];
    localStorage.removeItem('atc_carrito');
    localStorage.removeItem('atc_local_id');
    _actualizarContador();
}

function getTotalCarrito() {
    return carrito.reduce((acc, i) => acc + i.precio * i.cantidad, 0);
}

function getCantidadProducto(idProducto) {
    const item = carrito.find(i => i.id === idProducto);
    return item ? item.cantidad : 0;
}

function _guardarCarrito() {
    localStorage.setItem('atc_carrito', JSON.stringify(carrito));
    _actualizarContador();
}

function _actualizarContador() {
    const total = carrito.reduce((acc, i) => acc + i.cantidad, 0);
    const el = document.getElementById('contador-carrito');
    if (el) {
        el.textContent = total;
        el.style.display = total > 0 ? 'flex' : 'none';
    }

    // Cart pill en la página principal
    const pill = document.getElementById('cart-pill');
    if (pill) {
        const countEl = pill.querySelector('.cart-count');
        const priceEl = pill.querySelector('.cart-price');
        if (countEl) countEl.textContent = total;
        if (priceEl) priceEl.textContent = '$' + getTotalCarrito().toLocaleString('es-AR');
        pill.classList.toggle('hidden', total === 0);
    }
}

function _mostrarToast(msg) {
    const t = document.createElement('div');
    t.textContent = msg;
    Object.assign(t.style, {
        position:'fixed', bottom:'80px', left:'50%', transform:'translateX(-50%)',
        background:'var(--bg-card)', border:'1px solid var(--emerald-border)',
        color:'var(--emerald)', padding:'10px 20px', borderRadius:'var(--radius-pill)',
        fontSize:'13px', fontWeight:'500', zIndex:'300', whiteSpace:'nowrap',
        animation:'fadeUp .25s ease', boxShadow:'0 4px 20px rgba(0,0,0,.3)'
    });
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 2000);
}

document.addEventListener('DOMContentLoaded', _actualizarContador);