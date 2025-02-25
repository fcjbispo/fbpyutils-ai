from typing import List
from fbpyutils_ai.tools.crawl import FireCrawlTool

# Initialize FireCrawl tool
_firecrawl = FireCrawlTool()


async def _metadata_to_markdown(metadata: dict) -> str:
    title = metadata.get("title") or metadata.get("ogTitle") or "Sem Título"
    description = metadata.get("description") or metadata.get("ogDescription") or "Sem descrição"
    url = metadata.get("url") or metadata.get("ogUrl") or metadata.get("sourceURL") or ""
    language = metadata.get("language") or "N/A"
    author = metadata.get("sailthru.author") or metadata.get("article:author") or "Desconhecido"
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


async def _links_to_markdown(links: list) -> str:
    markdown_lines = ["# Page Links", ""]
    for link in links:
        markdown_lines.append(f"- [{link}]({link})")
    return "\n".join(markdown_lines)


async def _scrape_result_to_markdown(scrape_result: dict) -> str:
    if not (scrape_result['success'], scrape_result['returnCode']) == (True, 200):
        return "# No content found"
    else:
        scrape_content = {
            k: scrape_result['data'][k] 
            for  k in scrape_result['data'].keys() 
            if k in ['metadata', 'markdown', 'linksOnPage']
        }

        contents = scrape_content['markdown']
        metadata = await _metadata_to_markdown(scrape_content['metadata'])
        links = await _links_to_markdown(scrape_content['linksOnPage'])

        return f"""
        # Page Contents:
        {contents}
        ---
        {metadata}
        ---
        {links}
        """

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

    scrape_result = await _firecrawl.scrape(
        url=url,
        pageOptions={
            "includeHtml": False,
            "includeRawHtml": False,
            "onlyMainContent": True,
            "removeTags": tags_to_remove,
            "replaceAllPathsWithAbsolutePaths": True,
            "waitFor": 200
        },
        extractorOptions={
            "mode": "markdown"
        },
        timeout=timeout,
    )

    return await _scrape_result_to_markdown(scrape_result)

