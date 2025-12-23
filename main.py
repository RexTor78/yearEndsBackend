from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import os
from datetime import datetime

app = FastAPI()

# =========================
# CORS (MUY IMPORTANTE)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # luego se puede restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# CONFIGURACIÓN
# =========================
UPLOAD_DIR = "uploads"
PRODUCTS_DIR = "products"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PRODUCTS_DIR, exist_ok=True)

# =========================
# DATOS SIMULADOS (FASE 1)
# =========================
families = {
    "Ingrid": {
        "needs_products": False,
        "special_message": None
    },
    "Alexandra": {
        "needs_products": False,
        "special_message": (
            "Se ha detectado un miembro de nacionalidad dudosa. "
            "El acceso está autorizado, pero nuestra seguridad permanecerá alerta. "
            "Por favor, compórtense debidamente."
        )
    },
    "Ona": {
        "needs_products": True,
        "products": ["vino", "uvas", "turrón"],
        "strict": True  # fallará la primera foto
    },
    "Aitana": {
        "needs_products": True,
        "products": ["cerveza", "patatas"],
        "strict": False
    }
}

# Guardamos estados simples en memoria
family_state = {}

# =========================
# UTILIDADES
# =========================
def fake_family_recognition():
    """
    Simula reconocimiento de familia.
    En el futuro aquí irá la IA real.
    """
    import random
    return random.choice(list(families.keys()))


# =========================
# ENDPOINT: SELFIE FAMILIA
# =========================
@app.post("/upload")
async def upload_selfie(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.jpg")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    family = fake_family_recognition()

    # Inicializamos estado
    family_state[family] = {
        "product_attempts": 0
    }

    response = {
        "family": family,
        "needs_products": families[family]["needs_products"],
        "required_products": families[family].get("products", []),
        "special_message": families[family]["special_message"],
        "message": f"Familia {family} reconocida correctamente."
    }

    return JSONResponse(response)


# =========================
# ENDPOINT: FOTO PRODUCTOS
# =========================
@app.post("/upload-products/{family_name}")
async def upload_products(family_name: str, file: UploadFile = File(...)):
    if family_name not in families:
        return JSONResponse(
            {"message": "Familia no reconocida."},
            status_code=400
        )

    file_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(
        PRODUCTS_DIR,
        f"{family_name}_{timestamp}_{file_id}.jpg"
    )

    with open(file_path, "wb") as f:
        f.write(await file.read())

    family_state[family_name]["product_attempts"] += 1
    attempts = family_state[family_name]["product_attempts"]

    # Caso estricto: falla la primera vez
    if families[family_name]["strict"] and attempts == 1:
        return JSONResponse({
            "confirmed": False,
            "message": (
                "No se detectan todos los productos indicados. "
                "Por favor, repitan la foto de los productos."
            )
        })

    # Segunda vez o familia no estricta → acceso
    return JSONResponse({
        "confirmed": True,
        "message": (
            "Productos validados correctamente. "
            "El administrador autoriza el acceso. "
            "Bienvenidos a la villa."
        )
    })


# =========================
# ENDPOINT SALUD
# =========================
@app.get("/")
def health():
    return {"status": "Backend operativo"}
