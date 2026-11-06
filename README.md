# Tienda Online: Django + React

Backend en Django REST Framework con autenticación JWT y frontend en React (Vite).
Incluye el consumo de una API de terceros (Open-Meteo) y de un Web Service SOAP (zeep).

## Tecnologías

| Parte | Tecnologías |
| --- | --- |
| Backend | Python 3.14, Django 5.2, Django REST Framework, SimpleJWT, django-cors-headers, zeep, MySQL |
| Frontend | Node 24, React 18, Vite 8, React Router 6, Semantic UI React, Formik, Yup, Sass, React Toastify |

## Estructura

```text
.
├── manage.py
├── requirements.txt
├── tienda_online/     Configuración del proyecto Django
├── products/          Productos y categorías (API protegida con JWT)
├── users/             Registro y datos del usuario autenticado
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
CREATE DATABASE hackathon CHARACTER SET utf8mb4;
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

## Uso

1. Abre `http://localhost:5173` y entra a **Registrarme**.
2. Crea una cuenta. La contraseña necesita 8 caracteres, una mayúscula, un número y un carácter especial.
3. Inicia sesión con tu **usuario** y contraseña. Se abrirá el Dashboard.

El login usa el nombre de usuario, no el correo, porque el proyecto conserva el modelo `User` de Django.

## Endpoints

| Método | Ruta | Acceso | Descripción |
| --- | --- | --- | --- |
| POST | `/api/token/` | Público | Inicia sesión y devuelve el JWT |
| POST | `/api/token/refresh/` | Público | Renueva el token de acceso |
| POST | `/api/auth/register/` | Público | Registra un usuario |
| GET | `/api/auth/me/` | JWT | Datos del usuario autenticado |
| GET | `/api/soap/countries/<iso>/` | JWT | Datos de un país por SOAP, por ejemplo `MX` |
| GET, POST | `/api/products/` | JWT | Lista y crea productos |
| GET, PUT, PATCH, DELETE | `/api/products/<id>/` | JWT | Consulta, edita y elimina un producto |
| GET | `/api/products/<id>/precio-final/` | JWT | Precio con descuento según la categoría |
| GET, POST | `/api/categories/` | JWT | Lista y crea categorías |
| GET, PUT, PATCH, DELETE | `/api/categories/<id>/` | JWT | Consulta, edita y elimina una categoría |

Ejemplo del endpoint SOAP en PowerShell:

```powershell
$credenciales = @{ username = 'TU_USUARIO'; password = 'TU_CONTRASENA' } | ConvertTo-Json
$token = (Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/token/ -ContentType 'application/json' -Body $credenciales).access
Invoke-RestMethod -Uri http://localhost:8000/api/soap/countries/MX/ -Headers @{ Authorization = "Bearer $token" }
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

- `Login.jsx` escribe el token en la consola porque el entregable pide esa evidencia.
  Hay que quitar esa línea antes de usar el proyecto en producción.
- `npm audit` reporta 2 avisos moderados de React Router 6, y la corrección requiere pasar a la versión 7.
  Se conserva la 6 porque la pide la actividad. Los avisos no afectan a este proyecto: los enlaces son
  fijos y no hay renderizado en servidor.
- React está en la versión 18 porque `semantic-ui-react` no es compatible con React 19.
