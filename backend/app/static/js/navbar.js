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
      A<em>Tu</em>Casa
    </a>
    <div class="search-bar">
      <i class="fa-solid fa-magnifying-glass"></i>
      <input type="text" id="search-input" placeholder="Buscar locales, comidas...">
    </div>
    <div class="nav-actions">
      ${_botonesUsuario}
      <button class="btn-ghost" id="btn-carrito" style="position:relative;padding:7px 14px">
        <i class="fa-solid fa-bag-shopping"></i>
        <span id="contador-carrito" style="position:absolute;top:-4px;right:-4px;width:18px;height:18px;background:var(--emerald);color:#0a0f0d;border-radius:50%;font-size:10px;font-weight:700;display:flex;align-items:center;justify-content:center;display:none">0</span>
      </button>
    </div>
  </div>
</nav>
`);

document.getElementById('btn-carrito')?.addEventListener('click', () => {
    window.location.href = `${_base}views/checkout.html`;
});