<<<<<<< HEAD
"# Tiku" 
=======
# Tiku Web Crawler

Tiku is an advanced Python-based web crawler tool designed for reconnaissance and security testing. It supports various features such as JS file extraction, form detection, subdomain crawling, Wayback URLs fetch, auth header/cookie support, and much more.

## Features

- **Crawl Depth Control**: Control the depth of the crawling process to limit how deep the crawler explores.
- **JS File Extraction**: Automatically detect and extract JS files linked within web pages.
- **Form Detection**: Identify forms on web pages and extract their details (action URL, method).
- **Subdomain Crawling**: Detect and crawl subdomains linked to the target domain.
- **Wayback URLs Fetch**: Fetch archived URLs from the Wayback Machine.
- **Gau URLs Fetch**: Integrate with the Gau tool for fetching URLs.
- **Auth Header/Cookie Support**: Support for custom authentication headers and cookies.
- **Fast Async Crawling (aiohttp)**: Efficient asynchronous crawling with `aiohttp` for faster response times.
- **BeautifulSoup/Regex-based HTML Parsing**: Uses BeautifulSoup for HTML parsing and Regex for endpoint detection.
- **Static + JS Endpoint Extraction**: Extract static endpoints and dynamic JS-rendered endpoints.
- **Endpoint Filtering**: Apply GF-style endpoint filtering to categorize URLs into different types (XSS, SQLi, etc.).
- **Vulnerability Scanning Integrations**: Integrate with Nuclei templates for vulnerability scanning.
- **Advanced Technology Fingerprinting**: Detect technologies like PHP, ASP.NET, React, WordPress, etc.
- **CSP/Headers Analysis**: Collect and analyze security headers like CSP, X-Frame-Options, etc.
- **JavaScript Endpoint Extraction**: Extract endpoints from JS files (e.g., `/api/`, `/v1/`).
- **Screenshot Support**: Capture page screenshots using `pyppeteer` or `selenium`.
- **Open Redirect Detection**: Detect open redirect vulnerabilities in URLs.
- **Content Discovery**: Perform brute-force directory discovery using a wordlist.

## Requirements

The following libraries are required to run Tiku:

- `aiohttp==3.8.1`
- `beautifulsoup4==4.11.1`
- `requests-html==0.10.0`
- `tldextract==3.2.0`

To install the required libraries, you can use the following command:

```bash
pip install -r requirements.txt

Installation
Clone the repository:
git clone https://github.com/your-repository/tiku-crawler.git
cd tiku-crawler

Install dependencies:
pip install -r requirements.txt

Usage
To run Tiku, use the following command:
python tiku.py -u <target-url> -d <depth> --output <output-file> --format <json/csv> [optional flags]

Example Usage:
python tiku.py -u https://example.com -d 2 --output output.json --format json --use-js --wayback --filter


Arguments:
-u or --url: Target URL to crawl (required).

-d or --depth: The depth of the crawl (default: 1).

--auth-header: Provide authentication headers (optional).

--cookie: Provide cookie string for session (optional).

--output: Output file name (default: output.json).

--format: Output format, either json or csv (default: json).

--wayback: Include Wayback URLs in crawling (optional).

--use-js: Render JavaScript content using requests_html (optional).

--filter: Apply GF-style endpoint filtering (optional).

Example Output
The output will be saved in the chosen format (JSON or CSV), containing crawled URLs, detected endpoints, forms, subdomains, technologies, and more.

Sample JSON Output:
[
  {
    "url": "https://example.com",
    "links": ["https://example.com/about", "https://example.com/contact"],
    "js_files": ["https://example.com/js/app.js"],
    "forms": [{"action": "https://example.com/login", "method": "POST"}],
    "subdomains": ["sub.example.com"],
    "js_endpoints": ["/api/v1/user", "/api/v1/posts"],
    "technologies": ["PHP", "jQuery"],
    "headers": {
      "csp": "default-src 'self'",
      "x_frame": "DENY",
      "x_content_type": "nosniff"
    },
    "parameters": ["id", "name"]
  }
]

Sample CSV Output:
URL,Links,JS Files,Forms,Subdomains,JS Endpoints,Technologies,Headers,Parameters
https://example.com,"https://example.com/about, https://example.com/contact","https://example.com/js/app.js","[{\"action\": \"https://example.com/login\", \"method\": \"POST\"}]","sub.example.com","/api/v1/user, /api/v1/posts","PHP, jQuery","{\"csp\": \"default-src 'self'\", \"x_frame\": \"DENY\", \"x_content_type\": \"nosniff\"}","id, name"

Advanced Features
Here are some additional features you can enable:

JavaScript Endpoint Extraction: The tool can parse JavaScript files for potential endpoints like /api/, /v1/, etc.

Automatic Subdomain Extraction: Extract subdomains from HTML, JS files, and Wayback URLs.

URL Parameter Wordlist Generator: Collect parameters (e.g., id, name) to use in fuzzing.

Screenshot Support: Capture screenshots of the crawled pages using tools like pyppeteer or selenium.

Content Discovery: Brute-force directories using a wordlist (like dirsearch).

CSP/Headers Analysis: Collect and analyze headers like Content-Security-Policy.


### To use it:
1. Copy this content into a `README.md` file.
2. Save the file in your project directory.

This file will serve as the documentation for your crawler tool, explaining everything from setup to usage and features. Let me know if you need any more adjustments!


Open Redirect Detection: Detect URLs with potential open redirects.

Technology Fingerprinting: Detect technologies like PHP, WordPress, React, and more.

Vulnerability Scanning Integrations: Use Nuclei templates to scan for vulnerabilities.
>>>>>>> 59eefa2d2951eda7abc8e9edf3d15297ddf67ad3
