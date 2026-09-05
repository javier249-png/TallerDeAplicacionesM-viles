from fastapi import FastAPI

app = FastAPI(title="API de Música")

CANCIONES = [
    {"id": 1, "titulo": "Bohemian Rhapsody", "artista": "Queen", "duracion": "5:55", "url_audio": "http://example.com/audio1.mp3"},
    {"id": 2, "titulo": "Blinding Lights", "artista": "The Weeknd", "duracion": "3:20", "url_audio": "http://example.com/audio2.mp3"}
]

@app.get("/")
def inicio():
    return {"mensaje": "API de música activa"}

@app.get("/canciones")
def listar_canciones():
    return CANCIONES

@app.get("/canciones/{cancion_id}")
def obtener_cancion(cancion_id: int):
    cancion = next((c for c in CANCIONES if c["id"] == cancion_id), None)
    if cancion:
        return cancion
    return {"error": "Canción no encontrada"}