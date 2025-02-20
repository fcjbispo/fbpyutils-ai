# mytools/janus/model.py
from transformers import pipeline

def load_text_to_image_pipeline():
    """
    Carrega o pipeline para geração de imagens a partir de texto usando o modelo Janus-Pro-7B.
    """
    return pipeline("text-to-image", model="deepseek-ai/Janus-Pro-7B")

def load_image_to_text_pipeline():
    """
    Carrega o pipeline para extração de informações de imagens usando o modelo Janus-Pro-7B.
    """
    return pipeline("image-to-text", model="deepseek-ai/Janus-Pro-7B")
