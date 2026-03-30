const parametrosURL = new URLSearchParams(window.location.search);
const idLocal = parseInt(parametrosURL.get('id'));

const localActual = comercios.find(local => local.id === idLocal);

if (localActual) {
    document.getElementById('info-local').innerHTML = `
        <div class="card shadow-sm">
            <img src="${localActual.imagen}" style="height: 300px; object-fit: cover;">
            <div class="card-body">
                <h1 class="display-5">${localActual.nombre}</h1>
                <span class="badge bg-secondary">${localActual.categoria}</span>
            </div>
        </div>
        <h3 class="mt-4 mb-3">Menú</h3>
    `;
    
    if (localActual.productos) {
        localActual.productos.forEach(prod => {
            document.getElementById('menu-productos').innerHTML += `
                <div class="card mb-2 shadow-sm">
                    <div class="card-body d-flex justify-content-between align-items-center">
                        <div>
                            <h5 class="m-0">${prod.nombre}</h5>
                            <strong class="text-success">${prod.precio} $</strong>
                        </div>
                        <button class="btn btn-outline-primary" onclick="agregarAlCarrito(${prod.id}, '${prod.nombre}', ${prod.precio})">Agregar</button>
                    </div>
                </div>
            `;
        });
    }
} else {
    document.getElementById('info-local').innerHTML = `<h1 class="text-center mt-5">Local no encontrado</h1>`;
}