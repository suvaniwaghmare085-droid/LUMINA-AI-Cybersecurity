"""Offline URL feature analysis. LUMINA never opens or fetches submitted URLs."""
from urllib.parse import urlparse
import ipaddress
import re

SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "cutt.ly", "ow.ly"}
SUSPICIOUS_WORDS = {"login", "verify", "secure", "update", "account", "banking", "wallet", "prize", "claim", "gift", "password"}

def analyze_url(raw_url):
    value = str(raw_url or "").strip()
    if not value:
        raise ValueError("Please enter a URL.")
    if len(value) > 2048:
        raise ValueError("URL is too long (maximum 2048 characters).")
    candidate = value if "://" in value else "https://" + value
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("That does not look like a valid HTTP or HTTPS URL.")
    host = parsed.hostname.lower().rstrip(".")
    reasons = []
    points = 0

    if parsed.scheme == "http":
        reasons.append("Uses unencrypted HTTP instead of HTTPS")
        points += 12
    if "@" in parsed.netloc:
        reasons.append("Contains an @ symbol that can disguise the actual destination")
        points += 25
    if host.startswith("xn--") or ".xn--" in host:
        reasons.append("Contains an internationalized/punycode domain")
        points += 20
    try:
        ipaddress.ip_address(host)
        reasons.append("Uses a raw IP address instead of a familiar domain")
        points += 25
    except ValueError:
        pass
    if host in SHORTENERS:
        reasons.append("Uses a URL-shortening service that hides the final destination")
        points += 18
    if len(host) > 45:
        reasons.append("Unusually long domain name")
        points += 10
    if host.count(".") >= 4:
        reasons.append("Many subdomain levels")
        points += 12
    if host.count("-") >= 3:
        reasons.append("Several hyphens in the domain")
        points += 10
    if parsed.port:
        reasons.append("Uses a non-default port")
        points += 10
    components = (host + " " + parsed.path + " " + parsed.query).lower()
    found_words = sorted(word for word in SUSPICIOUS_WORDS if re.search(rf"\b{re.escape(word)}\b", components))
    if found_words:
        reasons.append("Contains sensitive-action wording: " + ", ".join(found_words))
        points += min(18, 6 * len(found_words))
    if len(parsed.query) > 120:
        reasons.append("Has an unusually long query string")
        points += 8

    return {
        "normalized_url": candidate,
        "domain": host,
        "signals": reasons,
        "heuristic_score": min(100, points),
        "is_https": parsed.scheme == "https",
    }
