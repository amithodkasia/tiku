# 🕷️ Tiku Web Crawler

**Tiku** is an advanced Python-based asynchronous web crawler designed for recon, endpoint discovery, and security testing. It supports JS rendering, form detection, subdomain crawling, Wayback URL fetching, and integrates with tools like **Nuclei**.

## 🚀 Features
- 🔁 Crawl Depth Control
- 📜 JS File Extraction
- 🧾 Form Detection
- 🕸 Subdomain Discovery
- 🕰 Wayback Machine URL Integration
- 🍪 Auth Header & Cookie Support
- ⚡ Async Crawling (via aiohttp)
- 🧠 Static + JS Endpoint Extraction
- 🔍 Technology Fingerprinting
- 🧪 Security Header Analysis (CSP, X-Frame, etc.)
- ⚠️ GF-style Vulnerability Filtering (XSS, SQLi, etc.)
- 🧨 Nuclei Scanner Integration
- 📊 CSV/JSON Output Format

## ✅ Requirements
Install dependencies:
```bash
pip install -r requirements.txt
```
Required Packages:
- aiohttp==3.8.1
- beautifulsoup4==4.11.1
- requests-html==0.10.0
- tldextract==3.2.0

## 🧪 Compatibility
✅ Works with Python 3.7+ (tested on 3.7–3.11)  
❌ Python 2.x is not supported

## 🔧 Installation
Clone the repository:
```bash
git clone https://github.com/amithodkasia/tiku.git
cd tiku
```
Install dependencies:
```bash
pip install -r requirements.txt
```

## 🧪 Usage
```bash
python tiku.py -u <target-url> [options]
```
Example:
```bash
python tiku.py -u https://example.com -d 2 --use-js --wayback --filter --output result.json --format json
```

## 📦 Output Format
Supports JSON and CSV.

## 🔐 Integrations
- Nuclei Scanner
- Wayback Machine

## 📸 Coming Soon
- Screenshot support
- Directory brute-forcing
- Gau integration

## 🛠 Maintainer
- 👤 Amit Hodkasia
- 🔗 https://github.com/amithodkasia

## 📜 License
MIT License
