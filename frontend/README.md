# Refugio Gestión — Frontend

The frontend is a responsive HTML5/CSS3/JavaScript interface. It uses native
JavaScript modules and sends REST/JSON requests to the FastAPI backend. It does
not use React.

## Local development

1. Start FastAPI from `backend`:
   `.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload`
2. From this folder, install the development tool:
   `npm install`
3. Start the UI with `npm run dev` and open
   `http://127.0.0.1:5175`.

Vite proxies the backend API routes to `http://127.0.0.1:8000`. The browser
session uses the backend's HttpOnly cookie. Database credentials remain in
`backend/.env`; never copy them into this project.

## Access control and modules

The sidebar stays the same for every signed-in user. Opening a module the
current account cannot access shows a permission notice; the backend remains
the authority and validates every protected request.

The UI connects the in-scope backend modules for sign-in/session management,
users, locations, products and suppliers, per-location inventory, tables, and
open orders. Payment, order closing, sales reports, Excel export, and deployment
configuration are not included.

## Checks

- `npm run build`
