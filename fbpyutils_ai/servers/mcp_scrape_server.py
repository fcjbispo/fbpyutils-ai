from typing import List, AsyncGenerator, Union, Dict, Any, Tuple
import asyncio
from fbpyutils_ai.tools.scrape import FireCrawlTool

# Initialize FireCrawl tool
_firecrawl = FireCrawlTool()


async def _metadata_to_markdown(metadata: Dict[str, Any]) -> str:
    """Converts metadata dictionary to a Markdown formatted string."""
    title = metadata.get("title") or metadata.get("ogTitle") or "Sem Título"
    description = (
        metadata.get("description") or metadata.get("ogDescription") or "Sem descrição"
    )
    url = (
        metadata.get("url") or metadata.get("ogUrl") or metadata.get("sourceURL") or ""
    )
    language = metadata.get("language") or "N/A"
    author = (
        metadata.get("sailthru.author")
        or metadata.get("article:author")
        or "Desconhecido"
    )
    tags = metadata.get("sailthru.tags") or metadata.get("parsely-tags") or ""
    favicon = metadata.get("favicon")
    og_image = metadata.get("ogImage") or metadata.get("og:image")

    markdown_lines = [
        "# Page Metadata",
        "",
        f"**Page**:{title}",
        "",
        f"**Descrição**: {description}",
        "",
    ]
    if url:
        markdown_lines.append(f"**URL**: [{url}]({url})")
        markdown_lines.append("")
    markdown_lines.append(f"**Idioma**: {language}")
    markdown_lines.append("")
    markdown_lines.append(f"**Autor**: {author}")
    markdown_lines.append("")
    if tags:
        markdown_lines.append(f"**Tags**: {tags}")
        markdown_lines.append("")
    if favicon:
        markdown_lines.append(f"**Favicon**: ![Favicon]({favicon})")
        markdown_lines.append("")
    if og_image:
        markdown_lines.append(f"**Imagem Principal**: ![Imagem Principal]({og_image})")
        markdown_lines.append("")

    return "\n".join(markdown_lines)


async def _links_to_markdown(links: List[str]) -> str:
    """Converts a list of links to a Markdown formatted list."""
    markdown_lines = ["# Page Links", ""]
    for link in links:
        markdown_lines.append(f"- [{link}]({link})")
    return "\n".join(markdown_lines)


async def _scrape_result_to_markdown(scrape_result: Dict[str, Any]) -> str:
    """Converts the scrape result dictionary to Markdown format."""
    try:
        if not isinstance(scrape_result, dict):
            return f"# Error: Invalid scrape result type: {type(scrape_result)}"

        if not (
            scrape_result.get("success") and 
            scrape_result.get("data", {}).get("metadata", {}).get("statusCode") == 200
        ):
            return "# No content found"

        data = scrape_result.get("data", {})
        if not isinstance(data, dict):
            return f"# Error: Invalid data type: {type(data)}"

        scrape_content = {
            k: data[k] for k in ["metadata", "markdown", "linksOnPage"] if k in data
        }

        if not all(
            k in scrape_content for k in ["metadata", "markdown"]
        ):
            missing = [
                k
                for k in ["metadata", "markdown"]
                if k not in scrape_content
            ]
            return f"# Error: Missing required fields: {', '.join(missing)}"

        contents = scrape_content["markdown"]
        metadata = await _metadata_to_markdown(scrape_content["metadata"])
        links = await _links_to_markdown(scrape_content.get("linksOnPage",[]))

        return f"""# Page Contents:
        {contents}
        ---
        {metadata}
        ---
        {links}"""
    except Exception as e:
        return f"# Error processing scrape result\nError: {str(e)}"


async def scrape(url: str, tags_to_remove: List[str] = [], timeout: int = 30000) -> str:
    """
    Scrapes a webpage and extracts full content in Markdown format.

    Args:
        url: The URL of the webpage to scrape.
        tags_to_remove: A list of HTML tags to remove. Ex: ['/script', '/ad']. Defaults to an empty list.
        timeout: Maximum time to wait for scraping. Defaults to 30000.
    """
    tags_to_remove = tags_to_remove or []
    for t in ["script", ".ad", "#footer"]:
        if t not in tags_to_remove:
            tags_to_remove.append(t)

    try:
        # _firecrawl.scrape é síncrono, não precisa de await
        scrape_result = _firecrawl.scrape(
            url=url,
            formats=["markdown"],
            onlyMainContent=True,
            excludeTags=tags_to_remove or ["script", ".ad", "#footer"],
            waitFor=200,
            timeout=timeout,
            removeBase64Images=True,
        )
        # _scrape_result_to_markdown é assíncrono, precisa de await
        return await _scrape_result_to_markdown(scrape_result)
    except Exception as e:
        # Captura qualquer exceção durante o scrape e retorna uma mensagem de erro
        return f"# Error scraping {url}\nError: {str(e)}"


async def scrape_n(
    urls: List[str],
    tags_to_remove: List[str] = [],
    timeout: int = 30000,
    stream: bool = False,
) -> Union[List[str], AsyncGenerator[str, None]]:
    """
    Scrapes multiple webpages in parallel and extracts full content in Markdown format.

    Args:
        urls: List of URLs to scrape.
        tags_to_remove: A list of HTML tags to remove. Ex: ['/script', '/ad']. Defaults to an empty list.
        timeout: Maximum time to wait for scraping. Defaults to 30000.
        stream: If True, returns results incrementally as they become available. Defaults to False.

    Returns:
        If stream=False: List of markdown strings in the same order as input URLs
        If stream=True: AsyncGenerator yielding markdown strings as they become available
    """
    if not urls:
        if stream:

            async def empty_gen():
                if False:  # Hack para criar um generator assíncrono vazio
                    yield

            return empty_gen()
        return []

    async def process_url(url: str) -> Tuple[int, str]:
        """
        Processes a single URL scrape request.

        Args:
            url: The URL to scrape.

        Returns:
            A tuple containing the original index of the URL and the scrape result string.
        """
        try:
            # _firecrawl.scrape é síncrono, não precisa de await
            scrape_result = _firecrawl.scrape(
                url=url,
                formats=["markdown"],
                onlyMainContent=True,
                excludeTags=tags_to_remove or ["script", ".ad", "#footer"],
                waitFor=200,
                timeout=timeout,
                removeBase64Images=True,
            )
            # _scrape_result_to_markdown é assíncrono, precisa de await
            result = await _scrape_result_to_markdown(scrape_result)
            return urls.index(url), result
        except Exception as e:
            return urls.index(url), f"# Error scraping {url}\nError: {str(e)}"

    if stream:

        async def stream_results() -> AsyncGenerator[str, None]:
            """Yields scrape results as they become available."""
            tasks = []
            for url in urls:
                task = asyncio.create_task(process_url(url))
                tasks.append(task)

            for completed in asyncio.as_completed(tasks):
                _, result = await completed
                yield result

        return stream_results()
    else:
        tasks: List[asyncio.Task] = []
        for url in urls:
            task: asyncio.Task = asyncio.create_task(process_url(url))
            tasks.append(task)

        results: List[Tuple[int, str]] = await asyncio.gather(*tasks)
        # Sort results back to the original order based on the index
        return [r[1] for r in sorted(results, key=lambda x: x[0])]
