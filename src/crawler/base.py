import requests
from typing import Dict, Any
from datetime import datetime
from dataclasses import dataclass
from abc import ABC, abstractmethod

from src.crawler.utils import retry, get_soup
from config import Config


@dataclass
class News:
    title: str
    author: str
    created_at: datetime
    content: str
    url: str


class BaseCrawler(ABC):

    def __init__(self, *args, **kwargs):
        self.__timeout = kwargs.get("timeout", 60)
        self.__parent_url = kwargs.get("parent_url", None)
        self.__n_news = kwargs.get("n_news", 100)

        assert self.__parent_url is not None, "parent_url must be provided."

    @classmethod
    def from_dict(cls, config: Dict[str, Any]):
        return cls(config)

    @property
    def timeout(self):
        return self.__timeout

    @property
    def parent_url(self):
        return self.__parent_url

    @property
    def number_of_news(self):
        return self.__n_news

    @get_soup
    @retry(times=Config.RETRY_TIMES)
    def _fetch(self, url: str, *args, **kwargs):
        timeout = kwargs.get("timeout") or self.timeout
        response = requests.get(url, timeout=timeout, headers=Config.HEADER)

        assert response.status_code == 200, "Cannot load page"

        return response.text

    @abstractmethod
    def _scrape_news(self, url: str, *args, **kwargs) -> News:
        raise NotImplementedError("_scrape_news() must be implemented.")

    @abstractmethod
    def crawl(self):
        raise NotImplementedError("crawl() must be implemented.")

    @abstractmethod
    def scrape_news(self, url: str, *args, **kwargs) -> News:
        raise NotImplemented("scrape_news() must be implemented.")
