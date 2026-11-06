# Tienda Online: Django + React

API de una tienda en línea con Django REST Framework, usuarios personalizados, login con JWT y
documentación en Swagger. Incluye un frontend en React (Vite), el consumo de una API de terceros
(Open-Meteo) y de un Web Service SOAP (zeep).

## Tecnologías

| Parte | Tecnologías |
| --- | --- |
| Backend | Python 3.14, Django 5.2, Django REST Framework, SimpleJWT, drf-yasg, django-cors-headers, zeep, MySQL |
| Frontend | Node 24, React 18, Vite 8, React Router 6, Semantic UI React, Formik, Yup, Sass, React Toastify |

## Estructura

```text
.
├── manage.py
├── requirements.txt
├── tienda_online/     Configuración del proyecto Django
├── products/          Productos y categorías (API protegida con JWT)
├── users/             Modelo de usuario, CRUD, registro, login y datos personales
├── countries/         Consumo del servicio SOAP de países
└── frontend/          Aplicación de React
    └── src/
        ├── api/         Comunicación con el backend y con Open-Meteo
        ├── components/  Widget del clima
        ├── context/     AuthContext
        ├── hooks/       useAuth y useUser
        ├── layouts/     Layouts de admin, cliente y común
        ├── pages/       Páginas de admin, cliente y común
        └── routes/      Rutas con React Router
```

## Requisitos previos

- Python 3.12 o superior
- Node.js 20 o superior
- MySQL 8

## Instalación

### 1. Base de datos

Crea la base de datos en MySQL:

```sql
CREATE DATABASE tienda_online CHARACTER SET utf8mb4;
```

Si tu usuario o contraseña de MySQL son distintos, ajústalos en `DATABASES` dentro de
`tienda_online/settings.py`.

### 2. Backend

Desde la raíz del proyecto, en PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

El backend queda en `http://localhost:8000`.

### 3. Frontend

En otra terminal, desde la raíz del proyecto:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

El frontend queda en `http://localhost:5173`. El backend solo acepta peticiones de ese origen
(`CORS_ALLOWED_ORIGINS` en `settings.py`), así que no cambies el puerto.

## Documentación de la API

- Swagger: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

Para probar un endpoint protegido en Swagger:

1. Ejecuta `POST /auth/token/` con tu correo y contraseña, y copia el valor de `access`.
2. Abre **Authorize** y escribe `Bearer TU_TOKEN`.

## Usuarios

- El login usa el **correo** y la contraseña.
- El modelo `users.User` agrega el campo `telefono`, visible en el admin, en la API y en Swagger.
- El token de acceso dura 1 hora (`ACCESS_TOKEN_LIFETIME` en `settings.py`).
- La API nunca devuelve la contraseña. Al editar un usuario, la contraseña solo cambia si se envía.

## Endpoints

Todas las rutas empiezan con `/api/v1`.

| Método | Ruta | Acceso | Descripción |
| --- | --- | --- | --- |
| POST | `/auth/token/` | Público | Inicia sesión y devuelve el JWT |
| POST | `/auth/token/refresh/` | Público | Renueva el token de acceso |
| POST | `/auth/register/` | Público | Registra un usuario |
| GET | `/auth/me/` | JWT | Datos personales del usuario autenticado |
| GET, POST | `/users/` | Administrador | Lista y crea usuarios |
| GET, PUT, PATCH, DELETE | `/users/<id>/` | Administrador | Consulta, edita y elimina un usuario |
| GET | `/soap/countries/<iso>/` | JWT | Datos de un país por SOAP, por ejemplo `MX` |
| GET, POST | `/products/` | JWT | Lista y crea productos |
| GET, PUT, PATCH, DELETE | `/products/<id>/` | JWT | Consulta, edita y elimina un producto |
| GET | `/products/<id>/precio-final/` | JWT | Precio con descuento según la categoría |
| GET, POST | `/categories/` | JWT | Lista y crea categorías |
| GET, PUT, PATCH, DELETE | `/categories/<id>/` | JWT | Consulta, edita y elimina una categoría |

Ejemplo en PowerShell:

```powershell
$credenciales = @{ email = 'TU_CORREO'; password = 'TU_CONTRASENA' } | ConvertTo-Json
$token = (Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/auth/token/ -ContentType 'application/json' -Body $credenciales).access
Invoke-RestMethod -Uri http://localhost:8000/api/v1/auth/me/ -Headers @{ Authorization = "Bearer $token" }
```

## Servicios externos

- **Open-Meteo** (`https://open-meteo.com/`): clima del Dashboard. Es gratis y no necesita clave.
  Para cambiar de ciudad, edita `CITY` en `frontend/src/api/weather.js`.
- **CountryInfoService** (`http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL`):
  servicio SOAP público. Si no responde, el endpoint devuelve `502`.

## Pruebas

```powershell
python manage.py test
```

Las pruebas crean una base de datos temporal, por lo que el usuario de MySQL necesita permiso para crearla.

## Notas

- `Login.jsx` escribe el token en la consola porque un entregable pedía esa evidencia.
  Hay que quitar esa línea antes de usar el proyecto en producción.
- `npm audit` reporta 2 avisos moderados de React Router 6, y la corrección requiere pasar a la versión 7.
  Se conserva la 6 porque la pide la actividad. Los avisos no afectan a este proyecto: los enlaces son
  fijos y no hay renderizado en servidor.
- React está en la versión 18 porque `semantic-ui-react` no es compatible con React 19.
