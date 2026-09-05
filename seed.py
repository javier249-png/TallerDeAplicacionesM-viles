from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models import Audio

def poblar_base_de_datos():
    create_db_and_tables()
    with Session(engine) as session:
        # Verificar si ya existen audios creados
        existente = session.exec(select(Audio)).first()
        if existente:
            print("La base de datos ya contiene información.")
            return

        audios_iniciales = [
            Audio(
                titulo="Lluvia en la Ventana", 
                tipo_sonido="Ruido Blanco", 
                categoria="Relax", 
                duracion="30:00", 
                url_audio="/static/audio/lluvia.mp3", 
                puntos_requeridos=0
            ),
            Audio(
                titulo="Ondas Alpha 432Hz", 
                tipo_sonido="Binaural", 
                categoria="Estudio Profundo", 
                duracion="45:00", 
                url_audio="/static/audio/lluvia.mp3", 
                puntos_requeridos=100
            ),
            Audio(
                titulo="Cafetería de Fondo", 
                tipo_sonido="Sonido Neutro", 
                categoria="Lectura", 
                duracion="60:00", 
                url_audio="/static/audio/lluvia.mp3", 
                puntos_requeridos=50
            )
        ]

        session.add_all(audios_iniciales)
        session.commit()
        print("Base de datos poblada con éxito.")

if __name__ == "__main__":
    poblar_base_de_datos()