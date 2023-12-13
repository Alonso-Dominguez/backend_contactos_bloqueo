import fastapi
import sqlite3
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from uuid import uuid4 as new_token
import hashlib
# Importamos CORS para el acceso
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer, HTTPAuthorizationCredentials
import time

security = HTTPBasic()

securirtyBearer = HTTPBearer()

# Crea la base de datos
conn = sqlite3.connect("sql/contactos.db")

app = fastapi.FastAPI()

# Permitimos los origenes para conectarse
origins = [

    
    "http://0.0.0.0:8080",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "https://frontend-contactos-bloqueo-49a8fc94c0ff.herokuapp.com",
]

# Agregamos las opciones de origenes, credenciales, métodos y headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class Contacto(BaseModel):
    nombre: str
    primer_apellido: str
    segundo_apellido: str
    email: str
    telefono: str


# Respuesta de error
def error_response(mensaje: str, status_code: int):
    return JSONResponse(content={"mensaje": mensaje}, status_code=status_code)


async def cambiar_token_en_login(email):
    token = str(new_token())
    c = conn.cursor()
    c.execute("UPDATE usuarios SET token = ? WHERE username = ?", (token, email))
    conn.commit()
    return token
    
async def get_user_token(email: str, password_hash: str):
    c = conn.cursor()
    c.execute("SELECT token FROM usuarios WHERE username = ? AND password = ?", (email, password_hash))
    result = c.fetchone()
    return result


@app.get("/token/")
async def validate_user(credentials: HTTPBasicCredentials = Depends(security)):
    email = credentials.username
    password_hash = hashlib.md5(credentials.password.encode()).hexdigest()

    user_token = await get_user_token(email, password_hash)

    if user_token:
        token = await cambiar_token_en_login(email)
        response = {"token": token}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )

    return response


@app.get("/")
async def root(credentialsv: HTTPAuthorizationCredentials = Depends(securirtyBearer)):
    token = credentialsv.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    c = conn.cursor()
    c.execute("SELECT token FROM usuarios WHERE token = ?", (token,))
    result = c.fetchone()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no válido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"message": "Token válido"}


# Rutas para las operaciones CRUD

@app.post("/contactos")
async def crear_contacto(contacto: Contacto, credentialsv: HTTPAuthorizationCredentials = Depends(securirtyBearer)):
    token = credentialsv.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        c = conn.cursor()
        c.execute('INSERT INTO contactos (nombre, primer_apellido, segundo_apellido, email, telefono) VALUES (?, ?, ?, ?, ?)',
                  (contacto.nombre, contacto.primer_apellido, contacto.segundo_apellido, contacto.email, contacto.telefono))
        conn.commit()
        return contacto
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email ya existe")
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al consultar los datos")


@app.get("/contactos")
async def obtener_contactos(credentialsv: HTTPAuthorizationCredentials = Depends(securirtyBearer)):
    token = credentialsv.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    """Obtiene todos los contactos."""
    try:
        c = conn.cursor()
        c.execute('SELECT * FROM contactos;')
        response = []
        for row in c:
            contacto = {"id_contacto": row[0], "nombre": row[1], "primer_apellido": row[2], "segundo_apellido": row[3], "email": row[4], "telefono": row[5]}
            response.append(contacto)
        if not response:
            return []
        return response
    except sqlite3.Error:
        return error_response("Error al consultar los datos", 500)


@app.get("/contactos/{email}")
async def obtener_contacto(email: str, credentialsv: HTTPAuthorizationCredentials = Depends(securirtyBearer)):
    token = credentialsv.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    """Obtiene un contacto por su email."""
    try:
        c = conn.cursor()
        c.execute('SELECT * FROM contactos WHERE email = ?', (email,))
        contacto = None
        for row in c:
            contacto = {"id_contacto": row[0], "nombre": row[1], "primer_apellido": row[2], "segundo_apellido": row[3], "email": row[4], "telefono": row[5]}
        if not contacto:
            return error_response("El email de no existe", 404)
        return contacto
    except sqlite3.Error:
        return error_response("Error al consultar los datos", 500)

#Actualiza el contacto por el id
@app.put("/actualizar_contactos/{contacto_id}")
async def actualizar_contacto_por_id(contacto_id: int, contacto: Contacto, credentialsv: HTTPAuthorizationCredentials = Depends(securirtyBearer)):
    token = credentialsv.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    """Actualiza un contacto por ID."""
    try:
        c = conn.cursor()
        c.execute('UPDATE contactos SET nombre = ?, primer_apellido = ?, segundo_apellido = ?, telefono = ? WHERE id_contacto = ?',
                  (contacto.nombre, contacto.primer_apellido, contacto.segundo_apellido, contacto.telefono, contacto_id))
        conn.commit()
        return contacto
    except sqlite3.Error:
        return error_response("El contacto no existe" if not obtener_contacto_por_id(contacto_id) else "Error al consultar los datos", 400)


async def obtener_contacto_por_id(contacto_id: int):
    c = conn.cursor()
    c.execute('SELECT * FROM contactos WHERE id_contacto = ?', (contacto_id,))
    contacto = None
    for row in c:
        contacto = {
            "id_contacto": row[0],
            "nombre": row[1],
            "primer_apellido": row[2],
            "segundo_apellido": row[3],
            "email": row[4],
            "telefono": row[5],
        }
    return contacto

@app.delete("/contactos/{email}")
async def eliminar_contacto(email: str, credentialsv: HTTPAuthorizationCredentials = Depends(securirtyBearer)):
    token = credentialsv.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    """Elimina un contacto."""
    try:
        c = conn.cursor()
        c.execute('DELETE FROM contactos WHERE email = ?', (email,))
        conn.commit()
        if c.rowcount == 0:
            return error_response("El contacto no existe", 404)
        return {"mensaje": "Contacto eliminado"}
    except sqlite3.Error:
        return error_response("Error al consultar los datos", 500)
