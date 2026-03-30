const contenedor = document.getElementById('contenedor-locales');

function cargarLocales() {
    comercios.forEach(local => {
        const tarjeta = `
            <div class="col-md-4 mb-4">
                <div class="card h-100 shadow-sm">
                    <img src="${local.imagen}" class="card-img-top" style="height: 200px; object-fit: cover;">
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title">${local.nombre}</h5>
                        <p class="text-muted">${local.categoria}</p>
                        <button class="btn btn-primary mt-auto" onclick="verLocal(${local.id})">Hacer pedido</button>
                    </div>
                </div>
            </div>
        `;
        contenedor.innerHTML += tarjeta;
    });
}

function verLocal(id) {
    window.location.href = `../views/local.html?id=${id}`;
}

document.addEventListener('DOMContentLoaded', () => {
    cargarLocales();
});