import sqlite3
import hashlib
import secrets
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitimos los origenes para conectarse
origins = [
    "http://0.0.0.0:8080",  
    "http://localhost:8080",  
    "http://127.0.0.1:8080", 
    "https://frontend-contactos-jadc-acbf7ce35d15.herokuapp.com",
]

# Agregamos las opciones de origenes, credenciales, métodos y headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

security = HTTPBasic()
security_bearer = HTTPBearer()

# Conexión a la base de datos SQLite
conn = sqlite3.connect('sql/usuarios.db')

# Función para manejar la ruta "/" que valida un token de autenticación
@app.get("/")
async def root(credentials: HTTPAuthorizationCredentials = Depends(security_bearer)):
    token = credentials.credentials  # Obtener el token del encabezado de autorización
    user = validate_token(conn, token)  # Validar el token en la base de datos
    return {"message": "Token válido para el usuario: {}".format(user)}

# Función para manejar la ruta "/token/" que valida las credenciales de usuario y devuelve un token
@app.get("/token/")
async def validate_user(credentials: HTTPBasicCredentials = Depends(security)):
    # Obtiene el nombre de usuario y la contraseña de las credenciales básicas
    email = credentials.username
    password_plain = credentials.password
    
    # Hashear la contraseña antes de validar las credenciales
    password_hash = hash_password(password_plain)
    
    user_token = validate_credentials(conn, email, password_hash)  # Valida las credenciales en la base de datos y obtiene el token
    
    return {"Tu token es": user_token}

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
