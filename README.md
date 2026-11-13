# Lab 12 — Ajax y Servicios Web (CORS + React + Axios)

Laboratorio de la Semana 12 de Desarrollo de Aplicaciones Empresariales (Tecsup). Dos proyectos en un repositorio:

| Carpeta | Qué es | Origen / puerto |
|---|---|---|
| `api/` | API de cuestionarios del Lab 8 (Django REST Framework) + `django-cors-headers` | `http://127.0.0.1:8000` |
| `web/` | Cliente React (Vite) del Lab 11 con Axios | `http://localhost:5173` |

## Qué origen espera cada lado

- **La API** acepta peticiones de **un solo origen**: `http://localhost:5173` (el de React). No usa el comodín `*`.
  Para otro origen: variable de entorno `CORS_ALLOWED_ORIGINS` (separados por coma).
- **React** llama a la API en `VITE_API_URL` (por defecto `http://127.0.0.1:8000/api`). Esa dirección está en un solo
  sitio: `web/src/api/quizApi.js`.

## Cómo levantar la API

```powershell
cd api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_quiz        # imprime los tokens de «profe» y «agente»
python manage.py runserver 8000
```

## Cómo levantar React

Crea `web/.env.local` (no se sube a git) con el token de la persona (`profe`) que imprimió `seed_quiz`:

```
VITE_API_URL=http://127.0.0.1:8000/api
VITE_QUIZ_TOKEN=<token de profe>
```

```powershell
cd web
npm install
npm run dev                       # http://localhost:5173
```

Leer exámenes no necesita token; **crear y eliminar sí** (regla del Lab 8: el servidor decide quién escribe).

## Qué hace la pantalla

| Momento | Petición | Estado y lo que se ve |
|---|---|---|
| Al entrar | `GET /api/exams/?page_size=50` dentro de `useEffect` | **Carga**: esqueleto gris · **Datos**: tabla · **Error**: mensaje rojo con «Reintentar» |
| Eliminar | `DELETE /api/exams/{id}/` y vuelve a pedir la lista | El botón dice «Borrando…» y la fila desaparece sin recargar |
| Guardar examen | `POST /api/exams/` con `{ "title": ... }` | Vuelve al listado; si la API responde 400, muestra su mensaje |

## Límites

- El token de la persona va en una variable de Vite: sirve para el laboratorio, pero en producción un token así no
  debe viajar en el código del navegador (se usaría un inicio de sesión).
- El mensaje de error es el mismo si el servidor está apagado o si CORS bloquea; solo la consola del navegador los
  distingue (`blocked by CORS policy` frente a `ERR_CONNECTION_REFUSED`).
