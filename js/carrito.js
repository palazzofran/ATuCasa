// =============================================
// carrito.js — Gestión del carrito de compras
// =============================================

let carrito = JSON.parse(localStorage.getItem('carrito')) || [];

function agregarAlCarrito(idProducto, nombre, precio) {
    const index = carrito.findIndex(item => item.id === idProducto);

    if (index !== -1) {
        carrito[index].cantidad += 1;
    } else {
        carrito.push({ id: idProducto, nombre, precio, cantidad: 1 });
    }

    guardarCarrito();
}

function eliminarDelCarrito(idProducto) {
    carrito = carrito.filter(item => item.id !== idProducto);
    guardarCarrito();
}

function actualizarContador() {
    const contador = document.getElementById('contador-carrito');
    if (contador) {
        const total = carrito.reduce((acc, item) => acc + item.cantidad, 0);
        contador.innerText = total;
    }
}

function guardarCarrito() {
    localStorage.setItem('carrito', JSON.stringify(carrito));
    renderizarCarrito();
    actualizarContador();
}

function renderizarCarrito() {
    const contenedor = document.getElementById('vista-carrito-offcanvas');
    const totalElemento = document.getElementById('total-carrito-offcanvas');

    if (!contenedor) return;

    contenedor.innerHTML = '';
    let total = 0;

    if (carrito.length === 0) {
        contenedor.innerHTML = '<p class="text-center text-muted mt-4">El carrito está vacío</p>';
        if (totalElemento) totalElemento.innerText = '0';
        return;
    }

    carrito.forEach(item => {
        const subtotal = item.precio * item.cantidad;
        total += subtotal;

        contenedor.innerHTML += `
            <div class="d-flex justify-content-between align-items-center mb-2 border-bottom pb-2">
                <span><strong>${item.cantidad}x</strong> ${item.nombre}</span>
                <span>$${subtotal.toLocaleString('es-AR')}</span>
                <button class="btn btn-sm btn-outline-danger" onclick="eliminarDelCarrito(${item.id})">🗑</button>
            </div>
        `;
    });

    if (totalElemento) {
        totalElemento.innerText = total.toLocaleString('es-AR');
    }
}

function limpiarCarrito() {
    carrito = [];
    localStorage.removeItem('carrito');
    localStorage.removeItem('local_id_actual');
    renderizarCarrito();
    actualizarContador();
}

document.addEventListener('DOMContentLoaded', () => {
    renderizarCarrito();
    actualizarContador();
});
