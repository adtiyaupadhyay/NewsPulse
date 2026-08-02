"""
selenium_scraper.py
---------------------
For sites where content loads via JavaScript AFTER the initial page
load — requests+BeautifulSoup would see an empty shell, since they
only capture the very first server response, before any JS runs.

Selenium instead opens a real (headless = invisible) browser, waits
for the page's JavaScript to finish rendering, THEN grabs the HTML —
so we see the same fully-rendered content a human visitor would see.
"""

import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from scrapers.base_scraper import BaseScraper


class SeleniumScraper(BaseScraper):
    def fetch_html(self) -> str:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        )

        driver = webdriver.Chrome(options=options)
        try:
            driver.get(self.url)
            wait = WebDriverWait(driver, 10)
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.selectors["article_row"])
                )
            )
            return driver.page_source
        finally:
            driver.quit()

    def parse(self, html: str) -> list[dict]:
        """Overrides the base parse() because this source has no
        per-item URL like news articles do — it's quotes, not
        articles with links. So we generate a stable synthetic URL
        by hashing the quote's own text. Same quote text -> same
        hash -> same URL every time -> dedup still works correctly."""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select(self.selectors["article_row"])

        articles = []
        for row in rows:
            title_tag = row.select_one(self.selectors["title"])
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)

            text_hash = hashlib.md5(title.encode()).hexdigest()[:12]
            synthetic_url = f"{self.url}#{text_hash}"

            articles.append({
                "source": self.name,
                "title": title,
                "url": synthetic_url,
            })
        return articles