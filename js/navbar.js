const rutaBase = window.location.pathname.includes('/views/') ? '../' : './';

document.body.insertAdjacentHTML('afterbegin', `
<nav class="navbar navbar-expand-lg bg-body-tertiary shadow-sm mb-4">
    <div class="container-fluid">
        <a class="navbar-brand" href="${rutaBase}index.html">ATuCasa</a>
        
        <div class="d-flex ms-auto align-items-center">
            <form class="d-flex me-3" role="search">
                <input class="form-control me-2" type="search" placeholder="Search" aria-label="Search"/>
                <button class="btn btn-outline-success" type="submit">Buscar</button>
            </form>
            
            <button class="btn btn-light position-relative" id="btn-abrir-carrito">
                <i class="fa-solid fa-cart-shopping">🛒</i>
                <span id="contador-carrito" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">0</span>
            </button>
        </div>
    </div>
</nav>
`);

document.body.insertAdjacentHTML('beforeend', `
<div class="offcanvas offcanvas-end" tabindex="-1" id="offcanvasCarrito" aria-labelledby="offcanvasCarritoLabel">
    <div class="offcanvas-header border-bottom">
        <h5 class="offcanvas-title" id="offcanvasCarritoLabel">Tu Pedido</h5>
        <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
    </div>
    <div class="offcanvas-body d-flex flex-column">
        <div id="vista-carrito-offcanvas" class="flex-grow-1 overflow-auto"></div>
        <div class="border-top pt-3 mt-3">
            <h5 class="text-end mb-3">Total: $<span id="total-carrito-offcanvas">0</span></h5>
            <button class="btn btn-success w-100">Confirmar Pedido</button>
        </div>
    </div>
</div>
`);

const btnCarrito = document.getElementById('btn-abrir-carrito');
const menuCarrito = document.getElementById('offcanvasCarrito');
const offcanvasInstance = new bootstrap.Offcanvas(menuCarrito);

btnCarrito.addEventListener('click', (e) => {
    e.preventDefault();
    offcanvasInstance.toggle();
});