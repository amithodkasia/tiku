# tiku.py - Custom Web Crawler Tool with Advanced Recon Features + Nuclei Integration

import argparse
import asyncio
import csv
import json
import re
import os
import ssl
import subprocess
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession
from aiohttp import ClientSession

WAYBACK_URL = "http://web.archive.org/cdx/search/cdx?url={domain}/*&output=text&fl=original&collapse=urlkey"
HEADERS = {"User-Agent": "TikuCrawler/2.0"}
visited_urls = set()
ENDPOINT_PATTERNS = {
    "xss": re.compile(r'(\?|&)([a-zA-Z0-9_\-]*=)[^&]*', re.IGNORECASE),
    "sqli": re.compile(r'(\?|&)(id|user|uid|page)=', re.IGNORECASE),
    "lfi": re.compile(r'(\?|&)(file|path|dir)=', re.IGNORECASE),
    "ssrf": re.compile(r'(\?|&)(url|uri|next)=', re.IGNORECASE),
    "redirect": re.compile(r'(\?|&)(redirect|url)=https?://', re.IGNORECASE)
}

TECH_SIGNATURES = {
    'PHP': re.compile(r'\.php'),
    'ASP.NET': re.compile(r'\.aspx'),
    'Java': re.compile(r'\.jsp'),
    'WordPress': re.compile(r'wp-content|wp-includes'),
    'jQuery': re.compile(r'jquery'),
    'React': re.compile(r'react', re.IGNORECASE),
    'Angular': re.compile(r'angular', re.IGNORECASE),
    'Vue': re.compile(r'vue', re.IGNORECASE)
}

ssl._create_default_https_context = ssl._create_unverified_context

def apply_filters(links):
    filtered = {k: [] for k in ENDPOINT_PATTERNS}
    for link in links:
        for key, pattern in ENDPOINT_PATTERNS.items():
            if pattern.search(link):
                filtered[key].append(link)
    return filtered

def extract_technologies(html):
    techs = set()
    for name, pattern in TECH_SIGNATURES.items():
        if pattern.search(html):
            techs.add(name)
    return list(techs)

def extract_headers_analysis(headers):
    return {
        'csp': headers.get('Content-Security-Policy', ''),
        'x_frame': headers.get('X-Frame-Options', ''),
        'x_content_type': headers.get('X-Content-Type-Options', '')
    }

def extract_params(links):
    params = set()
    for link in links:
        parts = urlparse(link)
        if parts.query:
            for param in parts.query.split("&"):
                key = param.split("=")[0]
                params.add(key)
    return list(params)

def parse_js_endpoints(js_content):
    return re.findall(r'/[a-zA-Z0-9_/\-]+', js_content)

async def fetch(session, url, headers=None, cookies=None):
    try:
        async with session.get(url, headers=headers, cookies=cookies, timeout=10) as resp:
            if 'text/html' in resp.headers.get('Content-Type', ''):
                text = await resp.text()
                return text, dict(resp.headers)
    except:
        pass
    return None, {}

async def fetch_js_rendered(url):
    try:
        session = AsyncHTMLSession()
        r = await session.get(url)
        await r.html.arender(timeout=10)
        return r.html.html
    except:
        return None

async def fetch_js_file(session, url):
    try:
        async with session.get(url, timeout=10) as resp:
            if resp.status == 200 and 'javascript' in resp.headers.get('Content-Type', ''):
                return await resp.text()
    except:
        pass
    return ""

def extract_links(base_url, html):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    js_files = set()
    forms = []
    subdomains = set()

    for tag in soup.find_all(['a', 'script', 'form']):
        if tag.name == 'a' and tag.get('href'):
            link = urljoin(base_url, tag.get('href'))
            links.add(link)
        elif tag.name == 'script' and tag.get('src'):
            js = urljoin(base_url, tag.get('src'))
            js_files.add(js)
        elif tag.name == 'form':
            forms.append({
                'action': urljoin(base_url, tag.get('action', '')),
                'method': tag.get('method', 'GET').upper()
            })

    for link in links.union(js_files):
        domain = urlparse(link).netloc
        base_domain = urlparse(base_url).netloc
        if domain != base_domain and domain.endswith(base_domain):
            subdomains.add(domain)

    return links, js_files, forms, subdomains

async def crawl(url, depth, headers, cookies, use_js):
    if url in visited_urls or depth < 0:
        return []
    visited_urls.add(url)

    async with ClientSession() as session:
        html, resp_headers = await fetch(session, url, headers, cookies)

        if use_js and not html:
            html = await fetch_js_rendered(url)

        if not html:
            return []

        links, js_files, forms, subdomains = extract_links(url, html)
        js_endpoints = []
        for js in js_files:
            js_content = await fetch_js_file(session, js)
            js_endpoints.extend(parse_js_endpoints(js_content))

        techs = extract_technologies(html)
        headers_info = extract_headers_analysis(resp_headers)
        params = extract_params(links)

        result = [{
            'url': url,
            'links': list(links),
            'js_files': list(js_files),
            'forms': forms,
            'subdomains': list(subdomains),
            'js_endpoints': js_endpoints,
            'technologies': techs,
            'headers': headers_info,
            'parameters': params
        }]

        for link in links:
            if urlparse(link).netloc == urlparse(url).netloc:
                sub_results = await crawl(link, depth - 1, headers, cookies, use_js)
                result.extend(sub_results)

        return result

def run_nuclei(target_urls):
    print("\n[*] Running nuclei scan...")
    with open("tiku_nuclei_targets.txt", "w") as f:
        f.write("\n".join(target_urls))

    try:
        subprocess.run(["nuclei", "-l", "tiku_nuclei_targets.txt", "-o", "nuclei_results.txt"])
        print("[+] Nuclei scan completed. Results saved to nuclei_results.txt")
    except FileNotFoundError:
        print("[!] Nuclei not found. Please install it from https://github.com/projectdiscovery/nuclei")

def save_output(data, output_format, output_file):
    if output_format == 'json':
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
    elif output_format == 'csv':
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Links', 'JS Files', 'Forms', 'Subdomains', 'JS Endpoints', 'Technologies', 'Headers', 'Parameters'])
            for entry in data:
                writer.writerow([
                    entry['url'], ', '.join(entry['links']), ', '.join(entry['js_files']),
                    json.dumps(entry['forms']), ', '.join(entry['subdomains']),
                    ', '.join(entry['js_endpoints']), ', '.join(entry['technologies']),
                    json.dumps(entry['headers']), ', '.join(entry['parameters'])
                ])

def get_wayback_urls(domain):
    try:
        import requests
        res = requests.get(WAYBACK_URL.format(domain=domain))
        if res.status_code == 200:
            return set(res.text.strip().split('\n'))
    except:
        pass
    return set()

async def main():
    parser = argparse.ArgumentParser(description='Tiku - Advanced Web Crawler')
    parser.add_argument('-u', '--url', required=True, help='Target URL')
    parser.add_argument('-d', '--depth', type=int, default=1, help='Crawl depth')
    parser.add_argument('--auth-header', help='Auth header')
    parser.add_argument('--cookie', help='Cookie string')
    parser.add_argument('--output', default='output.json', help='Output file')
    parser.add_argument('--format', choices=['json', 'csv'], default='json')
    parser.add_argument('--wayback', action='store_true', help='Include Wayback URLs')
    parser.add_argument('--use-js', action='store_true', help='Render JS pages')
    parser.add_argument('--filter', action='store_true', help='Apply GF-style endpoint filtering')
    parser.add_argument('--nuclei', action='store_true', help='Run nuclei scan on crawled URLs')

    args = parser.parse_args()

    headers = HEADERS.copy()
    cookies = {}

    if args.auth_header:
        k, v = args.auth_header.split(":", 1)
        headers[k.strip()] = v.strip()

    if args.cookie:
        cookies = dict(item.split("=") for item in args.cookie.split(";"))

    start_urls = [args.url]
    if args.wayback:
        wayback = get_wayback_urls(urlparse(args.url).netloc)
        start_urls.extend(wayback)

    all_data = []
    collected_urls = set()

    for url in start_urls:
        crawled = await crawl(url, args.depth, headers, cookies, args.use_js)
        for entry in crawled:
            collected_urls.add(entry['url'])
            if args.filter:
                entry['filtered'] = apply_filters(entry['links'])
            all_data.append(entry)

    save_output(all_data, args.format, args.output)

    if args.nuclei:
        run_nuclei(list(collected_urls))

if __name__ == '__main__':
    asyncio.run(main())
