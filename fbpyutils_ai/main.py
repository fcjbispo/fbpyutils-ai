# mytools/main.py
import io
import base64
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from PIL import Image

# Importa os métodos de carregamento dos pipelines do serviço Janus
from mytools.janus.model import load_text_to_image_pipeline, load_image_to_text_pipeline

app = FastAPI(
    title="MyTools API Service",
    description="Serviço API para os serviços de imagem do modelo Janus-Pro-7B",
    version="0.1.0"
)

# Variáveis globais para os pipelines do modelo Janus
text_to_image_pipeline = None
image_to_text_pipeline = None

class TextPrompt(BaseModel):
    prompt: str

@app.on_event("startup")
async def startup_event():
    global text_to_image_pipeline, image_to_text_pipeline
    try:
        text_to_image_pipeline = load_text_to_image_pipeline()
        image_to_text_pipeline = load_image_to_text_pipeline()
    except Exception as e:
        raise RuntimeError("Falha ao carregar os pipelines do modelo Janus.") from e

@app.post("/janus/generate-image")
async def generate_image(prompt: TextPrompt):
    """
    Endpoint para gerar uma imagem a partir de um prompt de texto usando o modelo Janus.
    """
    if not text_to_image_pipeline:
        raise HTTPException(status_code=500, detail="Pipeline do modelo não carregado.")
    try:
        output = text_to_image_pipeline(prompt.prompt)
        if not output or not isinstance(output, list):
            raise HTTPException(status_code=500, detail="Pipeline não retornou um resultado válido.")
        # Ajusta a extração conforme o formato retornado pelo pipeline
        image = output[0] if isinstance(output[0], Image.Image) else output[0].get("image")
        if image is None:
            raise HTTPException(status_code=500, detail="Nenhuma imagem foi gerada.")
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return {"image_base64": img_str}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/janus/read-image")
async def read_image(file: UploadFile = File(...)):
    """
    Endpoint para extrair informações de uma imagem usando o modelo Janus.
    """
    if not image_to_text_pipeline:
        raise HTTPException(status_code=500, detail="Pipeline do modelo não carregado.")
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        result = image_to_text_pipeline(image)
        if isinstance(result, list) and result:
            result_text = result[0] if isinstance(result[0], str) else result[0].get("generated_text", "")
        else:
            result_text = str(result)
        return {"text": result_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
