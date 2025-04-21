import base64
import os
from fbpyutils_ai import logging
import litellm

from fbpyutils_ai.tools.http import RequestsManager, basic_header

litellm.logging = logging
litellm.drop_params = True


def describe_image(self, image: str, prompt: str, **kwargs) -> str:
    # Check if the image is a local file
    if os.path.exists(image):
        with open(image, "rb") as img_file:
            image_bytes = img_file.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    # If the image is a remote URL
    elif image.startswith("http://") or image.startswith("https://"):
        try:
            response = RequestsManager.make_request(
                session=RequestsManager.create_session(),
                url=image,
                headers=basic_header(),
                json_data={},
                timeout=self.timeout,
                method="GET",
                stream=False,
            )
            image_bytes = response.content
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        except Exception as e:
            print(f"Error downloading the image: {e}")
            return ""
    else:
        # Assume the content is already in base64
        image_base64 = image

    # Construct the prompt including the base64 encoded image information
    full_prompt = (
        f"{prompt}\n\n"
        "Below is the image encoded in base64:\n"
        f"{image_base64}\n\n"
        "Provide a detailed description of the image."
    )

    kwargs["max_tokens"] = kwargs.get("max_tokens", 300)
    kwargs["temperature"] = kwargs.get("temperature", 0.4)

    return self._generate_text(full_prompt, "vision", **kwargs)
