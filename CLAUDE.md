# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

ATuCasa is a food/delivery app (in the style of PedidosYa). Everything lives under `backend/`: a FastAPI REST API plus a static HTML/JS frontend kept in `backend/app/`. The code, comments, API messages and identifiers are all in Spanish (`local` = store, `pedido` = order, `comercio` = merchant role, `carrito` = cart). Keep new code in Spanish to match.

## Commands

Run everything from `backend/`. `app/core/config.py` loads `.env` relative to the working directory, so starting from anywhere else fails because `DATABASE_URL` and `SECRET_KEY` are missing.

```bash
cd backend
.venv/Scripts/activate              # Windows venv (Python 3.12); on PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload       # http://localhost:8000, Swagger at /docs
```

Required `.env` keys: `DATABASE_URL`, `SECRET_KEY` (plus optional `ALGORITHM` and `ACCESS_TOKEN_EXPIRE_MINUTES`). See `backend/.env.example`. For local development use `DATABASE_URL=sqlite:///./atucasa.db`. PostgreSQL is the intended production database.

The project has no tests, linter or formatter configured. Alembic is in `requirements.txt` but isn't set up: there's no `alembic.ini` and no migrations.

## Architecture

**Backend (`backend/app/`)** is organized in layers: `models/` (SQLAlchemy ORM), `schemas/` (Pydantic v2 request/response models with `from_attributes`), `routers/` (one per resource: `auth`, `locales`, `pedidos`, `favoritos`), and `core/` (settings, DB session and security).

- **Schema creation:** `main.py` runs `Base.metadata.create_all()` on import. Changing a model doesn't alter existing tables, so in development delete the SQLite file or alter the table by hand.
- **Auth:** JWT bearer tokens with `sub` set to the user id (as a string) and a `rol` claim. Routers get the user through the `get_current_user` dependency. Merchant-only endpoints use `require_comercio`, which returns 403 unless `rol == "comercio"`. Ownership checks (`local.propietario_id == current_user.id`) are written inline in each handler, not in a shared dependency.
- **Roles:** `cliente` or `comercio`, stored as a DB enum on `Usuario`.
- **Relationships set with `backref`:** `Usuario.locales` and `Usuario.pedidos` are created by `backref` in `local.py` and `pedido.py` rather than declared on `Usuario`.
- **Orders:** `POST /pedidos` computes the total on the server from current product prices and stores `precio_unitario` on each `ItemPedido`. Every product must belong to `local_id` and be `disponible`. Status flow: `pendiente → en_preparacion → enviado → entregado`. Customers may only set `cancelado`; the store owner may set any status. Transitions aren't enforced.
- **Search:** `GET /locales?q=` filters in Python (not SQL) so it can ignore case and accents (`_normalizar` in `routers/locales.py`); every word must appear in the store's name/category/description or in one of its available products.
- **Favorites:** `Favorito` table (unique per user+store); `GET /favoritos`, idempotent `PUT`/`DELETE /favoritos/{local_id}` returning 204. `api.js` handles empty 204 bodies.
- **Order emails:** if a `Local` has `email`, `POST /pedidos` queues `services/correos_pedidos.notificar_nuevo_pedido` (BackgroundTasks, own DB session) which mails the store accept/reject links. Links carry a signed JWT (`tipo: respuesta_pedido`, expires after `RESPUESTA_PEDIDO_EXPIRE_HOURS`) and go to `routers/respuesta_pedido.py`: GET shows a confirmation page, POST applies it (accept → `enviado`, reject → `cancelado`, only from `pendiente`) and mails the client. `Local.email` is not in `LocalResponse` on purpose.
- **Mail sending:** `core/email.py` uses SMTP from `.env` (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `APP_URL`); with no `SMTP_HOST` it writes each mail as an .html file to `backend/correos_salientes/` (gitignored). See `backend/.env.example`.
- **Schema changes:** there are no migrations. `agregar_columnas_faltantes()` in `core/database.py` runs at startup and adds new nullable columns to existing tables; new non-nullable columns would still need a manual migration.
- **Soft visibility:** public listings filter on `Local.activo` and `Producto.disponible`. Products are hard-deleted.
- **CORS:** all origins are allowed.

**Frontend (`backend/app/index.html`, `views/`, `static/`)** is plain HTML with vanilla JS, Bootstrap and Font Awesome from CDNs. **FastAPI does not serve these files** (no `StaticFiles` mount and no template rendering), so open them with a static server or Live Server. They call the API at the hard-coded `API_BASE = 'http://localhost:8000'` in `static/js/api.js`.

- `api.js` wraps `fetch`, adds the token from `localStorage.atc_token`, and redirects to login on a 401. `auth.js` stores `atc_token` and `atc_usuario`. `carrito.js` keeps the cart in `atc_carrito`.
- Page paths are relative: `index.html` sits at the `app/` root and uses `./static/...` and `./views/...`; pages in `views/` use `../static/...` and `../index.html`. `getBase()` in `api.js` relies on this layout.
- Theming: all colors are CSS variables at the top of `style.css` (`--brand` for button backgrounds, `--brand-text` for red text). Dark mode follows `prefers-color-scheme` by default; the navbar toggle in `navbar.js` sets `data-theme` on `<html>` and stores it in `localStorage.atc_tema`. Each page has an inline `<head>` script that applies the saved theme before first paint. Asset links carry a `?v=N` query for cache busting; bump it when CSS/JS changes.
- `main.js`, `local.js` and `datos.js` (hard-coded mock stores) aren't referenced by any page. `index.html` and `local.html` have their own inline scripts instead.
- `ATuCasa/` is its own git repo (remote `origin` on GitHub, branch `main`), nested inside the outer `Dev` repo. Run git commands from `ATuCasa/`.
