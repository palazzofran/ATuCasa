const _base = window.location.pathname.includes('/views/') ? '../' : './';
const _usuario = (typeof getUsuarioActual === 'function') ? getUsuarioActual() : null;

const _botonesUsuario = _usuario
    ? `<span style="font-size:13px;color:var(--text-secondary)">Hola, <strong style="color:var(--text-primary)">${_usuario.nombre.split(' ')[0]}</strong></span>
       <button class="btn-ghost" onclick="logout()"><i class="fa-solid fa-right-from-bracket"></i></button>`
    : `<a href="${_base}views/login.html" class="btn-ghost">Ingresar</a>
       <a href="${_base}views/registro.html" class="btn-primary">Registrarse</a>`;

document.body.insertAdjacentHTML('afterbegin', `
<nav class="navbar">
  <div class="nav-inner">
    <a href="${_base}index.html" class="logo">
      <div class="logo-icon"><i class="fa-solid fa-house"></i></div>
      <span>A<em>Tu</em>Casa</span>
    </a>
    <div class="search-bar">
      <i class="fa-solid fa-magnifying-glass"></i>
      <input type="text" id="search-input" placeholder="Buscar locales, comidas...">
    </div>
    <div class="nav-actions">
      ${_botonesUsuario}
      <button class="btn-ghost btn-tema" id="btn-tema" type="button"><i class="fa-solid fa-moon"></i></button>
      <button class="btn-ghost" id="btn-carrito" style="position:relative;padding:7px 14px">
        <i class="fa-solid fa-bag-shopping"></i>
        <span id="contador-carrito" style="position:absolute;top:-4px;right:-4px;width:18px;height:18px;background:var(--brand);color:#fff;border-radius:50%;font-size:10px;font-weight:700;display:flex;align-items:center;justify-content:center;display:none">0</span>
      </button>
    </div>
  </div>
</nav>
`);

// ── Buscador ──
// En la portada filtra mientras escribís (index.html escucha el evento 'input').
// En las demás páginas, Enter lleva a la portada con la búsqueda (?q=...).
const _inputBusqueda = document.getElementById('search-input');
if (_inputBusqueda) {
    _inputBusqueda.value = new URLSearchParams(window.location.search).get('q') || '';
    _inputBusqueda.addEventListener('keydown', (e) => {
        if (e.key !== 'Enter' || window.ATC_BUSQUEDA_EN_PAGINA) return;
        const q = _inputBusqueda.value.trim();
        window.location.href = `${_base}index.html${q ? '?q=' + encodeURIComponent(q) : ''}`;
    });
}

document.getElementById('btn-carrito')?.addEventListener('click', () => {
    window.location.href = `${_base}views/checkout.html`;
});

// ── Tema claro/oscuro ──
// Por defecto sigue al sistema. El botón fija data-theme en <html> y lo guarda;
// si elegís lo mismo que tiene el sistema, se borra y vuelve a seguirlo.
const _mqOscuro = window.matchMedia('(prefers-color-scheme: dark)');

function _temaSistema() { return _mqOscuro.matches ? 'dark' : 'light'; }
function _temaActual() { return document.documentElement.dataset.theme || _temaSistema(); }

function _pintarBotonTema() {
    const btn = document.getElementById('btn-tema');
    if (!btn) return;
    const oscuro = _temaActual() === 'dark';
    btn.innerHTML = `<i class="fa-solid ${oscuro ? 'fa-sun' : 'fa-moon'}"></i>`;
    btn.title = oscuro ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro';
    btn.setAttribute('aria-label', btn.title);
}

document.getElementById('btn-tema')?.addEventListener('click', () => {
    const nuevo = _temaActual() === 'dark' ? 'light' : 'dark';
    try {
        if (nuevo === _temaSistema()) {
            delete document.documentElement.dataset.theme;
            localStorage.removeItem('atc_tema');
        } else {
            document.documentElement.dataset.theme = nuevo;
            localStorage.setItem('atc_tema', nuevo);
        }
    } catch (e) {
        document.documentElement.dataset.theme = nuevo;
    }
    _pintarBotonTema();
});

_mqOscuro.addEventListener('change', _pintarBotonTema);
_pintarBotonTema();