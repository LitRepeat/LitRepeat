# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import re
import unicodedata
from pathlib import Path

from itemadapter import ItemAdapter


OUTPUT_DIR = Path("output")


def slugify_title(title: str) -> str:
    """Convert a title to a shell-path-friendly slug.

    - Capitalise first letter, lower-case the rest
    - Remove punctuation
    - Replace whitespace runs with a single dash
    """
    # Capitalise first letter, lower-case remainder
    title = title.capitalize()
    # Strip accents / combining marks (optional, keeps ASCII-clean paths)
    title = unicodedata.normalize("NFKD", title)
    title = "".join(c for c in title if not unicodedata.combining(c))
    # Remove anything that is not alphanumeric or whitespace
    title = re.sub(r"[^\w\s]", "", title)
    # Collapse whitespace to single dashes
    title = re.sub(r"\s+", "-", title).strip("-")
    return title


def extract_year(date_str: str) -> str:
    """Pull a 4-digit year from a date string, or return 'Unknown'."""
    m = re.search(r"\b(\d{4})\b", date_str)
    return m.group(1) if m else "Unknown"


class JsonFilePipeline:
    """Write each item to  output/<Year>-<Title>.json"""

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        year = extract_year(adapter.get("publication_date", ""))
        title = adapter.get("title", "untitled") or "untitled"
        slug = slugify_title(title)

        OUTPUT_DIR.mkdir(exist_ok=True)
        stem = f"{year}-{slug}"

        # Write JSON
        json_path = OUTPUT_DIR / f"{stem}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            # Exclude bibtex from the JSON (it gets its own file)
            data = {k: v for k, v in adapter.asdict().items() if k != "bibtex"}
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Write BibTeX with reference name matching the filename stem
        bibtex = adapter.get("bibtex", "")
        if bibtex:
            # Replace the original citation key with our Year-Title stem
            bibtex = re.sub(
                r"(@\w+\{)[^,]+,",
                rf"\g<1>{stem},",
                bibtex,
                count=1,
            )
            bib_path = OUTPUT_DIR / f"{stem}.bib"
            with open(bib_path, "w", encoding="utf-8") as f:
                f.write(bibtex)
            spider.logger.info(f"Wrote {bib_path}")

        spider.logger.info(f"Wrote {json_path}")
        return item
