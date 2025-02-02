import time
from bs4 import Tag
from tqdm import tqdm
from typing import List
from slugify import slugify
from datetime import datetime
from urllib.parse import urljoin
from collections import defaultdict

from config import Config
from src.crawler.base import BaseCrawler, News


class Dantri(BaseCrawler):

    def __init__(self, *args, **kwargs):
        super().__init__(parent_url="https://dantri.com.vn/", *args, **kwargs)

    def _scrape_news(self, url: str, *args, **kwargs):
        """
        Getting the details of a news.

        Args:
        -----------
        url: str
            The url of the news.

        Returns:
        -----------
        news: News
            The news object.
        """
        news_soup = self._fetch(url, *args, **kwargs)
        title = news_soup.find("h1", class_="title-page detail")
        author_name = news_soup.select_one(
            "div.author-wrap > div.author-meta > div.author-name"
        )
        author_time = news_soup.select_one(
            "div.author-wrap > div.author-meta > time.author-time"
        )
        div_content = news_soup.select_one("div.singular-content")

        if all([title, author_name, author_time, div_content]):
            return News(
                title=title.text,
                author=author_name.text,
                created_at=datetime.strptime(
                    author_time.get("datetime"), "%Y-%m-%d %H:%M"
                ),
                content=div_content.text,
                url=url,
            )
        return None

    def _scrape_topic(self, url: str, n_th_page: int = 1, *args, **kwargs):
        """
        Scraping links from topic.

        Args:
        -----------
        url: str
            url of the topic (including pagination).
        n_th_page: int
            The n-th page of the topic.

        Returns:
        -----------
        news_links: List[str]
            List of news links in the topic.
        """
        # Sleep for a while
        time.sleep(Config.SLEEP_TIME)

        # Check if the number of pagination is greater than the maximum pagination
        max_pagination = kwargs.get("max_pagination", Config.MAX_PAGINATION)

        # If the number of pagination is greater than the maximum pagination, return an empty list
        if n_th_page > max_pagination:
            return []

        # Get news links
        news_links = []
        topic_soup = self._fetch(url, *args, **kwargs)
        article_tags = topic_soup.select(
            "div#bai-viet > div.main > .article.list > article.article-item"
        )

        news_links.extend(
            [
                article.find("a", href=True).get("href")
                for article in article_tags
                if isinstance(article, Tag)
            ]
        )
        # go the the next page
        next_page_tag = topic_soup.select_one("div.pagination > a.next", href=True)

        if isinstance(next_page_tag, Tag):
            pbar = kwargs.get("pbar")
            if pbar:
                pbar.set_postfix(url=url)

            next_page_url = next_page_tag.get("href")
            news_links.extend(
                self._scrape_topic(
                    urljoin(self.parent_url, next_page_url),
                    n_th_page + 1,
                    *args,
                    **kwargs,
                )
            )

        return news_links

    def crawl(
        self, max_pagination: int = 5, link_only: bool = False, *args, **kwargs
    ) -> List[News] | List[str]:
        """
        Crawl news from Dantri (https://dantri.com.vn/). This method will crawl all news from all topics in the website.

        Args:
        -----------
        n_pagination: int
            Number of pagination to crawl news in each topic. Default is 5.
        link_only: bool
            Return only links which are scraped

        Returns:
        -----------
        news_link (if link_only is set to True)
            All the links of news which are crawled

        news: List[News]
            List of news crawled from Dantri.
        """

        # Exploring topics
        main_page_soup = self._fetch(self.parent_url)
        nav_bar_tag = main_page_soup.find("nav", {"role": "navigation"})
        assert (nav_bar_tag is not None) or isinstance(
            nav_bar_tag, Tag
        ), "Cannot find navigation bar"

        # Get all topics and all of them have childs

        li_tags = [
            li_tag
            for li_tag in nav_bar_tag.find_all("li", class_="has-child")
            if isinstance(li_tag, Tag)
        ]
        assert len(li_tags) > 0, "Cannot find any topics"

        topics = defaultdict(List[str])
        for l_tag in li_tags:
            main_topic = l_tag.find("a")
            topic_key = slugify(main_topic.text.strip())

            sub_menu_tag = l_tag.find("ol", class_="submenu")

            topics[topic_key] = [
                a_tag.get("href")
                for a_tag in sub_menu_tag.find_all("a", href=True)
                if isinstance(a_tag, Tag)
            ]

        print(f"There are {len(topics)} main topics. Start scraping news links ...")
        news_links = []
        for key, val in (pbar := tqdm(topics.items())):
            pbar.set_description(f"Processing {key}")
            topic_links = []
            for v in val:
                topic_links += self._scrape_topic(
                    v, max_pagination=max_pagination, pbar=pbar
                )

            news_links.extend(topic_links)
            pbar.set_postfix(n_news=len(news_links))
            pbar.set_description(f"Sleeping for {Config.SLEEP_TIME}s ...")
            time.sleep(Config.SLEEP_TIME)

        if link_only:
            return news_links

        print("After scraping news links, start scraping news content ...")
        news = []
        for link in (pbar := tqdm(news_links)):
            result = self._scrape_news(link)
            if result:
                news.append(result)
            time.sleep(Config.SLEEP_TIME)

        return news

    def scrape_news(self):
        return self._scrape_news
