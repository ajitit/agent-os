"""
File: crawler.py

Purpose:
Smart web crawler for the Knowledge Management module. Auto-detects sitemaps, falls
back to single-page or depth-limited crawling, extracts main content, and returns
structured objects.
"""

import asyncio
import re
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


class WebCrawler:
    def __init__(self, delay_ms: int = 500, max_depth: int = 3):
        self.delay_ms = delay_ms
        self.max_depth = max_depth
        self.visited = set()
        self.results = []

    async def crawl(self, url: str, source_id: str) -> list[dict[str, Any]]:
        self.visited.clear()
        self.results.clear()
        self.source_id = source_id

        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            sitemap_urls = await self._find_sitemaps(client, url)
            if sitemap_urls:
                await self._crawl_sitemaps(client, sitemap_urls)
            else:
                await self._crawl_page(client, url, current_depth=0)

        return self.results

    async def _find_sitemaps(self, client: httpx.AsyncClient, base_url: str) -> list[str]:
        parsed = urlparse(base_url)
        root_url = f"{parsed.scheme}://{parsed.netloc}"

        # Check robots.txt
        robots_url = f"{root_url}/robots.txt"
        sitemaps = []
        try:
            resp = await client.get(robots_url)
            if resp.status_code == 200:
                for line in resp.text.splitlines():
                    if line.lower().startswith("sitemap:"):
                        sitemaps.append(line.split(":", 1)[1].strip())
        except Exception:
            pass

        if not sitemaps:
            sitemaps = [f"{root_url}/sitemap.xml", f"{root_url}/sitemap_index.xml"]

        valid_sitemaps = []
        for sm in sitemaps:
            try:
                r = await client.head(sm)
                if r.status_code == 200:
                    valid_sitemaps.append(sm)
            except Exception:
                pass

        return valid_sitemaps

    async def _crawl_sitemaps(self, client: httpx.AsyncClient, sitemap_urls: list[str]):
        queue = sitemap_urls.copy()
        while queue:
            sm_url = queue.pop(0)
            if sm_url in self.visited:
                continue
            self.visited.add(sm_url)

            try:
                resp = await client.get(sm_url)
                if resp.status_code != 200:
                    continue
                soup = BeautifulSoup(resp.content, "xml")

                # Check if it's a sitemap index
                sitemaps = soup.find_all("sitemap")
                if sitemaps:
                    for s in sitemaps:
                        loc = s.find("loc")
                        if loc and loc.text:
                            queue.append(loc.text)
                    continue

                # Normal sitemap
                urls = soup.find_all("url")
                for u in urls:
                    loc = u.find("loc")
                    if loc and loc.text:
                        page_url = loc.text
                        await self._crawl_page(client, page_url, current_depth=0)
            except Exception as e:
                print(f"Error parsing sitemap {sm_url}: {e}")

    async def _crawl_page(self, client: httpx.AsyncClient, url: str, current_depth: int):
        # Normalize URL to avoid duplicates like end slashes
        norm_url = url.rstrip('/')
        if norm_url in self.visited or current_depth > self.max_depth:
            return

        self.visited.add(norm_url)

        await asyncio.sleep(self.delay_ms / 1000.0)

        try:
            resp = await client.get(url)
            if resp.status_code != 200 or "text/html" not in resp.headers.get("content-type", ""):
                return

            soup = BeautifulSoup(resp.text, "html.parser")

            # Content Extraction Heuristics
            title = soup.title.string if soup.title else url

            # Strip junk
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
                tag.decompose()

            main_content = soup.find("main") or soup.find("article") or soup.find("body")
            if not main_content:
                return

            text = main_content.get_text(separator="\n", strip=True)
            # Basic cleanup of excessive newlines
            text = re.sub(r'\n{3,}', '\n\n', text)

            self.results.append({
                "url": url,
                "title": title.strip() if title else "",
                "content": text,
                "sourceId": self.source_id
            })

            # Link discovery logic for documentation
            if any(path in url for path in ["/docs/", "/guide/", "/api/", "/manual/"]) and current_depth < self.max_depth:
                links = main_content.find_all("a", href=True)
                for a in links:
                    href = a["href"]
                    full_loc = urljoin(url, href).split("#")[0]
                    if self._is_same_domain(url, full_loc):
                        await self._crawl_page(client, full_loc, current_depth + 1)

        except Exception as e:
            print(f"Error crawling {url}: {e}")

    def _is_same_domain(self, url1: str, url2: str) -> bool:
        return urlparse(url1).netloc == urlparse(url2).netloc
