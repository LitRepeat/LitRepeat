# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticleMetadata(scrapy.Item):
    """Metadata about a scholarly article, provider-agnostic."""

    url = scrapy.Field()           # Original URL used for the request
    doi = scrapy.Field()           # Digital Object Identifier
    title = scrapy.Field()         # Article title
    authors = scrapy.Field()       # List of author names
    abstract = scrapy.Field()      # Abstract text
    publication_date = scrapy.Field()  # Publication date string
    venue = scrapy.Field()         # Journal / conference / proceedings name
    pages = scrapy.Field()         # Page range, e.g. "15-26"
    publisher = scrapy.Field()     # Publisher name
    provider = scrapy.Field()      # Data-provider identifier, e.g. "acm"
    bibtex = scrapy.Field()        # BibTeX citation string
