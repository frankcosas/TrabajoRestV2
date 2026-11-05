# Gourmet Restó – Django + MySQL + API REST

## Puesta en marcha
1. Iniciar MySQL (XAMPP) y crear la base: `CREATE DATABASE restaurante_db CHARACTER SET utf8mb4;`
2. `pip install -r requirements.txt`
3. `python manage.py makemigrations && python manage.py migrate`
4. `python manage.py createsuperuser` (o usar `/registro/` en la web)
5. `python manage.py runserver`

Credenciales de MySQL por defecto: usuario `root`, sin contraseña. Se pueden cambiar con las variables
`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.

## Web
`/login/`, `/logout/`, `/registro/` y CRUD de platos en `/platos/` (requiere sesión iniciada).

## API REST (JSON, autenticación por token)
Al iniciar sesión desde `/login/` o crear una cuenta desde `/registro/`, Django genera (o reutiliza) el token del usuario y lo guarda en su sesión. El frontend lo recibe como `window.GOURMET_API_TOKEN`; para llamar a endpoints protegidos desde JavaScript utiliza `gourmetApiFetch(url, options)`, que agrega automáticamente `Authorization: Token <token>`.

1. Obtener token: `POST /api/token/` con `{"username": "...", "password": "..."}` → `{"token": "..."}`
2. Enviarlo en cada solicitud: cabecera `Authorization: Token <token>`

| Método | URL | Acción | Respuestas |
|---|---|---|---|
| GET | `/api/platos/` | Listar | 200 |
| GET | `/api/platos/<id>/` | Consultar por ID | 200 / 404 |
| POST | `/api/platos/` | Crear | 201 / 400 |
| PUT | `/api/platos/<id>/` | Actualizar | 200 / 400 / 404 |
| DELETE | `/api/platos/<id>/` | Eliminar | 204 / 404 |

Lo mismo para `/api/categorias/`. Sin token o con token inválido: **401**.

```bash
curl -X POST http://127.0.0.1:8000/api/token/ -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"tu_clave"}'
curl http://127.0.0.1:8000/api/platos/ -H "Authorization: Token TU_TOKEN"
curl -X POST http://127.0.0.1:8000/api/platos/ -H "Authorization: Token TU_TOKEN" \
     -H "Content-Type: application/json" -d '{"nombre":"Cazuela","precio":6500}'
```

## Pruebas
`python manage.py test` (usa una base de datos de prueba; requiere permiso de MySQL para crearla).
