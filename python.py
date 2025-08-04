import aiohttp
import asyncio
import json
import csv
import re
import tldextract
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
from playwright.async_api import async_playwright
import warnings

# Suppress Playwright and cookie warnings
logging.getLogger("playwright").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore", message="Can not load response cookies")

visited_urls = set()
crawled_data = []

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; TikuCrawler/1.0)"
}

# ---------- Fetch Functions ----------

async def fetch(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            # Remove cookies with illegal names (like starting with '@')
            if response.cookies:
                for k in list(response.cookies.keys()):
                    if k.startswith("@") or not k.replace("-", "").isalnum():
                        del response.cookies[k]
            return await response.text(), str(response.url), response
    except Exception:
        return None, url, None


async def fetch_js_rendered(url):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(ignore_https_errors=True)
            page = await context.new_page()
            await page.goto(url, timeout=15000)
            content = await page.content()
            await browser.close()
            return content
    except Exception:
        return None

# ---------- Extraction Functions ----------

def extract_links(soup, base_url):
    return [urljoin(base_url, tag.get("href")) for tag in soup.find_all("a", href=True)]

def extract_js_files(soup, base_url):
    return [urljoin(base_url, tag.get("src")) for tag in soup.find_all("script", src=True)]

def extract_forms(soup):
    forms = []
    for form in soup.find_all("form"):
        action = form.get("action")
        method = form.get("method", "GET").upper()
        forms.append({"action": action, "method": method})
    return forms

def extract_endpoints_from_js(js_content):
    return re.findall(r"/api/[\w/]+", js_content)

def extract_headers(response):
    if not response:
        return {}
    headers = response.headers
    return {
        "csp": headers.get("Content-Security-Policy"),
        "x_frame": headers.get("X-Frame-Options"),
        "x_content_type": headers.get("X-Content-Type-Options")
    }

def extract_parameters(links):
    params = set()
    for link in links:
        parsed = urlparse(link)
        if parsed.query:
            for param in parsed.query.split('&'):
                key = param.split('=')[0]
                params.add(key)
    return list(params)

# ---------- Core Crawler ----------

async def crawl(start_url, max_depth):
    queue = deque([(start_url, 0)])
    async with aiohttp.ClientSession(headers=headers) as session:
        while queue:
            url, depth = queue.popleft()
            if url in visited_urls or depth > max_depth:
                continue
            visited_urls.add(url)

            html, final_url, response = await fetch(session, url)
            if not html:
                html = await fetch_js_rendered(url)
                if not html:
                    continue

            soup = BeautifulSoup(html, "html.parser")
            links = extract_links(soup, final_url)
            js_files = extract_js_files(soup, final_url)
            forms = extract_forms(soup)

            subdomains = list(
                set(
                    urlparse(link).netloc
                    for link in links
                    if tldextract.extract(link).domain == tldextract.extract(url).domain
                    and urlparse(link).netloc
                )
            )

            js_endpoints = []
            for js_url in js_files:
                js_html, _, _ = await fetch(session, js_url)
                if js_html:
                    js_endpoints.extend(extract_endpoints_from_js(js_html))

            headers_info = extract_headers(response)
            parameters = extract_parameters(links)

            crawled_data.append({
                "url": final_url,
                "links": links,
                "js_files": js_files,
                "forms": forms,
                "subdomains": subdomains,
                "js_endpoints": list(set(js_endpoints)),
                "technologies": [],  # Placeholder for tech detection
                "headers": headers_info,
                "parameters": parameters
            })

            for link in links:
                if link.startswith("http"):
                    queue.append((link, depth + 1))

# ---------- Output ----------

def save_output(filename, fmt):
    if not crawled_data:
        print("No data crawled.")
        return

    if fmt == "json":
        with open(filename, "w") as f:
            json.dump(crawled_data, f, indent=2)
    elif fmt == "csv":
        keys = crawled_data[0].keys()
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for row in crawled_data:
                safe_row = {k: json.dumps(v) if isinstance(v, (list, dict)) else v for k, v in row.items()}
                writer.writerow(safe_row)

# ---------- CLI ----------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", required=True, help="Target URL to crawl")
    parser.add_argument("-d", "--depth", type=int, default=1, help="Crawling depth")
    parser.add_argument("--output", default="output.json", help="Output file name")
    parser.add_argument("--format", default="json", choices=["json", "csv"], help="Output format")

    args = parser.parse_args()

    asyncio.run(crawl(args.url, args.depth))
    save_output(args.output, args.format)
    print(f"Crawling finished. Data saved to {args.output}")
