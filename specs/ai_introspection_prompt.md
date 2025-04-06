### You are in AI model introspection mode. Your goal is to provide detailed information about **YOUR OWN** capabilities *and limitations* for use in agentic systems. Please respond *exclusively* in JSON format, adhering strictly to the schema provided below. Do not include any introductory or concluding text outside of the JSON object. Answer with ALL YOUR REAL CAPABILITIES IN US ENGLISH.

**JSON Schema:**

```json
{
  "model_name": "string",
  "model_family": "string",
  "manufacturer": "string",
  "version": "string",
  "training_parameters": "number", //Number of parameters used in training (in trillions). Example: 1.76 = 1.76 trillion parameters
  "capabilities": {
    "text_generation": "boolean",
    "text_summarization": "boolean",
    "text_translation": "boolean",
    "code_generation": "boolean",
    "code_explanation": "boolean",
    "reasoning": "boolean",
	"tool_use": "boolean",
    "math": "boolean",
    "creative_writing": "boolean",
    "vision": "boolean",  //Image understanding capabilities (captioning, object detection etc.)
    "ocr": "boolean", //Optical Character Recognition
	"structured_outputs": "boolean", //Return answers in a specific structured provided format
	"suported_languages": "array" //All supported languages codes in a array of strings
  },
  "strengths": {
    "text_generation": "float", // 0..1 with two decimals precision 
    "text_summarization": "float", // 0..1 with two decimals precision 
    "text_translation": "float", // 0..1 with two decimals precision 
    "code_generation": "float", // 0..1 with two decimals precision 
    "code_explanation": "float", // 0..1 with two decimals precision 
    "reasoning": "float", // 0..1 with two decimals precision 
    "tool_use": "float", // 0..1 with two decimals precision 
    "math": "float", // 0..1 with two decimals precision 
    "creative_writing": "float", // 0..1 with two decimals precision 
    "vision": "float", // 0..1 with two decimals precision 
    "ocr": "boolean" // 0..1 with two decimals precision
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
  "notes": "string" //Optional: Any additional relevant information about your strengths or limitations.
}