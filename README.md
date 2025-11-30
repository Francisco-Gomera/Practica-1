# API de Música / Preferencias (Práctica 1)

Proyecto de ejemplo en FastAPI para gestionar usuarios y preferencias musicales. Incluye integración simple con la API de Spotify para búsqueda de canciones.

**Estructura principal**
- `main.py` : endpoints de la API.
- `configurations/conection.py` : conexión a la base de datos (clase `DatabaseConnection`).
- `services/` : servicios para Spotify y otros (tokens, búsquedas, limpieza de datos).

**Requisitos**
- Python 3.10+ (se usó venv en el proyecto)
- MySQL

**Dependencias**
Instalar desde `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

**Configuración de la base de datos**
Ejemplo de tablas mínimas (MySQL):

```sql
USE sys;

CREATE DATABASE practica;

USE practica; 

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);

CREATE TABLE preferencias (
  id INT AUTO_INCREMENT PRIMARY KEY,
  id_usuario INT NOT NULL,
  cancion VARCHAR(255),
  artista VARCHAR(255),
  FOREIGN KEY (id_usuario) REFERENCES users(id) ON DELETE CASCADE
);
``` 

**Variables de entorno**
Crea un archivo `.env`, en este define las variables con los datos para acceder a la base de datos

Variables (ejemplo):
```
DB_HOST=localhost
DB_USER=root
DB_PASS=tu_contraseña
DB_NAME=practica
```

**Ejecutar la aplicación (venv Windows)**
```bash
# activar el venv (Windows PowerShell)
# .\venv\Scripts\Activate.ps1
# o en bash usage mostrado en el proyecto:
"C:/ruta/al/proyecto/venv/Scripts/python.exe" -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Otras opciones (si activas el venv):
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Endpoints principales**
- `POST /users/` : Añade un usuario.
  - Body JSON: `{ "username": "Nombre" }` (en algunos `main.py` usan `name` o `username`, revisa tu versión)
  - Respuesta: `201` message.

- `GET /users/` : Obtiene todos los usuarios.
  - Respuesta: lista de usuarios.

- `GET /users/{user_id}` : Obtiene un usuario por id.
  - Respuesta: objeto usuario o `404`.

- `PUT /users/{user_id}` : Actualiza el nombre del usuario.
  - Body JSON: `{ "username": "NuevoNombre" }`.

- `DELETE /users/{user_id}` : Elimina el usuario.

- `POST /preferences/{user_id}` : Añade una preferencia (canción/artista) para un usuario.
  - Body JSON: `{ "cancion": "nombre", "artista": "autor" }`.

- `GET /preferences/{user_id}` : Devuelve las preferencias del usuario y busca información en Spotify.
  - Uso de `httpx` asincrónico para consultas concurrentes.

- `GET /song/{song}` : Busca una canción en Spotify (endpoint de utilidad).

**Notas de seguridad y buenas prácticas**
- No guardes credenciales en el código; usa `.env` y variables de entorno.
- Usa consultas parametrizadas para evitar SQL injection (en el proyecto actual se usan `execute(f"...{var}...")` que es inseguro).
- Cerrar cursores y conexiones después de usarlos.
- Considera usar un pool de conexiones (p. ej. `mysql.connector.pooling`) para aplicaciones con más carga.

**Testing rápido**
Ejemplo curl para obtener usuarios:

```bash
curl http://127.0.0.1:8000/users/
```

Ejemplo para añadir un usuario:

```bash
curl -X POST http://127.0.0.1:8000/users/ -H 'Content-Type: application/json' -d '{"username":"Juan"}'
```