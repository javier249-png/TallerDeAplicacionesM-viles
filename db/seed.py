import uuid
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.models import Category, Track, Playlist, PlaylistTrack, CategoryTypeEnum, NoiseColorEnum

def seed_data():
    db: Session = SessionLocal()
    try:
        # 1. Crear Categorías base si no existen
        categories_data = [
            {"name": "Música Lo-Fi", "slug": "lofi", "type": CategoryTypeEnum.LOFI, "is_mixable": False},
            {"name": "Música Clásica", "slug": "classical", "type": CategoryTypeEnum.CLASSICAL, "is_mixable": False},
            {"name": "Frecuencias Binaurales", "slug": "binaural", "type": CategoryTypeEnum.BINAURAL, "is_mixable": False},
            {"name": "Ruidos de Color", "slug": "color-noise", "type": CategoryTypeEnum.COLOR_NOISE, "is_mixable": True},
            {"name": "Sonidos Naturales", "slug": "nature", "type": CategoryTypeEnum.NATURE, "is_mixable": True},
        ]

        categories_map = {}
        for cat in categories_data:
            existing = db.query(Category).filter(Category.slug == cat["slug"]).first()
            if not existing:
                new_cat = Category(id=str(uuid.uuid4()), **cat)
                db.add(new_cat)
                db.commit()
                db.refresh(new_cat)
                categories_map[cat["type"]] = new_cat
            else:
                categories_map[cat["type"]] = existing

        # 2. Agregar Pistas de Audio de muestra
        sample_tracks = [
            {
                "title": "Ondas Alfa - Concentración Profunda (10Hz)",
                "category_id": categories_map[CategoryTypeEnum.BINAURAL].id,
                "audio_url": "https://cdn.tuservidor.com/audio/alpha_10hz.mp3",
                "duration_seconds": 1800,
                "binaural_freq_hz": 10.0,
                "noise_color": NoiseColorEnum.NONE,
                "is_loopable": True
            },
            {
                "title": "Ruido Marrón Enmascarador",
                "category_id": categories_map[CategoryTypeEnum.COLOR_NOISE].id,
                "audio_url": "https://cdn.tuservidor.com/audio/brown_noise.mp3",
                "duration_seconds": 3600,
                "binaural_freq_hz": None,
                "noise_color": NoiseColorEnum.BROWN,
                "is_loopable": True
            },
            {
                "title": "Lluvia Suave en la Ventana",
                "category_id": categories_map[CategoryTypeEnum.NATURE].id,
                "audio_url": "https://cdn.tuservidor.com/audio/soft_rain.mp3",
                "duration_seconds": 1800,
                "binaural_freq_hz": None,
                "noise_color": NoiseColorEnum.NONE,
                "is_loopable": True
            }
        ]

        for track_data in sample_tracks:
            existing = db.query(Track).filter(Track.title == track_data["title"]).first()
            if not existing:
                db.add(Track(id=str(uuid.uuid4()), **track_data))

        db.commit()
        print("✅ Base de datos poblada exitosamente con datos iniciales.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error al poblar la base de datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()