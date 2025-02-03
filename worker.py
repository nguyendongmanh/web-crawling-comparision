import time
import random
import requests
from queue import Queue
from typing import List
from threading import Thread
from datetime import datetime

from config import Config
from src.crawler.base import News
from src.crawler.dantri import Dantri
from src.crawler.utils import get_soup, retry


class Producer(Thread):
    def __init__(self, queue: Queue, urls: List[str]):
        Thread.__init__(self)
        self.q = queue
        self.urls = urls

    def run(self):
        for url in self.urls:
            self.q.put(url)


class Consumer(Thread):
    def __init__(
        self,
        queue: Queue,
        consumer_id: int,
        timeout: int = 60,
        sleep_time: float = 0.2,
        *args,
        **kwargs,
    ):
        Thread.__init__(self)
        self.q = queue
        self.timeout = timeout
        self.sleep_time = sleep_time
        self.consumer_id = consumer_id
        self.progress_bar = kwargs.get("progress_bar")

    def run(self):
        while not self.q.empty():
            url = self.q.get(timeout=self.timeout)
            result = self._scrape_news(url=url)
            # handle more task
            self.q.task_done()

            if self.progress_bar:
                self.progress_bar.update(1)

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
        time.sleep(self.sleep_time)
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

    @get_soup
    @retry(times=Config.RETRY_TIMES)
    def _fetch(self, url: str, *args, **kwargs):

        headers = Config.HEADER
        headers["User-Agent"] = random.choice(Config.USER_AGENTS)

        timeout = kwargs.get("timeout") or self.timeout
        response = requests.get(url, timeout=timeout, headers=headers)

        assert response.status_code == 200, "Cannot load page"

        return response.text
