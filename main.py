from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import cloudinary
import cloudinary.uploader

app = FastAPI()

# CORS para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://beautiful-ganache-c76dc4.netlify.app/"],  # Cambiar a dominio frontend en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Configuración Cloudinary
cloudinary.config(
    cloud_name="dsuh8ytfw",
    api_key="355974142769758",
    api_secret="Or-pP5Q-OiF1_aUiw4Fvr7vLs10"
)


# Datos de ejemplo de familias
families_db = ["Ingrid", "Alexandra", "Ona", "Aitana"]

# Endpoint de prueba raíz
@app.get("/")
async def root():
    return {"status": "Backend operativo"}

# Endpoint para subir selfie de la familia
@app.post("/upload")
async def upload_selfie(file: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(file.file, folder="villa-uploads/selfies")
        url = result.get("secure_url")

        # Aquí podrías hacer reconocimiento IA y devolver info
        # Para pruebas, elegimos familia aleatoria
        import random
        family = random.choice(families_db)
        special_message = ""
        needs_products = family in ["Ingrid", "Alexandra"]  # ejemplo
        message = f"Familia detectada: {family}"

        if family == "Alexandra":
            special_message = "Se ha detectado un miembro de nacionalidad dudosa, seguridad pendiente."

        return {
            "message": message,
            "family": family,
            "special_message": special_message,
            "needs_products": needs_products,
            "url": url
        }

    except Exception as e:
        return {"message": f"Error al subir la foto: {str(e)}"}

# Endpoint para subir foto de productos
@app.post("/upload-products")
async def upload_products(file: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(file.file, folder="villa-uploads/products")
        url = result.get("secure_url")
        # Aquí podrías validar productos, devolver estado
        message = "Foto de productos recibida y procesada."
        return {"message": message, "url": url}

    except Exception as e:
        return {"message": f"Error al subir la foto de productos: {str(e)}"}

# Endpoint para subir foto de celebración (uvas / fiesta)
@app.post("/upload-celebration")
async def upload_celebration(file: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(file.file, folder="villa-uploads/celebration")
        url = result.get("secure_url")
        message = "Foto de celebración recibida."
        return {"message": message, "url": url}

    except Exception as e:
        return {"message": f"Error al subir la foto de celebración: {str(e)}"}
