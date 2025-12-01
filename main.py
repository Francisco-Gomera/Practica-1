from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from configurations.conection import DatabaseConnection
from services.spotifyservices import get_spotify_token_sync, search_spotify_song
import asyncio
import httpx
import os

HOST = os.getenv("DB_HOST")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("DB_PASS")
DATABASE = os.getenv("DB_DATABASE") or os.getenv("DB_NAME")

app = FastAPI()

@app.post("/users/")
async def post_user(request: Request):
    mydb = DatabaseConnection(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
    mydb_conn = None
    try:
        mydb_conn = await mydb.get_connection()
        request = await request.json()
        username = request['username']
        mycursor = mydb_conn.cursor()
        mycursor.execute(f"INSERT INTO users (name) VALUES ('{username}')")
        mydb_conn.commit()
        return JSONResponse(content={"message": "Usuario añadido correctamente"}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    finally:
        try:
            if mydb_conn:
                mydb_conn.close()
        except Exception:
            pass

@app.get("/users/")
async def get_users():
    mydb = DatabaseConnection(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
    mydb_conn = None
    try:
        mydb_conn = await mydb.get_connection()
        mycursor = mydb_conn.cursor()
        mycursor.execute("SELECT * FROM users")
        data = mycursor.fetchall()
        mydb_conn.commit()
        if not data:
            return JSONResponse(content={"message": "No hay usuarios"}, status_code=404)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    finally:
        try:
            if mydb_conn:
                mydb_conn.close()
        except Exception:
            pass

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    mydb = DatabaseConnection(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
    mydb_conn = None
    try:
        mydb_conn = await mydb.get_connection()
        mycursor = mydb_conn.cursor()
        mycursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
        data = mycursor.fetchone()
        mydb_conn.commit()
        if data is None:
            return JSONResponse(content={"message": "Usuario no encontrado"}, status_code=404)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    finally:
        try:
            if mydb_conn:
                mydb_conn.close()
        except Exception:
            pass

@app.put("/users/{user_id}")
async def put_user(user_id: int, request: Request):
    mydb = DatabaseConnection(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
    mydb_conn = None
    try:
        mydb_conn = await mydb.get_connection()
        mycursor = mydb_conn.cursor()
        request = await request.json()
        username = request['username']
        mycursor.execute(f"UPDATE users SET name = '{username}' WHERE id = {user_id}")
        mydb_conn.commit()
        return JSONResponse(content={"message": "Usuario actualizado correctamente"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    finally:
        try:
            if mydb_conn:
                mydb_conn.close()
        except Exception:
            pass

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    mydb = DatabaseConnection(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
    mydb_conn = None
    try:
        mydb_conn = await mydb.get_connection()
        mycursor = mydb_conn.cursor()
        mycursor.execute(f"DELETE FROM users WHERE id = {user_id}")
        affected = mycursor.rowcount
        mydb_conn.commit()
        if affected == 0:
            return JSONResponse(content={"message": "Usuario no encontrado"}, status_code=404)
        return JSONResponse(content={"message": "Usuario eliminado correctamente"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    finally:
        try:
            if mydb_conn:
                mydb_conn.close()
        except Exception:
            pass

@app.post("/preferences/{user_id}")
async def post_preferences(user_id: int, request: Request):
    mydb = DatabaseConnection(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
    mydb_conn = None
    try:
        mydb_conn = await mydb.get_connection()
        mycursor = mydb_conn.cursor()
        mycursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
        data = mycursor.fetchone()
        mydb_conn.commit()
        if data is None:
            return JSONResponse(content={"message": "No existe este Usuario para añadirle preferencias"}, status_code=404)
        request = await request.json()
        cancion = request['cancion']
        artiasta = request['artista']
        mycursor.execute(f"INSERT INTO preferencias (id_usuario, cancion, artista) VALUES ({user_id}, '{cancion}', '{artiasta}')")
        mydb_conn.commit()
        return JSONResponse(content={"message": "Preferencia añadida correctamente"}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    finally:
        try:
            if mydb_conn:
                mydb_conn.close()
        except Exception:
            pass

@app.get("/preferences/{user_id}")
async def get_preferences(user_id: int):
    try:
        mydb = DatabaseConnection(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
        mydb_conn = await mydb.get_connection()         
        mycursor = mydb_conn.cursor()
        mycursor.execute(f"SELECT name FROM users WHERE id = {user_id}")
        user_data = mycursor.fetchone()
        if user_data is None:
            mydb_conn.close()
            return JSONResponse(content={"message": "Usuario no encontrado"}, status_code=404)
        username = user_data[0]
        query = f"SELECT cancion, artista FROM preferencias WHERE id_usuario = {user_id}"
        mycursor.execute(query)
        rows = mycursor.fetchall()
        mydb_conn.close() 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

    if not rows:
        return JSONResponse(content={"usuario": user_id, "message": "No se le encontraron preferencias"}, status_code=404)

    token = get_spotify_token_sync()
    if not token:
        raise HTTPException(status_code=500, detail="No se pudo obtener token de Spotify")

    async with httpx.AsyncClient() as client:
        tasks = []
        for row in rows:
            cancion_db = row[0]
            artista_db = row[1]

            tasks.append(search_spotify_song(client, token, cancion_db, artista_db))

        resultados_spotify = await asyncio.gather(*tasks)

    return JSONResponse(content={"Usuario": user_id, "Nombre": username, "Lista de Preferencias": resultados_spotify}, status_code=200)

    
def clean_spotify_data(raw_json):
    if not raw_json or 'tracks' not in raw_json:
        return []

    items = raw_json['tracks']['items']
    cleaned_data = []

    for item in items:

        track = {
            "titulo": item.get('name'),
            "artistas": ", ".join([artist['name'] for artist in item['artists']]),
            "album": item['album']['name'],
            "popularidad": item['popularity'],
            "imagen": item['album']['images'][0]['url'] if item['album']['images'] else None,
            "preview_url": item.get('preview_url'),
            "spotify_url": item['external_urls'].get('spotify'),
            "track_id": item.get('id')
        }
        cleaned_data.append(track)
    
    return cleaned_data


