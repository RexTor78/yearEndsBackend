from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cloudinary
import cloudinary.uploader
import os

app = FastAPI()

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yearends.netlify.app/"],  # luego restringimos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Cloudinary config (ENV)
# =========================
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
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
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Archivo no válido")

    try:
        result = cloudinary.uploader.upload(
            file.file,
            folder="villa-uploads/selfies",
            resource_type="image"
        )

        url = result.get("secure_url")
        if not url:
            raise Exception("No se pudo obtener la URL")

        # 🔮 Simulación IA ORDENADA
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

        return {
            "url": url,
            "predictions": predictions
        }

    except Exception as e:
        print("ERROR UPLOAD:", e)
        raise HTTPException(
            status_code=500,
            detail="Error procesando la imagen"
        )
