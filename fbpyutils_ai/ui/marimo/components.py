from fbpyutils_ai import logging
from typing import Dict, Any, Optional
import html  # Use html library for proper escaping


def _escape(value: Any) -> str:
    """Safely escape values for HTML display."""
    return html.escape(str(value))

def get_llm_models_cards(
    base_model: Optional[Dict[str, Any]],
    embed_model: Optional[Dict[str, Any]],
    vision_model: Optional[Dict[str, Any]],
    border_radius: int = 10
) -> str:
    """
    Generates an HTML string displaying LLM model configurations in side-by-side cards
    following specific layout rules.

    Args:
        base_model: Dictionary containing the base model configuration, or None.
        embed_model: Dictionary containing the embedding model configuration, or None.
        vision_model: Dictionary containing the vision model configuration, or None.
        border_radius: The border radius for the cards in pixels (default: 10).

    Returns:
        An HTML string representing the cards. Returns an empty string if all models are None.
    """
    logging.debug(f"Generating LLM model cards with border radius: {border_radius}px")

    models = {
        "Base Model": base_model,
        "Embedding Model": embed_model,
        "Vision Model": vision_model,
    }

    # Filter out models that are explicitly None, keep empty dicts for now to handle 'Undefined' provider
    active_models_data = {title: data for title, data in models.items() if data is not None}

    if not active_models_data:
        logging.warning("No model data provided (all models are None).")
        return "" # Return empty string if all models are None

    cards_html = ""
    # Ensure all three potential card slots are considered, even if data is None initially
    for title in models.keys():
        model_data = models.get(title) # Get data, could be None or a dict

        card_content_html = ""
        card_class = "llm-card" # Default class

        # Check if model_data is None, empty, or provider is "Undefined"
        if not model_data or model_data.get("provider") == "Undefined":
            card_class += " empty" # Add empty class
            # Use Material Icons ligature for the icon
            card_content_html = '<i class="material-icons llm-empty-icon">disabled_by_default</i>'
            logging.debug(f"Rendering empty card for '{title}'.")
        else:
            # Render the card with model details
            model_id = _escape(model_data.get("model_id", "N/A"))
            provider = _escape(model_data.get("provider", "N/A"))
            api_base_url = _escape(model_data.get("api_base_url", "N/A"))
            api_key = _escape(model_data.get("api_key", "N/A"))

            # Mask the API key partially for security/display purposes
            masked_api_key = api_key[:4] + '...' + api_key[-4:] if len(api_key) > 8 else api_key

            card_content_html = f"""
                <div class="llm-model-id">{model_id}</div>
                <hr class="llm-separator">
                <div class="llm-provider">{provider}</div>
                <div class="llm-api-details">
                    <div>URL: {api_base_url}</div>
                    <div>Key: {masked_api_key}</div>
                </div>
            """
            logging.debug(f"Rendering card for '{title}' with provider '{provider}'.")

        # Construct the full card HTML
        cards_html += f"""
        <div class="{card_class}">
            <div class="llm-card-header">{title}</div>
            <div class="llm-card-content">
                {card_content_html}
            </div>
        </div>
        """

    # Use inline style to set the CSS variable for border-radius
    container_html = f"""
    <div class="llm-cards-container" style="--card-border-radius: {border_radius}px;">
        {cards_html}
    </div>
    """
    logging.info("Successfully generated LLM model cards HTML with updated layout.")
    return container_html
