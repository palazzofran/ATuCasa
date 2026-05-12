// =============================================
// main.js — Pantalla principal: listado de locales
// =============================================

const contenedor = document.getElementById('contenedor-locales');

async function cargarLocales() {
    try {
        contenedor.innerHTML = `
            <div class="col-12 text-center py-5">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="mt-2 text-muted">Cargando locales...</p>
            </div>`;

        const locales = await api.get('/locales');

        if (locales.length === 0) {
            contenedor.innerHTML = `<p class="text-center text-muted mt-5">No hay locales disponibles.</p>`;
            return;
        }

        contenedor.innerHTML = '';
        locales.forEach(local => {
            const tarjeta = `
                <div class="col-md-4 mb-4">
                    <div class="card h-100 shadow-sm">
                        <img src="${local.imagen_url || 'https://via.placeholder.com/500x200?text=Local'}"
                             class="card-img-top" style="height: 200px; object-fit: cover;"
                             onerror="this.src='https://via.placeholder.com/500x200?text=Local'">
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title">${local.nombre}</h5>
                            <p class="text-muted small">${local.categoria || ''}</p>
                            <p class="card-text text-secondary flex-grow-1">${local.descripcion || ''}</p>
                            <button class="btn btn-primary mt-auto" onclick="verLocal(${local.id})">
                                Ver menú
                            </button>
                        </div>
                    </div>
                </div>`;
            contenedor.innerHTML += tarjeta;
        });

    } catch (error) {
        contenedor.innerHTML = `
            <div class="col-12">
                <div class="alert alert-warning text-center">
                    No se pudo conectar con el servidor. 
                    <button class="btn btn-sm btn-outline-warning ms-2" onclick="cargarLocales()">Reintentar</button>
                </div>
            </div>`;
        console.error('Error cargando locales:', error);
    }
}

function verLocal(id) {
    window.location.href = `./views/local.html?id=${id}`;
}

document.addEventListener('DOMContentLoaded', () => {
    cargarLocales();
});
