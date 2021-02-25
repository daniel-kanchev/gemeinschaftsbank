import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from gemeinschaftsbank.items import Article


class GemeinschaftsbankSpider(scrapy.Spider):
    name = 'gemeinschaftsbank'
    start_urls = ['https://www.gemeinschaftsbank.ch/aktuelles?command=archive']

    def parse(self, response):
        links = response.xpath('//h4/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('(//div[@id="pagination"]//a)[last()]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@id="middle"]/p/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@id="middle"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[3:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
