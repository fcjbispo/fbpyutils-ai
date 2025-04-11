# FBPyUtils-AI Development Guidelines

## Build/Test/Lint Commands

```bash
# Install dependencies
make install

# Build project
make build

# Run all tests
.venv/Scripts/python -m dotenv run pytest -s -vv

# Run a specific test file
.venv/Scripts/python -m dotenv run pytest tests/tools/test_llm.py -v

# Run a specific test function
.venv/Scripts/python -m dotenv run pytest tests/tools/test_llm.py::test_list_models_base -v

# Clean build artifacts
make clean
```

## Code Style Guidelines

1. **Imports**: Standard library first, then third-party, then local imports. Group imports by type and alphabetize within groups.

2. **Type Annotations**: Use Python type hints for all function parameters and return values.

3. **Documentation**: Write docstrings for all classes and methods with descriptions, args, returns, and examples.

4. **Error Handling**: Use try/except blocks with specific exceptions. Log errors appropriately.

5. **Logging**: Use the logging module for all logging needs. Set the logging level to DEBUG for development and INFO for production.
   - Use the `logging` object from `fbpyutils_ai` module for logging.
   - Always write relevant logs for each function or process at relevant points in order to clarify the flow of the code and help with debugging.

6. **Naming Conventions**:
   - Classes: PascalCase
   - Functions/Methods: snake_case
   - Variables: snake_case
   - Constants: UPPER_SNAKE_CASE

7. **Abstract Interfaces**: Implement abstract interfaces for key functionalities (LLMService, VectorDatabase).

8. **Language**: English for logs, documentation, and code.
   - If some comments or docstrings still in Portuguese, rewrite them in English with the same meaning. For example, if a comment says "Retorna uma lista de modelos", rewrite it as "Returns a list of models". 
