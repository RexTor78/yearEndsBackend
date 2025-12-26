from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cloudinary
import cloudinary.uploader
import os
import json
from io import BytesIO
from PIL import Image
from facenet_pytorch import InceptionResnetV1, MTCNN
import torch

app = FastAPI()

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajustar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Cloudinary config
# =========================
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

# =========================
# Cargar familias JSON
# =========================
with open("families.json", "r", encoding="utf-8") as f:
    families_data = json.load(f)["families"]

# =========================
# Modelos de reconocimiento facial
# =========================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
mtcnn = MTCNN(keep_all=True, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

# Preprocesar embeddings de cada miembro
family_embeddings = {}

for family in families_data:
    embeddings = []
    for member in family["members"]:
        try:
            img = Image.open(member["photo"]).convert("RGB")
            face = mtcnn(img)
            if face is not None:
                embedding = resnet(face.unsqueeze(0).to(device))
                embeddings.append({
                    "name": member["name"],
                    "embedding": embedding,
                    "sospechoso": member.get("sospechoso", False),
                    "sospechoso_message": member.get("sospechoso_message", "")
                })
        except Exception as e:
            print(f"Error cargando imagen {member['photo']}: {e}")
    family_embeddings[family["id"]] = {
        "display_name": family["display_name"],
        "special_message": family.get("special_message", ""),
        "members": embeddings
    }

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
        # Subir imagen a Cloudinary
        result = cloudinary.uploader.upload(file.file, folder="villa-uploads/selfies", resource_type="image")
        url = result.get("secure_url")
        if not url:
            raise Exception("No se pudo obtener la URL")

        # =========================
        # Reconocimiento facial
        # =========================
        uploaded_image = Image.open(BytesIO(await file.read())).convert("RGB")
        faces = mtcnn(uploaded_image)
        if faces is None:
            return {"url": url, "predictions": []}

        uploaded_embeddings = resnet(faces.unsqueeze(0).to(device))

        # Comparar con cada familia
        predictions = []
        for family_id, family in family_embeddings.items():
            for member in family["members"]:
                dist = (uploaded_embeddings - member["embedding"]).norm().item()
                if dist < 0.9:  # umbral, ajustar según pruebas
                    predictions.append({
                        "id": family_id,
                        "family": family["display_name"],
                        "confidence": round(1 - dist, 2),
                        "needs_products": True,
                        "special_message": family["special_message"],
                        "sospechoso_member": member["name"] if member["sospechoso"] else None,
                        "sospechoso_message": member.get("sospechoso_message", "")
                    })
                    break  # con detectar 1 miembro basta

        # Ordenar por confianza
        predictions = sorted(predictions, key=lambda x: x["confidence"], reverse=True)

        return {
            "url": url,
            "predictions": predictions
        }

    except Exception as e:
        print("ERROR UPLOAD:", e)
        raise HTTPException(status_code=500, detail="Error procesando la imagen")
