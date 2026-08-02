# NewsPulse — AI-Powered News Intelligence Pipeline

A pipeline that scrapes news sources, deduplicates and stores articles,
and (in later phases) uses an LLM to summarize/classify them and
visualizes trends on a dashboard.

## Current Status: Phase 1 complete

- [x] Config-driven source management (`config.py`)
- [x] Base scraper design (static scraping working, Selenium slot ready)
- [x] SQLite storage with dedup (won't insert the same URL twice)
- [x] Pipeline orchestrator with per-source error isolation
- [ ] Phase 2: AI summarization + classification (Claude API, JSON-mode prompting)
- [ ] Phase 3: Streamlit dashboard (trends, sentiment charts)
- [ ] Phase 4: Excel export + scheduled automation

## Setup

```bash
pip install -r requirements.txt
python pipeline.py
```

First run creates `newspulse.db` (SQLite) automatically.

## Architecture

```
config.py           <- add/remove news sources here, nowhere else
database.py         <- SQLite storage, dedup logic
scrapers/
  base_scraper.py    <- abstract class: fetch_html() + parse()
  static_scraper.py  <- requests-based, for sites with no JS rendering needed
pipeline.py          <- orchestrator: scrape all sources -> dedup -> store
```

## Design decisions worth noting

- **Config-driven sources**: adding a new site means adding a dict to
  `config.py`, not writing new scraper code.
- **Abstract base scraper**: `fetch_html()` differs by scraper type
  (requests vs Selenium), but `parse()` is shared — the pipeline treats
  every scraper identically.
- **Dedup at two layers**: an explicit check before insert (cheap,
  readable) plus a `UNIQUE` constraint on the `url` column as a safety
  net against race conditions.
- **Per-source error isolation**: if one source fails to scrape (site
  down, structure changed), the pipeline logs it and keeps going
  instead of crashing the whole run.

## A note on testing

This was built and verified inside a sandboxed environment with no
general internet access. `test_parsing_offline.py` proves the HTML
parsing logic is correct using a real Hacker News HTML structure as a
fixture. `fetch_html()` (the actual network call) should be verified
on your own machine with real internet access — run
`python -c "from scrapers.static_scraper import StaticScraper; from config import SOURCES; print(StaticScraper(SOURCES[0]).scrape())"`
