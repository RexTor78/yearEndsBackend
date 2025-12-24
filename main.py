from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import cloudinary
import cloudinary.uploader
import random

app = FastAPI()

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción puedes restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Cloudinary config
# =========================
cloudinary.config(
    cloud_name="dsuh8ytfw",
    api_key="355974142769758",
    api_secret="Or-pP5Q-OiF1_aUiw4Fvr7vLs10"
)

# =========================
# Root
# =========================
@app.get("/")
async def root():
    return {"status": "Backend operativo"}

# =========================
# Upload selfie
# =========================
@app.post("/upload")
async def upload_selfie(file: UploadFile = File(...)):
    try:
        # Subir imagen
        result = cloudinary.uploader.upload(
            file.file,
            folder="villa-uploads/selfies"
        )

        url = result["secure_url"]

        # Simulación IA (orden de confianza)
        predictions = [
            {
                "family": "Ingrid",
                "confidence": 0.82,
                "needs_products": True,
                "special_message": ""
            },
            {
                "family": "Alexandra",
                "confidence": 0.61,
                "needs_products": True,
                "special_message": "Se ha detectado un miembro de nacionalidad dudosa."
            },
            {
                "family": "Ona",
                "confidence": 0.34,
                "needs_products": False,
                "special_message": ""
            },
            {
                "family": "Aitana",
                "confidence": 0.22,
                "needs_products": False,
                "special_message": ""
            }
        ]

        # Barajamos para simular variación
        random.shuffle(predictions)

        return {
            "predictions": predictions,
            "url": url
        }

    except Exception as e:
        return {
            "error": True,
            "message": str(e)
        }
