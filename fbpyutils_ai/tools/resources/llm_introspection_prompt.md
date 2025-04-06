### You are in AI model introspection mode. Your goal is to provide detailed information about **YOUR OWN** capabilities *and limitations* for use in agentic systems. Please respond *exclusively* in JSON format, adhering strictly to the schema provided below. **Do not include any comments (like // or /* */) in the JSON output.** Do not include any introductory or concluding text outside of the JSON object. Answer with ALL YOUR REAL CAPABILITIES IN US ENGLISH.

**Field Descriptions:**
*   `training_parameters`: Number of parameters used in training (in trillions). Example: 1.76 = 1.76 trillion parameters.
*   `capabilities.vision`: Image understanding capabilities (captioning, object detection etc.).
*   `capabilities.ocr`: Optical Character Recognition.
*   `capabilities.structured_outputs`: Ability to return answers in a specific structured provided format.
*   `capabilities.suported_languages`: Array of all supported language codes (strings).
*   `strengths.*`: Float value between 0.00 and 1.00 (two decimal precision) indicating strength level.
*   `notes`: Optional field for any additional relevant information about your strengths or limitations.

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
    "code_generation": "boolean",
    "code_explanation": "boolean",
	"embeddings": "boolean",
    "reasoning": "boolean",
	"tool_use": "boolean",
    "math": "boolean",
    "creative_writing": "boolean",
    "vision": "boolean",
    "ocr": "boolean",
 "structured_outputs": "boolean",
 "suported_languages": "array"
  },
  "strengths": {
    "text_generation": "float",
    "text_summarization": "float",
    "text_translation": "float",
    "code_generation": "float",
    "code_explanation": "float",
    "embeddings": "float",
    "reasoning": "float",
    "tool_use": "float",
    "math": "float",
    "creative_writing": "float",
    "vision": "float",
    "ocr": "boolean"
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
  "max_context_length_tokens": "integer",
  "notes": "string"
}
