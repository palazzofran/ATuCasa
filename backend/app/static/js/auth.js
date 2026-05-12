async function login(email, password) {
    const data = await api.post('/auth/login', { email, password });
    localStorage.setItem('atc_token', data.access_token);
    localStorage.setItem('atc_usuario', JSON.stringify(data.usuario));
    return data.usuario;
}

async function registro(datos) {
    const data = await api.post('/auth/registro', datos);
    localStorage.setItem('atc_token', data.access_token);
    localStorage.setItem('atc_usuario', JSON.stringify(data.usuario));
    return data.usuario;
}

function logout() {
    localStorage.removeItem('atc_token');
    localStorage.removeItem('atc_usuario');
    localStorage.removeItem('atc_carrito');
    window.location.href = getBase() + 'index.html';
}

function getUsuarioActual() {
    const raw = localStorage.getItem('atc_usuario');
    return raw ? JSON.parse(raw) : null;
}

function estaLogueado() {
    return !!localStorage.getItem('atc_token');
}