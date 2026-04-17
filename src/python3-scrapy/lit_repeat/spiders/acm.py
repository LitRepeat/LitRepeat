import re

import scrapy

from lit_repeat.items import ArticleMetadata


class AcmSpider(scrapy.Spider):
    """Spider that extracts article metadata from ACM Digital Library pages.

    Usage:
        scrapy crawl acm -a url=https://dl.acm.org/doi/abs/10.1145/1232425.1232431
    """

    name = "acm"
    allowed_domains = ["dl.acm.org"]

    # Expect a single URL passed via -a url=...
    def __init__(self, url: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if url is None:
            raise ValueError("Please provide a url argument: -a url=<ACM URL>")
        self.start_url = url

    def start_requests(self):
        # ACM exposes richer metadata on the full (non-abstract) page.
        url = self.start_url.replace("/doi/abs/", "/doi/")
        yield scrapy.Request(
            url,
            callback=self.parse,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                # Wait until network is idle so JS-rendered content is available
                "playwright_page_goto_kwargs": {
                    "wait_until": "networkidle",
                },
            },
        )

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    async def parse(self, response):
        page = response.meta["playwright_page"]

        item = ArticleMetadata()
        item["url"] = self.start_url
        item["provider"] = "acm"

        # --- DOI ----------------------------------------------------------
        doi = response.xpath(
            '//meta[@name="dc.Identifier" and @scheme="doi"]/@content'
        ).get()
        if doi is None:
            # Try to extract from the URL itself
            m = re.search(r"(10\.\d{4,9}/[^\s]+)", self.start_url)
            doi = m.group(1) if m else None
        item["doi"] = doi

        # --- Title --------------------------------------------------------
        item["title"] = (
            response.css("h1 ::text").get("")
            or response.xpath('//meta[@name="dc.Title"]/@content').get("")
        ).strip()

        # --- Authors ------------------------------------------------------
        # Build "Given Family" pairs from structured author markup
        authors = []
        for author_el in response.css('[property="author"]'):
            given = author_el.css('[property="givenName"] ::text').get("")
            family = author_el.css('[property="familyName"] ::text').get("")
            full = f"{given} {family}".strip()
            if full and full not in authors:
                authors.append(full)
        item["authors"] = authors

        # --- Abstract -----------------------------------------------------
        # ACM uses <div role="paragraph"> instead of <p> for abstract text
        abstract_parts = response.css(
            '[role="doc-abstract"] [role="paragraph"] ::text'
        ).getall()
        if not abstract_parts:
            abstract_parts = response.css(
                '[role="doc-abstract"] p ::text'
            ).getall()
        item["abstract"] = " ".join(p.strip() for p in abstract_parts).strip()

        # --- Publication date ---------------------------------------------
        item["publication_date"] = (
            response.css(".core-date-published ::text").get("")
            or response.xpath('//meta[@name="dc.Date"]/@content').get("")
        ).strip()

        # --- Venue --------------------------------------------------------
        item["venue"] = (
            response.css(".book-meta ::text").get("")
            or response.xpath(
                '//meta[@name="citation_conference_title"]/@content'
            ).get("")
            or response.xpath(
                '//meta[@name="citation_journal_title"]/@content'
            ).get("")
        ).strip()

        # --- Pages --------------------------------------------------------
        first = response.xpath(
            '//meta[@name="citation_firstpage"]/@content'
        ).get("")
        last = response.xpath(
            '//meta[@name="citation_lastpage"]/@content'
        ).get("")
        if first and last:
            item["pages"] = f"{first}-{last}"
        elif first:
            item["pages"] = first
        else:
            item["pages"] = ""

        # --- Publisher ----------------------------------------------------
        item["publisher"] = (
            response.css(".publisher__name ::text").get("")
            or response.xpath('//meta[@name="dc.Publisher"]/@content').get("")
        ).strip()

        # Fetch BibTeX via the browser's own session using doi.org content negotiation
        bibtex = ""
        try:
            bibtex = await page.evaluate(
                """async (doi) => {
                    const resp = await fetch('https://doi.org/' + doi, {
                        headers: {'Accept': 'application/x-bibtex'}
                    });
                    if (resp.ok) return await resp.text();
                    return '';
                }""",
                item["doi"],
            )
        except Exception as e:
            self.logger.warning(f"Failed to fetch BibTeX: {e}")
        finally:
            await page.close()

        item["bibtex"] = bibtex.strip()
        yield item
