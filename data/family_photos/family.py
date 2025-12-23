from fastapi.responses import FileResponse
from fastapi import HTTPException
import glob

@app.get("/family_photos/{family}")
async def get_family_photos(family: str):
    folder = "uploaded_photos"  # Carpeta donde se guardan todas las fotos
    files = glob.glob(f"{folder}/{family}_*.jpg")
    if not files:
        raise HTTPException(status_code=404, detail="No se encontraron fotos para esta familia")
    # Devolver lista de URLs relativas para frontend
    photo_urls = [f"/photos/{f.split('/')[-1]}" for f in files]
    return {"family": family, "photos": photo_urls}

# Endpoint para servir fotos
from fastapi.staticfiles import StaticFiles
app.mount("/photos", StaticFiles(directory="uploaded_photos"), name="photos")
