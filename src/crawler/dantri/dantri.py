from src.crawler.base import BaseCrawler


class Dantri(BaseCrawler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _scrape_news(self, url):
        print(f"Scraping {url}")

    def crawl(self):
        print("Crawling data")


if __name__ == "__main__":
    dantri = Dantri(parent_url="https://dantri.com.vn", n_news=10)
    dantri.crawl()
