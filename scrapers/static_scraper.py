"""
static_scraper.py
-------------------
For sites where all the content is already in the HTML the server
sends back — no JavaScript needs to run first. Hacker News is a
good example: view-source on it and you'll see the article titles
sitting right there in plain HTML.
"""

import requests
from scrapers.base_scraper import BaseScraper


class StaticScraper(BaseScraper):
    def fetch_html(self) -> str:
        # A User-Agent header makes our request look like it's coming
        # from a real browser, not a bot. Many sites block requests
        # that don't send one. This is a real, common gotcha —
        # worth mentioning if asked "what problems did you hit?"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }
        response = requests.get(self.url, headers=headers, timeout=10)
        response.raise_for_status()  # throws an error if the site returns 4xx/5xx
        return response.text
