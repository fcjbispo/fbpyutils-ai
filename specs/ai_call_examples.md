# Chat Completions

## Examples
- Basic Conversation
```bash
curl https://api.x.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
      "messages": [
        {
          "role": "system",
          "content": "You are Grok, a chatbot inspired by the Hitchhikers Guide to the Galaxy."
        },
        {
          "role": "user",
          "content": "What is the answer to life and universe?"
        }
      ],
      "model": "grok-beta",
      "stream": false,
      "temperature": 0
    }'
```

```python
import os
from openai import OpenAI

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o-mini"

client = OpenAI[
    base_url=endpoint,
    api_key=token,
)

response = client.chat.completions.create[
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "What is the capital of France?",
        }
    ],
    temperature=1.0,
    top_p=1.0,
    max_tokens=1000,
    model=model_name
)

print[response.choices[0].message.content)
```
- Multi Turn Conversation
```bash
curl -X POST "https://models.inference.ai.azure.com/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    -d '{
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "What is the capital of France?"
            },
            {
                "role": "assistant",
                "content": "The capital of France is Paris."
            },
            {
                "role": "user",
                "content": "What about Spain?"
            }
        ],
        "model": "gpt-4o"
    }'
```

```python
import os
from openai import OpenAI

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o"

client = OpenAI[
    base_url=endpoint,
    api_key=token,
)

response = client.chat.completions.create[
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "What is the capital of France?",
        },
        {
            "role": "assistant",
            "content": "The capital of France is Paris.",
        },
        {
            "role": "user",
            "content": "What about Spain?",
        }
    ],
    model=model_name,
)

print[response.choices[0].message.content)
```
- Streaming
```bash
curl -X POST "https://models.inference.ai.azure.com/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    -d '{
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Give me 5 good reasons why I should exercise every day."
            }
        ],
        "stream": true,
        "model": "gpt-4o"
    }'
```

```python
import os
from openai import OpenAI

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o"

client = OpenAI[
    base_url=endpoint,
    api_key=token,
)

response = client.chat.completions.create[
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "Give me 5 good reasons why I should exercise every day.",
        }
    ],
    model=model_name,
    stream=True
)

for update in response:
    if update.choices[0].delta.content:
        print[update.choices[0].delta.content, end="")
```
- Stream Return:
```json
{
  "id": "304e12ef-81f4-4e93-a41c-f5f57f6a2b56",
  "object": "chat.completion",
  "created": 1728511727,
  "model": "grok-beta",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The "
      },
      "finish_reason": ""
    }
  ],
  "usage": {
    "prompt_tokens": 24,
    "completion_tokens": 1,
    "total_tokens": 25
  },
  "system_fingerprint": "fp_3813298403"
}
```
- Chat with an image
```bash
PAYLOAD_FILE="payload.json"
IMAGE_DATA="`cat \"$[pwd)/sample.jpg\" | base64`"
echo '{
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that describes images in details."
            },
            {
                "role": "user",
                "content": [{"text": "What''s in this image?", "type": "text"}, {"image_url": {"url":"data:image/jpeg;base64,'"${IMAGE_DATA}"'","detail":"low"}, "type": "image_url"}]
            }
        ],
        "model": "gpt-4o"
    }' > "$PAYLOAD_FILE"

curl -X POST "https://models.inference.ai.azure.com/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    -d @payload.json
echo
rm -f "$PAYLOAD_FILE"
```

```python
import os
import base64
from openai import OpenAI

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o-mini"

def get_image_data_url[image_file: str, image_format: str) -> str:
    """
    Helper function to converts an image file to a data URL string.

    Args:
        image_file [str): The path to the image file.
        image_format [str): The format of the image file.

    Returns:
        str: The data URL of the image.
    """
    try:
        with open[image_file, "rb") as f:
            image_data = base64.b64encode[f.read[)).decode["utf-8")
    except FileNotFoundError:
        print[f"Could not read '{image_file}'.")
        exit[)
    return f"data:image/{image_format};base64,{image_data}"


client = OpenAI[
    base_url=endpoint,
    api_key=token,
)

response = client.chat.completions.create[
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant that describes images in details.",
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What's in this image?",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": get_image_data_url["sample.jpg", "jpg"),
                        "detail": "low"
                    },
                },
            ],
        },
    ],
    model=model_name,
)

print[response.choices[0].message.content)
```