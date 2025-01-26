from src.crawler.dantri import Dantri


if __name__ == "__main__":
    dantri = Dantri()
    news = dantri.crawl(max_pagination=1)

    print(news[0])
