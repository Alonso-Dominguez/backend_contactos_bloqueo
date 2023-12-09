from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

# Permitimos los origenes para conectarse
origins = [
    "http://0.0.0.0:8080",  
    "http://localhost:8080",  
    "http://127.0.0.1:8080", 
    #"https://frontend-contactos-jadc-acbf7ce35d15.herokuapp.com",
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
