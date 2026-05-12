// =============================================
// local.js — Vista de un local y su menú
// =============================================

const parametrosURL = new URLSearchParams(window.location.search);
const idLocal = parseInt(parametrosURL.get('id'));

async function cargarLocal() {
    if (!idLocal) {
        document.getElementById('info-local').innerHTML = `<h1 class="text-center mt-5">Local no encontrado</h1>`;
        return;
    }

    try {
        // Traer el local con sus productos en un solo request
        const local = await api.get(`/locales/${idLocal}`);

        document.getElementById('info-local').innerHTML = `
            <div class="card shadow-sm">
                <img src="${local.imagen_url || 'https://via.placeholder.com/1200x300?text=Local'}"
                     style="height: 300px; object-fit: cover; border-radius: 0.375rem 0.375rem 0 0;"
                     onerror="this.src='https://via.placeholder.com/1200x300?text=Local'">
                <div class="card-body">
                    <h1 class="display-5">${local.nombre}</h1>
                    <span class="badge bg-secondary">${local.categoria || 'General'}</span>
                    <p class="mt-2 text-muted">${local.descripcion || ''}</p>
                </div>
            </div>
            <h3 class="mt-4 mb-3">Menú</h3>
        `;

        const contenedorProductos = document.getElementById('menu-productos');

        if (!local.productos || local.productos.length === 0) {
            contenedorProductos.innerHTML = `<p class="text-muted">Este local no tiene productos disponibles.</p>`;
            return;
        }

        local.productos.forEach(prod => {
            if (!prod.disponible) return;
            contenedorProductos.innerHTML += `
                <div class="card mb-2 shadow-sm">
                    <div class="card-body d-flex justify-content-between align-items-center">
                        <div>
                            <h5 class="m-0">${prod.nombre}</h5>
                            <small class="text-muted">${prod.descripcion || ''}</small>
                            <div><strong class="text-success">$${prod.precio.toLocaleString('es-AR')}</strong></div>
                        </div>
                        <button class="btn btn-outline-primary"
                            onclick="agregarAlCarrito(${prod.id}, '${prod.nombre.replace(/'/g, "\\'")}', ${prod.precio})">
                            Agregar
                        </button>
                    </div>
                </div>
            `;
        });

        // Guardar el local_id para usarlo al crear el pedido
        localStorage.setItem('local_id_actual', idLocal);

    } catch (error) {
        document.getElementById('info-local').innerHTML = `
            <div class="alert alert-danger">No se pudo cargar el local. <a href="../index.html">Volver al inicio</a></div>`;
        console.error('Error cargando local:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    cargarLocal();
});
