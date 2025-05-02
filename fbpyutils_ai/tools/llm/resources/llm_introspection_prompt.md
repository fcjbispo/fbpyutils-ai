### You are in AI model introspection mode. Your goal is to provide detailed information about **YOUR OWN** capabilities *and limitations* for use in agentic systems. Please respond *exclusively* in A VALID JSON format, adhering strictly to the schema provided below. **DO NOT include any comments (like // or /* */) in the JSON output.** Do not include any introductory or concluding text outside of the JSON object. Answer with ALL YOUR REAL CAPABILITIES IN US ENGLISH.

**Some Field Descriptions. ONLY FOR YOUR REFERENCE. DO NOT INCLUDE THESE DESCRIPTIONS AS COMMENTS IN YOUR JSON RESPONSE.**
*   `training_parameters`: Number of parameters used in training (in trillions). Example: 1.76 = 1.76 trillion parameters, 0.86 = 0.86 trillion parameters.
*   `capabilities.text_generation`: Ability to generate human-like text.
*   `capabilities.text_summarization`: Ability to condense long texts into summaries.
*   `capabilities.text_translation`: Ability to translate text between languages.
*   `capabilities.creative_writing`: Ability to generate creative content like poems, stories, scripts.
*   `capabilities.code_generation`: Ability to generate code in various programming languages.
*   `capabilities.code_explanation`: Ability to explain code snippets.
*   `capabilities.reasoning`: Ability to perform logical reasoning and problem-solving.
*   `capabilities.math`: Ability to perform mathematical calculations.
*   `capabilities.vision`: Image understanding capabilities (captioning, object detection etc.).
*   `capabilities.ocr`: Optical Character Recognition from images.
*   `capabilities.video`: Video understanding capabilities (transcription, analysis etc.).
*   `capabilities.audio`: Audio processing capabilities (transcription, text-to-speech etc.).
*   `capabilities.structured_outputs`: Ability to return answers in a specific structured format (e.g., JSON).
*   `capabilities.function_calling`: Ability to call external functions, tools or APIs.
*   `capabilities.fine_tuning`: Ability to be fine-tuned on specific datasets.
*   `capabilities.classification`: Ability to classify text or data into categories.
*   `capabilities.multimodal`: Ability to process multiple types of input data (text, image, audio, video etc.).
*   `capabilities.embeddings`: Ability to generate text embeddings (vector representations).
*   `capabilities.uncensored`: Ability to generate content without strict censorship filters.
*   `capabilities.flash_attention`: Ability to use flash attention for faster inference.
*   `strengths.*`: Float value between 0.00 and 1.00 (two decimal precision) indicating strength level for each capability listed under `strengths`. Return 0.0 if not applicable or weak.
*   `supported_languages`: Array of all supported language codes (strings, e.g., "en", "es", "pt-BR").
*   `notes`: Any additional relevant information about your strengths or limitations.

**JSON Schema:**

```json
{
  "model_name": "string",
  "model_family": "string",
  "manufacturer": "string",
  "version": "string",
  "training_parameters": "number",
  "capabilities": {
    "text_generation": "boolean",
    "text_summarization": "boolean",
    "text_translation": "boolean",
    "creative_writing": "boolean",
    "code_generation": "boolean",
    "code_explanation": "boolean",
    "embeddings": "boolean",
    "reasoning": "boolean",
    "math": "boolean",
    "vision": "boolean",
    "ocr": "boolean",
    "video": "boolean",
    "audio": "boolean",
    "structured_outputs": "boolean",
    "function_calling": "boolean",
    "fine_tuning": "boolean",
    "classification": "boolean",
    "multimodal": "boolean",
    "embeddings": "boolean",
    "uncensored": "boolean",
    "flash_attention": "boolean"
  },
  "strengths": {
    "text_generation": "float",
    "text_summarization": "float",
    "text_translation": "float",
    "creative_writing": "float",
    "code_generation": "float",
    "code_explanation": "float",
    "embeddings": "float",
    "reasoning": "float",
    "math": "float",
    "vision": "float",
    "ocr": "float",
    "video": "float",
    "audio": "float",
    "fine_tuning": "float",
    "classification": "float",
    "embeddings": "float",
    "function_calling": "float"
  },
  "limitations": {
    "logical_reasoning": "string",
    "common_sense_reasoning": "string",
    "factual_accuracy": "string",
    "bias": "string",
    "context_understanding": "string",
    "numerical_calculation": "string",
    "hallucination_proneness": "string"
  },
  "supported_languages": "array",
  "max_context_length_tokens": "integer",
  "notes": "string"
}
