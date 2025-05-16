import os
import pytest
from dotenv import load_dotenv

from fbpyutils_ai.tools import LLMServiceModel
from fbpyutils_ai.tools.llm import OpenAILLMService
from fbpyutils_ai.tools.llm.utils import get_llm_resources

_ = load_dotenv()

(
    LLM_PROVIDERS,
    LLM_COMMON_PARAMS,
    LLM_INTROSPECTION_PROMPT,
    LLM_INTROSPECTION_VALIDATION_SCHEMA,
) = get_llm_resources()

models_config = (
    ("lmstudio", "http://127.0.0.1:1234/v1", "NeedsNoKey", True, "marco-o1"),
    ("lmstudio", "http://127.0.0.1:1234/v1", "NeedsNoKey", True, "gemma-3-1b-it-qat"),
    ("lmstudio", "http://127.0.0.1:1234/v1", "NeedsNoKey", True, "gemma-3-4b-it-qat"),
    ("ollama", "http://127.0.0.1:11434/v1", "NeedsNoKey", True, "gemma3:latest"),
    ("ollama", "http://127.0.0.1:11434/v1", "NeedsNoKey", True, "qwen2.5:3b"),
    ("ollama", "http://127.0.0.1:11434/v1", "NeedsNoKey", True, "nomic-embed-text:latest"),
    ("lmstudio", "http://127.0.0.1:1234/v1", "NeedsNoKey", True, "gemma-3-12b-it-qat"),
)

@pytest.fixture(scope="module")
def llm_service():
    _model = lambda x: LLMServiceModel(
        provider=x[0],
        api_base_url=x[1],
        api_key=x[2],
        is_local=x[3],
        model_id=x[4],
    )

    llm = OpenAILLMService(
        base_model=_model(models_config[1]),
        vision_model=_model(models_config[2]),
        embed_model=_model(models_config[5]),
        timeout=120000,
        retries=5,
    )
    return llm

def test_list_models(llm_service):
    models_list = OpenAILLMService.list_models(
        llm_service.model_map['base'].api_base_url,
        llm_service.model_map['base'].api_key,
    )
    assert all([isinstance(m, dict) for m in models_list])

def test_get_providers():
    providers = OpenAILLMService.get_providers()
    assert isinstance(providers, dict)

def test_model_map_initialization(llm_service):
    assert isinstance(llm_service.model_map, dict) and len(llm_service.model_map) == 3

def test_generate_embeddings(llm_service):
    embeddings = llm_service.generate_embeddings(["Olá, mundo!", "Ok, tchau!"])
    assert all([isinstance(f, float) for f in embeddings])

def test_generate_text(llm_service):
    question = "Qual a raiz quadrada de 0.56?"
    response = llm_service.generate_text(question)
    assert response is not None

def test_generate_completions(llm_service):
    question = "Qual a raiz quadrada de 0.56?"
    # Need to call generate_text first to get a response for the messages list
    response = llm_service.generate_text(question)
    response2 = llm_service.generate_completions(
        messages=[
            {"role": "system", "content": "Você é um assistente especializado em matemática."},
            {"role": "user", "content": question},
            {"role": "assistant", "content": response},
            {"role": "user", "content": "E esse valor multiplicado pela raiz quadrada de 3?"},
        ],
        stream=False,
        timeout=120000,
        top_p=1,
        temperature=0.0,
    )
    assert response2 is not None

def test_describe_image(llm_service):
    image = r"tests_integration\gato.jpg"
    # Check if the image file exists before attempting to describe it
    if not os.path.exists(image):
        pytest.skip(f"Image file not found at {image}")
    response3 = llm_service.describe_image(
        image,
        "Descreva esta imagem em detalhes em português brasileiro."
    )
    assert response3 is not None

def test_generate_tokens(llm_service):
    tokens = llm_service.generate_tokens("Olá, mundo!")
    assert all([isinstance(t, int) for t in tokens])

def test_get_model_details_no_introspection(llm_service):
    response4 = llm_service.get_model_details(model_type="base", introspection=False)
    assert isinstance(response4, dict) and len(response4) > 0

def test_get_model_details_with_introspection(llm_service):
    response5 = llm_service.get_model_details(model_type="base", introspection=True)
    assert isinstance(response5, dict) and len(response5) > 0
