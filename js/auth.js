// =============================================
// auth.js — Autenticación y manejo de sesión
// =============================================

async function login(email, password) {
    const data = await api.post('/auth/login', { email, password });
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('usuario', JSON.stringify(data.usuario));
    return data.usuario;
}

async function registro(datos) {
    const data = await api.post('/auth/registro', datos);
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('usuario', JSON.stringify(data.usuario));
    return data.usuario;
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('usuario');
    window.location.href = '/index.html';
}

function getUsuarioActual() {
    const raw = localStorage.getItem('usuario');
    return raw ? JSON.parse(raw) : null;
}

function estaLogueado() {
    return !!localStorage.getItem('token');
}
