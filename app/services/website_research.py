"""
Official Website Research Service for MSME Compliance & Schemes.
Features:
  - Strict SSRF (Server-Side Request Forgery) protection
  - Domain allowlist (.gov.in, .nic.in, .org.in, cgtmse.in, sidbi.in, etc.)
  - Private IP and Cloud Metadata IP rejection (127.0.0.1, 10.0.0.0/8, 192.168.0.0/16, 169.254.169.254)
  - Enforced response timeouts and size caps (max 2MB)
  - Structured extraction of requirements, checklists, and authorities
"""
import socket
import ipaddress
import urllib.parse
from datetime import datetime
import re
import requests
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

ALLOWED_DOMAIN_PATTERNS = [
    r'\.gov\.in$',
    r'\.nic\.in$',
    r'\.org\.in$',
    r'\.ac\.in$',
    r'cgtmse\.in$',
    r'sidbi\.in$',
    r'jansamarth\.in$',
    r'startupindia\.gov\.in$',
    r'investindia\.gov\.in$',
    r'standupmitra\.in$',
    r'gem\.gov\.in$',
    r'nsws\.gov\.in$'
]

DISALLOWED_IPS = [
    ipaddress.ip_network('127.0.0.0/8'),
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('169.254.0.0/16'),  # Cloud metadata IP range
    ipaddress.ip_network('0.0.0.0/8'),
    ipaddress.ip_network('::1/128'),
    ipaddress.ip_network('fc00::/7'),
    ipaddress.ip_network('fe80::/10')
]

class SSRFProtectionError(ValueError):
    pass

class WebsiteResearchService:
    def __init__(self, timeout=8, max_bytes=2 * 1024 * 1024):
        self.timeout = timeout
        self.max_bytes = max_bytes

    def is_domain_allowed(self, hostname: str) -> bool:
        """Checks whether the hostname is an authorized official Indian portal or scheme domain."""
        if not hostname:
            return False
        hostname = hostname.lower().strip()
        for pat in ALLOWED_DOMAIN_PATTERNS:
            if re.search(pat, hostname):
                return True
        return False

    def validate_target_url(self, url: str) -> str:
        """
        Validates URL scheme, domain allowlist, and IP address to prevent SSRF.
        Raises SSRFProtectionError if validation fails.
        """
        if not url:
            raise SSRFProtectionError("URL cannot be empty")

        parsed = urllib.parse.urlparse(url.strip())
        if parsed.scheme not in ('http', 'https'):
            raise SSRFProtectionError(f"Unsupported scheme '{parsed.scheme}'. Only http and https are allowed.")

        hostname = parsed.hostname
        if not hostname:
            raise SSRFProtectionError("Invalid URL: missing hostname")

        # Allow localhost ONLY if strictly running in simulated test mode via flag
        if not self.is_domain_allowed(hostname):
            raise SSRFProtectionError(
                f"Domain '{hostname}' is not in the official portal allowlist. "
                "Only official Indian government and scheme domains (*.gov.in, *.nic.in, *.org.in, cgtmse.in, sidbi.in, etc.) are permitted."
            )

        # Resolve IP to verify non-private / non-loopback
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            ip_addrs = [item[4][0] for item in addr_info]
        except Exception as e:
            raise SSRFProtectionError(f"Unable to resolve host '{hostname}': {e}")

        for ip_str in ip_addrs:
            try:
                ip_obj = ipaddress.ip_address(ip_str)
            except ValueError:
                continue

            for subnet in DISALLOWED_IPS:
                if ip_obj in subnet:
                    raise SSRFProtectionError(f"SSRF violation: Host '{hostname}' resolves to private/internal IP {ip_str}.")

        return url.strip()

    def research_official_portal(self, url: str) -> dict:
        """
        Safely fetches and analyzes an official government or regulatory portal.
        Extracts structural headings, document requirements, and summary.
        """
        clean_url = self.validate_target_url(url)
        headers = {
            'User-Agent': 'MSMENavigatorIndia-ResearchBot/2.0 (+https://msmenavigator.gov.in/bot-policy)'
        }

        try:
            with requests.get(clean_url, headers=headers, timeout=self.timeout, stream=True) as resp:
                if resp.status_code != 200:
                    return {
                        'success': False,
                        'url': clean_url,
                        'error': f"Target portal returned HTTP status {resp.status_code}"
                    }

                content_chunks = []
                bytes_read = 0
                for chunk in resp.iter_content(chunk_size=8192):
                    content_chunks.append(chunk)
                    bytes_read += len(chunk)
                    if bytes_read > self.max_bytes:
                        break

                html_content = b"".join(content_chunks).decode('utf-8', errors='ignore')

            if BeautifulSoup is not None:
                soup = BeautifulSoup(html_content, 'html.parser')

                # Remove scripts, styles, navigations
                for s in soup(['script', 'style', 'nav', 'footer', 'aside']):
                    s.decompose()

                title = (soup.title.string or '').strip() if soup.title else 'Official Portal'
                headings = [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3']) if h.get_text().strip()][:10]

                # Extract body text
                paragraphs = [p.get_text().strip() for p in soup.find_all('p') if len(p.get_text().strip()) > 20]
                main_text = "\n\n".join(paragraphs[:15])

                # Extract document requirements or checklists
                checklist_items = []
                for li in soup.find_all('li'):
                    text = li.get_text().strip()
                    if any(w in text.lower() for w in ['pan', 'aadhaar', 'udyam', 'certificate', 'gst', 'bank', 'itr', 'financial', 'statement', 'turnover']):
                        if 10 < len(text) < 200:
                            checklist_items.append(text)

                # Deduplicate checklist
                unique_docs = list(dict.fromkeys(checklist_items))[:10]
            else:
                title = 'Official Portal'
                headings = []
                main_text = re.sub(r'<[^>]+>', ' ', html_content)[:1000]
                unique_docs = []

            return {
                'success': True,
                'url': clean_url,
                'domain': urllib.parse.urlparse(clean_url).hostname,
                'title': title,
                'headings': headings,
                'summary_text': main_text[:2000],
                'extracted_checklist': unique_docs,
                'fetched_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
            }

        except requests.RequestException as e:
            return {
                'success': False,
                'url': clean_url,
                'error': f"Failed to connect to official portal: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'url': clean_url,
                'error': f"Processing error: {str(e)}"
            }

website_research_service = WebsiteResearchService()
