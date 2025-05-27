import marimo

__generated_with = "0.13.11"
app = marimo.App(
    width="medium",
    app_title="FBPyUtils for AI - Main UI",
    css_file="styles.css",
)


@app.cell
def _(mo):
    mo.sidebar(
        [
            mo.md("# FBPyUtils AI"),
            mo.nav_menu(
                {
                    "#home": f"{mo.icon('lucide:home')} Home",
                    "Tools": {
                        "#llm": f"{mo.icon('lucide:bot')} LLM",
                        "#search": f"{mo.icon('lucide:binoculars')} Search",
                        "#scrape": f"{mo.icon('lucide:cloud-cog')} Scrape"},
                    "Links": {
                        "https://github.com/fcjbispo/FBPyUtils-AI": f"{mo.icon('lucide:github')}GitHub",
                    },
                },
                orientation="vertical",
            ),
        ]
    )
    return


@app.cell
def _(firecrawl_tool_output, llm_tool_output, mo, searxng_tool_output):
    def render_home_page():
        return mo.md("""
        # Welcome to FBPyUtils-AI UI

        This application provides a user-friendly interface to interact with the powerful AI tools developed in the FBPyUtils-AI library. It serves as a demonstration and an interactive playground for various functionalities, including web search, web scraping, and large language model (LLM) interactions.

        ## Available Tools:

        - **LLM Tool**: Explore capabilities of Large Language Models, including text generation, embeddings, and image description.
            [Access LLM Tool](#llm)

        - **Search Tool**: Perform interactive web searches using the integrated SearXNG service.
            [Access Search Tool](#search)

        - **Scrape Tool**: Extract content from web pages using the Firecrawl API for efficient web scraping.
            [Access Scrape Tool](#scrape)

        ## Project Overview:

        FBPyUtils-AI is a Python library designed to offer a suite of AI utilities. Key features include:
        - **Web Search**: Generic and SearXNG-specific search functionalities.
        - **Web Scraping**: Data extraction from web pages using Firecrawl API.
        - **HTTP Requests**: Tools for making various HTTP requests.
        - **Document Conversion**: Wrapper for `docling` for format conversions.
        - **Vector Database & Embedding**: Tools for managing vector embeddings (ChromaDB, PgVectorDB, PineconeDB).
        - **OpenAI Compatible LLM**: Interface for OpenAI-compatible APIs for text, embeddings, and vision.

        For more detailed information, please refer to the project's [GitHub repository](https://github.com/fcjbispo/FBPyUtils-AI).
        """)

    def render_llm_service_page():
        return llm_tool_output

    def render_search_page():
        return searxng_tool_output

    def render_scrape_page():
        return firecrawl_tool_output
    return (
        render_home_page,
        render_llm_service_page,
        render_scrape_page,
        render_search_page,
    )


@app.cell
def _(
    mo,
    render_home_page,
    render_llm_service_page,
    render_scrape_page,
    render_search_page,
):
    mo.routes(
        {
            "#home": render_home_page,
            "#llm": render_llm_service_page,
            "#search": render_search_page,
            "#scrape": render_scrape_page,
            mo.routes.CATCH_ALL: render_home_page,
        }
    )
    return


@app.cell
def _():
    # LLM Tool
    return


@app.cell
def _(
    llm_app_sections,
    llm_model_cards,
    llm_model_request_retries,
    llm_model_request_timeout,
    llm_selected_base_model_ui,
    llm_selected_embed_model_ui,
    llm_selected_provider_ui,
    llm_selected_vision_model_ui,
    mo,
):
    llm_tool_output = mo.md(f"""
    #### Select..
    - {llm_selected_provider_ui}
    - {llm_selected_base_model_ui}
    - {llm_selected_embed_model_ui}
    - {llm_selected_vision_model_ui}
    #### Set..
    - {mo.hstack([llm_model_request_timeout, mo.md(f"Current value: {llm_model_request_timeout.value}")])}
    - {mo.hstack([llm_model_request_retries, mo.md(f"Current value: {llm_model_request_retries.value}")])}
    #### Selected Models
    ---
    {llm_model_cards}
    {llm_app_sections}
    """)
    return (llm_tool_output,)


@app.cell
def _(
    check_model_selection,
    llm_generate_completions_section,
    llm_generate_embeddings_section,
    llm_generate_text_section,
    llm_model_describe_image_section,
    llm_model_details_section,
    mo,
):
    if check_model_selection():
        llm_app_sections = mo.accordion(
            {
                "Generate Text": llm_generate_text_section,
                "Generate Embeddings": llm_generate_embeddings_section,
                "Generate Completions": llm_generate_completions_section,
                "Describe Image": llm_model_describe_image_section,
                "Model Details": llm_model_details_section,
            }
        )
    else:
        llm_app_sections = mo.md("")
    return (llm_app_sections,)


@app.cell
def _(
    get_llm_generate_completions_section,
    get_llm_generate_embeddings_section,
    get_llm_generate_text_section,
):
    llm_generate_text_section = get_llm_generate_text_section()
    llm_generate_embeddings_section = get_llm_generate_embeddings_section()
    llm_generate_completions_section = get_llm_generate_completions_section()
    return (
        llm_generate_completions_section,
        llm_generate_embeddings_section,
        llm_generate_text_section,
    )


@app.cell
def _(TextExtractor, llm, mo):
    def llm_completions_process_single_message(message):
        if isinstance(message.content, str):
            parser = TextExtractor()
            parser.feed(message.content)
            clean_text = parser.get_text()
        else:
            clean_text = ""

        return {
            "role": message.role,
            "content": clean_text,
            "attachments": message.attachments
        }

    def llm_completions(messages, config):
        params = config.__dict__.copy()
        llm_generate_completions_messages.append(
            llm_completions_process_single_message(messages[-1])
        )
        return llm.generate_completions(
            messages=llm_generate_completions_messages,
            stream=False,
            **params,
        )

    def simple_echo_model(messages, config):
        return f"You said: {messages[-1].content}"

    def get_llm_generate_completions_section():
        return mo.md(f"""{
            llm_generate_completions_ui
        }""")

    llm_generate_completions_messages = []

    llm_generate_completions_ui = mo.ui.chat(
        llm_completions,
        prompts=["Hello", "How are you?"],
        show_configuration_controls=True
    )
    return (get_llm_generate_completions_section,)


@app.cell
def _():
    ## Generate Text
    return


@app.cell
def _(mo):
    llm_generate_text_input = mo.ui.text_area(
        placeholder="Enter text to generate...",
        max_length=None,
        rows=5,
        label="Input Text:",
        full_width=True,
    )

    llm_generate_text_temperature = mo.ui.number(
        start=0.0, 
        stop=1, 
        step=0.1, 
        value=0.5,
        label="Temperature",
    )

    llm_generate_text_max_tokens = mo.ui.number(
        start=100, 
        stop=8192, 
        step=10, 
        value=1000,
        label="Max Tokens",
    )
    # top_p: controla a diversidade da saída
    llm_generate_text_top_p = mo.ui.number(
        start=0.0,
        stop=1.0,
        step=0.05,
        value=1.0,
        label="Top P",
    )

    # top_k: limita o número de tokens considerados
    llm_generate_text_top_k = mo.ui.number(
        start=0,
        stop=100,
        step=10,
        value=40,
        label="Top K",
    )

    # presence_penalty: penaliza ou incentiva a introdução de novos tópicos
    llm_generate_text_presence_penalty = mo.ui.number(
        start=-2.0,
        stop=2.0,
        step=0.1,
        value=0.0,
        label="Presence Penalty",
    )

    # frequency_penalty: penaliza ou incentiva a repetição de palavras
    llm_generate_text_frequency_penalty = mo.ui.number(
        start=-2.0,
        stop=2.0,
        step=0.1,
        value=0.0,
        label="Frequency Penalty",
    )

    return (
        llm_generate_text_frequency_penalty,
        llm_generate_text_input,
        llm_generate_text_max_tokens,
        llm_generate_text_presence_penalty,
        llm_generate_text_temperature,
        llm_generate_text_top_k,
        llm_generate_text_top_p,
    )


@app.cell
async def _(
    llm,
    llm_generate_text_frequency_penalty,
    llm_generate_text_input,
    llm_generate_text_max_tokens,
    llm_generate_text_presence_penalty,
    llm_generate_text_temperature,
    llm_generate_text_top_k,
    llm_generate_text_top_p,
    mo,
):
    async def get_llm_generate_text_async(
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 1.0,
        top_k: int = 40,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
    ):
        with mo.status.spinner(title="Generating text...") as _spinner:
            try:
                llm_generated_text = llm.generate_text(
                    prompt=prompt,
                    vision=False,
                    temperature=llm_generate_text_temperature.value,
                    max_tokens=llm_generate_text_max_tokens.value,
                    top_p=llm_generate_text_top_p.value,
                    top_k=llm_generate_text_top_k.value,
                    presence_penalty=llm_generate_text_presence_penalty.value,
                    frequency_penalty=llm_generate_text_frequency_penalty.value,
                )
                _spinner.update("Done!")
            except Exception as e:
                _spinner.update(f"Error: {e}")
                llm_generated_text = f"Error: {str(e)}"
        return llm_generated_text

    llm_generate_text_output = mo.plain_text(
        text=(await get_llm_generate_text_async(
            prompt=llm_generate_text_input.value,
        ) if llm_generate_text_input.value 
        else "")
    )

    def get_llm_generate_text_section():
        output = f"""
        {llm_generate_text_input}
        {
            mo.hstack([
                mo.md("Parameters:"),
                mo.vstack([
                    mo.hstack([llm_generate_text_temperature, llm_generate_text_max_tokens]),
                    mo.hstack([llm_generate_text_top_p, llm_generate_text_top_k]),
                    mo.hstack([llm_generate_text_presence_penalty, llm_generate_text_frequency_penalty]),
                ])
            ])
        }
        """
        if llm_generate_text_input.value:    ### Generated Text:
            output = f"""
            {output}
            Generated Text:
            {llm_generate_text_output}
            """
        return mo.md(output)
    return (get_llm_generate_text_section,)


@app.cell
def _():
    ## Generate Embeddings
    return


@app.cell
def _(mo):
    llm_generate_embeddings_input = mo.ui.text_area(
        placeholder="Enter text to generate embeddings for...",
        max_length=None,
        rows=5,
        label="Input Text:",
        full_width=True,
    )
    return (llm_generate_embeddings_input,)


@app.cell
async def _(llm, llm_generate_embeddings_input, mo):
    async def get_llm_generate_embeddings_async(
        prompt: str,
    ):
        with mo.status.spinner(title="Generating embeddings...") as _spinner:
            try:
                llm_embeddings = {
                    "Embeddings": llm.generate_embeddings(
                        input=prompt,
                    )
                }
                _spinner.update("Done!")
            except Exception as e:
                _spinner.update(f"Error: {e}")
                llm_embeddings = {"Error": str(e)}
        return llm_embeddings

    llm_generate_embeddings_output = mo.json(
        (await get_llm_generate_embeddings_async(
            prompt=llm_generate_embeddings_input.value,
        ) if llm_generate_embeddings_input.value 
        else {})
    )

    def get_llm_generate_embeddings_section():
        return mo.md(f"""
        {llm_generate_embeddings_input}
        Generated Embeddings:
        {llm_generate_embeddings_output}
        """)
    return get_llm_generate_embeddings_section, llm_generate_embeddings_output


@app.cell
def _(
    llm,
    llm_generate_embeddings_input,
    llm_generate_embeddings_output,
    mo,
    value,
):
    if llm_generate_embeddings_input.value:
        with mo.status.spinner(title="Generating embeddings...") as _spinner:
            try:
                generated_embeddings = llm.generate_embedding(
                    text=value,
                )
                llm_generate_embeddings_output.value = generated_embeddings
                _spinner.update("Done!")
            except Exception as e:
                _spinner.update(f"Error: {e}")
                llm_generate_embeddings_output.value = {"Error": str(e)}
    else:
        llm_generate_embeddings_output.value = {}
    return


@app.cell
def _(get_llm_model_describe_image_section):
    llm_model_describe_image_section = get_llm_model_describe_image_section()
    return (llm_model_describe_image_section,)


@app.cell
def _(
    llm_model_describe_image_description_ui,
    llm_model_describe_image_file_drag_and_drop_ui,
    llm_model_describe_image_image_ui,
    llm_model_describe_image_prompt_ui,
    mo,
):
    def get_llm_model_describe_image_section():
        return mo.md(
                f"""
                {
                    mo.vstack([
                        llm_model_describe_image_prompt_ui,
                        llm_model_describe_image_file_drag_and_drop_ui,
                        mo.hstack([
                            llm_model_describe_image_image_ui,
                            llm_model_describe_image_description_ui, 
                        ]),
                    ])
                }
                """
        )
    return (get_llm_model_describe_image_section,)


@app.cell
def _(mo):
    llm_model_describe_image_prompt_ui = mo.ui.text(
        value="Describe this image in maximum details.",
        full_width=True,
        disabled=True,
    )

    llm_model_describe_image_file_drag_and_drop_ui = mo.ui.file(
        filetypes=[".png", ".jpg"], multiple=False,
        kind="area"
    )
    return (
        llm_model_describe_image_file_drag_and_drop_ui,
        llm_model_describe_image_prompt_ui,
    )


@app.cell
async def _(
    base64,
    llm,
    llm_model_describe_image_file_drag_and_drop_ui,
    llm_model_describe_image_prompt_ui,
    mo,
    os,
):
    async def get_llm_image_description_async(
        image_contents: bytes,
        prompt: str,
    ):
        image_base64 = base64.b64encode(image_contents).decode("utf-8")
        image_description = ""
        with mo.status.spinner(title="Processing image description...") as _spinner:
            try:
                image_description = llm.describe_image(
                    image=image_base64,
                    prompt=prompt,
                )
                _spinner.update("Done!") 
            except Exception as e:
                _spinner.update(f"Error: {e}")
                image_description = f"Error: Failed to describe image: {e}"
        return image_description


    llm_model_describe_image_no_image = os.path.sep.join([
        os.path.abspath(os.path.dirname(__file__)), 'no-image-placeholder.png'
    ])

    llm_model_describe_image_image = (
        llm_model_describe_image_file_drag_and_drop_ui.value[0].contents 
        if llm_model_describe_image_file_drag_and_drop_ui.value else llm_model_describe_image_no_image
    )

    llm_model_describe_image_image_ui = mo.image(
        width="320px",
        height="240px",
        alt="Image",
        src=llm_model_describe_image_image
    )

    llm_model_describe_image_description = (
        await get_llm_image_description_async(
            image_contents=llm_model_describe_image_file_drag_and_drop_ui.value[0].contents,
            prompt=llm_model_describe_image_prompt_ui.value
        ) if llm_model_describe_image_file_drag_and_drop_ui.value 
        else ""
    )

    llm_model_describe_image_description_ui = mo.plain_text(
        text=llm_model_describe_image_description,
    )
    return (
        llm_model_describe_image_description_ui,
        llm_model_describe_image_image_ui,
    )


@app.cell
async def _(
    app_dir,
    get_llm_model_details_section,
    json,
    llm,
    llm_map,
    llm_model_details_container_full_introspection_ui,
    llm_model_details_container_model_selector_ui,
    llm_model_details_container_use_cache_ui,
    mo,
    os,
    print,
    time,
):
    def get_llm_model_details_from_cache(provider: str, model_id: str):
        cache_file = os.path.sep.join([app_dir, f"{provider}.{model_id}.json"])
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def save_llm_model_details_to_cache(provider: str, model_id: str, data: dict):
        cache_file = os.path.sep.join([app_dir, f"{provider}.{model_id}.json"])
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    async def get_llm_model_details_async(
        base_type: str = "base",
        full_introspection: bool = False,
        use_cache: bool = True,
    ):
        provider, api_base, api_key, is_local, model_id = llm_map[base_type].__dict__.values()

        model_details = {}
        if use_cache:
            model_details = get_llm_model_details_from_cache(provider, model_id)

        if model_details:
            return model_details
        else:
            try:
                model_details = llm.get_model_details(
                    model_type=base_type,
                    introspection=full_introspection,
                )
                save_llm_model_details_to_cache(provider, model_id, model_details)
            except Exception as e:
                print(f"Error: {e}")
                model_details = {"Error": str(e)}
        return model_details

    if llm_model_details_container_model_selector_ui.value:
        llm_model_details_response = {}
        models = [
            (llm_map[m], m)
            for m in llm_map.keys()
            if llm_map[m].model_id
            == llm_model_details_container_model_selector_ui.value
        ]
        if len(models) > 0:
            _, base_type = models[0]
            with mo.status.spinner(title="Generating model details...") as _spinner:
                try:
                    llm_model_details_response = await get_llm_model_details_async(
                        base_type=base_type,
                        full_introspection=llm_model_details_container_full_introspection_ui.value,
                        use_cache=llm_model_details_container_use_cache_ui.value,
                    )
                    _spinner.update("Done!")
                except Exception as e:
                    _spinner.update(f"Error: {e}")
                    time.sleep(2)
                    llm_model_details_response = {"Error generating model details": str(e)}
        llm_model_details_section = get_llm_model_details_section(
            llm_model_details_response,
            llm_model_details_container_model_selector_ui,
            llm_model_details_container_full_introspection_ui,
            llm_model_details_container_use_cache_ui,
        )
    else:
        llm_model_details_section = get_llm_model_details_section(
            {},
            llm_model_details_container_model_selector_ui,
            llm_model_details_container_full_introspection_ui,
            llm_model_details_container_use_cache_ui,
        )

    return (llm_model_details_section,)


@app.cell
def _(mo):
    def get_llm_model_details_section(
        llm_model_details_response: dict,
        llm_model_details_container_model_selector_ui: mo.ui.dropdown,
        llm_model_details_container_full_introspection_ui: mo.ui.switch,
        llm_model_details_container_use_cache_ui: mo.ui.switch,
    ):
        if llm_model_details_container_full_introspection_ui.value:
            return mo.md(
                    f"""
                    {
                        mo.hstack([
                            llm_model_details_container_model_selector_ui,
                            mo.vstack([
                                llm_model_details_container_full_introspection_ui, 
                                llm_model_details_container_use_cache_ui,
                            ]),
                        ])
                    }
                    {
                        mo.json(
                            llm_model_details_response
                        )
                    }
                    """
            )
        else:
            return mo.md(
                    f"""
                    {
                        mo.hstack([
                            llm_model_details_container_model_selector_ui,
                            llm_model_details_container_full_introspection_ui, 
                        ])
                    }
                    {
                        mo.json(
                            llm_model_details_response
                        )
                    }
                    """
            )
    return (get_llm_model_details_section,)


@app.cell
def _(llm_selected_models, mo):
    llm_model_details_container_model_selector_ui = mo.ui.dropdown(
        label="Selected the model:", options=llm_selected_models
    )

    llm_model_details_container_full_introspection_ui = mo.ui.switch(
        label="Full Introspection", value=False
    )

    llm_model_details_container_use_cache_ui = mo.ui.switch(
        label="Use Cache", value=True
    )
    return (
        llm_model_details_container_full_introspection_ui,
        llm_model_details_container_model_selector_ui,
        llm_model_details_container_use_cache_ui,
    )


@app.cell
def _(llm_base_model, llm_embed_model, llm_vision_model):
    llm_selected_models = [
        m.model_id
        for m in (
            llm_base_model,
            llm_embed_model,
            llm_vision_model,
        )
        if m.provider != "Undefined"
    ]

    def check_model_selection():
        for m in (llm_base_model, llm_embed_model, llm_vision_model):
            if m.provider != "Undefined":
                return True
    return check_model_selection, llm_selected_models


@app.cell
def _(
    LLMServiceModel,
    OpenAILLMService,
    get_llm_models_cards,
    llm_model_request_retries,
    llm_model_request_timeout,
    llm_selected_base_model_ui,
    llm_selected_embed_model_ui,
    llm_selected_provider_ui,
    llm_selected_vision_model_ui,
):
    llm_dummy_model = LLMServiceModel(
        provider="Undefined",
        api_base_url="Undefined",
        api_key="Undefined",
        model_id="Undefined",
    )

    llm_base_model = (
        llm_dummy_model
        if not llm_selected_base_model_ui.value
        else LLMServiceModel.get_llm_service_model(
            llm_selected_base_model_ui.value, llm_selected_provider_ui.value
        )
    )

    llm_embed_model = (
        llm_base_model
        if not llm_selected_embed_model_ui.value
        else LLMServiceModel.get_llm_service_model(
            llm_selected_embed_model_ui.value, llm_selected_provider_ui.value
        )
    )

    llm_vision_model = (
        llm_base_model
        if not llm_selected_vision_model_ui.value
        else LLMServiceModel.get_llm_service_model(
            llm_selected_vision_model_ui.value, llm_selected_provider_ui.value
        )
    )

    llm_model_cards = get_llm_models_cards(
        llm_base_model.__dict__,
        llm_embed_model.__dict__,
        llm_vision_model.__dict__,
    )

    llm, llm_map = None, {}
    if all(
        [
            llm_base_model != llm_dummy_model,
            llm_embed_model != llm_dummy_model,
            llm_vision_model != llm_dummy_model,
        ]
    ):
        llm = OpenAILLMService(
            llm_base_model, 
            llm_embed_model, 
            llm_vision_model,
            timeout=llm_model_request_timeout.value,
            retries=llm_model_request_retries.value,
        )
        llm_map = {"base": llm_base_model, "embed": llm_embed_model, "vision": llm_vision_model}
    return (
        llm,
        llm_base_model,
        llm_embed_model,
        llm_map,
        llm_model_cards,
        llm_vision_model,
    )


@app.cell
def _(llm_models, mo):
    llm_selected_base_model_ui = mo.ui.dropdown(
        options=llm_models,
        label="The base model",
    )

    llm_selected_embed_model_ui = mo.ui.dropdown(
        options=llm_models,
        label="The embedding model (optional)",
    )

    llm_selected_vision_model_ui = mo.ui.dropdown(
        options=llm_models,
        label="The vision model (optional)",
    )

    llm_model_request_timeout = mo.ui.slider(
        start=0,
        stop=1800,
        step=1,
        label="Request Timeout (seconds)",
        value=300,
        full_width=False,
    )

    llm_model_request_retries = mo.ui.slider(
        start=1, stop=5, step=1, label="Retries", value=3, full_width=False
    )
    return (
        llm_model_request_retries,
        llm_model_request_timeout,
        llm_selected_base_model_ui,
        llm_selected_embed_model_ui,
        llm_selected_vision_model_ui,
    )


@app.cell
def _(mo):
    def llm_get_common_params_ui_set(
        temperature_var, top_p_var, max_tokens_var, stream_var, tool_choice_var
    ):
        return {
            "temperature": mo.ui.slider(
                start=0,
                stop=2,
                step=0.01,
                label="Temperature",
                value=temperature_var,
                full_width=False,
            ),
            "top_p": mo.ui.slider(
                start=0,
                stop=1,
                step=0.01,
                label="Top P",
                value=top_p_var,
                full_width=False,
            ),
            "max_tokens": mo.ui.slider(
                start=1,
                stop=32768,
                step=1,
                label="Max Tokens",
                value=max_tokens_var,
                full_width=False,
            ),
            "stream": mo.ui.switch(label="Stream", value=stream_var),
            "tool_choice": mo.ui.switch(label="Use tools", value=tool_choice_var),
        }
    return


@app.cell
async def _(OpenAILLMService, llm_selected_provider_ui, mo, os, time):
    async def load_llm_models_async(api_base_url, api_key):
        llm_models = [
            m["id"] for m in OpenAILLMService.list_models(api_base_url, api_key)
        ]
        llm_models.sort()
        return llm_models

    if llm_selected_provider_ui.value is None:
        llm_models = []
    else:
        llm_models = []
        with mo.status.spinner(title="Loading provider models...") as _spinner:
            try:
                llm_models = await load_llm_models_async(
                    api_base_url=llm_selected_provider_ui.value["base_url"],
                    api_key=os.environ.get(llm_selected_provider_ui.value["env_api_key"]),
                )
                _spinner.update("Done!")
            except Exception as e:
                _spinner.update(f"Error: {e}")
                time.sleep(2)
    return (llm_models,)


@app.cell
def _(llm_providers, mo):
    llm_selected_provider_ui = mo.ui.dropdown(
        options=llm_providers,
        label="A provider",
    )
    return (llm_selected_provider_ui,)


@app.cell
async def _(get_llm_resources_async, mo, time):
    with mo.status.spinner(title="Loading providers...") as _spinner:
        try:
            (
                llm_providers,
                llm_common_params,
                llm_introspection_prompt,
                llm_introspection_validation_schema,
            ) = await get_llm_resources_async()
            _spinner.update("Sorting...")
            provider_names = list(set([p for p in llm_providers]))
            provider_names.sort()
            llm_providers = {k: llm_providers[k] for k in provider_names}
            _spinner.update("Done!")
        except Exception as e:
            _spinner.update(f"Error: {e}")
            time.sleep(2)
    return (llm_providers,)


@app.cell
def _(get_llm_resources):
    async def get_llm_resources_async():
        return get_llm_resources()
    return (get_llm_resources_async,)


@app.cell
def _(os):
    import time
    import base64
    import asyncio
    import pandas as pd

    from time import sleep
    from jsonschema import validate, ValidationError

    from fbpyutils_ai import app_dir, logging, log_dir
    from fbpyutils_ai.tools.llm import OpenAILLMService, LLMServiceModel
    from fbpyutils_ai.tools.llm.utils import get_llm_resources
    from fbpyutils_ai.ui.marimo.components import get_llm_models_cards, TextExtractor

    os.environ["LITELLM_LOG"] = os.environ.get("FBPY_LOG_LEVEL", "DEBUG").lower()
    return (
        LLMServiceModel,
        OpenAILLMService,
        TextExtractor,
        app_dir,
        base64,
        get_llm_models_cards,
        get_llm_resources,
        time,
    )


@app.cell
def _():
    # Scrape Tool
    return


@app.cell
def _(firecrawl_tool_output_scrape, firecrawl_tool_output_search, mo):
    firecrawl_tool_output = mo.accordion(
        {
            "Scrape": firecrawl_tool_output_scrape,
            "Search": firecrawl_tool_output_search,
        }
    )
    return (firecrawl_tool_output,)


@app.cell
def _(FireCrawlTool, mo):
    firecrawl_tool = FireCrawlTool()

    firecrawl_scrape_url = mo.ui.text_area(
        placeholder="Enter URL to scrape...",
        max_length=None,
        rows=3,
        label="URL to Scrape:",
        full_width=True,
    )

    firecrawl_scrape_formats = mo.ui.dropdown(
        options=["markdown", "html", "rawHtml", "links", "screenshot"],
        value="markdown",
        label="Formats:",
    )

    firecrawl_scrape_only_main_content = mo.ui.switch(
        value=False, label="Only Main Content"
    )

    firecrawl_search_query = mo.ui.text_area(
        placeholder="Enter search query...",
        max_length=None,
        rows=3,
        label="Search Query:",
        full_width=True,
    )

    firecrawl_search_limit = mo.ui.slider(
        start=1, stop=20, step=1, value=5, label="Limit Results:"
    )

    firecrawl_search_lang = mo.ui.text(
        value="en", label="Language (e.g., 'en', 'pt'):"
    )
    return (
        firecrawl_scrape_formats,
        firecrawl_scrape_only_main_content,
        firecrawl_scrape_url,
        firecrawl_search_lang,
        firecrawl_search_limit,
        firecrawl_search_query,
        firecrawl_tool,
    )


@app.cell
def _(
    firecrawl_scrape_formats,
    firecrawl_scrape_only_main_content,
    firecrawl_scrape_url,
    firecrawl_tool,
    json,
    mo,
):
    firecrawl_scrape_format = firecrawl_scrape_formats.value
    firecrawl_scrape_results = None
    if firecrawl_scrape_url.value:
        with mo.status.spinner(title="Scraping URL...") as _spinner:
            try:
                scrape_result = firecrawl_tool.scrape(
                    url=firecrawl_scrape_url.value,
                    formats=[firecrawl_scrape_format],
                    onlyMainContent=firecrawl_scrape_only_main_content.value,
                )
                firecrawl_scrape_results = scrape_result["data"][firecrawl_scrape_format] if (scrape_result.get('success') and scrape_result.get("data", {}).get("metadata", {}).get("statusCode") == 200) else json.dumps(scrape_result, indent=4, ensure_ascii=False)
                _spinner.update("Done!")
            except Exception as e:
                _spinner.update(f"Error: {e}")
                firecrawl_scrape_results = f"Error: {str(e)}"

    firecrawl_tool_output_scrape = mo.md(
        f"""
        {firecrawl_scrape_url}
        {firecrawl_scrape_formats}
        {firecrawl_scrape_only_main_content}

        ### Scrape Results:
        {firecrawl_scrape_results if firecrawl_scrape_results else "## No results."}
        """
    )
    return (firecrawl_tool_output_scrape,)


@app.cell
def _(
    firecrawl_search_lang,
    firecrawl_search_limit,
    firecrawl_search_query,
    firecrawl_tool,
    mo,
):
    firecrawl_search_results = {}
    if firecrawl_search_query.value:
        with mo.status.spinner(title="Searching...") as _spinner:
            try:
                firecrawl_search_results = firecrawl_tool.search(
                    query=firecrawl_search_query.value,
                    limit=firecrawl_search_limit.value,
                    lang=firecrawl_search_lang.value,
                )
                _spinner.update("Done!")
            except Exception as e:
                _spinner.update(f"Error: {e}")
                firecrawl_search_results = {"Error": str(e)}

    firecrawl_tool_output_search = mo.md(
        f"""
        {firecrawl_search_query}
        {firecrawl_search_limit}
        {firecrawl_search_lang}

        ### Search Results:
        {mo.json(firecrawl_search_results) if firecrawl_search_results else "No results."}
        """
    )
    return (firecrawl_tool_output_search,)


@app.cell
def _():
    from fbpyutils_ai.tools.scrape import FireCrawlTool
    return (FireCrawlTool,)


@app.cell
def _():
    # SearXNG Tool
    return


@app.cell
def _(
    json,
    mo,
    quote_plus,
    searxng_categories,
    searxng_copy_to_clipboard,
    searxng_resuls_data,
    searxng_results,
    searxng_safe_search,
    searxng_safe_search_level,
    searxng_search_text,
    searxng_selected_categories,
    searxng_selected_language,
    searxng_show_parameters,
):
    searxng_parameters_output = (
        f"""
    ---
    ##### search={quote_plus(searxng_search_text.value)}
    ##### categories={searxng_categories}
    ##### safe_search={searxng_safe_search_level}
    ##### language={searxng_selected_language.value}
    ---
    """
        if searxng_show_parameters.value
        else ""
    )

    searxng_resuls_data_items = {
        i['url']: mo.json(
            json.dumps(i, 
            indent=4, ensure_ascii=False)
        ) for i in searxng_resuls_data.to_dict(orient='records')
    }

    searxng_tool_output = mo.md(f"""
    {searxng_search_text}

    {searxng_selected_categories}\n
    {searxng_selected_language}\n
    {searxng_safe_search}

    {searxng_show_parameters}\t{searxng_copy_to_clipboard}

    {searxng_parameters_output}

    {mo.accordion(searxng_resuls_data_items) if len(searxng_results) > 0 else "### No results found."}
    """)
    return (searxng_tool_output,)


@app.cell
def _(
    SearXNGTool,
    SearXNGUtils,
    searxng_safe_search,
    searxng_search_text,
    searxng_selected_categories,
    searxng_selected_language,
    searxng_tool,
):
    searxng_categories = [
        SearXNGTool.CATEGORIES[indice]
        for indice, valor in enumerate(searxng_selected_categories.value)
        if valor
    ]

    searxng_safe_search_level = [
        e[0]
        for e in enumerate(searxng_safe_search.options.items())
        if e[1][0] == searxng_safe_search.value
    ][0]

    if searxng_search_text.value:
        searxng_results = searxng_tool.search(
            searxng_search_text.value,
            categories=searxng_categories,
            language=searxng_selected_language.value,
            safesearch=searxng_safe_search_level,
        )
    else:
        searxng_results = []

    searxng_resuls_data = SearXNGUtils.convert_to_dataframe(searxng_results)
    return (
        searxng_categories,
        searxng_resuls_data,
        searxng_results,
        searxng_safe_search_level,
    )


@app.cell
def _(SearXNGTool, mo):
    searxng_tool = SearXNGTool()

    searxng_selected_categories = mo.ui.array(
        [mo.ui.switch(value=(c == "general"), label=c) for c in SearXNGTool.CATEGORIES],
        label="Select categories to search on:",
    )

    searxng_safe_search = mo.ui.radio(
        options=["None", "Moderate", "Strict"], value="None", label="Safe search level:"
    )

    searxng_selected_language = mo.ui.dropdown(
        options=SearXNGTool.LANGUAGES,
        label="Select languages to search in:",
        value="auto",
    )

    searxng_show_parameters = mo.ui.switch(value=True, label="Show search parameters")

    searxng_copy_to_clipboard = mo.ui.switch(
        value=False, label="Copy search results to clipboard"
    )

    searxng_search_text = mo.ui.text_area(
        placeholder="Enter an expression to search for...",
        max_length=None,
        rows=3,
        label="Search expression:",
        full_width=True,
    )
    return (
        searxng_copy_to_clipboard,
        searxng_safe_search,
        searxng_search_text,
        searxng_selected_categories,
        searxng_selected_language,
        searxng_show_parameters,
        searxng_tool,
    )


@app.cell
def _():
    # Initialize the app
    return


@app.cell
def _():
    import os
    import json
    from rich import print
    from dotenv import load_dotenv
    from urllib.parse import quote_plus
    from fbpyutils_ai.tools.search import SearXNGTool, SearXNGUtils

    _ = load_dotenv()
    return SearXNGTool, SearXNGUtils, json, os, print, quote_plus


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
