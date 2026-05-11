// =============================================
// api.js — Cliente HTTP centralizado para la API
// =============================================

const API_BASE = 'http://localhost:8000'; // Cambiar en producción

async function apiFetch(endpoint, options = {}) {
    const token = localStorage.getItem('token');

    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...(options.headers || {}),
    };

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
    });

    if (response.status === 401) {
        // Token expirado o inválido — limpiar sesión
        localStorage.removeItem('token');
        localStorage.removeItem('usuario');
        window.location.href = '/views/login.html';
        return;
    }

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || 'Error en la solicitud');
    }

    return data;
}

// Métodos de conveniencia
const api = {
    get:    (endpoint)       => apiFetch(endpoint, { method: 'GET' }),
    post:   (endpoint, body) => apiFetch(endpoint, { method: 'POST',   body: JSON.stringify(body) }),
    put:    (endpoint, body) => apiFetch(endpoint, { method: 'PUT',    body: JSON.stringify(body) }),
    patch:  (endpoint, body) => apiFetch(endpoint, { method: 'PATCH',  body: JSON.stringify(body) }),
    delete: (endpoint)       => apiFetch(endpoint, { method: 'DELETE' }),
};
