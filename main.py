from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
import sqlite3
import hashlib
import secrets


app = FastAPI()

# Permitimos los origenes para conectarse
origins = [
    "http://0.0.0.0:8080",  
    "http://localhost:8080",  
    "http://127.0.0.1:8080", 
    "https://frontend-contactos-bloqueo-49a8fc94c0ff.herokuapp.com/",
]

# Agregamos las opciones de origenes, credenciales, métodos y headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Modelo para la creación de un nuevo contacto
class ContactoCreate(BaseModel):
    nombre: str
    primer_apellido: str
    segundo_apellido: str
    email: str
    telefono: str

# Conéctate a la base de datos SQLite y crea una tabla para almacenar los contactos si no existe
def connect_to_database():
    conn = sqlite3.connect("sql/contactos.db")
    cursor = conn.cursor()
    return conn, cursor

def close_database_connection(conn):
    conn.close()

# Función para obtener todos los contactos
def obtener_contactos(cursor):
    cursor.execute("SELECT * FROM contactos")
    contactos = cursor.fetchall()
    return [dict(zip(["id_contacto", "nombre", "primer_apellido", "segundo_apellido", "email", "telefono"], c)) for c in contactos]

# Endpoint para agregar un nuevo contacto
@app.post("/contactos", description="Agregar un nuevo contacto", response_model=dict)
async def agregar_contacto(contacto: ContactoCreate):
    try:
        conn, cursor = connect_to_database()
        cursor.execute('''
            INSERT INTO contactos (nombre, primer_apellido, segundo_apellido, email, telefono)
            VALUES (?, ?, ?, ?, ?)
        ''', (contacto.nombre, contacto.primer_apellido, contacto.segundo_apellido, contacto.email, contacto.telefono))
        conn.commit()
        close_database_connection(conn)
        return contacto.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al agregar el contacto")

# Endpoint para obtener todos los contactos
@app.get("/contactos", description="Obtener todos los contactos", response_model=list[dict])
async def get_contactos():
    try:
        conn, cursor = connect_to_database()
        result = obtener_contactos(cursor)
        close_database_connection(conn)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener los contactos")

# Endpoint para actualizar un contacto por id_contacto
@app.put("/contactos/{contacto_id}", description="Actualizar un contacto por su ID", response_model=dict)
@app.patch("/contactos/{contacto_id}", description="Actualizar un contacto por su ID", response_model=dict)
async def actualizar_contacto(contacto_id: int, contacto: ContactoCreate):
    try:
        conn, cursor = connect_to_database()
        cursor.execute('''
            UPDATE contactos
            SET nombre = ?, primer_apellido = ?, segundo_apellido = ?, email = ?, telefono = ?
            WHERE id_contacto = ?
        ''', (contacto.nombre, contacto.primer_apellido, contacto.segundo_apellido, contacto.email, contacto.telefono, contacto_id))
        conn.commit()

        if cursor.rowcount == 0:
            close_database_connection(conn)
            raise HTTPException(status_code=404, detail="Contacto no encontrado")
        
        close_database_connection(conn)
        return { "id_contacto": contacto_id, **contacto.dict() }

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="Error al actualizar el contacto")

# Endpoint para borrar un contacto por id_contacto
@app.delete("/contactos/{contacto_id}", description="Borrar un contacto por su ID", response_model=dict)
async def borrar_contacto(contacto_id: int):
    try:
        conn, cursor = connect_to_database()

        cursor.execute("SELECT * FROM contactos WHERE id_contacto = ?", (contacto_id,))
        contacto = cursor.fetchone()

        if not contacto:
            close_database_connection(conn)
            raise HTTPException(status_code=404, detail="Contacto no encontrado")

        cursor.execute("DELETE FROM contactos WHERE id_contacto = ?", (contacto_id,))
        conn.commit()

        close_database_connection(conn)

        return { "id_contacto": contacto_id, **dict(zip(["nombre", "primer_apellido", "segundo_apellido", "email", "telefono"], contacto)) }

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="Error al borrar el contacto")


# Endpoint para buscar un contacto por email 
@app.get("/contactos/buscar", description="Buscar contactos por email", response_model=list[dict])
async def buscar_contactos_por_email(email: str):
    try:
        print(f'Búsqueda de contactos por email: {email}')
        conn, cursor = connect_to_database()
        cursor.execute('SELECT * FROM contactos WHERE email LIKE ?', ('%' + email + '%',))
        contactos = cursor.fetchall()
        print(f'Resultados de la búsqueda: {contactos}')
        close_database_connection(conn)
        return [dict(zip(["id_contacto", "nombre", "primer_apellido", "segundo_apellido", "email", "telefono"], c)) for c in contactos]
    except Exception as e:
        print(f'Error al buscar contactos por email: {e}')
        raise HTTPException(status_code=500, detail="Error al buscar contactos por email")
    
security = HTTPBasic()
security_bearer = HTTPBearer()

# Conexión a la base de datos SQLite
conn = sqlite3.connect('sql/usuarios.db')


class TokenResponseModel(BaseModel):
    token: str

@app.get("/")
async def root(credentials: HTTPBasicCredentials = Depends(security)):
    user = validate_credentials(conn, credentials.username, hashlib.sha512(credentials.password.encode()).hexdigest())
    return {"message": "Token válido para el usuario: {}".format(user)}

@app.get("/token/", response_model=TokenResponseModel)
async def validate_user(credentials: HTTPBasicCredentials = Depends(security)):
    usuario = credentials.username
    password_hash = hashlib.sha512(credentials.password.encode()).hexdigest()

    user_token = await get_user_token(usuario, password_hash)

    if user_token:
        token = await cambiar_token_en_login(usuario)
        return TokenResponseModel(token=token)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )

def cambiar_token_en_login(usuario):
    token = str(new_token())
    c = conn.cursor()
    c.execute("UPDATE usuarios SET token = ? WHERE username = ?", (token, usuario))
    return token

async def get_user_token(usuario: str, password_hash: str):
    try:
        c = conn.cursor()
        c.execute("SELECT token FROM usuarios WHERE username = ? AND contrasena = ?", (usuario, password_hash))
        result = c.fetchone()
        return result
    except sqlite3.Error as e:
        # Manejar la excepción de manera adecuada, loggear o notificar según sea necesario
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener token del usuario",
        )

# Nuevo endpoint para la ruta "/registro/"
@app.post("/registro/")
async def registro(usuario: str, contrasena: str):
    contrasena_hash = hash_password(contrasena)  # Hashear la contraseña
    token = generate_token()  # Generar un token aleatorio
    token_hash = hash_password(token)  # Encriptar el token

    # Insertar datos en la base de datos
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (usuario, contrasena, token) VALUES (?, ?, ?)", (usuario, contrasena_hash, token_hash))
    conn.commit()

    return {"message": "Usuario registrado exitosamente"}

# Nuevo endpoint para la ruta "/login/"
@app.post("/login/")
async def login(usuario: str, contrasena: str):
    contrasena_hash = hash_password(contrasena)

    # Validar el inicio de sesión consultando la base de datos
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND contrasena = ?", (usuario, contrasena_hash))
    result = cursor.fetchone()

    # Verificar si se encontró un usuario válido en la base de datos
    if result:
        usuario_token = decrypt_token(result[2])  # Obtener el token del usuario y desencriptarlo
        return {"message": "Inicio de sesión exitoso", "user_token": usuario_token}
    else:
        # Mostrar un mensaje de error y devolver un error HTTP
        raise HTTPException(status_code=401, detail="Usuario no encontrado, intente de nuevo por favor")

# Función para validar un token en la base de datos
def validate_token(conn: sqlite3.Connection, token: str) -> str:
    # Crear un cursor para ejecutar la consulta en la base de datos
    c = conn.cursor()

    # Ejecutar una consulta para obtener el usuario asociado con el token
    c.execute("SELECT usuario FROM usuarios WHERE token = ?", (token,))

    # Obtener el resultado de la consulta
    result = c.fetchone()

    # Verificar si se encontró un usuario y devolverlo, de lo contrario, lanzar una excepción
    if result:
        return result[0]
    else:
        raise HTTPException(status_code=401, detail="Token no válido")

# Función para validar las credenciales de usuario en la base de datos y obtener un token
def validate_credentials(conn: sqlite3.Connection, email: str, password_hash: str) -> str:
    # Crear un cursor para ejecutar la consulta en la base de datos
    c = conn.cursor()

    # Ejecutar una consulta para obtener el token asociado con el usuario y la contraseña
    c.execute("SELECT token FROM usuarios WHERE usuario = ? AND contrasena = ?", (email, password_hash))

    # Obtener el resultado de la consulta
    result = c.fetchone()

    # Verificar si se encontró un token y devolverlo, de lo contrario, lanzar una excepción
    if result:
        return result[0]
    else:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

# Función para hashear una contraseña
def hash_password(password: str) -> str:
    # Utilizar el hash SHA-512 para la contraseña
    return hashlib.sha512(password.encode()).hexdigest()

# Función para generar un token aleatorio
def generate_token() -> str:
    return secrets.token_hex(32)

# Función para desencriptar un token
def decrypt_token(encrypted_token: str) -> str:
    return encrypted_token


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
