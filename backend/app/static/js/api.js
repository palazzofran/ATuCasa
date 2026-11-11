const API_BASE = 'http://localhost:8000';

async function apiFetch(endpoint, options = {}) {
    const token = localStorage.getItem('atc_token');
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...(options.headers || {}),
    };
    const response = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });

    if (response.status === 401) {
        localStorage.removeItem('atc_token');
        localStorage.removeItem('atc_usuario');
        window.location.href = getBase() + 'views/login.html';
        return;
    }

    // 204 No Content (por ejemplo, al marcar un favorito) no trae cuerpo
    const texto = await response.text();
    const data = texto ? JSON.parse(texto) : null;
    if (!response.ok) {
        const detalle = data && data.detail;
        throw new Error(typeof detalle === 'string' ? detalle : 'Error en la solicitud');
    }
    return data;
}

function getBase() {
    return window.location.pathname.includes('/views/') ? '../' : './';
}

const api = {
    get:    (ep)       => apiFetch(ep, { method: 'GET' }),
    post:   (ep, body) => apiFetch(ep, { method: 'POST',   body: JSON.stringify(body) }),
    put:    (ep, body) => apiFetch(ep, { method: 'PUT',    body: JSON.stringify(body) }),
    patch:  (ep, body) => apiFetch(ep, { method: 'PATCH',  body: JSON.stringify(body) }),
    delete: (ep)       => apiFetch(ep, { method: 'DELETE' }),
};