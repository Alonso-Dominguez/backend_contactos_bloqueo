# Desin Document: API REST CONTACTOS 

## 1. Descripción 
Ejempko de una API REST pata gestionar contactos en una BD utilizando FastAPI.

## 2. Objetivo
Realizar un ejemplo de diseño de una API REST de tipo CRUD y su posterior codificación untilizando el Framework [FastAPI](https://fastapi.tiangolo.com/).

## 3. Diseño de la BD 
Para este ejemplo se utlizara el gestor de bases de datos [SQLite3](https://sqlite.org) con las siguientes tablas: 

3.1
|No.|Campo|Tipo|Restricciones|Descrición|
|--|--|--|--|--|
|1|id-contactos|int|PRIMARY KEY|Llave primariace la tabla|

3.2
```sql
CREATE TABLE IF NOT EXISTS contactos (
    id_contacto        INT PRIMARY KEY NOT NULL,
    nombre             VARCHAR(100) NOT NULL,
    primer_apellido    VARCHAR(50) NOT NULL,
    segundo_apellido   VARCHAR(50) NOT NULL,
    telefono           VARCHAR(20) NOT NULL,
    correo_electronico VARCHAR(50) NOT NULL
);
```
## 5. Diseño de los métodos

### 5.1 GET - http://localhost:8000/
|No|Propiedad|Detalle|
|--|--|--|
|1|Description|Endpoint raíz de la API|
|2|Summary|Endpoint raiz|
|3|Method|GET|
|4|Endpoint|http://localhost:8000/|
|5|QueryParam|NA|
|6|PathParam|NA|
|7|DATA|NA|
|8|Versiones|V1|
|9|Status code|200 ok|
|10|Response-Type|application/json|
|11|Response|{"version":"v1","message":"endpoint raiz","datatime":"18/9/23 11:05"}|
|12|Curl|curl -X 'GET' 'http://localhost:8000/' -H 'accept: application/json'|
|13|Status code(error)|NA|
|14|Response Type(error)|NA|
|15|Response(error)|NA|

### 5.2 GET - http://localhost:8000/contactos
|No|Propiedad|Detalle|
|--|--|--|
|1|Description|Endpoint para obtener datos|
|2|Summary|Endpoint para listar|
|3|Method|GET|
|4|Endpoint|http://localhost:8000/contactos|
|5|QueryParam|limit:int, offset:int, nombre:string|
|6|PathParam|NA|
|7|DATA|NA|
|8|Versiones|V1|
|9|Status code|200 ok|
|10|Response-Type|application/json|
|11|Response|{"version":"v1","message":"Lista de contactos","datatime":"20/9/23 8:43"}|
|12|Curl|curl -X 'GET' 'http://localhost:8000/?limit=10&offset=0&nombre=Juan' -H 'accept: application/json'|
|13|Status code(error)|400|
|14|Response Type(error)|application/json|
|15|Response(error)|{"version":"v1","message-error":"ocurrió un error","datatime":"21/9/27 9:43"}|

### 5.3 POST - http://localhost:8000/contactos
|No|Propiedad|Detalle|
|--|--|--|
|1|Description|Endpoint para enviar datos a la API|
|2|Summary|Endpoint para enviar datos|
|3|Method|POST|
|4|Endpoint|http://localhost:8000/contactos|
|5|QueryParam|NA|
|6|PathParam|NA|
|7|DATA|{"id_contacto":int, "nombre":string, "apellido_paterno":string, "apellido_materno":string, "email":string, "telefono":string}|
|8|Versiones|V1|
|9|Status code|201 Created|
|10|Response-Type|application/json|
|11|Response|{"version":"v1","message":"Lista de contactos","datatime":"22/9/23 9:20"}|
|12|Curl|curl -X 'POST' 'http://localhost:8000/contactos' -H 'accept: application/json' -d '{"id_contacto":int, "nombre":string, "apellido_paterno":string, "apellido_materno":string, "email":string, "telefono":string}'|
|13|Status code(error)|400 Bad Request|
|14|Response Type(error)|application/json|
|15|Response(error)|{"version":"v1","message-error":"ocurrió un error","datatime":"22/9/23 8:55"}|

### 5.4 DELETE - http://localhost:8000/contactos/?id_contacto=
|No|Propiedad|Detalle|
|--|--|--|
|1|Description|Endpoint para eliminar un recurso de la API|
|2|Summary|Endpoint para eliminar un recurso|
|3|Method|DELETE|
|4|Endpoint|http://localhost:8000/contactos/?id_contacto=|
|5|QueryParam|id_contacto|
|6|PathParam|NA|
|7|DATA|NA|
|8|Versiones|V1|
|9|Status code|204 No Content|
|10|Response-Type|application/json|
|11|Response|{"version":"v1","message":"Se eliminó con éxito","datatime":"24/9/23 10:12"}|
|12|Curl|curl -X 'DELETE' 'http://localhost:8000/?id_contacto=1' -H 'accept: application/json'|
|13|Status code(error)|400 Bad Request|
|14|Response Type(error)|application/json|
|15|Response(error)|{"version":"v1","message-error":"ocurrió un error al eliminar","datatime":"25/9/27 10:14"}|

### 5.5 PUT - http://localhost:8000/contactos/?id_contactos=
|No|Propiedad|Detalle|
|--|--|--|
|1|Description|Endpoint para actualizar recursos de la API|
|2|Summary|Endpoint para actulizar datos|
|3|Method|PUT|
|4|Endpoint|http://localhost:8000/contactos/?id_contacto=|
|5|QueryParam|id_contacto|
|6|PathParam|NA|
|7|DATA|NA|
|8|Versiones|V1|
|9|Status code|200 Ok|
|10|Response-Type|application/json|
|11|Response|{"version":"v1","message":"Actualizado con éxito","datatime":"25/9/23 11:36"}|
|12|Curl|curl -X 'DELETE' 'http://localhost:8000/?id_contacto=1' -H 'accept: application/json'|
|13|Status code(error)|400 Bad Request|
|14|Response Type(error)|application/json|
|15|Response(error)|{"version":"v1","message-error":"ocurrió un error al actualizar","datatime":"26/9/23 12:46"}|
