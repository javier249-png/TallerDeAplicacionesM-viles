#!/bin/sh
set -e

echo "=== [1/3] Iniciando el script de entrada de la API ==="

# 1. Esperar a que la Base de Datos esté lista (evita fallos al arrancar el contenedor)
echo "Esperando a que la base de datos MySQL acepte conexiones..."
python -c "
import time, os
from sqlalchemy import create_engine

url = os.getenv('DATABASE_URL')
if url:
    retries = 30
    while retries > 0:
        try:
            engine = create_engine(url)
            with engine.connect() as conn:
                print('✓ Conexión exitosa a MySQL.')
                break
        except Exception:
            retries -= 1
            print(f'Esperando a MySQL... reintentos restantes: {retries}')
            time.sleep(2)
"

# 2. Ejecutar las migraciones pendientes con Alembic
echo "=== [2/3] Ejecutando migraciones de Alembic ==="
python -m alembic upgrade head
echo "✓ Migraciones aplicadas correctamente."

# 3. Iniciar Uvicorn (reemplaza el proceso del script para ser el PID 1 del contenedor)
echo "=== [3/3] Iniciando el servidor Uvicorn en el puerto 9000 ==="
exec uvicorn app.main:app --host 0.0.0.0 --port 9000 --workers 4