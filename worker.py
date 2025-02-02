import time
from queue import Queue
from typing import List
from threading import Thread
from src.crawler.dantri import Dantri


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
        self, queue: Queue, instance: Dantri, timeout: int = 60, sleep_time: float = 0.2
    ):
        Thread.__init__(self)
        self.q = queue
        self.scrape_news = instance.scrape_news()
        self.timeout = timeout
        self.sleep_time = sleep_time

    def run(self):
        while not self.q.empty():
            url = self.q.get(timeout=self.timeout)

            print("Scraping ", url)
            time.sleep(self.sleep_time)
            result = self.scrape_news(url=url)

            # handle more task

            self.q.task_done()
